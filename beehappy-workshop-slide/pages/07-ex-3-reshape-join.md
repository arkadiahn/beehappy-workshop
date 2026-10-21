---
layout: center
class: bh-section
---

# Exercise 3 · Reshape and join

Attach `role`. Split hive vs weather. The table stays **long**.

<div class="mt-8 bh-small">
<code>.map()</code> · <code>.assign()</code> · boolean filter · <code>merge(on=, how=)</code>
</div>

<!--
The wide reshape — unstack — is Exercise 4. Say that out loud so nobody
starts pivoting here.
-->

---

# Mapping roles with `.map` and `.assign`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
ROLE = {
    "LoRaWAN Dragino-S31-LB": "food_chamber",
    "LoRaWAN Dragino-D23-LB": "brood_chamber",
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
<pre class="bh-out">   sensor_id  beehive_id             sensor_type           role
0          1           1  LoRaWAN SenseCAP-S2120        weather
1          2           2  LoRaWAN SenseCAP-S2120        weather
2          3           3  LoRaWAN SenseCAP-S2120        weather
3          4           1  LoRaWAN Dragino-S31-LB   food_chamber
4          5           3  LoRaWAN Dragino-S31-LB   food_chamber
5          6           2  LoRaWAN Dragino-S31-LB   food_chamber
6          7           3  LoRaWAN Dragino-D23-LB  brood_chamber
7          8           1  LoRaWAN Dragino-D23-LB  brood_chamber
8          9           2  LoRaWAN Dragino-D23-LB  brood_chamber
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

# Filtering rows

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
# Boolean filtering: build a mask, then index with it
mask = sensors["role"] == "weather"
sensors[mask]

# split hive readings vs weather readings
weather_rows = data[data["role"] == "weather"]
hive_rows = data[data["role"] != "weather"]

# combine with & (and), | (or), ~ (not)
# parentheses are REQUIRED around each condition
data[(data["sensor_id"] == 8) &
     (data["value"] > 35)]
```

<div class="bh-out-label mt-2">len of each part</div>
<pre class="bh-out">hive_rows       82,192
weather_rows   310,152
weather sensor_ids: [1 2 3]
</pre>

</div>
<div>

<div class="bh-out-label">mask (a Series of booleans)</div>
<pre class="bh-out">0     True
1     True
2     True
3    False
...
8    False
Name: role, dtype: bool
</pre>

<div class="bh-out-label mt-3">sensors[mask]</div>
<pre class="bh-out">   sensor_id  beehive_id             sensor_type     role
0          1           1  LoRaWAN SenseCAP-S2120  weather
1          2           2  LoRaWAN SenseCAP-S2120  weather
2          3           3  LoRaWAN SenseCAP-S2120  weather
</pre>

<div class="bh-warn mt-3">
Python's <code>and</code> / <code>or</code> do <strong>not</strong> work on Series. Use <code>&</code> and <code>|</code>, and wrap each condition in parentheses.
</div>

</div>
</div>

---

# `merge` — joining two tables

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
SENSOR_COLUMNS = ["sensor_id", "beehive_id", "role"]
ON_COLUMNS = ["sensor_id", "beehive_id"]

before = len(data)
data = data.merge(sensors[SENSOR_COLUMNS],
                  on=ON_COLUMNS, how="left")
print(f"data {before:,} -> {len(data):,} after merge")
# data 392,344 -> 392,344 after merge
```

| `how` | Keeps |
|---|---|
| `"left"` | every row of the left table |
| `"inner"` | only rows matching in both |
| `"outer"` | everything from both |
| `"right"` | every row of the right table |

</div>
<div>

<div class="bh-warn">
<strong>A merge can change your row count even with <code>how="left"</code>.</strong>
If the right table has <em>two</em> rows for a key, the left row is duplicated. No error. No warning.
</div>

```python
# a careless join: on the hive, not the device
print(len(data))     # 392,344
data.merge(sensors[["beehive_id", "role"]],
           on="beehive_id", how="left")
                     # 1,177,032  ← WHY?
```

<div class="bh-note mt-3">
Defensive habit — make pandas check for you:

```python
data.merge(sensors[SENSOR_COLUMNS], on=ON_COLUMNS,
           how="left", validate="many_to_one")
```
It raises if the right side is not unique on the key.
</div>

</div>
</div>

<!--
If both sides have a column with the same name, pandas suffixes them _x and _y
(change it with suffixes=).

data already has beehive_id. Joining on both keys means a reading cannot be attached
to a device registered on a different hive.
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
That single reflex catches the most expensive mistake in this dataset. After the split you still have two <strong>long</strong> frames. Going wide is Exercise 4.
</div>

<!--
Say this twice. Once now, once when the first person's row count triples in Exercise 3.

Instructor only: the weather station is registered three times (sensor_ids 1, 2, 3,
same sensor_name), so every weather reading is stored three times, once per hive.
weather_rows.drop_duplicates(subset=["measurement_unit", "ts"]) goes 310,152 -> 103,384.
The solution keeps weather per hive and merges on (beehive_id, hour) in Exercise 4.
Collapsing to one station and joining on hour alone is the other valid path. Do not mix the two.
-->
