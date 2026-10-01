---
layout: center
class: bh-section
---

# Exercise 1 · Profile

What is actually in these tables?

<div class="mt-8 bh-small">
<code>head</code> · <code>dtypes</code> · <code>value_counts</code> · <code>isna</code> · <code>describe</code>
</div>

---

# First look: shape, head, dtypes

```python
data.shape          # (511937, 6)      -> (rows, columns)
len(data)           # 511937           -> rows only
data.columns        # Index(['reading_id', 'sensor_id', 'beehive_id', 'measurement_unit', 'ts', 'value'])
data.head(3)        # first 3 rows.  .tail(3) for the last
```

<div class="grid grid-cols-5 gap-5 mt-4">
<div class="col-span-3">

<div class="bh-out-label">data.head(3)</div>
<pre class="bh-out" style="font-size:0.56rem">   reading_id  sensor_id  beehive_id measurement_unit                      ts  value
0     2072737          8           1           tempC3 2026-06-28 12:22:52.471   37.3
1     2072738          8           1           tempC1 2026-06-28 12:22:52.471   35.5
2     2072739          8           1           tempC2 2026-06-28 12:22:52.471   35.7
</pre>

</div>
<div class="col-span-2">

<div class="bh-out-label">data.dtypes</div>
<pre class="bh-out">reading_id                   int64
sensor_id                    int64
beehive_id                   int64
measurement_unit               str
ts                  datetime64[us]
value                      float64
</pre>

<div class="bh-small mt-2">
<code>str</code> is text (older pandas versions print <code>object</code>).
<code>datetime64[…]</code> is what you want <code>ts</code> to be. Check this <em>first</em>, every time.
</div>

</div>
</div>

---

# Selecting columns

```python
data["value"]                   # one column -> Series
data[["ts", "value"]]           # several   -> DataFrame
```

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-out-label">data["value"]</div>
<pre class="bh-out">0    37.3
1    35.5
2    35.7
Name: value, dtype: float64
</pre>

</div>
<div>

<div class="bh-out-label">data[["ts", "value"]]</div>
<pre class="bh-out">                       ts  value
0 2026-06-28 12:22:52.471   37.3
1 2026-06-28 12:22:52.471   35.5
2 2026-06-28 12:22:52.471   35.7
</pre>

<div class="bh-note mt-3">
One pair of brackets returns a <strong>Series</strong>. Two pairs — a list of names — returns a <strong>DataFrame</strong>.
</div>

</div>
</div>

---

# Counting things: `value_counts`, `nunique`, `isna`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
data["measurement_unit"].value_counts()
```

<div class="bh-out-label">output</div>
<pre class="bh-out">measurement_unit
temperature         78760
relativeHumidity    78760
lightIntensity      39381
rainGauge           39381
...
tempC3              39377
tempC1              39377
tempC2              39377
Name: count, dtype: int64
</pre>

<div class="bh-small mt-2">Your single best first move on any unfamiliar column.</div>

</div>
<div>

```python
data["sensor_id"].nunique()      # 9
data["sensor_id"].unique()       # array([8, 6, 1, ...])

data["ts"].min(), data["ts"].max()
data["ts"].max() - data["ts"].min()  # 91 days 23:51:50

data["value"].isna().sum()       # 0   <- no NULLs
```

<div class="bh-warn mt-3">
Zero NULLs does <strong>not</strong> mean nothing is missing. In this dataset, an hour with no reading has no <em>row</em> at all. Exercise 4 exists because of that sentence.
</div>

<div class="bh-small mt-3">
Also look at <code>sensors</code> and <code>beehives</code> whole. They are tiny, and they are how you attach context later. <code>sensors.loc[0, "measurement_units"]</code> lists what one device type reports.
</div>

</div>
</div>

---

# Descriptive statistics

```python
data["value"].describe()
data.groupby("measurement_unit")["value"].describe()   # per group
```

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-out-label">value.describe()</div>
<pre class="bh-out">count    511937.000000
mean       9359.079351
std       28067.571822
min           0.000000
25%           4.400000
50%          29.400000
75%          60.300000
max      126795.000000
Name: value, dtype: float64
</pre>

</div>
<div>

Single values, when you want just one:

```python
s.min()  s.max()  s.mean()  s.median()
s.sum()  s.std()  s.quantile(0.99)
s.idxmax()          # the *index label* of the max
```

<div class="bh-note mt-3">
That <code>max</code> of 126,795 is light intensity in lux, sitting in the same column as temperatures in °C and air pressure in pascals (~100,000). Long format mixes units in one column, so <code>describe()</code> on the whole column means nothing until you group.
</div>

</div>
</div>
