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
data.shape          # (1_203_441, 5)   -> (rows, columns)
len(data)           # 1203441          -> rows only
data.columns        # Index(['reading_id', 'sensor_id', 'measurement_unit', 'ts', 'value'], ...)
data.head(3)        # first 3 rows.  .tail(3) for the last
```

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-out-label">data.head(3)</div>
<pre class="bh-out">   reading_id  sensor_id measurement_unit               ts  value
0     9182344          3           tempC1 2025-08-01 04:11   34.9
1     9182345          3           tempC2 2025-08-01 04:11   35.2
2     9182346          3           tempC3 2025-08-01 04:11   34.7
</pre>

</div>
<div>

<div class="bh-out-label">data.dtypes</div>
<pre class="bh-out">reading_id                   int64
sensor_id                    int64
measurement_unit            object
ts                  datetime64[ns]
value                      float64
</pre>

<div class="bh-small mt-2">
<code>object</code> means "Python objects" — usually strings.
<code>datetime64[ns]</code> is what you want <code>ts</code> to be. Check this <em>first</em>, every time.
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
<pre class="bh-out">0    34.9
1    35.2
2    34.7
Name: value, dtype: float64
</pre>

</div>
<div>

<div class="bh-out-label">data[["ts", "value"]]</div>
<pre class="bh-out">                  ts  value
0  2025-08-01 04:11   34.9
1  2025-08-01 04:11   35.2
2  2025-08-01 04:11   34.7
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
tempC1              184_221
tempC2              184_221
tempC3              184_221
temperature         121_004
relativeHumidity    121_004
windSpeed            98_330
Name: count, dtype: int64
</pre>

<div class="bh-small mt-2">Your single best first move on any unfamiliar column.</div>

</div>
<div>

```python
data["sensor_id"].nunique()      # 9
data["sensor_id"].unique()       # array([1, 2, 3, ...])

data["ts"].min(), data["ts"].max()

data["value"].isna().sum()       # 0   <- no NULLs
```

<div class="bh-warn mt-3">
Zero NULLs does <strong>not</strong> mean nothing is missing. In this dataset, an hour with no reading has no <em>row</em> at all. Exercise 4 exists because of that sentence.
</div>

<div class="bh-small mt-3">
Also look at <code>sensors</code> and <code>beehives</code> whole — they are tiny, and they are how you will attach context later.
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
<pre class="bh-out">count    1.203441e+06
mean     3.021473e+01
std      2.884201e+01
min     -9.700000e+00
25%      1.840000e+01
50%      2.760000e+01
75%      3.489000e+01
max      1.019400e+05
dtype: float64
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
That <code>max</code> of 101,940 is air pressure in pascals sharing a column with temperatures in °C. Long format mixes units in one column — <code>describe()</code> on the whole column is meaningless until you group.
</div>

</div>
</div>
