---
layout: center
class: bh-section
---

# Exercise 4 · Align time and handle gaps

One clock. Long to wide. Every hive-hour, even the silent ones.

<div class="mt-8 bh-small">
<code>.dt.floor("h")</code> · <code>groupby().mean()</code> · <code>unstack</code> · <code>reindex</code> · <code>merge</code>
</div>

---

# Floor timestamps to the hour

<JupyterCell n="29">

```python
hive_rows = hive_rows.assign(hour=hive_rows["ts"].dt.floor("h"))
hive_rows[["ts", "hour"]].head()
```

<template #output>
<pre>                        ts                hour
0  2026-07-28 10:28:39.165 2026-07-28 10:00:00
1  2026-07-28 10:28:39.165 2026-07-28 10:00:00
26 2026-07-28 10:34:28.255 2026-07-28 10:00:00
27 2026-07-28 10:34:28.255 2026-07-28 10:00:00
28 2026-07-28 10:34:28.255 2026-07-28 10:00:00</pre>
</template>
</JupyterCell>

<div v-click class="bh-note mt-4">
<code>.dt</code> unlocks datetime methods on a whole column. Do the same for <code>weather_rows</code>.
</div>

<!--
Hive devices report every ~20 min, the weather station every ~10 min, so every hour
has readings to average.

The index jumps 1 -> 26 because the weather rows were filtered out.

If .dt raises "Can only use .dt accessor with datetimelike values", the column is a
string: pd.to_datetime(col) fixes it, or they saved CSV in Exercise 0.
-->

---

# groupby + mean: still long

<JupyterCell n="30">

```python
hive_hourly = hive_rows.groupby(["beehive_id", "hour", "measurement_unit"])["value"].mean()
hive_hourly.head()
```

<template #output>
<pre>beehive_id  hour                 measurement_unit
1           2026-07-28 10:00:00  relativeHumidity    65.70
                                 tempC1              32.70
                                 tempC2              29.05
                                 tempC3              30.20
                                 temperature         30.85
Name: value, dtype: float64</pre>
</template>
</JupyterCell>

<div v-click class="bh-note mt-4">
One value per hive, hour and measurement. Look at the <strong>index</strong>: three levels, still one measurement per row.
</div>

<!--
A device reports about three times an hour, and mean() collapses those into one value.

Pass observed=True when grouping categoricals to avoid materialising unused combinations.
-->

---

# Long → wide: unstack

<JupyterCell n="31" at="1">

```python
hive_hourly = hive_hourly.unstack("measurement_unit")
hive_hourly.head()
```

<template #output>
<pre>measurement_unit                relativeHumidity     tempC1     tempC2  tempC3  temperature
beehive_id hour
1          2026-07-28 10:00:00         65.700000  32.700000  29.050000    30.2    30.850000
           2026-07-28 11:00:00         61.266667  33.466667  30.133333    31.5    31.433333
           2026-07-28 12:00:00         59.566667  34.033333  31.433333    32.9    31.766667
           2026-07-28 13:00:00         59.600000  35.066667  32.666667    33.9    32.433333
           2026-07-28 14:00:00         57.500000  35.150000  33.450000    34.6    33.233333</pre>
</template>
</JupyterCell>

<JupyterCell n="32" at="2" label="same three verbs for weather">

<div class="relative">
<div v-click.hide="3">

```python
weather_rows = weather_rows.assign(hour=...)
weather_hourly = weather_rows.groupby([...])["value"].mean()
```

</div>
<div v-click="3" class="absolute inset-0">

```python
weather_rows = weather_rows.assign(hour=weather_rows["ts"].dt.floor("h"))
weather_hourly = weather_rows.groupby(["hour", "measurement_unit"])["value"].mean()
```

</div>
</div>

</JupyterCell>

<JupyterCell n="33" at="4">

```python
weather_hourly = weather_hourly.unstack("measurement_unit").add_prefix("outside_")
```

</JupyterCell>

<div v-click="5" class="bh-small mt-3">
Weather has no hive: its grain is just <code>hour</code>. <code>add_prefix</code> stops <code>temperature</code> clashing with the brood sensor's.
</div>

<!--
unstack takes one index level and spreads it across columns; stack is the inverse.
df.pivot_table(index=..., columns=..., values=..., aggfunc="mean") does the same job in one call.

Ask the room for the weather groupby keys before the reveal click.
-->

---

# Building a complete index: date_range + reindex

