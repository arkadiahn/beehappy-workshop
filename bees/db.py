"""Postgres load layer: schema setup, dimension upserts, fact inserts."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

import psycopg
from psycopg import sql

from bees.config import PROJECT_ROOT, HiveSpec

logger = logging.getLogger(__name__)

SCHEMA_PATH = PROJECT_ROOT / "data_schema.sql"

# VARCHAR widths in data_schema.sql, so an over-long value degrades to a
# warning instead of aborting a multi-hour backfill.
SENSOR_NAME_MAX = 50
SENSOR_TYPE_MAX = 50


def connect(database_url: str, connect_timeout: int = 15) -> psycopg.Connection:
    """Open a connection. Autocommit is off: each phase commits explicitly.

    The keepalive settings matter for a hosted database (Railway, RDS, ...):
    a backfill spends most of its wall-clock waiting on the beehive API, and an
    idle TCP connection crossing a cloud NAT is liable to be silently dropped.
    Without keepalives the next INSERT fails on a connection that still looks
    open. These are libpq defaults everywhere except the aggressive idle time.
    """
    return psycopg.connect(
        database_url,
        connect_timeout=connect_timeout,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
        application_name="the_bees_etl",
    )


def init_schema(conn: psycopg.Connection, schema_path: Path | None = None) -> None:
    """Apply data_schema.sql. Every statement is CREATE ... IF NOT EXISTS."""
    path = schema_path or SCHEMA_PATH
    logger.info("Applying schema from %s", path)
    with conn.cursor() as cur:
        cur.execute(path.read_text())
    conn.commit()


# ------------------------------------------------------------------ helpers


def as_point(latitude: float | None, longitude: float | None) -> str | None:
    """Postgres POINT literal, x = longitude and y = latitude."""
    if latitude is None or longitude is None:
        return None
    return f"({longitude},{latitude})"


def _truncate(value: str | None, limit: int, label: str) -> str | None:
    if value is not None and len(value) > limit:
        logger.warning("Truncating %s %r to %d characters", label, value, limit)
        return value[:limit]
    return value


def _chunked(rows: Sequence[Any], size: int) -> Iterator[Sequence[Any]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


# --------------------------------------------------------------- dimensions


def upsert_hive(conn: psycopg.Connection, spec: HiveSpec) -> int:
    """Insert or refresh one hive; return its id.

    hives.toml is authoritative for the fields it declares. Fields it leaves
    out keep whatever a human entered directly in the database -- notably
    last_inspection_date, which the API knows nothing about.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO hives (hive_name, location, installation_date,
                               last_inspection_date, comment)
            VALUES (%s, %s::point, %s::date, %s::date, %s)
            ON CONFLICT (hive_name) DO UPDATE SET
                location             = COALESCE(EXCLUDED.location, hives.location),
                installation_date    = COALESCE(EXCLUDED.installation_date,
                                                hives.installation_date),
                last_inspection_date = COALESCE(EXCLUDED.last_inspection_date,
                                                hives.last_inspection_date),
                comment              = COALESCE(EXCLUDED.comment, hives.comment)
            RETURNING id
            """,
            (
                spec.hive_name[:50],
                as_point(spec.latitude, spec.longitude),
                spec.installation_date,
                spec.last_inspection_date,
                spec.comment,
            ),
        )
        return cur.fetchone()[0]


def upsert_sensor(
    conn: psycopg.Connection,
    sensor_name: str,
    sensor_type: str | None,
    hive_id: int | None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> int:
    """Insert or refresh one sensor; return its id.

    hive_id is rewritten on every run, so moving a device between hives in
    hives.toml moves it in the database too. Historical measurements are not
    rewritten -- they stay attached to the sensor, and the hive they belonged
    to at the time is not recorded per row.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sensors (sensor_name, sensor_type, hive_id, location, is_active)
            VALUES (%s, %s, %s, %s::point, TRUE)
            ON CONFLICT (sensor_name) DO UPDATE SET
                sensor_type = COALESCE(EXCLUDED.sensor_type, sensors.sensor_type),
                hive_id     = EXCLUDED.hive_id,
                location    = COALESCE(EXCLUDED.location, sensors.location),
                is_active   = TRUE
            RETURNING id
            """,
            (
                _truncate(sensor_name, SENSOR_NAME_MAX, "sensor_name"),
                _truncate(sensor_type, SENSOR_TYPE_MAX, "sensor_type"),
                hive_id,
                as_point(latitude, longitude),
            ),
        )
        return cur.fetchone()[0]


def deactivate_missing_sensors(
    conn: psycopg.Connection, seen_sensor_names: Iterable[str]
) -> int:
    """Flag sensors the API no longer lists as inactive. Rows are never deleted."""
    names = list(seen_sensor_names)
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE sensors SET is_active = FALSE "
            "WHERE is_active AND NOT (sensor_name = ANY(%s))",
            (names,),
        )
        return cur.rowcount or 0


# -------------------------------------------------------------------- facts


def watermarks(conn: psycopg.Connection, table: str) -> dict[int, datetime]:
    """Newest recorded_at per sensor, used to resume incremental loads."""
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("SELECT sensor_id, MAX(recorded_at) FROM {} GROUP BY sensor_id").format(
                sql.Identifier(table)
            )
        )
        return {sensor_id: newest for sensor_id, newest in cur.fetchall() if newest}


def insert_measurements(
    conn: psycopg.Connection,
    table: str,
    columns: Sequence[str],
    rows: Sequence[tuple[Any, ...]],
    batch_size: int = 1000,
) -> int:
    """Insert rows, skipping ones already present.

    ON CONFLICT DO NOTHING against UNIQUE (sensor_id, recorded_at) makes the
    whole pipeline idempotent: overlapping windows, re-runs and crash recovery
    all converge to the same table.

    Does not commit -- the caller owns the transaction boundary, so a failure
    part-way through a sensor leaves nothing behind.

    Returns the number of rows actually written (conflicts excluded).
    """
    if not rows:
        return 0

    statement = sql.SQL(
        "INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
        "ON CONFLICT (sensor_id, recorded_at) DO NOTHING"
    ).format(
        table=sql.Identifier(table),
        columns=sql.SQL(", ").join(sql.Identifier(c) for c in columns),
        placeholders=sql.SQL(", ").join(sql.Placeholder() * len(columns)),
    )

    inserted = 0
    with conn.cursor() as cur:
        for chunk in _chunked(rows, batch_size):
            cur.executemany(statement, chunk)
            # psycopg reports the sum across the batch; -1 means "unknown".
            inserted += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0

    return inserted


def table_counts(conn: psycopg.Connection) -> dict[str, int]:
    """Row counts for the end-of-run summary."""
    counts: dict[str, int] = {}
    with conn.cursor() as cur:
        for table in ("hives", "sensors", "hive_measurements", "weather"):
            cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
            counts[table] = cur.fetchone()[0]
    return counts
