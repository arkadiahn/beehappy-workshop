---
layout: center
class: bh-section
---

# Exercise 3 · Reshape and join

Attach `role`. Split hive from weather. Collapse the weather.

<div class="mt-8 bh-small">
<code>.map()</code> · <code>.assign()</code> · <code>merge(on=, how=)</code> · boolean filter · <code>drop_duplicates</code>
</div>

<!--
The wide reshape — unstack — is Exercise 4. Say that out loud so nobody
starts pivoting here.
-->

---

# Why not just unstack?

<JupyterCell n="?" label="a shortcut, not in the notebook">

```python
wide = (distinct_sensor_readings
        .set_index(["beehive_id", "ts", "measurement_unit"])["value"]
        .unstack("measurement_unit"))
wide[["temperature", "relativeHumidity", "windSpeed"]].head(4)
```

<template #output>
<pre>measurement_unit                    temperature  relativeHumidity  windSpeed
beehive_id ts
1          2026-07-28 10:28:39.165         30.7              68.5        NaN
           2026-07-28 10:31:23.976         29.0              33.0        0.7
           2026-07-28 10:34:28.255          NaN               NaN        NaN
           2026-07-28 10:41:41.145         28.6              34.0        1.0</pre>
</template>
</JupyterCell>

<div class="grid grid-cols-3 gap-4 mt-4">
<div v-click class="bh-card">
<div class="bh-card-h">Two sensors, one column</div>
<span class="bh-small">30.7 is the brood sensor, 29.0 the weather station. Both are <code>temperature</code>. No error.</span>
</div>
<div v-click class="bh-card">
<div class="bh-card-h">One device per row</div>
<span class="bh-small">Every device has its own <code>ts</code>: 72,243 rows, mostly <code>NaN</code>.</span>
</div>
<div v-click class="bh-card">
<div class="bh-card-h">Weather three times</div>
<span class="bh-small">The station is registered to every hive, so each hive gets its own copy.</span>
</div>
</div>

<!--
Run this live or just click through: it runs, and that is the problem.

Row 1 has no windSpeed, so it is the brood sensor (Dragino-S31). Row 2 has windSpeed, so
it is the weather station. Same column name, different devices. Row 3 is the brood
sensor, which has none of these columns.

The fix is the rest of this exercise: role tells the devices apart, the split keeps
weather separate, and Exercise 4 floors to the hour and adds the outside_ prefix.
-->

---

# First step: hive or weather?

<div class="bh-note mt-2">
The hives and the weather station measure different places, so in the final table they become different columns. First split every reading: does it belong to a <strong>hive</strong> or to the <strong>weather station</strong>?
</div>

<div class="grid grid-cols-2 gap-6 mt-5">

<div v-click="1" class="bh-card">
<div class="bh-card-h">Way 1 · by <code>measurement_unit</code> ✗</div>
<span class="bh-small">Wind, UV, light, pressure and rain only come from the weather station. But <code>temperature</code> and <code>relativeHumidity</code> come from the weather station <strong>and</strong> the brood sensor, so the unit alone cannot tell them apart.</span>
</div>

<div v-click="2" class="bh-card">
<div class="bh-card-h">Way 2 · by device role ✓</div>
<span class="bh-small">Give every sensor a <code>role</code> from its <code>sensor_type</code>, attach it to each reading with a <code>merge</code>, then split on the role: <code>"weather"</code> or not.</span>
</div>

</div>

<div v-click="3" class="bh-small mt-5">
Next: <code>.map</code> to assign the roles, <code>merge</code> to attach them, a boolean filter to split.
</div>

<!--
This is the "why" for the rest of Exercise 3. The previous slide showed the problem:
the brood sensor and the weather station both land in "temperature".

Ask the room first: how would you separate weather rows from hive rows? Someone will say
"by measurement_unit". Click 1 shows why that half-works: the weather-only units are fine,
but temperature and relativeHumidity are shared. Click 2: the device, not the unit, says
where a reading comes from.
-->