<div class="bh-note bh-small">
<strong>Invisible NULLs.</strong> A power outage or a broken sensor leaves no NULL behind: the row is simply missing. A complete grid turns every missing hour into a row of <code>NaN</code> you can count.
</div>

<JupyterCell n="34" at="2">

<div class="relative">
<div v-click.hide="1">

```python
START_TIME_H = ...
END_TIME_H = ...
hours = pd.date_range(START_TIME_H, END_TIME_H, freq="h", name="hour")
```

</div>
<div v-click="1" class="absolute inset-0">

```python
START_TIME_H = distinct_sensor_readings["ts"].min().floor("h")
END_TIME_H = distinct_sensor_readings["ts"].max().floor("h")
hours = pd.date_range(START_TIME_H, END_TIME_H, freq="h", name="hour")
```

</div>
</div>

</JupyterCell>

<JupyterCell n="35" at="3" label="every hive × every hour">

```python
grid = pd.MultiIndex.from_product(
    [beehives["beehive_id"], hours], names=["beehive_id", "hour"]
)
features = hive_hourly.reindex(grid)
print(f"hive hours: {len(hive_hourly):,} observed vs {len(features):,} complete")
```

<template #output>
<pre>hive hours: 6,564 observed vs 6,627 complete</pre>
</template>
</JupyterCell>

<JupyterCell n="36" at="4" label="weather: every hour, no hive">

```python
observed = len(weather_hourly)
weather_hourly = weather_hourly.reindex(hours)
print(f"weather hours: {observed:,} observed vs {len(weather_hourly):,} complete")
```

<template #output>
<pre>weather hours: 2,209 observed vs 2,209 complete</pre>
</template>
</JupyterCell>

<!--
Ask the room for the start and end before the reveal click. Build the grid from the
extract window, not from what one device happened to cover.

reindex turns every expected-but-absent row into a row of NaN you can count. On the local
extract: 6,564 observed hive-hours vs 6,627 in the grid, so 63 are absent. The weather
station has no missing hours in this window.
-->

---

# Measuring gaps

<JupyterCell n="37">

```python
hive_hourly.reset_index().groupby("beehive_id")["hour"].diff()
```

<template #output>
<pre>0                  NaT
1      0 days 01:00:00
2      0 days 01:00:00
3      0 days 01:00:00
4      0 days 01:00:00
             ...
6559   0 days 01:00:00
6560   0 days 01:00:00
6561   0 days 01:00:00
6562   0 days 01:00:00
6563   0 days 01:00:00
Name: hour, Length: 6564, dtype: timedelta64[us]</pre>
</template>
</JupyterCell>

<JupyterCell n="38" label="the longest gap">

```python
hive_hourly.reset_index().groupby("beehive_id")["hour"].diff().max()
```

<template #output>
<pre>Timedelta('0 days 05:00:00')</pre>
</template>
</JupyterCell>

<div v-click class="bh-note mt-3">
The time since the previous observed hour, per hive. <code>1 hour</code> means no gap. Missing hours stay <code>NaN</code>.
</div>

<!--
Add .value_counts() to see the gaps. On the local extract:
  1 hour 6,509 · 2 hours 45 · 3 hours 4 · 4 hours 2 · 5 hours 1
The first row of each hive is NaT: there is no previous hour to compare with.
-->

---

# Attach the weather: merge on hour

<JupyterCell n="39" at="2">

<div class="relative">
<div v-click.hide="1">

```python
before = len(features)
features = features.reset_index().merge(
    weather_hourly.reset_index(), on=..., how="left", validate="many_to_one"
)
print(f"features {before:,} -> {len(features):,} after weather merge")
```

</div>
<div v-click="1" class="absolute inset-0">

```python
before = len(features)
features = features.reset_index().merge(
    weather_hourly.reset_index(), on="hour", how="left", validate="many_to_one"
)
print(f"features {before:,} -> {len(features):,} after weather merge")
```

</div>
</div>

<template #output>
<pre>features 6,627 -> 6,627 after weather merge</pre>
</template>
</JupyterCell>

<div v-click="3" class="bh-note mt-4">
One weather hour attaches to all three hives. <code>validate="many_to_one"</code> proves weather has one row per hour, so the row count cannot grow.
</div>

<!--
Ask the room for the merge key before the reveal click.

reset_index() turns the index levels into columns so merge(on=...) can find hour.
Most alignment bugs in pandas are index bugs: when two frames refuse to line up, print
df.index on both.

weather_hourly has no beehive_id after the Exercise 3 collapse, so on=["beehive_id", "hour"]
raises a KeyError. That error is the hint.
-->
