---
layout: center
class: bh-section
---

# Exercise 1 · Profile

What is actually in these tables?

<div class="mt-8 bh-small">
<code>head</code> · <code>tail</code> · <code>dtypes</code> · <code>value_counts</code> · <code>isna</code> · <code>describe</code> · <code>loc</code>
</div>

---

# First look: head

<JupyterCell n="1">

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

<JupyterCell n="2">

```python
raw_sensor_readings.head(10)
```

<template #output>
<pre>   reading_id  sensor_id  beehive_id  measurement_unit                      ts     value
0     2236597          4           1       temperature 2026-07-28 10:28:39.165      30.7
1     2236598          4           1  relativeHumidity 2026-07-28 10:28:39.165      68.5
2     2236636          4           1       temperature 2026-07-28 10:28:39.165      30.7
3     2236637          4           1  relativeHumidity 2026-07-28 10:28:39.165      68.5
4     2236612          1           1    lightIntensity 2026-07-28 10:31:23.976   96248.0
5     2236613          1           1         rainGauge 2026-07-28 10:31:23.976       0.0
6     2236614          1           1  relativeHumidity 2026-07-28 10:31:23.976      33.0
7     2236615          1           1       temperature 2026-07-28 10:31:23.976      29.0
8     2236616          1           1          pressure 2026-07-28 10:31:23.976  100450.0
9     2236617          1           1     windDirection 2026-07-28 10:31:23.976      96.0</pre>
</template>
</JupyterCell>

<!--
head() shows 5 rows by default; pass a number for more. Long format: one row per
measurement, so one uplink becomes several rows with the same ts.
-->

---

# First look: tail and dtypes

<JupyterCell n="3">

```python
raw_sensor_readings.tail()
```

<template #output>
<pre>        reading_id  sensor_id  beehive_id measurement_unit                      ts     value
515708     2752310          3           3      temperature 2026-10-28 10:18:10.743      12.5
515709     2752311          3           3         pressure 2026-10-28 10:18:10.743  100940.0
515710     2752312          3           3    windDirection 2026-10-28 10:18:10.743     354.0
515711     2752313          3           3          uvIndex 2026-10-28 10:18:10.743       2.9
515712     2752314          3           3        windSpeed 2026-10-28 10:18:10.743       1.1</pre>
</template>
</JupyterCell>

<div class="grid grid-cols-2 gap-6">
<div>

<JupyterCell n="4">

```python
raw_sensor_readings.dtypes
```

<template #output>
<pre>reading_id                   int64
sensor_id                    int64
beehive_id                   int64
measurement_unit               str
ts                  datetime64[us]
value                      float64
dtype: object</pre>
</template>
</JupyterCell>

</div>
<div class="bh-small mt-6">

The index on the left of `tail()` is the row count: **515,713 rows**.

`ts` must be `datetime64`. Check this *first*, every time.

</div>
</div>

<!--
str is text; older pandas versions print object.
-->

---

# Selecting columns

```python
raw_sensor_readings["value"]                   # one column -> Series
raw_sensor_readings[["ts", "value"]]           # several   -> DataFrame
```

### One column: measurement_unit

<div class="grid gap-4" style="grid-template-columns: 0.8fr 1fr">
<div>

<JupyterCell n="5">

```python
raw_sensor_readings["measurement_unit"]
```

<template #output>
<pre>0              temperature
1         relativeHumidity
2              temperature
3         relativeHumidity
4           lightIntensity
                ...
515708         temperature
515709            pressure
515710       windDirection
515711             uvIndex
515712           windSpeed
Name: measurement_unit, Length: 515713, dtype: str</pre>
</template>
</JupyterCell>

</div>
<div>

<JupyterCell n="6">

```python
raw_sensor_readings["measurement_unit"].value_counts()
```

<template #output>
<pre>measurement_unit
temperature         79343
relativeHumidity    79343
tempC3              39671
tempC1              39671
tempC2              39671
lightIntensity      39669
rainGauge           39669
pressure            39669
windDirection       39669
uvIndex             39669
windSpeed           39669
Name: count, dtype: int64</pre>
</template>
</JupyterCell>

</div>
</div>

<!--
One pair of brackets gives a Series. value_counts() is the single best first move on any
unfamiliar column. temperature and relativeHumidity count twice: the food sensor and the
weather station both report them.
-->

---

# When, and is anything missing?

<div class="grid grid-cols-2 gap-6">
<div>

<JupyterCell n="7" at="1">

```python
raw_sensor_readings["ts"].min()
```

<template #output>
<pre>Timestamp('2026-07-28 10:28:39.165000')</pre>
</template>
</JupyterCell>

<JupyterCell n="8" at="2">

```python
raw_sensor_readings["ts"].max()
```

<template #output>
<pre>Timestamp('2026-10-28 10:18:10.743000')</pre>
</template>
</JupyterCell>

<JupyterCell n="10" at="4">

```python
raw_sensor_readings["value"].isna().sum()
```

