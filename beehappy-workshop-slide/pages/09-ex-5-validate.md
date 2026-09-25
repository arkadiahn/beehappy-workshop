---
layout: center
class: bh-section
---

# Exercise 5 · Validate and document

Prove the grain. Name every column. Write every decision down.

<div class="mt-8 bh-small">
<code>tz_localize</code> / <code>tz_convert</code> · <code>rename</code> · <code>assert</code> · <code>to_parquet</code>
</div>

---

# Time zones: localize, then convert

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

`ts` is *naive* — no zone attached — but holds UTC. The hive is in Germany.

```python
features = features.reset_index()

local = (features["hour"]
         .dt.tz_localize("UTC")
         .dt.tz_convert("Europe/Berlin"))

# did this window cross a clock change?
local.dt.strftime("%z").unique()

features["hour_local"] = local.dt.hour
features["month"]      = local.dt.month
features["dayofweek"]  = local.dt.dayofweek
```

</div>
<div>

<div class="bh-warn mt-2">
<code>tz_localize</code> <strong>attaches</strong> a zone without moving the clock.
<code>tz_convert</code> <strong>moves</strong> the clock. Getting these the wrong way round shifts every local-time feature by two hours and nothing will complain.
</div>

<div class="bh-note mt-4">
Germany changes its clocks. The offset is +01:00 or +02:00 depending on the date — never hardcode it, let the zone database do it.
</div>

<div class="bh-small mt-4">
<code>.dt.hour</code> / <code>.dt.month</code> / <code>.dt.dayofweek</code> (Monday = 0) extract calendar fields after the conversion, not before.
</div>

</div>
</div>

---

# Rename to the target schema

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

`hive_name` lives on `beehives`, not on the readings.

```python
features = features.merge(
    beehives[["beehive_id", "name"]],
    on="beehive_id", how="left",
)

features = features.rename(columns={
    "name": "hive_name",
    "tempC1": "brood_temp_c1",
    "tempC2": "brood_temp_c2",
    "tempC3": "brood_temp_c3",
    "temperature": "food_temp",
    "relativeHumidity": "food_humidity",
    "outside_temperature": "outside_temp",
    "outside_relativeHumidity": "outside_humidity",
})
```

</div>
<div>

The validator enforces **exactly** these names. Weather columns after `add_prefix("outside_")` still have the raw `measurement_unit` suffixes — map those too (`outside_windSpeed` → `outside_wind_speed`, and so on).

<div class="bh-note mt-4">
Print <code>len(features)</code> before and after the <code>beehives</code> merge. Three hive names, three ids — this one should not change the row count.
</div>

<div class="bh-small mt-3">
The full mapping is in the notebook starter. Match it; do not invent nearby names.
</div>

</div>
</div>

---

# Checking your own work: `assert`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

An `assert` is a claim about your data that stops the notebook if it is false. Write them as you go.

```python
# the grain: one row per hive per hour, no repeats
assert not features.duplicated(
    subset=["beehive_id", "hour"]).any()

# the table is a complete rectangle
assert len(features) == (
    features["beehive_id"].nunique()
    * features["hour"].nunique()
)

# ranges that physics allows
assert features["food_humidity"].between(0, 100).all()

# nothing lost in a join
assert len(after) == len(before), (
    f"join changed rows: {len(before)} -> {len(after)}"
)
```

</div>
<div>

<div class="bh-note">
An assertion that has never failed still earns its place: it is documentation that <em>executes</em>. Six months later it tells the next person what you believed about this table.
</div>

<div class="bh-out-label mt-4">when one fails</div>
<pre class="bh-out">AssertionError: join changed rows: 939523 -> 1142006
</pre>

<div class="mt-4">

Useful companions:

```python
df.duplicated(subset=[...]).any()
df["col"].between(lo, hi).all()
df["col"].notna().all()
set(a["id"]) - set(b["id"])      # what failed to match
```

</div>

</div>
</div>

---

# Document, save, validate

Write `DATA_DICTIONARY.md` **as you go**, not at the end. Every column, its unit, and **every decision**:

- the window you extracted
- what you dropped, and why
- what you filled, and the gap rule
- what you left empty, and why

```python
features.to_parquet(OUT / "features_hourly.parquet", index=False)
```

```bash
uv run python workshop/validate_features.py workshop/out/features_hourly.parquet
```

<div class="bh-note mt-4">
Green is not the goal. A table that passes but whose gap policy you cannot defend is worse than one that fails honestly.
</div>
