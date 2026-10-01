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
<pre class="bh-out">                       ts                hour
0 2026-06-28 12:22:52.471 2026-06-28 12:00:00
1 2026-06-28 12:22:52.471 2026-06-28 12:00:00
2 2026-06-28 12:22:52.471 2026-06-28 12:00:00
3 2026-06-28 12:23:27.991 2026-06-28 12:00:00
</pre>

</div>
<div>

```python
ts = hive_rows["ts"]

ts.dt.floor("h")      # 12:22:52 -> 12:00:00
ts.min(), ts.max()    # the period you actually have
ts.diff()             # gap to previous row (Timedelta)
```

<div class="bh-small mt-3">
If <code>.dt</code> raises <em>"Can only use .dt accessor with datetimelike values"</em>, your column is a string. <code>pd.to_datetime(col)</code> fixes it — or you saved CSV in Exercise 0.
</div>

<div class="bh-note mt-3">
Repeat the same <code>.assign(hour=...)</code> on <code>weather_rows</code>. Hive devices report every ~20 min, the weather station every ~10 min, so every hour has readings to average.
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
1           2026-06-28 12:00:00  relativeHumidity    62.25
                                 tempC1              35.65
                                 tempC2              35.75
                                 tempC3              37.40
                                 temperature         35.25
            2026-06-28 13:00:00  relativeHumidity    60.50
Name: value, dtype: float64
</pre>

</div>
<div>

A device reports about three times an hour, and `mean()` collapses those into one value. Look at the **index** — three levels, still one measurement per row.

<div class="bh-note mt-3">
Same three verbs for weather, with the same grain: <code>(beehive_id, hour, measurement_unit)</code>.
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

<div class="grid grid-cols-5 gap-5 mt-4">
<div class="col-span-2">

<div class="bh-out-label">after groupby().mean() — long</div>
<pre class="bh-out">beehive_id  hour                 measurement_unit
1           2026-06-28 12:00:00  relativeHumidity    62.25
                                 tempC1              35.65
                                 tempC2              35.75
                                 tempC3              37.40
                                 temperature         35.25
Name: value, dtype: float64
</pre>

</div>
<div class="col-span-3">

<div class="bh-out-label">after .unstack() — wide</div>
<pre class="bh-out">measurement_unit     relativeHumidity  tempC1  tempC2  tempC3  temperature
beehive_id hour
1          06-28 12:00          62.25   35.65   35.75   37.40        35.25
           06-28 13:00          60.50   36.10   36.30   37.77        35.57
</pre>
<div class="bh-small mt-1">hour shortened to fit the slide</div>

</div>
</div>

<div class="grid grid-cols-2 gap-6 mt-4">
<div class="bh-note">
<code>unstack</code> takes one index level and spreads it across columns. <code>stack</code> is the inverse. <code>df.pivot_table(index=…, columns=…, values=…, aggfunc="mean")</code> does the same job in one call.
</div>
<div class="bh-note">
<code>.add_prefix("outside_")</code> renames every column at once. Use it right after unstacking the weather frame: <code>temperature</code> becomes <code>outside_temperature</code> and no longer clashes with the food chamber's.
</div>
</div>

---

# Building a complete index: `date_range` + `reindex`

```python
START_TIME_H = data["ts"].min().floor("h")
END_TIME_H = data["ts"].max().floor("h")
hours = pd.date_range(START_TIME_H, END_TIME_H, freq="h")
grid = pd.MultiIndex.from_product(
    [beehives["beehive_id"], hours], names=["beehive_id", "hour"])

features = hive_h.reindex(grid)     # rows not present become all-NaN
# observed hive-hours 6,504 vs complete grid 6,627  -> 123 absent
```

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-out-label">before reindex — only observed hours</div>
<pre class="bh-out">beehive_id hour              tempC1
1          2026-07-10 15:00    35.0
1          2026-07-10 16:00    35.0
1          2026-07-11 09:00    33.2   ← 16 hours skipped
</pre>

</div>
<div>

