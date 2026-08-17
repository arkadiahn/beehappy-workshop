"""Client for the Bildungscampus Digital Beehive API (OpenAPI v0.8.18).

The API is four GET endpoints, authenticated with an `x-apikey` query
parameter:

    /authGroup                                              -> device groups
    /authGroup/{g}/valueType                                -> keys per group
    /authGroup/{g}/entityId?page=n                          -> devices + latest
    /authGroup/{g}/entityId/{id}/valueType/timeseries       -> history

Two behaviours of the timeseries endpoint drive the design of this module and
are not stated correctly in the spec:

1. The server caps a response at 500 points PER KEY, truncating from the newest
   end. A request spanning more than ~500 readings silently returns only the
   most recent 500 -- there is no flag saying data was dropped.
2. Points come back NEWEST FIRST, even though the spec says "sorted from oldest
   to newest".

So `iter_timeseries` walks backwards: request [start, cursor], keep the batch,
move the cursor to just before the oldest point received, repeat until a short
batch arrives. One key at a time, because the cap is per key and two keys on
the same device can in principle truncate at different points.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Iterator

import requests

logger = logging.getLogger(__name__)

# Server-side cap on points per key per response.
PAGE_LIMIT = 500

# A short batch means we reached the start of the range; a full one means we
# were probably truncated and must page again.
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


class BeehiveAPIError(RuntimeError):
    """A request failed in a way retrying will not fix."""


@dataclass(frozen=True)
class Device:
    """One device as described by /entityId, with its latest values."""

    entity_id: str
    auth_group: str
    name: str
    device_type: str
    latitude: float | None
    longitude: float | None
    location: str | None
    timeseries_keys: tuple[str, ...]

    @property
    def is_weather_station(self) -> bool:
        return "S2120" in self.device_type


@dataclass(frozen=True)
class Point:
    ts_ms: int
    value: str


class DigitalBeehiveClient:
    """Thin, retrying wrapper over the four endpoints."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 4,
        session: requests.Session | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._session = session or requests.Session()

    # ------------------------------------------------------------------ HTTP

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}/{path.lstrip('/')}"
        query = dict(params or {})
        query["x-apikey"] = self._api_key

        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._session.get(url, params=query, timeout=self._timeout)
            except requests.RequestException as exc:
                last_error = exc
                logger.warning(
                    "GET %s failed (%s), attempt %d/%d", path, exc, attempt, self._max_retries
                )
            else:
                if response.status_code == 200:
                    return response.json()

                # 400/403 are our fault (bad key, bad range, no rights).
                # Retrying sends the same request and gets the same answer.
                if response.status_code not in RETRY_STATUS:
                    raise BeehiveAPIError(
                        f"GET {path} -> HTTP {response.status_code}: "
                        f"{_safe_body(response)}"
                    )

                last_error = BeehiveAPIError(
                    f"GET {path} -> HTTP {response.status_code}: {_safe_body(response)}"
                )
                logger.warning(
                    "GET %s -> HTTP %d, attempt %d/%d",
                    path, response.status_code, attempt, self._max_retries,
                )

            if attempt < self._max_retries:
                time.sleep(2 ** (attempt - 1))

        raise BeehiveAPIError(f"GET {path} failed after {self._max_retries} attempts") from last_error

    # -------------------------------------------------------------- metadata

    def auth_groups(self) -> list[str]:
        payload = self._get("/authGroup")
        return [g["authGroupName"] for g in payload.get("authGroup", [])]

    def timeseries_keys(self, auth_group: str) -> list[str]:
        """Keys this group is allowed to expose.

        Asking for a key outside this list makes the whole request fail with
        400 "Forbidden keys used", so we always request from this list rather
        than from a hardcoded set.
        """
        payload = self._get(f"/authGroup/{auth_group}/valueType")
        entries = payload.get("valueType", {}).get("TIME_SERIES", [])
        return [entry["key"] for entry in entries]

    def devices(self, auth_group: str) -> list[Device]:
        """All devices in a group, following pagination."""
        devices: list[Device] = []
        page = 0
        while True:
            payload = self._get(f"/authGroup/{auth_group}/entityId", {"page": page})
            for entity in payload.get("entities", []):
                devices.append(_parse_device(entity, auth_group))

            if not payload.get("hasNext"):
                break
            page += 1

            if page > 1000:  # pragma: no cover - runaway guard
                raise BeehiveAPIError(f"{auth_group}: entityId pagination did not terminate")

        return devices

    # ------------------------------------------------------------ timeseries

    def iter_timeseries(
        self,
        auth_group: str,
        entity_id: str,
        key: str,
        start_ms: int,
        end_ms: int,
    ) -> Iterator[Point]:
        """Yield every point for one key in [start_ms, end_ms], oldest last.

        Pages backwards from `end_ms` because the server truncates to the 500
        most recent points per response.
        """
        if start_ms > end_ms:
            return

        cursor = end_ms
        seen_ts: set[int] = set()
        requests_made = 0

        while cursor >= start_ms:
            payload = self._get(
                f"/authGroup/{auth_group}/entityId/{entity_id}/valueType/timeseries",
                {"keys": key, "startTs": start_ms, "endTs": cursor},
            )
            requests_made += 1
            batch = payload.get("timeseries", {}).get(key, [])
            if not batch:
                return

            oldest = None
            for raw in batch:
                ts = int(raw["ts"])
                oldest = ts if oldest is None else min(oldest, ts)
                # A batch boundary can repeat a point; dedupe so downstream
                # row-building never sees the same timestamp twice.
                if ts not in seen_ts:
                    seen_ts.add(ts)
                    yield Point(ts_ms=ts, value=raw["value"])

            # Short batch => the range is exhausted, not truncated.
            if len(batch) < PAGE_LIMIT or oldest is None:
                return

            # Strictly decreasing, so the loop always terminates.
            cursor = oldest - 1

            if requests_made > 5000:  # pragma: no cover - runaway guard
                raise BeehiveAPIError(
                    f"{entity_id}/{key}: timeseries pagination did not terminate"
                )


def _parse_device(entity: dict[str, Any], auth_group: str) -> Device:
    fields = entity.get("ENTITY_FIELD", {})
    attributes = entity.get("SERVER_ATTRIBUTE", {})
    series = entity.get("TIME_SERIES", {})

    return Device(
        entity_id=entity["entityId"]["id"],
        auth_group=auth_group,
        name=fields.get("name", ""),
        device_type=fields.get("type", ""),
        latitude=_attribute_as_float(attributes, "latitude"),
        longitude=_attribute_as_float(attributes, "longitude"),
        location=_attribute_as_string(attributes, "location"),
        timeseries_keys=tuple(sorted(series)),
    )


def _attribute_as_string(attributes: dict[str, Any], key: str) -> str | None:
    """Server attributes are {"ts": ..., "value": ...}; unset ones are "" at ts 0."""
    entry = attributes.get(key)
    if not isinstance(entry, dict):
        return None
    value = str(entry.get("value", "")).strip()
    return value or None


def _attribute_as_float(attributes: dict[str, Any], key: str) -> float | None:
    value = _attribute_as_string(attributes, key)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        logger.debug("Ignoring non-numeric %s=%r", key, value)
        return None


def _safe_body(response: requests.Response) -> str:
    """Error text for logs, truncated and never containing the API key."""
    try:
        body = response.json()
        text = body.get("errorText", str(body)) if isinstance(body, dict) else str(body)
    except ValueError:
        text = response.text
    return text[:300]
