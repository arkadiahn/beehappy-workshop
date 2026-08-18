"""Freeze a snapshot of ChatBotDB for the Data Foundation workshop.

The snapshot is deliberately UNCLEANED. Every defect in the live database is
teaching material, so this script copies the three tables verbatim:

  * ~22% of `data` rows are exact duplicates, up to 797 copies of one reading
  * the weather station is registered three times, once per beehive
  * ~3-6% of hours have no rows at all, with outages up to ~5 days
  * `ts` is `timestamp without time zone` holding UTC

Do not "fix" anything here. If the collector bug is ever repaired upstream, this
frozen copy is what keeps the workshop working.

Usage:
    uv run python workshop/scripts/export_snapshot.py
    uv run python workshop/scripts/export_snapshot.py --out workshop/data

Connection comes from CHATBOTDB_URL, or DATABASE_URL as a fallback. Use the
read-only grafana_ro role, never the postgres superuser.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg

# The three tables, in dependency order. SELECT * on purpose: any column added
# upstream should land in the snapshot without editing this script.
TABLES = ("beehives", "sensors", "data")

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "workshop" / "data"


def connection_url() -> str:
    url = os.environ.get("CHATBOTDB_URL") or os.environ.get("DATABASE_URL")
    if not url:
        sys.exit(
            "Set CHATBOTDB_URL (or DATABASE_URL) to ChatBotDB's connection string.\n"
            "Use the read-only grafana_ro role. Railway exposes the public URL as\n"
            "  railway variables -s ChatBotDB --json | ... DATABASE_PUBLIC_URL"
        )
    return url


def export(conn: psycopg.Connection, out_dir: Path) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for table in TABLES:
        # Built from a cursor rather than pd.read_sql, which warns about
        # non-SQLAlchemy connections. Fine at these sizes (~2.4M rows).
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table}")
            columns = [c.name for c in cur.description]
            frame = pd.DataFrame(cur.fetchall(), columns=columns)
        target = out_dir / f"{table}.parquet"
        frame.to_parquet(target, index=False)
        size_mb = target.stat().st_size / 1e6
        print(f"  {table:10} {len(frame):>9,} rows -> {target.name} ({size_mb:.1f} MB)")
        frames[table] = frame
    return frames


def profile(frames: dict[str, pd.DataFrame]) -> dict[str, object]:
    """The numbers the workshop's answers depend on.

    Recorded in the manifest so drift is detectable: if a future snapshot does
    not reproduce these, the exercises need revisiting.
    """
    data = frames["data"]
    key = ["sensor_id", "measurement_unit", "ts"]
    distinct = len(data.drop_duplicates(subset=key))
    dupe_groups = data.groupby(key, observed=True).size()

    return {
        "rows_data": len(data),
        "distinct_keys": distinct,
        "pct_redundant": round(100 * (1 - distinct / len(data)), 1),
        "max_duplicate_multiplicity": int(dupe_groups.max()),
        "keys_with_conflicting_values": int(
            (data.groupby(key, observed=True)["value"].nunique() > 1).sum()
        ),
        "null_values": int(data["value"].isna().sum()),
        "measurement_units": int(data["measurement_unit"].nunique()),
        "sensors": len(frames["sensors"]),
        "beehives": len(frames["beehives"]),
        "weather_sensor_registrations": int(
            (frames["sensors"]["sensor_type"] == "LoRaWAN SenseCAP-S2120").sum()
        ),
        "first_ts": str(data["ts"].min()),
        "last_ts": str(data["ts"].max()),
        "days_spanned": int((data["ts"].max() - data["ts"].min()).days) + 1,
    }


def write_manifest(out_dir: Path, stats: dict[str, object]) -> None:
    taken = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Snapshot manifest",
        "",
        f"Taken: **{taken}** from ChatBotDB (Railway project `bee-happy`).",
        "",
        "Copied verbatim — no deduplication, no filtering, no repair. The defects",
        "are the workshop. If a future export does not reproduce these numbers, the",
        "upstream data changed and the exercises need rechecking.",
        "",
        "| Property | Value |",
        "|---|---|",
    ]
    lines += [f"| `{k}` | {v} |" for k, v in stats.items()]
    lines += [
        "",
        "## Known defects, all intentional",
        "",
        "- **Duplicate rows.** A live bug in the `ChatBotCollector` service, running at",
        "  20-28% in every month observed. `reading_id` is retained so it is provable",
        "  these are separate INSERTs rather than a query artifact.",
        "- **Weather station registered three times** (`sensor_id` 1/2/3) with the same",
        "  device MAC `LoRa-2CF7F1C0613005BC`, one per beehive. Joining hive readings to",
        "  weather without collapsing these triples every weather row.",
        "- **Implicit missingness.** No NULLs anywhere; rows are simply absent for hours",
        "  a device did not report. Only a complete time index reveals them.",
        "- **`ts` is `timestamp without time zone` holding UTC.** Local-time analysis",
        "  needs Europe/Berlin, and the span covers two DST transitions.",
        "",
        "## Caveats not visible in the data",
        "",
        "- The hive-to-sensor mapping is **unconfirmed** — `hives.toml` marks it",
        "  `UNBESTÄTIGT`, and ChatBotDB's mapping disagrees with that guess.",
        "- `rainGauge` reaches 228.6 and looks cumulative rather than per-interval;",
        "  unverified against the source API.",
    ]
    (out_dir / "MANIFEST.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    print(f"Exporting to {args.out}")
    with psycopg.connect(connection_url(), connect_timeout=30) as conn:
        frames = export(conn, args.out)

    stats = profile(frames)
    write_manifest(args.out, stats)

    print("\nProfile:")
    for k, v in stats.items():
        print(f"  {k:32} {v}")
    print(f"\nManifest written to {args.out / 'MANIFEST.md'}")


if __name__ == "__main__":
    main()
