"""Runtime settings and the hive/sensor topology.

Two kinds of configuration live here:

`Settings`  -- credentials and knobs, read from the environment / .env.
`Topology`  -- which physical hive each device belongs to, read from hives.toml.
              The API cannot tell us this, so a human maintains it.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, urlsplit, urlunsplit

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_BASE_URL = "https://apis.smartcity.hn/bildungscampus/iotplatform/digitalbeehive/v1"


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    """Everything the pipeline needs that is not the hive topology."""

    api_key: str
    database_url: str
    base_url: str = DEFAULT_BASE_URL

    # How far back the first load reaches when a sensor has no rows yet.
    backfill_days: int = 90

    # On incremental runs, re-request this much time before the newest row we
    # already hold. Guards against readings that reach the platform late; the
    # upserts make the overlap free.
    overlap_minutes: int = 60

    # HTTP behaviour.
    request_timeout: int = 30
    max_retries: int = 4

    # Rows sent to Postgres per executemany batch.
    batch_size: int = 1000

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "Settings":
        load_dotenv(env_file or PROJECT_ROOT / ".env")

        api_key = os.getenv("BILDUNGSCAMPUS_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "BILDUNGSCAMPUS_API_KEY is not set. Add it to .env "
                "(get one at https://data-library.smartcity.hn/my-apps/new-app)."
            )

        return cls(
            api_key=api_key,
            database_url=_database_url(),
            base_url=os.getenv("BEEHIVE_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            backfill_days=_env_int("BEEHIVE_BACKFILL_DAYS", 90),
            overlap_minutes=_env_int("BEEHIVE_OVERLAP_MINUTES", 60),
            request_timeout=_env_int("BEEHIVE_REQUEST_TIMEOUT", 30),
            max_retries=_env_int("BEEHIVE_MAX_RETRIES", 4),
            batch_size=_env_int("BEEHIVE_BATCH_SIZE", 1000),
        )


# Hosts reachable without crossing the public internet, so TLS is not forced.
# Railway's private network resolves service names under *.railway.internal.
_TRUSTED_HOST_SUFFIXES = (".railway.internal", ".internal", ".local")
_TRUSTED_HOSTS = ("localhost", "127.0.0.1", "::1", "")


def _database_url() -> str:
    """Resolve the connection string.

    Order matters for Railway. Inside a Railway service, DATABASE_URL is set to
    the private-network address (no egress charge). From a laptop that host does
    not resolve, so DATABASE_PUBLIC_URL -- the TCP proxy -- is used instead.
    Falling back to the standard PG* variables keeps plain local setups working.
    """
    for variable in ("DATABASE_URL", "DATABASE_PUBLIC_URL"):
        url = os.getenv(variable, "").strip()
        if url:
            return _require_ssl_if_remote(url)

    user = os.getenv("PGUSER", os.getenv("USER", "postgres"))
    password = os.getenv("PGPASSWORD", "")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    database = os.getenv("PGDATABASE", "bees")

    credentials = f"{user}:{password}@" if password else f"{user}@"
    return _require_ssl_if_remote(f"postgresql://{credentials}{host}:{port}/{database}")


def _require_ssl_if_remote(url: str) -> str:
    """Add sslmode=require when the connection leaves the machine.

    Railway's public proxy carries credentials over the open internet, and
    libpq's default (sslmode=prefer) silently accepts a plaintext connection if
    the server offers one. An explicit sslmode in the URL is always respected.
    """
    parsed = urlsplit(url)
    if "sslmode" in parse_qs(parsed.query):
        return url

    host = (parsed.hostname or "").lower()
    if host in _TRUSTED_HOSTS or host.endswith(_TRUSTED_HOST_SUFFIXES):
        return url

    query = f"{parsed.query}&sslmode=require" if parsed.query else "sslmode=require"
    return urlunsplit(parsed._replace(query=query))


@dataclass(frozen=True)
class HiveSpec:
    hive_name: str
    sensors: tuple[str, ...]
    comment: str | None = None
    installation_date: str | None = None
    last_inspection_date: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass(frozen=True)
class Topology:
    """Declared hives plus the device -> hive lookup derived from them."""

    hives: tuple[HiveSpec, ...] = ()
    unassigned: tuple[str, ...] = ()
    default_latitude: float | None = None
    default_longitude: float | None = None
    hive_by_sensor: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | None = None) -> "Topology":
        path = path or PROJECT_ROOT / "hives.toml"
        if not path.exists():
            # A missing topology file is not fatal: every device is simply
            # loaded with hive_id = NULL. Measurements are still captured.
            return cls()

        with path.open("rb") as handle:
            raw = tomllib.load(handle)

        defaults = raw.get("defaults", {})
        hives: list[HiveSpec] = []
        hive_by_sensor: dict[str, str] = {}

        for entry in raw.get("hives", []):
            name = entry.get("hive_name")
            if not name:
                raise ValueError(f"{path}: every [[hives]] entry needs a hive_name")

            sensors = tuple(entry.get("sensors", ()))
            for sensor_name in sensors:
                if sensor_name in hive_by_sensor:
                    raise ValueError(
                        f"{path}: sensor {sensor_name!r} is assigned to both "
                        f"{hive_by_sensor[sensor_name]!r} and {name!r}"
                    )
                hive_by_sensor[sensor_name] = name

            hives.append(
                HiveSpec(
                    hive_name=name,
                    sensors=sensors,
                    comment=entry.get("comment"),
                    installation_date=_as_date_string(entry.get("installation_date")),
                    last_inspection_date=_as_date_string(entry.get("last_inspection_date")),
                    latitude=entry.get("latitude", defaults.get("latitude")),
                    longitude=entry.get("longitude", defaults.get("longitude")),
                )
            )

        return cls(
            hives=tuple(hives),
            unassigned=tuple(raw.get("unassigned", {}).get("sensors", ())),
            default_latitude=defaults.get("latitude"),
            default_longitude=defaults.get("longitude"),
            hive_by_sensor=hive_by_sensor,
        )

    def hive_for(self, sensor_name: str) -> str | None:
        return self.hive_by_sensor.get(sensor_name)

    def is_known(self, sensor_name: str) -> bool:
        return sensor_name in self.hive_by_sensor or sensor_name in self.unassigned


def _as_date_string(value: object) -> str | None:
    """TOML dates arrive as datetime.date; everything else passes through."""
    if value is None:
        return None
    return value.isoformat() if hasattr(value, "isoformat") else str(value)
