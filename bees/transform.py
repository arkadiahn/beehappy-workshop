"""Turn per-key timeseries points into table rows.

The API is key-oriented: one list of (ts, value) per measurement key. The
warehouse is row-oriented: one row per (sensor, timestamp) with a column per
key. This module bridges the two.

All keys of a device share an uplink timestamp -- a Dragino D23-LB reports
tempC1/tempC2/tempC3 with the identical `ts` -- so timestamps are the natural
join. Where a key happens to be missing for a timestamp, the column is NULL.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

logger = logging.getLogger(__name__)

# API key -> column name, per destination table.
WEATHER_COLUMNS: dict[str, str] = {
    "temperature": "temperature",
    "relativeHumidity": "humidity",
    "windSpeed": "windspeed",
    "windDirection": "wind_direction",
    "uvIndex": "uv_index",
    "pressure": "air_pressure",       # pascals, stored as reported
    "lightIntensity": "light_intensity",
    "rainGauge": "rain_gauge",
}

HIVE_COLUMNS: dict[str, str] = {
    "tempC1": "temp_c1",
    "tempC2": "temp_c2",
    "tempC3": "temp_c3",
    "temperature": "temperature",
    "relativeHumidity": "relative_humidity",
}

WEATHER_TABLE = "weather"
HIVE_TABLE = "hive_measurements"

# Column order used for every INSERT, so rows are plain tuples.
WEATHER_INSERT_COLUMNS = ("sensor_id", "recorded_at", *WEATHER_COLUMNS.values())
HIVE_INSERT_COLUMNS = ("sensor_id", "recorded_at", *HIVE_COLUMNS.values())


def column_map_for(is_weather_station: bool) -> dict[str, str]:
    return WEATHER_COLUMNS if is_weather_station else HIVE_COLUMNS


def table_for(is_weather_station: bool) -> str:
    return WEATHER_TABLE if is_weather_station else HIVE_TABLE


def insert_columns_for(is_weather_station: bool) -> tuple[str, ...]:
    return WEATHER_INSERT_COLUMNS if is_weather_station else HIVE_INSERT_COLUMNS


def to_utc(ts_ms: int) -> datetime:
    """Epoch milliseconds (UTC, per the spec) -> aware datetime."""
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)


def parse_value(raw: Any) -> float | None:
    """Values arrive as strings; anything non-numeric becomes NULL."""
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        logger.debug("Dropping non-numeric value %r", raw)
        return None
    # NaN/inf would round-trip into Postgres as 'NaN'::float and poison
    # downstream aggregates; a missing reading is more honest.
    return value if value == value and value not in (float("inf"), float("-inf")) else None


def build_rows(
    sensor_id: int,
    points_by_key: Mapping[str, Iterable[tuple[int, Any]]],
    column_map: Mapping[str, str],
    insert_columns: tuple[str, ...],
) -> list[tuple[Any, ...]]:
    """Pivot {key: [(ts_ms, value)]} into rows ordered like `insert_columns`.

    Rows where every measurement column is NULL are dropped -- they carry no
    information and would only take up space and confuse `MAX(recorded_at)`
    watermarking.
    """
    by_timestamp: dict[int, dict[str, float | None]] = {}

    for key, points in points_by_key.items():
        column = column_map.get(key)
        if column is None:
            logger.debug("No column mapped for key %r; skipping", key)
            continue
        for ts_ms, raw in points:
            by_timestamp.setdefault(ts_ms, {})[column] = parse_value(raw)

    measurement_columns = insert_columns[2:]
    rows: list[tuple[Any, ...]] = []

    for ts_ms in sorted(by_timestamp):
        values = by_timestamp[ts_ms]
        if all(values.get(column) is None for column in measurement_columns):
            continue
        rows.append(
            (sensor_id, to_utc(ts_ms), *(values.get(column) for column in measurement_columns))
        )

    return rows