---

# Mapping roles with `.map` and `.assign`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
ROLE = {
    "LoRaWAN Dragino-S31-LB": "brood_sensor",
    "LoRaWAN Dragino-D23-LB": "probes",
    "LoRaWAN SenseCAP-S2120": "weather",
}
sensors = sensors.assign(
    role=sensors["sensor_type"].map(ROLE)
)
```

<div class="bh-note mt-3">
<code>.assign()</code> returns a <strong>new</strong> frame — it never mutates the original. Direct assignment (<code>sensors["role"] = ...</code>) also works.
</div>

</div>
<div>

<div class="bh-out-label">sensors after .map()</div>
<pre class="bh-out">   sensor_id  beehive_id             sensor_type          role
0          1           1  LoRaWAN SenseCAP-S2120       weather
1          2           2  LoRaWAN SenseCAP-S2120       weather
2          3           3  LoRaWAN SenseCAP-S2120       weather
3          4           1  LoRaWAN Dragino-S31-LB  brood_sensor
4          5           3  LoRaWAN Dragino-S31-LB  brood_sensor
5          6           2  LoRaWAN Dragino-S31-LB  brood_sensor
6          7           3  LoRaWAN Dragino-D23-LB        probes
7          8           1  LoRaWAN Dragino-D23-LB        probes
8          9           2  LoRaWAN Dragino-D23-LB        probes
</pre>

<div class="bh-note mt-3">
A key missing from the dict becomes <code>NaN</code> — so <code>sensors["role"].isna().sum()</code> is a free check that your mapping covered everything.
</div>

<div class="bh-small mt-3">
Look at the weather rows in <code>sensors</code> <strong>before</strong> you join. How many rows? How many distinct devices?
</div>

</div>
</div>

---

# Join types: a small example

<div class="flex justify-center gap-10 mt-2">
<div>
<div class="bh-out-label">readings (left)</div>
<pre class="bh-out" style="font-size:0.55rem">   sensor_id  value
0          1   21.5
1          4   30.7
2         99   18.0</pre>
</div>
<div>
<div class="bh-out-label">sensors (right)</div>
<pre class="bh-out" style="font-size:0.55rem">   sensor_id          role
0          1       weather
1          4  brood_sensor
2          8        probes</pre>
</div>
</div>

<div class="bh-small text-center mt-2">Sensors 1 and 4 are in both tables. 99 is only in <code>readings</code>, 8 only in <code>sensors</code>.</div>

<div class="grid grid-cols-4 gap-4 mt-5">

<div v-click="1">
<div class="bh-out-label">how="inner"</div>
<pre class="bh-out" style="font-size:0.55rem">   sensor_id  value          role
0          1   21.5       weather
1          4   30.7  brood_sensor</pre>
<div class="bh-small mt-1">Only keys in <strong>both</strong>. 99 and 8 are gone.</div>
</div>

<div v-click="2">
<div class="bh-out-label">how="left"</div>
<pre class="bh-out" style="font-size:0.55rem">   sensor_id  value          role
0          1   21.5       weather
1          4   30.7  brood_sensor
2         99   18.0           NaN</pre>
<div class="bh-small mt-1">Every <strong>left</strong> row. 99 has no role: <code>NaN</code>.</div>
</div>

<div v-click="3">
<div class="bh-out-label">how="right"</div>
<pre class="bh-out" style="font-size:0.55rem">   sensor_id  value          role
0          1   21.5       weather
1          4   30.7  brood_sensor
2          8    NaN        probes</pre>
<div class="bh-small mt-1">Every <strong>right</strong> row. Sensor 8 has no reading: <code>NaN</code>.</div>
</div>

<div v-click="4">
<div class="bh-out-label">how="outer"</div>
<pre class="bh-out" style="font-size:0.55rem">   sensor_id  value          role
0          1   21.5       weather
1          4   30.7  brood_sensor
2          8    NaN        probes
3         99   18.0           NaN</pre>
<div class="bh-small mt-1"><strong>Everything</strong> from both, gaps filled with <code>NaN</code>.</div>
</div>

</div>

<!--
One question per click: which rows survive? The keys that match (1 and 4) are always
there; the join type only decides what happens to the ones that do not.

In the notebook we use how="left": every reading stays, even if its sensor were missing
from the sensors table, and a missing role would show up as NaN instead of a vanished row.
-->

---

# merge: joining two tables

<JupyterCell n="21" at="2">

<div class="relative">
<div v-click.hide="1">

```python
SENSOR_COLUMNS = [...]  # columns to take from sensors
ON_COLUMNS = [...]      # keys both tables share
MERGE_TYPE = "left"

