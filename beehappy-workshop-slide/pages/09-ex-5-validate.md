---
layout: center
class: bh-section
---

# Exercise 5 · Validate and document

Local time. Target names. Prove the grain, then save.

<div class="mt-8 bh-small">
<code>tz_localize</code> / <code>tz_convert</code> · <code>rename</code> · <code>assert</code> · <code>to_parquet</code>
</div>

---

# Time zones: localize, then convert

<JupyterCell n="40" at="2">

<div class="relative">
<div v-click.hide="1">

```python
local = features["hour"].dt.tz_localize("UTC").dt.tz_convert("...")
```

</div>
<div v-click="1" class="absolute inset-0">

```python
local = features["hour"].dt.tz_localize("UTC").dt.tz_convert("Europe/Berlin")
```

</div>
</div>

</JupyterCell>

<JupyterCell n="41" at="3" label="did this window cross a clock change?">

```python
local.dt.strftime("%z").unique()
```

<template #output>
<pre>&lt;ArrowStringArray&gt;
['+0200', '+0100']
Length: 2, dtype: str</pre>
</template>
</JupyterCell>

<JupyterCell n="42" at="5">

<div class="relative">
<div v-click.hide="4">

```python
features["hour_local"] = local.dt.hour
features["month"] = ...
features["dayofweek"] = ...
```

</div>
<div v-click="4" class="absolute inset-0">

```python
features["hour_local"] = local.dt.hour
features["month"] = local.dt.month
features["dayofweek"] = local.dt.dayofweek
```

</div>
</div>

</JupyterCell>

<div v-click="6" class="bh-warn mt-3">
<code>tz_localize</code> <strong>attaches</strong> a zone. <code>tz_convert</code> <strong>moves</strong> the clock. Never hardcode +01/+02.
</div>

<!--
hour is naive but holds UTC; the hive is in Germany. Getting localize and convert the
wrong way round shifts every local-time feature by one or two hours and nothing complains.

This window (late July to late October) crosses the October clock change, so both
+0200 and +0100 appear. Let the zone database handle it.

.dt.hour / .dt.month / .dt.dayofweek (Monday = 0) extract calendar fields after the
conversion, not before.

The notebook's reset_index cell before this is skipped on the slides: after the weather
merge, hour is already a column.
-->

---

# Rename to the target schema

<JupyterCell n="43">

```python
features = features.rename(columns={
    "tempC1": "brood_probe_temp", "tempC2": "food_probe_temp", "tempC3": "top_probe_temp",
    "temperature": "brood_temp", "relativeHumidity": "brood_humidity",
    "outside_temperature": "outside_temp",
    "outside_relativeHumidity": "outside_humidity",
    "outside_windSpeed": "outside_wind_speed",
    "outside_windDirection": "outside_wind_dir",
    "outside_uvIndex": "outside_uv_index",
    "outside_pressure": "outside_pressure_pa",
    "outside_lightIntensity": "outside_light",
    "outside_rainGauge": "outside_rain",
})
```

</JupyterCell>

<div v-click class="bh-warn mt-3">
The validator expects <strong>exactly</strong> these names. A typo in a key is silently ignored: check <code>features.columns</code>.
</div>

<!--
A dict maps each old name to its new one; columns you do not mention keep their names.
The weather columns still carry the raw measurement_unit names after add_prefix, so they
need renaming too.
-->

---

# Save and validate

<JupyterCell n="44" at="2">

<div class="relative">
<div v-click.hide="1">

```python
assert ...  # one row per hive-hour
assert ...  # the grid is complete
features.to_parquet(..., index=False)
```

</div>
<div v-click="1" class="absolute inset-0">

```python
assert not features.duplicated(subset=["beehive_id", "hour"]).any()
assert len(features) == len(grid)
features.to_parquet(OUT / "features_hourly.parquet", index=False)
```

</div>
</div>

</JupyterCell>

<div v-click="3" class="bh-out-label mt-5">then, in a terminal from the repo root</div>

<div v-click="3">

```bash
uv run python workshop/validate_features.py workshop/out/features_hourly.parquet
```

</div>

<pre v-click="4" class="bh-out mt-3">Checking workshop/out/features_hourly.parquet  (6,627 rows x 18 columns)

  [PASS] columns present              all 18 present
  [PASS] one row per hive-hour        no duplicates
  [PASS] row count                    6,627 = 3 hives x 2,209 hours
  [PASS] hourly grid complete         2,209 consecutive hours
  [PASS] values in range              every column inside plausible bounds
  [PASS] missingness sane             worst column brood_temp at 6.7% -- gaps kept honest
  [PASS] weather shared across hives  one ambient value per hour

  All checks passed.</pre>

<div v-click="5" class="bh-note mt-3">
<strong>Homework:</strong> write <code>DATA_DICTIONARY.md</code>. Every column and its unit, and every decision: the window you extracted, what you dropped, what you left empty, and why.
</div>

<!--
An assert is a claim about the data that stops the notebook if it is false: documentation
that executes. Ask the room what to assert before the reveal click.

Run the validator in a terminal from the repo root, after saving features_hourly.parquet.
Every check says what it wanted and what it got, so a FAIL points at the mistake.
-->
