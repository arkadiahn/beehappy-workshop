"""Orchestration: discover devices, seed dimensions, load measurements.

A run has three phases.

1. Discover -- read /authGroup, /valueType and /entityId to learn which devices
   exist and which keys each one exposes. Nothing is hardcoded; a new sensor
   added to the platform is picked up automatically.

2. Seed -- write hives.toml into `hives`, and the discovered devices into
   `sensors`, so every measurement has a foreign key to point at.

3. Load -- for each sensor, work out the time window still missing, page the
   API backwards through it, pivot the keys into rows, and upsert.

The window per sensor is:
    start = max(newest row in DB - overlap, now - backfill_days)
    end   = now
A sensor with no rows yet gets the full backfill window. The overlap re-reads
recent data so late-arriving readings are picked up; the upserts absorb it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import psycopg

from bees import db, transform
from bees.api import DigitalBeehiveClient, Device
from bees.config import Settings, Topology

logger = logging.getLogger(__name__)


@dataclass
class SensorResult:
    sensor_name: str
    table: str
    window_start: datetime
    window_end: datetime
    points_fetched: int = 0
    rows_built: int = 0
    rows_inserted: int = 0
    error: str | None = None


@dataclass
class RunResult:
    hives_seeded: int = 0
    sensors_seeded: int = 0
    sensors_deactivated: int = 0
    unmapped_sensors: list[str] = field(default_factory=list)
    orphan_hives: list[str] = field(default_factory=list)
    sensors: list[SensorResult] = field(default_factory=list)
    table_counts: dict[str, int] = field(default_factory=dict)

    @property
    def rows_inserted(self) -> int:
        return sum(s.rows_inserted for s in self.sensors)

    @property
    def failures(self) -> list[SensorResult]:
        return [s for s in self.sensors if s.error]


def run(
    settings: Settings,
    topology: Topology,
    conn: psycopg.Connection,
    client: DigitalBeehiveClient | None = None,
    now: datetime | None = None,
    dry_run: bool = False,
) -> RunResult:
    """Execute one full ETL run against an already-open connection.

    With dry_run the API is still called and rows are still built, but nothing
    is inserted and nothing is committed, so the caller's rollback restores the
    database exactly.
    """
    client = client or DigitalBeehiveClient(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=settings.request_timeout,
        max_retries=settings.max_retries,
    )
    now = now or datetime.now(timezone.utc)
    result = RunResult()

    # ------------------------------------------------------------- discover
    devices, keys_by_group = _discover(client)
    logger.info("Discovered %d device(s) across %d group(s)", len(devices), len(keys_by_group))

    # ----------------------------------------------------------------- seed
    hive_ids = {spec.hive_name: db.upsert_hive(conn, spec) for spec in topology.hives}
    result.hives_seeded = len(hive_ids)

    sensor_ids: dict[str, int] = {}
    for device in devices:
        hive_name = topology.hive_for(device.name)
        if hive_name is None and not topology.is_known(device.name):
            # Not a failure: the device is loaded with hive_id NULL and can be
            # attached later by editing hives.toml and re-running.
            result.unmapped_sensors.append(device.name)
            logger.warning(
                "Device %s (%s) is not listed in hives.toml; loading with hive_id = NULL",
                device.name, device.device_type,
            )

        sensor_ids[device.name] = db.upsert_sensor(
            conn,
            sensor_name=device.name,
            sensor_type=device.device_type,
            hive_id=hive_ids.get(hive_name) if hive_name else None,
            site=device.location,
            latitude=device.latitude if device.latitude is not None else topology.default_latitude,
            longitude=device.longitude if device.longitude is not None else topology.default_longitude,
        )

    result.sensors_deactivated = db.deactivate_missing_sensors(conn, sensor_ids)
    result.sensors_seeded = len(sensor_ids)

    result.orphan_hives = db.orphan_hives(conn, [s.hive_name for s in topology.hives])
    for name in result.orphan_hives:
        logger.warning(
            "Hive %r is in the database but not in hives.toml and has no sensors "
            "(left over from a rename?). Delete it by hand once you are sure.",
            name,
        )

    if not dry_run:
        conn.commit()

    # ----------------------------------------------------------------- load
    hive_watermarks = db.watermarks(conn, transform.HIVE_TABLE)
    weather_watermarks = db.watermarks(conn, transform.WEATHER_TABLE)

    for device in devices:
        sensor_id = sensor_ids[device.name]
        is_weather = device.is_weather_station
        marks = weather_watermarks if is_weather else hive_watermarks

        start = _window_start(marks.get(sensor_id), now, settings)
        sensor_result = SensorResult(
            sensor_name=device.name,
            table=transform.table_for(is_weather),
            window_start=start,
            window_end=now,
        )

        try:
            _load_device(
                client=client,
                conn=conn,
                device=device,
                sensor_id=sensor_id,
                group_keys=keys_by_group.get(device.auth_group, ()),
                start=start,
                end=now,
                batch_size=settings.batch_size,
                outcome=sensor_result,
                dry_run=dry_run,
            )
            # Commit per sensor: a long backfill that dies half way keeps the
            # sensors it already finished, and the next run resumes from there.
            if not dry_run:
                conn.commit()
        except Exception as exc:  # one bad device must not abort the run
            if not dry_run:
                conn.rollback()
            sensor_result.error = f"{type(exc).__name__}: {exc}"
            logger.exception("Loading %s failed", device.name)

        result.sensors.append(sensor_result)

    result.table_counts = db.table_counts(conn)
    return result


# ------------------------------------------------------------------ phases


def _discover(
    client: DigitalBeehiveClient,
) -> tuple[list[Device], dict[str, tuple[str, ...]]]:
    devices: list[Device] = []
    keys_by_group: dict[str, tuple[str, ...]] = {}

    for group in client.auth_groups():
        keys_by_group[group] = tuple(client.timeseries_keys(group))
        group_devices = client.devices(group)
        logger.info(
            "Group %s: %d device(s), keys %s",
            group, len(group_devices), ", ".join(keys_by_group[group]) or "-",
        )
        devices.extend(group_devices)

    return devices, keys_by_group


def _window_start(
    watermark: datetime | None, now: datetime, settings: Settings
) -> datetime:
    """Earliest timestamp still worth requesting for one sensor."""
    floor = now - timedelta(days=settings.backfill_days)
    if watermark is None:
        return floor
    return max(floor, watermark - timedelta(minutes=settings.overlap_minutes))


def _load_device(
    client: DigitalBeehiveClient,
    conn: psycopg.Connection,
    device: Device,
    sensor_id: int,
    group_keys: tuple[str, ...],
    start: datetime,
    end: datetime,
    batch_size: int,
    outcome: SensorResult,
    dry_run: bool = False,
) -> None:
    """Fetch, pivot and upsert one device's window."""
    column_map = transform.column_map_for(device.is_weather_station)
    insert_columns = transform.insert_columns_for(device.is_weather_station)

    # Only request keys that are (a) permitted for the group -- an unpermitted
    # key makes the whole request 400 -- (b) actually present on this device,
    # and (c) mapped to a column we can store.
    candidate_keys = set(group_keys) & set(device.timeseries_keys) & set(column_map)
    unmapped = set(device.timeseries_keys) - set(column_map)
    if unmapped:
        logger.warning(
            "%s exposes key(s) with no column: %s (not loaded)",
            device.name, ", ".join(sorted(unmapped)),
        )

    if not candidate_keys:
        logger.info("%s has no loadable keys; skipping", device.name)
        return

    start_ms, end_ms = _to_ms(start), _to_ms(end)
    logger.info(
        "%s: fetching %s from %s to %s",
        device.name, ", ".join(sorted(candidate_keys)),
        start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds"),
    )

    points_by_key: dict[str, list[tuple[int, str]]] = {}
    for key in sorted(candidate_keys):
        points = [
            (point.ts_ms, point.value)
            for point in client.iter_timeseries(
                auth_group=device.auth_group,
                entity_id=device.entity_id,
                key=key,
                start_ms=start_ms,
                end_ms=end_ms,
            )
        ]
        points_by_key[key] = points
        outcome.points_fetched += len(points)
        logger.debug("%s/%s: %d point(s)", device.name, key, len(points))

    rows = transform.build_rows(sensor_id, points_by_key, column_map, insert_columns)
    outcome.rows_built = len(rows)

    if not dry_run:
        outcome.rows_inserted = db.insert_measurements(
            conn,
            table=outcome.table,
            columns=insert_columns,
            rows=rows,
            batch_size=batch_size,
        )
    logger.info(
        "%s: %d point(s) -> %d row(s), %d new",
        device.name, outcome.points_fetched, outcome.rows_built, outcome.rows_inserted,
    )


def _to_ms(moment: datetime) -> int:
    return int(moment.timestamp() * 1000)