before = len(distinct_sensor_readings)
distinct_sensor_readings = distinct_sensor_readings.merge(
    sensors[SENSOR_COLUMNS],
    on=ON_COLUMNS,
    how=MERGE_TYPE
)
print(f"distinct_sensor_readings {before:,} -> {len(distinct_sensor_readings):,} after merge")
```

</div>
<div v-click="1" class="absolute inset-0">

```python
SENSOR_COLUMNS = ["sensor_id", "beehive_id", "role"]
ON_COLUMNS = ["sensor_id", "beehive_id"]
MERGE_TYPE = "left"

before = len(distinct_sensor_readings)
distinct_sensor_readings = distinct_sensor_readings.merge(
    sensors[SENSOR_COLUMNS],
    on=ON_COLUMNS,
    how=MERGE_TYPE
)
print(f"distinct_sensor_readings {before:,} -> {len(distinct_sensor_readings):,} after merge")
```

</div>
</div>

<template #output>
<pre>distinct_sensor_readings 396,298 -> 396,298 after merge</pre>
</template>
</JupyterCell>

<div v-click="3" class="bh-small mt-4">
<code>how="left"</code> keeps every left row · <code>"inner"</code> only matches · <code>"outer"</code> everything · <code>"right"</code> every right row
</div>

<!--
Ask the room for SENSOR_COLUMNS and ON_COLUMNS before the reveal click.

distinct_sensor_readings already has beehive_id. Joining on both keys means a reading
cannot be attached to a device registered on a different hive.

If both sides have a column with the same name, pandas suffixes them _x and _y
(change it with suffixes=).
-->

---

# A careless join

<JupyterCell n="22">

```python
len(distinct_sensor_readings.merge(sensors[["beehive_id", "role"]], on="beehive_id", how="left"))
```

<template #output>
<pre>1188894</pre>
</template>
</JupyterCell>

<div v-click class="bh-warn mt-4">
Joined on the hive, not the device: each hive has 3 sensors, so every row is <strong>tripled</strong>. No error, no warning.
</div>

<div v-click class="bh-note mt-4">
Let pandas check for you: <code>merge(..., validate="many_to_one")</code> raises if the right side is not unique on the key.
</div>

---

# Filtering rows: hive vs weather

<JupyterCell n="23" at="1">

```python
mask = sensors['role'] == 'weather'
sensors[mask]
```

<template #output>
<pre style="font-size:0.52rem">   sensor_id  beehive_id            sensor_name            sensor_type      measurement_units installation_date              last_seen  is_active     role
0          1           1  LoRa-2CF7F1C0613005BC  LoRaWAN SenseCAP-S...  lightIntensity,rai...        2025-04-14 2025-06-13 13:51:12...       True  weather
1          2           2  LoRa-2CF7F1C0613005BC  LoRaWAN SenseCAP-S...  lightIntensity,rai...        2025-04-14 2025-06-13 13:51:12...       True  weather
2          3           3  LoRa-2CF7F1C0613005BC  LoRaWAN SenseCAP-S...  lightIntensity,rai...        2025-04-14 2025-06-13 13:51:12...       True  weather</pre>
</template>
</JupyterCell>

<JupyterCell n="24" at="2">

<div class="relative">
<div v-click.hide="3">

```python
hive_rows = ...
weather_rows = ...
```

</div>
<div v-click="3" class="absolute inset-0">

```python
hive_rows = distinct_sensor_readings[distinct_sensor_readings["role"] != "weather"]
weather_rows = distinct_sensor_readings[distinct_sensor_readings["role"] == "weather"]
```

</div>
</div>

</JupyterCell>

<!--
Mirrors notebook cells 39-40. Ask the room before the reveal click.

Point at sensor_name in the sensors[mask] output: three sensor_ids, one physical
weather station, registered once per hive. Hold that thought for the next slide.

Python's and / or do not work on Series. Use & and |, and wrap each condition in
parentheses: df[(df["sensor_id"] == 8) & (df["value"] > 35)]
-->

---

# One weather station, stored three times

<JupyterCell n="25" at="1">

```python
weather_rows["sensor_id"].unique()
```

<template #output>
<pre>array([1, 2, 3])</pre>
</template>
</JupyterCell>

<JupyterCell n="26" at="2">

```python
weather_rows.sort_values("measurement_unit").head(6)
```

<template #output>
<pre>    reading_id  sensor_id  beehive_id measurement_unit                      ts    value     role
2      2236612          1           1   lightIntensity 2026-07-28 10:31:23.976  96248.0  weather
10     2236620          2           2   lightIntensity 2026-07-28 10:31:23.976  96248.0  weather
18     2236628          3           3   lightIntensity 2026-07-28 10:31:23.976  96248.0  weather
34     2236651          1           1   lightIntensity 2026-07-28 10:41:41.145  97400.0  weather
42     2236659          2           2   lightIntensity 2026-07-28 10:41:41.145  97400.0  weather
50     2236667          3           3   lightIntensity 2026-07-28 10:41:41.145  97400.0  weather</pre>
</template>
</JupyterCell>

<JupyterCell n="27" at="4">

<div class="relative">
<div v-click.hide="3">

```python
# How many weather rows share the same (measurement_unit, ts)?
weather_rows = weather_rows.drop_duplicates(subset=[...])
```

</div>
<div v-click="3" class="absolute inset-0">

```python
# How many weather rows share the same (measurement_unit, ts)?
weather_rows = weather_rows.drop_duplicates(subset=["measurement_unit", "ts"])
```

</div>
</div>

</JupyterCell>

<JupyterCell n="28" at="5">

```python
weather_rows = weather_rows.drop(columns=["sensor_id", "beehive_id"])
```

</JupyterCell>

<!--
Mirrors notebook cells 41-44.

Sorted by measurement_unit, the copies sit next to each other: same ts, same value,
sensor_id 1, 2, 3. Ask the room which columns identify one weather reading before
the reveal click. On the local extract: weather_rows 313,056 -> 104,352 after the
drop_duplicates.

After the collapse, sensor_id and beehive_id would just say "1" for every row, which
is a lie: the station belongs to no hive. So drop them.
-->

---
layout: center
class: text-center
---

<div class="bh-kicker">The one habit that matters</div>

# Check your row count<br>after every join

<div class="mt-8 text-lg">

If it changes and you **cannot say exactly why** — stop and find out.

</div>

```python
print(len(df))            # before
df = df.merge(other, on="sensor_id", how="left")
print(len(df))            # after — did that number move? should it have?
```

<div class="mt-6 bh-small">
That single reflex catches the most expensive mistake in this dataset.
</div>

<!--
Say this twice. Once now, once when the first person's row count triples in Exercise 3.

Instructor only: the weather station is registered three times (sensor_ids 1, 2, 3,
same sensor_name), so every weather reading is stored three times, once per hive.
The solution collapses it to one station: drop_duplicates(subset=["measurement_unit", "ts"])
(313,056 -> 104,352 on the local extract), then drops sensor_id and beehive_id.
Exercise 4 builds weather_hourly at the grain of hour and merges it on hour alone.
-->