<div class="bh-out-label">after reindex — absence is now visible</div>
<pre class="bh-out">beehive_id hour              tempC1
1          2026-07-10 15:00    35.0
1          2026-07-10 16:00    35.0
1          2026-07-10 17:00     NaN
1          2026-07-10 18:00     NaN
...                             ...  (16 rows of NaN)
1          2026-07-11 08:00     NaN
1          2026-07-11 09:00    33.2
</pre>

</div>
</div>

<div class="bh-note mt-4">
Build the grid from the extract window, not from what one device happened to cover. <code>reindex</code> turns every expected-but-absent row into a <code>NaN</code> you can count.
</div>

---

# Handling gaps: measure first, then decide

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
# gap between consecutive observed hours, per hive
gaps = (hive_h.reset_index()
        .groupby("beehive_id")["hour"].diff())
gaps.max()            # Timedelta('0 days 17:00:00')
gaps.value_counts()
```

<div class="bh-out-label mt-2">gaps.value_counts()</div>
<pre class="bh-out">0 days 01:00:00    6443   ← no gap
0 days 02:00:00      45   ← one hour missing
0 days 03:00:00       4
0 days 04:00:00       2
0 days 05:00:00       4
0 days 17:00:00       3   ← 16 hours missing
</pre>

<div class="bh-note mt-3">
<strong>Our policy: leave NaN.</strong> The validator <em>fails</em> a column that is more than 25% empty and <em>warns</em> if nothing at all is missing. Honest gaps pass.
</div>

</div>
<div>

If you do fill, these are the tools:

```python
s.fillna(0)              # a constant
s.ffill()                # carry the last value forward
s.interpolate(
    method="time",       # respect the timestamp spacing
    limit=3,             # at most 3 consecutive NaNs
    limit_area="inside", # never extrapolate
)
```

<div class="bh-out-label mt-2">hive 1 tempC1 · before → after, limit=3</div>
<pre class="bh-out">2026-08-11 14:00   35.5    35.5
2026-08-11 15:00    NaN    34.9
2026-08-11 16:00    NaN    34.2
2026-08-11 17:00    NaN    33.6
2026-08-11 18:00   33.0    33.0
</pre>

<div class="bh-warn mt-3">
Every filled value is a value <strong>you invented</strong>. Whatever you choose, <strong>write the rule down</strong> in <code>DATA_DICTIONARY.md</code>.
</div>

</div>
</div>

---

# Attach the weather: `reset_index` + `merge`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
before = len(features)
features = features.reset_index().merge(
    weather_h.reset_index(),
    on=["beehive_id", "hour"], how="left",
)
print(f"features {before:,} -> {len(features):,} "
      "after weather merge")
# features 6,627 -> 6,627 after weather merge
```

<div class="bh-note mt-3">
<code>reset_index()</code> turns the <code>beehive_id</code> and <code>hour</code> index levels back into ordinary columns, so <code>merge(on=…)</code> can find them. After this, <code>features</code> has a plain 0, 1, 2… index.
</div>

```python
df.reset_index()            # index levels -> columns
df.set_index("hour")        # a column -> the index
df.groupby(level="beehive_id")  # by index level
```

</div>
<div>

<div class="bh-out-label">a MultiIndex, printed</div>
<pre class="bh-out">measurement_unit                tempC1  tempC2
beehive_id hour
1          2026-06-28 12:00:00    35.6    35.8
           2026-06-28 13:00:00    36.1    36.3
2          2026-06-28 12:00:00    36.8    34.9
           2026-06-28 13:00:00    37.2    35.2
</pre>

<div class="bh-small mt-2">
The blank cells under <code>1</code> are not missing. pandas does not repeat a repeated index label.
</div>

<div class="bh-warn mt-3">
Most alignment bugs in pandas are index bugs. When two frames refuse to line up, print <code>df.index</code> on both.
</div>

</div>
</div>

<!--
Weather was kept per hive in Exercise 3, so it merges on (beehive_id, hour). If someone
collapsed weather to one station instead, they merge on hour only. Both are valid as
long as they do not mix the two.
-->
