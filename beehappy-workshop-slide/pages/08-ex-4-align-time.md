---
layout: center
class: bh-section
---

# Exercise 4 · Align time and handle gaps

One clock. Long to wide. Every hive-hour, even the silent ones.

<div class="mt-8 bh-small">
<code>.dt.floor("h")</code> · <code>groupby().mean()</code> · <code>unstack</code> · <code>reindex</code> · <code>interpolate</code>
</div>

---

# Floor timestamps to the hour

`.dt` unlocks datetime methods on a whole column at once.

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
hive_rows = hive_rows.assign(
    hour=hive_rows["ts"].dt.floor("h")
)
hive_rows[["ts", "hour"]].head()
```

<div class="bh-out-label mt-3">ts vs hour</div>
<pre class="bh-out">                 ts                hour
2025-08-01 04:11:02 2025-08-01 04:00:00
2025-08-01 04:11:02 2025-08-01 04:00:00
2025-08-01 04:31:18 2025-08-01 04:00:00
</pre>

</div>
<div>

```python
ts = hive_rows["ts"]

ts.dt.floor("h")      # 04:11:02 -> 04:00:00
ts.min(), ts.max()    # the period you actually have
ts.diff()             # gap to previous row (Timedelta)
```

<div class="bh-small mt-3">
If <code>.dt</code> raises <em>"Can only use .dt accessor with datetimelike values"</em>, your column is a string. <code>pd.to_datetime(col)</code> fixes it — or you saved CSV in Exercise 0.
</div>

<div class="bh-note mt-3">
Repeat the same <code>.assign(hour=...)</code> on <code>weather_rows</code>. Weather's grain will be <code>(hour,)</code>, not <code>(beehive_id, hour)</code>.
</div>

</div>
</div>

---

# `groupby` + `mean` — still long

```python
hive_h = (hive_rows
    .groupby(["beehive_id", "hour", "measurement_unit"])["value"]
    .mean())     # Series with a 3-level MultiIndex
hive_h.head()
```

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-out-label">still long — one row per hive-hour-measurement</div>
<pre class="bh-out">beehive_id  hour                 measurement_unit
1           2025-08-01 04:00:00  tempC1           34.9
                                 tempC2           35.2
                                 tempC3           34.7
                                 temperature      21.3
Name: value, dtype: float64
</pre>

</div>
<div>

If a device reported twice in the same hour, `mean()` collapses them. Look at the **index** — three levels, still one measurement per row.

<div class="bh-note mt-3">
Same three verbs for weather, grain <code>(hour, measurement_unit)</code> — no <code>beehive_id</code>.
</div>

<div class="bh-small mt-3">
Pass <code>observed=True</code> when grouping categoricals to avoid materialising unused combinations.
</div>

</div>
</div>

---

# Long → wide: `unstack` (and `pivot`)

```python
hive_h = hive_h.unstack("measurement_unit")    # move that level up into columns
```

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-out-label">after groupby().mean() — long</div>
<pre class="bh-out">beehive_id  hour        measurement_unit
1           2025-08-01  tempC1           34.9
                        tempC2           35.2
                        tempC3           34.7
                        temperature      21.3
Name: value, dtype: float64
</pre>

</div>
<div>

<div class="bh-out-label">after .unstack() — wide</div>
<pre class="bh-out">measurement_unit    tempC1  tempC2  tempC3  temperature
beehive_id hour
1          2025-08-01  34.9    35.2    34.7         21.3
           2025-08-02  35.0    35.1    34.8         21.5
</pre>

</div>
</div>

<div class="grid grid-cols-2 gap-6 mt-4">
<div class="bh-note">
<code>unstack</code> takes one index level and spreads it across columns. <code>stack</code> is the inverse. <code>df.pivot_table(index=…, columns=…, values=…, aggfunc="mean")</code> does the same job in one call.
</div>
<div class="bh-note">
<code>.add_prefix("outside_")</code> renames every column at once — handy right after unstacking the weather frame.
</div>
</div>

---

# Building a complete index: `date_range` + `reindex`

```python
hours = pd.date_range(data["ts"].min().floor("h"),
                      data["ts"].max().floor("h"), freq="h")
