"""Grade a candidate feature table.

    uv run python workshop/validate_features.py workshop/out/features_hourly.parquet

Prints a scorecard. Every check says what it wanted and what it got, so a FAIL
points at the mistake rather than just announcing one.

This file is also the schema contract for Exercise 4 -- REQUIRED_COLUMNS and
RANGES below are what your data dictionary has to describe.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# name -> kind. "num" is anything numeric; the point is the column exists and
# holds numbers, not which exact float width you ended up with.
REQUIRED_COLUMNS: dict[str, str] = {
    "beehive_id": "num",
    "hive_name": "str",
    "hour": "datetime",
    # brood chamber, three probes on one device
    "brood_temp_c1": "num",
    "brood_temp_c2": "num",
    "brood_temp_c3": "num",
    # food chamber
    "food_temp": "num",
    "food_humidity": "num",
    # ambient
    "outside_temp": "num",
    "outside_humidity": "num",
    "outside_wind_speed": "num",
    "outside_wind_dir": "num",
    "outside_uv_index": "num",
    "outside_pressure_pa": "num",
    "outside_light": "num",
    "outside_rain": "num",
    # calendar, in Europe/Berlin local time
    "hour_local": "num",
    "month": "num",
    "dayofweek": "num",
}

# Generous bounds. These catch unit mistakes and bad joins, not unusual weather.
RANGES: dict[str, tuple[float, float]] = {
    "brood_temp_c1": (-20, 55),
    "brood_temp_c2": (-20, 55),
    "brood_temp_c3": (-20, 55),
    "food_temp": (-20, 55),
    "food_humidity": (0, 100),
    "outside_temp": (-30, 55),
    "outside_humidity": (0, 100),
    "outside_wind_speed": (0, 60),
    "outside_wind_dir": (0, 360),
    "outside_uv_index": (0, 20),
    # pascals, not hectopascals -- ~99_000, not ~990
    "outside_pressure_pa": (85_000, 115_000),
    "outside_light": (0, 250_000),
    "outside_rain": (0, 1_000),
    "hour_local": (0, 23),
    "month": (1, 12),
    "dayofweek": (0, 6),
}

EXPECTED_HIVES = 3


class Scorecard:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, status: str, name: str, detail: str = "") -> None:
        self.rows.append((status, name, detail))

    def report(self) -> int:
        width = max(len(n) for _, n, _ in self.rows)
        print()
        for status, name, detail in self.rows:
            print(f"  [{status:4}] {name:<{width}}  {detail}")
        fails = sum(1 for s, _, _ in self.rows if s == "FAIL")
        warns = sum(1 for s, _, _ in self.rows if s == "WARN")
        print()
        if fails:
            print(f"  {fails} FAILED, {warns} warnings. Not ready yet.")
        elif warns:
            print(f"  All checks passed with {warns} warnings worth reading.")
        else:
            print("  All checks passed.")
        return 1 if fails else 0


def is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def check(frame: pd.DataFrame) -> int:
    card = Scorecard()

    # --- schema ----------------------------------------------------------
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        card.add("FAIL", "columns present", f"missing: {', '.join(missing)}")
    else:
        card.add("PASS", "columns present", f"all {len(REQUIRED_COLUMNS)} present")

    for name, kind in REQUIRED_COLUMNS.items():
        if name not in frame.columns:
            continue
        col = frame[name]
        ok = (is_numeric(col) if kind == "num"
              else pd.api.types.is_datetime64_any_dtype(col) if kind == "datetime"
              else True)
        if not ok:
            card.add("FAIL", f"dtype {name}", f"wanted {kind}, got {col.dtype}")

    # --- grain -----------------------------------------------------------
    if {"beehive_id", "hour"} <= set(frame.columns):
        dupes = frame.duplicated(subset=["beehive_id", "hour"]).sum()
        if dupes:
            card.add("FAIL", "one row per hive-hour", f"{dupes:,} duplicate pairs")
        else:
            card.add("PASS", "one row per hive-hour", "no duplicates")

        hives = frame["beehive_id"].nunique()
        hours = frame["hour"].nunique()
        expected = hives * hours
        if hives != EXPECTED_HIVES:
            card.add("FAIL", "hive count", f"wanted {EXPECTED_HIVES}, got {hives}")
        if len(frame) != expected:
            ratio = len(frame) / expected if expected else 0
            hint = ""
            if ratio > 1.5:
                hint = ("  <- rows are a multiple of the grid. Something was joined "
                        "more times than it should have been.")
            card.add("FAIL", "row count",
                     f"wanted {expected:,} ({hives} hives x {hours:,} hours), "
                     f"got {len(frame):,}{hint}")
        else:
            card.add("PASS", "row count", f"{len(frame):,} = {hives} hives x {hours:,} hours")

        # A complete hourly grid has no missing hours between first and last.
        span = pd.date_range(frame["hour"].min(), frame["hour"].max(), freq="h")
        if hours != len(span):
            card.add("WARN", "hourly grid complete",
                     f"{hours:,} distinct hours over a {len(span):,}-hour span "
                     f"-- {len(span) - hours:,} hours absent entirely")
        else:
            card.add("PASS", "hourly grid complete", f"{hours:,} consecutive hours")

    # --- values ----------------------------------------------------------
    out_of_range = []
    for name, (lo, hi) in RANGES.items():
        if name not in frame.columns or not is_numeric(frame[name]):
            continue
        bad = int(((frame[name] < lo) | (frame[name] > hi)).sum())
        if bad:
            out_of_range.append(f"{name}={bad:,}")
    if out_of_range:
        card.add("FAIL", "values in range", ", ".join(out_of_range))
    else:
        card.add("PASS", "values in range", "every column inside plausible bounds")

    # --- missingness -----------------------------------------------------
    measured = [c for c in RANGES if c in frame.columns
                and c not in {"hour_local", "month", "dayofweek"}]
    if measured:
        na = frame[measured].isna().mean().mul(100)
        worst = na.max()
        if worst > 25:
            card.add("FAIL", "missingness sane",
                     f"{na.idxmax()} is {worst:.1f}% empty -- a join probably missed")
        elif worst == 0:
            card.add("WARN", "missingness sane",
                     "no gaps at all. The devices went offline for days at a time, so "
                     "either you filled outages you should have left, or dropped them "
                     "-- say which, in the data dictionary")
        else:
            card.add("PASS", "missingness sane",
                     f"worst column {na.idxmax()} at {worst:.1f}% -- gaps kept honest")

    # --- the fan-out trap -------------------------------------------------
    # Ambient readings belong to the site, not to a hive: at any hour the three
    # hives must agree on them. Disagreement means weather was attached per
    # registration rather than per site.
    if {"hour", "outside_temp"} <= set(frame.columns):
        spread = frame.groupby("hour", observed=True)["outside_temp"].nunique(dropna=True)
        disagreeing = int((spread > 1).sum())
        if disagreeing:
            card.add("FAIL", "weather shared across hives",
                     f"{disagreeing:,} hours where hives disagree on outside_temp")
        else:
            card.add("PASS", "weather shared across hives", "one ambient value per hour")

    return card.report()


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    if not path.exists():
        sys.exit(f"No such file: {path}")

    frame = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    print(f"Checking {path}  ({len(frame):,} rows x {frame.shape[1]} columns)")
    sys.exit(check(frame))


if __name__ == "__main__":
    main()
