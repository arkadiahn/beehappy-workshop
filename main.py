"""Command-line entry point for the Digital Beehive ETL.

    uv run main.py                     # incremental load (backfills if empty)
    uv run main.py --init-schema       # create tables first, then load
    uv run main.py --backfill-days 7   # override the backfill window
    uv run main.py --discover-only     # print what the API offers, touch nothing
    uv run main.py --dry-run           # fetch and transform, but do not write
"""

from __future__ import annotations

import argparse
import logging
import sys

from bees import db, etl
from bees.api import BeehiveAPIError, DigitalBeehiveClient
from bees.config import Settings, Topology

logger = logging.getLogger("bees")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load Digital Beehive data into Postgres.")
    parser.add_argument(
        "--init-schema", action="store_true",
        help="apply data_schema.sql before loading (safe to repeat)",
    )
    parser.add_argument(
        "--backfill-days", type=int, default=None,
        help="how far back to reach for sensors with no data yet (default 90)",
    )
    parser.add_argument(
        "--discover-only", action="store_true",
        help="list the API's groups, devices and keys, then exit without a database",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="run inside a transaction that is rolled back at the end",
    )
    parser.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        settings = Settings.from_env()
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 2

    if args.backfill_days is not None:
        settings = replace_backfill(settings, args.backfill_days)

    topology = Topology.load()

    try:
        if args.discover_only:
            return discover(settings)
        return load(settings, topology, dry_run=args.dry_run, init=args.init_schema)
    except BeehiveAPIError as exc:
        logger.error("API error: %s", exc)
        return 1
    except Exception as exc:  # noqa: BLE001 - top-level guard
        logger.exception("Run failed: %s", exc)
        return 1


def replace_backfill(settings: Settings, days: int) -> Settings:
    from dataclasses import replace

    return replace(settings, backfill_days=days)


def discover(settings: Settings) -> int:
    """Print the live shape of the API. Useful when the installation changes."""
    client = DigitalBeehiveClient(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=settings.request_timeout,
        max_retries=settings.max_retries,
    )

    for group in client.auth_groups():
        keys = client.timeseries_keys(group)
        print(f"\n{group}")
        print(f"  timeseries keys: {', '.join(keys) or '-'}")
        for device in client.devices(group):
            print(f"  - {device.name}  [{device.device_type}]")
            print(f"      entityId: {device.entity_id}")
            print(f"      location: {device.location or '-'}  "
                  f"lat/lon: {device.latitude}/{device.longitude}")
            print(f"      keys:     {', '.join(device.timeseries_keys) or '-'}")
    return 0


def load(settings: Settings, topology: Topology, dry_run: bool, init: bool) -> int:
    with db.connect(settings.database_url) as conn:
        if init:
            db.init_schema(conn)

        result = etl.run(settings, topology, conn, dry_run=dry_run)

        if dry_run:
            conn.rollback()
            logger.warning("--dry-run: transaction rolled back, nothing was written")

    report(result, dry_run=dry_run)
    return 1 if result.failures else 0


def report(result: etl.RunResult, dry_run: bool = False) -> None:
    print("\n" + "=" * 72)
    print("Digital Beehive ETL" + ("  (DRY RUN -- nothing written)" if dry_run else ""))
    print("=" * 72)
    print(f"hives seeded          {result.hives_seeded}")
    print(f"sensors seeded        {result.sensors_seeded}")
    if result.sensors_deactivated:
        print(f"sensors deactivated   {result.sensors_deactivated} (no longer in the API)")
    if result.unmapped_sensors:
        print(f"sensors without hive  {', '.join(result.unmapped_sensors)}")
        print("                      -> add them to hives.toml and re-run")
    if result.orphan_hives:
        print(f"empty hives in DB     {', '.join(result.orphan_hives)}")
        print("                      -> not in hives.toml and no sensors; delete by hand")

    print(f"\n{'sensor':<24}{'table':<20}{'fetched':>9}{'rows':>7}{'new':>7}")
    print("-" * 72)
    for sensor in result.sensors:
        status = f"  ERROR: {sensor.error}" if sensor.error else ""
        print(
            f"{sensor.sensor_name:<24}{sensor.table:<20}"
            f"{sensor.points_fetched:>9}{sensor.rows_built:>7}{sensor.rows_inserted:>7}{status}"
        )

    print("-" * 72)
    print(f"{'TOTAL new rows':<53}{result.rows_inserted:>7}")

    if result.table_counts:
        print("\ntable totals: " + "  ".join(
            f"{table}={count}" for table, count in result.table_counts.items()
        ))

    if result.failures:
        print(f"\n{len(result.failures)} sensor(s) failed; other sensors were still loaded.")
    print()


if __name__ == "__main__":
    sys.exit(main())