grid  = pd.MultiIndex.from_product(
    [beehives["beehive_id"], hours],
    names=["beehive_id", "hour"])

features = hive_h.reindex(grid)     # rows not present become all-NaN
```

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-out-label">before reindex — only observed hours</div>
<pre class="bh-out">beehive_id hour                 tempC1
1          2025-08-01 04:00      34.9
1          2025-08-01 05:00      35.0
1          2025-08-01 09:00      35.3   ← 3 hours skipped
</pre>

</div>
<div>

<div class="bh-out-label">after reindex — absence is now visible</div>
<pre class="bh-out">beehive_id hour                 tempC1
1          2025-08-01 04:00      34.9
1          2025-08-01 05:00      35.0
1          2025-08-01 06:00       NaN
1          2025-08-01 07:00       NaN
1          2025-08-01 08:00       NaN
1          2025-08-01 09:00      35.3
</pre>

</div>
</div>

<div class="bh-note mt-4">
Build the grid from the extract window, not from what one device happened to cover. <code>reindex</code> turns every expected-but-absent row into a <code>NaN</code> you can count.
</div>

---

# Handling gaps: `interpolate` and `fillna`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
s.fillna(0)              # a constant
s.ffill()                # carry the last value forward
s.bfill()                # carry the next value backward

s.interpolate(
    method="time",       # respect the timestamp spacing
    limit=3,             # at most 3 consecutive NaNs
    limit_area="inside", # never extrapolate
)
```

<div class="bh-out-label mt-3">before → after, limit=3</div>
<pre class="bh-out">04:00  34.9      34.9
05:00  35.0      35.0
06:00   NaN      35.1
07:00   NaN      35.2
08:00   NaN      35.2
09:00  35.3      35.3
</pre>

</div>
<div>

<div class="bh-warn">
Every filled value is a value <strong>you invented</strong>. A one-hour gap between two readings of 35.0 and 35.3 is a fair guess. A five-day outage is not — leave it <code>NaN</code>.
</div>

<div class="bh-note mt-3">
So: look at the <em>distribution</em> of gap lengths before choosing a policy.

```python
gaps = (hive_h.reset_index()
        .groupby("beehive_id")["hour"]
        .diff().dt.total_seconds() / 3600)
gaps.median(), gaps.quantile(0.99), gaps.max()
# (0.25, 4.0, 121.0)
```
</div>

<div class="bh-small mt-3">
Whatever you choose, <strong>write the rule down</strong>. That sentence belongs in <code>DATA_DICTIONARY.md</code>.
</div>

</div>
</div>

---

# Index gymnastics

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
df.reset_index()          # index levels -> columns
df.set_index("hour")      # a column -> the index
df.droplevel("beehive_id")  # drop one MultiIndex level
df.sort_index()

# group by an index level, not a column
df.groupby(level="beehive_id")

# join on an index level
features.join(weather_h, on="hour")
```

<div class="bh-note mt-3">
<code>join</code> is <code>merge</code>'s index-aware cousin: it lines the right frame's <em>index</em> up against a column or index level on the left. Perfect for attaching one weather table to every hive. Print <code>len</code> before and after.
</div>

</div>
<div>

<div class="bh-out-label">a MultiIndex, printed</div>
<pre class="bh-out">                        tempC1  tempC2
beehive_id hour
1          2025-08-01     34.9    35.2
           2025-08-02     35.0    35.1
2          2025-08-01     34.6    34.9
           2025-08-02     34.8    35.0
</pre>

<div class="bh-small mt-2">
The blank cells under <code>1</code> are not missing — pandas just does not repeat a repeated index label.
</div>

<div class="bh-warn mt-3">
Most alignment bugs in pandas are index bugs. When two frames refuse to line up, print <code>df.index</code> on both.
</div>

</div>
</div>