<template #output>
<pre>np.int64(0)</pre>
</template>
</JupyterCell>

</div>
<div>

<JupyterCell n="9" at="3">

```python
raw_sensor_readings["value"].isna()
```

<template #output>
<pre>0         False
1         False
2         False
3         False
4         False
          ...
515708    False
515709    False
515710    False
515711    False
515712    False
Name: value, Length: 515713, dtype: bool</pre>
</template>
</JupyterCell>

</div>
</div>

<!--
isna() gives True/False per row; .sum() counts the Trues. Exercise 4 exists because of
the last sentence.
-->

---

# Descriptive statistics: describe

<div class="grid grid-cols-2 gap-6">
<div>

<JupyterCell n="11">

```python
raw_sensor_readings["value"].describe()
```

<template #output>
<pre>count    515713.000000
mean       8873.198813
std       27484.013765
min           0.000000
25%           2.200000
50%          26.300000
75%          62.700000
max      111404.000000
Name: value, dtype: float64</pre>
</template>
</JupyterCell>

</div>
<div v-click class="bh-note mt-4 self-start">
A <code>max</code> of 111,404 is light in lux, in the same column as °C and pascals. Group first.
</div>
</div>

<JupyterCell n="12">

```python
raw_sensor_readings.groupby("measurement_unit")["value"].describe()
```

<template #output>
<pre>                    count           mean           std      min      25%       50%       75%       max
measurement_unit
lightIntensity    39669.0   14821.139530  24544.177910      0.0      0.0     992.0   18197.0  111404.0
pressure          39669.0  100106.224760    545.066852  98370.0  99700.0  100150.0  100470.0  101460.0
rainGauge         39669.0       0.128865      2.047008      0.0      0.0       0.0       0.0     152.4
relativeHumidity  79343.0      62.767007     15.955076     15.0     54.0      62.0      71.4      98.0
tempC1            39671.0      25.955280      6.226831      9.4     22.5      27.0      31.0      37.1
tempC2            39671.0      24.989229      5.669921      8.8     21.6      25.5      28.9      38.1
tempC3            39671.0      22.591253      7.023798      7.2     17.4      22.9      27.6      42.0
temperature       79343.0      23.696525      8.220606      3.9     16.8      24.9      31.3      43.9
uvIndex           39669.0       0.948453      1.840270      0.0      0.0       0.0       1.0       9.8
windDirection     39669.0     179.702110    115.009196      0.0     49.0     192.0     270.0     359.0
windSpeed         39669.0       0.542320      0.777330      0.0      0.0       0.0       1.0       7.0</pre>
</template>
</JupyterCell>

<!--
Long format mixes units in one column, so describe() on the whole column means nothing
until you group. Single values when you want just one: s.min(), s.max(), s.mean(),
s.median(), s.std(), s.quantile(0.99), s.idxmax().
-->

---

# The lookup tables

<JupyterCell n="13">

```python
sensors.loc[0, "measurement_units"]
```

<template #output>
<pre>'lightIntensity,rainGauge,relativeHumidity,temperature,pressure,windDirection,uvIndex,windSpeed'</pre>
</template>
</JupyterCell>

<JupyterCell n="14">

```python
beehives.loc[0, "location"]
```

<template #output>
<pre>'(49.15182633037482,9.215298005933729)'</pre>
</template>
</JupyterCell>

<div v-click class="bh-small mt-4">
<code>.loc[row, column]</code> picks one value. <code>sensors</code> and <code>beehives</code> are tiny: look at them whole.
</div>

---

# Four gotchas that will bite today

<div class="grid grid-cols-2 gap-4 mt-3 text-sm">

<div class="bh-card">
<div class="bh-card-h">1 · NaN is not equal to itself</div>

```python
np.nan == np.nan     # False
df[df["x"] == np.nan]   # always empty
df[df["x"].isna()]      # correct
```
Most aggregations silently *skip* NaN: `mean()` of `[1, NaN, 3]` is `2.0`, not `NaN`.
</div>

<div class="bh-card">
<div class="bh-card-h">2 · Chained assignment does nothing</div>

```python
df[df["x"] > 0]["y"] = 1        # df unchanged
df.loc[df["x"] > 0, "y"] = 1    # ✓
```
Since pandas 3, a filtered frame always behaves like a copy. Write through `.loc[rows, col]`, or build new frames with `.assign()`.
</div>

<div class="bh-card">
<div class="bh-card-h">3 · Most methods do not mutate</div>

```python
df.drop_duplicates(subset=KEY)   # discarded!
df = df.drop_duplicates(subset=KEY)   # ✓
```
`rename`, `merge`, `sort_values`, `reset_index`, `fillna` — all return a **new** frame.
</div>

<div class="bh-card">
<div class="bh-card-h">4 · Integers become floats</div>

Introduce a single NaN into an `int64` column and the whole column becomes `float64`. IDs turn into `1.0`, `2.0` and stop matching on a join. Use the nullable `"Int64"` dtype if you need both.
</div>

</div>
