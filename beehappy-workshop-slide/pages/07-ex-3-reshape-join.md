---
layout: center
class: bh-section
---

# Exercise 3 · Reshape and join

Attach hive and role. Split hive vs weather. The table stays **long**.

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
<pre class="bh-out">   sensor_id  beehive_id      sensor_type           role
0          3           1  Dragino-D23-LB  brood_chamber
1          4           1  Dragino-S31-LB   food_chamber
2          7           1  SenseCAP-S2120        weather
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
hive_rows = data[data["role"] != "weather"]
weather_rows = data[data["role"] == "weather"]

# combine with & (and), | (or), ~ (not)
# parentheses are REQUIRED around each condition
data[(data["sensor_id"] == 3) &
     (data["value"] > 35)]
```

</div>
<div>

<div class="bh-out-label">mask (a Series of booleans)</div>
<pre class="bh-out">0    False
1    False
2     True
Name: role, dtype: bool
</pre>

<div class="bh-out-label mt-3">sensors[mask]</div>
<pre class="bh-out">   sensor_id  beehive_id           role
2          7           1        weather
5          8           2        weather
8          9           3        weather
</pre>

<div class="bh-warn mt-3">
Python's <code>and</code> / <code>or</code> do <strong>not</strong> work on Series. Use <code>&</code> and <code>|</code>, and wrap each condition in parentheses — <code>&</code> binds tighter than <code>==</code>.
</div>

</div>
</div>

---

# `merge` — joining two tables

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
data = data.merge(
    sensors[["sensor_id", "beehive_id", "role"]],
    on="sensor_id",
    how="left",
)
```

| `how` | Keeps |
|---|---|
| `"left"` | every row of the left table |
| `"inner"` | only rows matching in both |
| `"outer"` | everything from both |
| `"right"` | every row of the right table |

<div class="bh-small mt-2">
<code>suffixes=("", "_s")</code> controls what happens when both sides have a column of the same name.
</div>

</div>
<div>

<div class="bh-warn">
<strong>A merge can change your row count even with <code>how="left"</code>.</strong>
If the right table has <em>two</em> rows for a key, the left row is duplicated. No error. No warning.
</div>

```python
print(len(data))                 # 939,523
data = data.merge(sensors, on="sensor_id", how="left")
print(len(data))                 # 1,142,006  ← WHY?
```

<div class="bh-note mt-3">
Defensive habit — make pandas check for you:

```python
data.merge(sensors, on="sensor_id",
           how="left", validate="many_to_one")
```
It raises if the right side is not unique on the key.
</div>

</div>
</div>

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
That single reflex catches the most expensive mistake in this dataset. After the split you still have two <strong>long</strong> frames — going wide is Exercise 4.
</div>

<!--
Say this twice. Once now, once when the first person's row count triples in Exercise 3.
-->
