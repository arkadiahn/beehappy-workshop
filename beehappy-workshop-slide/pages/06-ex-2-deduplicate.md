---
layout: center
class: bh-section
---

# Exercise 2 · Deduplicate

Name the grain. Let pandas check it.

<div class="mt-8 bh-small">
<code>duplicated</code> · <code>drop_duplicates(subset=)</code>
</div>

---

# Duplicates: what is one reading?

<JupyterCell n="16" at="1">

```python
raw_sensor_readings.duplicated().sum()
```

<template #output>
<pre>0</pre>
</template>
</JupyterCell>

<JupyterCell n="17" at="2">

```python
raw_sensor_readings.head()
```

<template #output>
<pre>   reading_id  sensor_id  beehive_id  measurement_unit                      ts    value
0     2236597          4           1       temperature 2026-07-28 10:28:39.165     30.7
1     2236598          4           1  relativeHumidity 2026-07-28 10:28:39.165     68.5
2     2236636          4           1       temperature 2026-07-28 10:28:39.165     30.7
3     2236637          4           1  relativeHumidity 2026-07-28 10:28:39.165     68.5
4     2236612          1           1    lightIntensity 2026-07-28 10:31:23.976  96248.0</pre>
</template>
</JupyterCell>


<!--
duplicated() with no subset compares whole rows; reading_id is unique, so it says 0. Let
the room conclude there are no duplicates, then show head(): rows 0 and 2 are the same
reading stored twice.
-->

---

# Duplicates: drop_duplicates

<JupyterCell n="18" at="2">

<div class="relative">
<div v-click.hide="1">

```python
KEYS = [...]  # which columns identify one real measurement?
```

</div>
<div v-click="1" class="absolute inset-0">

```python
KEYS = ["sensor_id", "measurement_unit", "ts", "value"]
```

</div>
</div>

</JupyterCell>

<JupyterCell n="19" at="3">

```python
before = len(raw_sensor_readings)
distinct = len(raw_sensor_readings.drop_duplicates(subset=KEYS))
print(f"{before:,} rows -> {distinct:,} distinct keys "
      f"({100 * (1 - distinct / before):.1f}% redundant)")
```

<template #output>
<pre>515,713 rows -> 396,298 distinct keys (23.2% redundant)</pre>
</template>
</JupyterCell>

<JupyterCell n="20" at="4">

```python
distinct_sensor_readings = raw_sensor_readings.drop_duplicates(subset=KEYS)
```

</JupyterCell>

<div v-click="5" class="bh-small mt-3">
Rows 0 and 2 are the same reading stored twice; only <code>reading_id</code> differs. So <code>duplicated()</code> on whole rows finds 0, and <code>subset=KEYS</code> is needed.
</div>

<!--
Mirrors the notebook cells for Exercise 2: define KEYS, count, then drop.
Ask the room for KEYS before the reveal click.
keep="first" is the default; keep="last" or keep=False also exist.

The duplicates come from a live bug in the ChatBotCollector service. They run at
21–27% per month and the rate is uneven, so they skew any mean weighted by row count.
Dropping them is not just cosmetic.

If the redundancy prints near zero, the bug was fixed upstream. Say so and teach it as
"here is how you would have caught it".
-->
