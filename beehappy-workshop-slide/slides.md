---
theme: default
title: BeeHappy — Data Foundation Workshop
info: |
  ## BeeHappy — Data Foundation
  From three raw tables of beehive sensor data to one model-ready dataframe.

  Intro + pandas 101 for the hands-on workshop.
colorSchema: light
class: bh-cover
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
fonts:
  sans: Inter
  mono: JetBrains Mono
duration: 45min
---

<div class="bh-kicker">Bildungscampus Heilbronn · Live LoRaWAN data</div>

# <span class="bh-brand">BeeHappy</span> — Data Foundation

Three tables of real beehive sensor data go in.<br>
**One dataframe fit to train a model on** comes out.

<div class="mt-10 flex gap-3 items-center">
  <span class="bh-pill">~4 hours</span>
  <span class="bh-pill">6 exercises</span>
  <span class="bh-pill">pandas + Jupyter</span>
</div>

<div @click="$slidev.nav.next" class="mt-12 py-1 cursor-pointer text-amber-700">
  Press Space to start <carbon:arrow-right class="inline" />
</div>

<!--
Welcome. Two things to say out loud before we begin:

1. This data is real and nobody has cleaned it. Every problem you hit today is a
   problem that actually exists in a production database right now.
2. You do not need to know pandas. The second half of this deck is the entire
   toolkit you will use, function by function.
-->

---
layout: center
class: bh-section
---

# 1 · Intro

What the data is, where it comes from, and why cleaning it is the job

---

# 🐝 What is BeeHappy?

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

**Three beehives** at Bildungscampus Heilbronn, wired with **LoRaWAN sensors**, reporting continuously since **2025**.

Each hive carries devices that measure what is happening inside and around it:

- **Brood chamber** — three temperature probes (`tempC1/C2/C3`)
- **Food chamber** — temperature + humidity
- **Weather station** — temperature, humidity, wind, UV, pressure, light, rain

Readings travel over LoRaWAN to a collector service, which writes them into a **PostgreSQL** database.

</div>
<div>

```mermaid {scale: 0.62, theme: 'base', themeVariables: {primaryColor: '#fef3c7', primaryBorderColor: '#f59e0b', primaryTextColor: '#92400e', lineColor: '#d97706', secondaryColor: '#fde68a', tertiaryColor: '#fffbeb', fontFamily: 'Inter, sans-serif'}}
graph TD
  A[Brood sensor<br/>Dragino D23-LB] --> G[LoRaWAN<br/>gateway]
  B[Food sensor<br/>Dragino S31-LB] --> G
  C[Weather station<br/>SenseCAP S2120] --> G
  G --> D[ChatBotCollector<br/>service]
  D --> E[(PostgreSQL)]
  E --> F[You, today]
```

<div class="bh-note mt-3">
The collector is a real service with real bugs. Remember that — it matters in Exercise 2.
</div>

</div>
</div>

<!--
The hardware detail is not trivia. Knowing that three *different device types* report
on three *different schedules* is what makes Exercise 4 make sense.
-->

---

# Why are we collecting this data?

<div class="grid grid-cols-3 gap-4 mt-6">

<div class="bh-card">
<div class="bh-card-h">🌡️ Colony health</div>
Brood temperature is tightly regulated by the bees at ~35 °C. When it drifts, something is wrong — and it drifts <em>before</em> the beekeeper can see it.
</div>

<div class="bh-card">
<div class="bh-card-h">🐝 Swarm prediction</div>
Swarming costs a beekeeper half a colony. The run-up shows up in temperature and activity patterns days in advance.
</div>

<div class="bh-card">
<div class="bh-card-h">❄️ Overwintering</div>
Most colony losses happen in winter. Humidity and temperature history tell you which hives are at risk while you can still act.
</div>

</div>

<div class="mt-8">

All three are the same shape of question:

> Given what the sensors said over the last *N* hours, **what is about to happen in this hive?**

That is a machine-learning question. And every ML model needs the same thing underneath it: **a rectangular table, one row per thing you want to predict about.**

</div>

<!--
Pull the group toward the framing: we are not doing data cleaning as an end in itself.
We are building the input a model needs.
-->

---
layout: two-cols
layoutClass: gap-10
---

# The gap

What the database gives you:

<div class="bh-out-label mt-2">data (long, one row per measurement)</div>
<pre class="bh-out">reading_id  sensor_id  measurement_unit  ts                value
   9182344          3  tempC1            2025-08-01 04:11   34.9
   9182345          3  tempC2            2025-08-01 04:11   35.2
   9182346          3  tempC3            2025-08-01 04:11   34.7
   9182347          7  temperature       2025-08-01 04:17   21.3
   9182348          7  relativeHumidity  2025-08-01 04:17   63.0
   9182349          3  tempC1            2025-08-01 04:11   34.9  ← ?
</pre>

::right::

What a model needs:

<div class="bh-out-label mt-2">features_hourly (wide, one row per hive-hour)</div>
<pre class="bh-out">hive  hour              brood_temp_c1  food_temp  outside_temp
   1  2025-08-01 04:00           34.9       21.3          17.4
   1  2025-08-01 05:00           35.0       21.5          17.9
   1  2025-08-01 06:00           35.1       21.9          19.1
   2  2025-08-01 04:00           34.6       20.8          17.4
</pre>

<div class="bh-note mt-6">
Closing that gap <strong>is</strong> the workshop. Everything in between is pandas.
</div>

---

# The data you are given

Three tables in Postgres. You pull them once, save them, and work from your copy.

<div class="grid grid-cols-3 gap-4 mt-6">

<div class="bh-card">
<div class="bh-card-h">beehives</div>
<span class="bh-small">~3 rows</span>

The hives themselves — id and name.
</div>

<div class="bh-card">
<div class="bh-card-h">sensors</div>
<span class="bh-small">~9 rows</span>

The devices: `sensor_id`, `sensor_type`, `sensor_name`, and which `beehive_id` each belongs to.
</div>

<div class="bh-card">
<div class="bh-card-h">data</div>
<span class="bh-small">millions of rows</span>

Every reading: `reading_id`, `sensor_id`, `measurement_unit`, `ts`, `value`.
</div>

</div>

<div class="mt-6">

You pull **the last three months** of `data` — filtered in SQL, not in pandas afterwards. The full history is far too big to be worth moving.

</div>

<div class="bh-note mt-4">
9 sensor rows for 7 physical devices. Worth staring at for a second longer than feels necessary.
</div>

---

# Long vs. wide — the first real reshape

<div class="grid grid-cols-2 gap-6 mt-2">
<div>

**Long format** — one row per *measurement*

<pre class="bh-out">ts                  unit              value
2025-08-01 04:11    tempC1             34.9
2025-08-01 04:11    tempC2             35.2
2025-08-01 04:11    tempC3             34.7
</pre>

<div class="bh-small mt-2">
One device uplink writes <em>several</em> rows — one per thing it measured.
Great for storage: add a new sensor type, no schema change.
</div>

</div>
<div>

**Wide format** — one row per *event*, one column per measurement

<pre class="bh-out">ts                tempC1  tempC2  tempC3
2025-08-01 04:11    34.9    35.2    34.7
</pre>

<div class="bh-small mt-2">
Terrible for storage, but it is the <em>only</em> shape statistics and ML libraries accept.
Every <code>fit(X, y)</code> in Python wants X rectangular.
</div>

</div>
</div>

<div class="mt-6">

In pandas the move between them is `pivot` / `unstack` (long → wide) and `melt` (wide → long). You will use `unstack` in Exercise 3.

</div>

---
layout: center
class: text-center
---

# Why data cleaning comes first

<div class="mt-8 text-left max-w-3xl mx-auto">

> A model cannot tell the difference between a signal and a mistake in your table.
> It will happily learn the mistake.

</div>

<div class="grid grid-cols-3 gap-4 mt-10 text-left">
<div class="bh-card">
<div class="bh-card-h">Duplicates</div>
<span class="bh-small">Your "average temperature" is silently a weighted average — weighted by how many times the collector happened to insert the same row.</span>
</div>
<div class="bh-card">
<div class="bh-card-h">Bad joins</div>
<span class="bh-small">Three times the rows, no error message, and every summary statistic you compute afterwards is wrong.</span>
</div>
<div class="bh-card">
<div class="bh-card-h">Silent gaps</div>
<span class="bh-small">A missing row is not a <code>NaN</code>. It is nothing at all — and nothing is very hard to notice.</span>
</div>
</div>

<div class="mt-8 bh-small">
The usual industry estimate is that 60–80% of any data science project is this step. Today is that step.
</div>

<!--
Do not moralise for too long. One sentence per card and move on — they will meet all
three of these for real within the hour.
-->

---

# The day: six exercises

| # | Exercise | What you produce | Time |
|---|---|---|---|
| **0** | **Extract** | Three months of `data` + both lookup tables, pulled once, saved to disk | 30 min |
| **1** | **Profile** | A written description of what is actually in there | 30 min |
| **2** | **Deduplicate** | `data` at one row per real measurement, and a number for what you removed | 30 min |
| **3** | **Reshape & join** | A hive frame and a weather frame, each with a grain you can state out loud | 60 min |
| **4** | **Align time & gaps** | One row per hive-hour, with a written gap policy | 60 min |
| **5** | **Validate & document** | `features_hourly.parquet` + `DATA_DICTIONARY.md` that pass the validator | 30 min |

<div class="mt-5">

Each exercise says **what to produce, not how**. The exercises build on each other, so do them in order.

</div>

---

# The target

One row per hive per hour. `validate_features.py` enforces exactly these names.

<div class="grid grid-cols-2 gap-6 mt-3 text-sm">
<div>

| Column | Meaning |
|---|---|
| `beehive_id`, `hive_name` | which hive |
| `hour` | the hour, **UTC** |
| `brood_temp_c1/c2/c3` | brood chamber, three probes |
| `food_temp`, `food_humidity` | food chamber |
| `hour_local`, `month`, `dayofweek` | calendar, **Europe/Berlin** |

</div>
<div>

| Column | Meaning |
|---|---|
| `outside_temp`, `outside_humidity` | ambient |
| `outside_wind_speed`, `outside_wind_dir` | ambient |
| `outside_uv_index`, `outside_pressure_pa` | ambient |
| `outside_light`, `outside_rain` | ambient |

</div>
</div>

```bash
uv run python workshop/validate_features.py workshop/out/features_hourly.parquet
```

<div class="bh-note mt-3">
Green is not the goal. A table that passes but whose gap policy you cannot defend is worse than one that fails honestly.
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
That single reflex catches the most expensive mistake in this dataset.
</div>

<!--
Say this twice. Once now, once when the first person's row count triples in Exercise 3.
-->

---
layout: center
class: bh-section
---

# 2 · Your toolbox

Jupyter in five minutes, then pandas properly

---

# Jupyter Notebook in five minutes

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

A notebook is a **list of cells**. Each cell is either **Markdown** (prose) or **Code** (Python).

You run a cell and its output appears directly underneath it. State — your variables — **persists between cells**, in one long-lived Python session called the *kernel*.

<div class="bh-note mt-4">
The last expression in a cell is displayed automatically. <code>df.head()</code> on its own line prints a nicely formatted table; <code>print(df.head())</code> prints plain text.
</div>

</div>
<div>

| Key | Does |
|---|---|
| <kbd>Shift</kbd>+<kbd>Enter</kbd> | run cell, go to next |
| <kbd>Ctrl</kbd>+<kbd>Enter</kbd> | run cell, stay |
| <kbd>Esc</kbd> then <kbd>A</kbd> / <kbd>B</kbd> | new cell above / below |
| <kbd>Esc</kbd> then <kbd>D</kbd><kbd>D</kbd> | delete cell |
| <kbd>Esc</kbd> then <kbd>M</kbd> / <kbd>Y</kbd> | to Markdown / to Code |
| <kbd>Tab</kbd> | autocomplete |
| <kbd>Shift</kbd>+<kbd>Tab</kbd> | show the docstring |

</div>
</div>

```bash
uv run jupyter lab workshop/notebooks/workshop.ipynb
```

---

# Jupyter: the one trap

<div class="bh-warn mt-4">
<strong>Cells remember. Out-of-order execution is the #1 source of "it worked yesterday".</strong>
</div>

<div class="grid grid-cols-2 gap-6 mt-5">
<div>

```python
# cell 1
data = pd.read_parquet("data.parquet")
len(data)     # 1,200,000
```

```python
# cell 2
data = data.drop_duplicates(subset=KEY)
len(data)     # 940,000
```

```python
# cell 2 again (you re-ran it)
len(data)     # 940,000 — no error, no warning
```

</div>
<div>

The variable `data` was **reassigned in place**. Re-running a cleaning cell twice is usually harmless; re-running a cell that *appends* or *merges* is not.

<div class="bh-note mt-4">
Fix: <strong>Kernel → Restart Kernel and Run All Cells</strong> before you trust a result. If your notebook does not survive that, it is not reproducible.
</div>

<div class="mt-4 bh-small">
The number in <code>[12]</code> beside a cell is its execution order, not its position. If those numbers are not ascending down the page, be suspicious.
</div>

</div>
</div>

---
layout: center
class: bh-section
---

# 3 · pandas 101

Every function you will need today, with its output

---

# What pandas is

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

**`DataFrame`** — a table. Named columns, a row **index**, and a `dtype` per column.

**`Series`** — one column. A 1-D array with an index attached.

A DataFrame is essentially a dict of Series that share an index.

```python
import pandas as pd

df = pd.DataFrame({
    "sensor_id": [3, 3, 7],
    "unit": ["tempC1", "tempC2", "temperature"],
    "value": [34.9, 35.2, 21.3],
})
df
```

</div>
<div>

<div class="bh-out-label">output</div>
<pre class="bh-out">   sensor_id         unit  value
0          3       tempC1   34.9
1          3       tempC2   35.2
2          7  temperature   21.3
</pre>

```python
df["value"]           # a Series
type(df["value"])     # pandas.core.series.Series
```

<pre class="bh-out mt-2">0    34.9
1    35.2
2    21.3
Name: value, dtype: float64
</pre>

<div class="bh-note mt-3">
The bold left-hand column is the <strong>index</strong>, not data. It comes back to matter in Exercise 4.
</div>

</div>
</div>

---

# Reading and writing files

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
data = pd.read_parquet(RAW / "data.parquet")
data.to_parquet(OUT / "features.parquet",
                index=False)

# also available
pd.read_csv(path)
pd.read_sql(query, conn)
```

<div class="bh-note mt-4">
<code>index=False</code> on write: your row index is usually just 0,1,2… — do not save it as a column.
</div>

</div>
<div>

### Why Parquet, not CSV?

| | CSV | Parquet |
|---|---|---|
| dtypes | **lost** | preserved |
| timestamps | become strings | stay timestamps |
| size | large | compressed |
| speed | slow | fast |

<div class="bh-warn mt-4">
Save <code>ts</code> to CSV and read it back and it is a <strong>string</strong>. Then <code>.dt.floor("h")</code> fails in Exercise 4 with an error message that never mentions CSV.
</div>

</div>
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

# Selecting columns and filtering rows

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
data["value"]                   # one column -> Series
data[["ts", "value"]]           # several   -> DataFrame

# Boolean filtering: build a mask, then index with it
mask = data["measurement_unit"] == "tempC1"
data[mask]

# combine with & (and), | (or), ~ (not)
# parentheses are REQUIRED around each condition
data[(data["sensor_id"] == 3) &
     (data["value"] > 35)]

# membership
data[data["measurement_unit"].isin(["tempC1","tempC2"])]
```

</div>
<div>

<div class="bh-out-label">mask (a Series of booleans)</div>
<pre class="bh-out">0     True
1    False
2    False
3    False
Name: measurement_unit, dtype: bool
</pre>

<div class="bh-out-label mt-3">data[mask]</div>
<pre class="bh-out">   sensor_id measurement_unit  value
0          3           tempC1   34.9
5          3           tempC1   34.9
</pre>

<div class="bh-warn mt-3">
Python's <code>and</code> / <code>or</code> do <strong>not</strong> work on Series. Use <code>&</code> and <code>|</code>, and wrap each condition in parentheses — <code>&</code> binds tighter than <code>==</code>.
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

data["value"].isna().sum()       # 0   <- no NULLs
data.isna().mean() * 100         # % missing per column
```

<div class="bh-out-label mt-3">data.isna().mean().mul(100).round(1)</div>
<pre class="bh-out">brood_temp_c1     4.2
brood_temp_c2     4.2
food_temp         6.1
outside_temp      0.8
dtype: float64
</pre>

<div class="bh-warn mt-3">
Zero NULLs does <strong>not</strong> mean nothing is missing. In this dataset, an hour with no reading has no <em>row</em> at all. Exercise 4 exists because of that sentence.
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

---

# Duplicates: `duplicated` and `drop_duplicates`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
KEY = ["sensor_id", "measurement_unit", "ts"]

# How many rows share a key?
data.duplicated(subset=KEY).sum()       # 263_918

# Drop them, keeping the first of each
clean = data.drop_duplicates(subset=KEY)

before, after = len(data), len(clean)
print(f"{before:,} -> {after:,} "
      f"({100*(1-after/before):.1f}% removed)")
```

<pre class="bh-out mt-2">1,203,441 -> 939,523 (21.9% removed)
</pre>

</div>
<div>

<div class="bh-note">
<code>subset=</code> is the important argument. Without it, pandas compares <em>whole rows</em> — and <code>reading_id</code> is unique on every row, so nothing is ever a duplicate.
</div>

Before you drop, ask whether the copies **agree**:

```python
conflicts = (data.groupby(KEY)["value"]
                 .nunique() > 1).sum()
conflicts        # 0 -> exact copies, safe to drop
                 # >0 -> you must arbitrate
```

<div class="bh-small mt-3">
<code>keep="first"</code> (default), <code>keep="last"</code>, or <code>keep=False</code> to mark <em>every</em> member of a duplicate set.
</div>

</div>
</div>

---

# `groupby` — split, apply, combine

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
# how many rows per key?
data.groupby(KEY).size()

# average value per hive per hour per unit
(data.groupby(["beehive_id", "hour", "unit"])["value"]
     .mean())

# several statistics at once
data.groupby("unit")["value"].agg(
    ["mean", "max", "count"])
```

<div class="bh-out-label mt-3">groupby("unit")["value"].agg([...])</div>
<pre class="bh-out">                   mean    max   count
unit
tempC1            34.71   38.9  184221
temperature       19.83   34.1  121004
relativeHumidity  61.40   99.0  121004
</pre>

</div>
<div>

The mental model:

<div class="mt-2 space-y-2">
  <div class="bh-flow"><span class="bh-pill">1 · split</span>
    <span class="arr">→</span><span class="box">rows where key = A</span>
    <span class="box">key = B</span><span class="box">key = C</span></div>
  <div class="bh-flow"><span class="bh-pill">2 · apply</span>
    <span class="arr">→</span><span class="box">mean() 34.7</span>
    <span class="box">mean() 21.3</span><span class="box">mean() 61.4</span></div>
  <div class="bh-flow"><span class="bh-pill">3 · combine</span>
    <span class="arr">→</span><span class="box">one row per group, key as the index</span></div>
</div>

<div class="bh-note mt-2">
The group keys become the <strong>index</strong> of the result. Several keys give a <strong>MultiIndex</strong> — a tuple per row. <code>.reset_index()</code> turns them back into ordinary columns.
</div>

<div class="bh-small mt-2">
Pass <code>observed=True</code> when grouping categoricals to avoid materialising unused combinations.
</div>

</div>
</div>

---

# Long → wide: `unstack` (and `pivot`)

```python
hive_h = (data.groupby(["beehive_id", "hour", "measurement_unit"])["value"]
              .mean()                          # Series with a 3-level MultiIndex
              .unstack("measurement_unit"))    # move that level up into columns
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

# Creating and renaming columns

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
# direct assignment
data["hour"] = data["ts"].dt.floor("h")

# .assign() — same thing, returns a new frame
# (chains nicely, never mutates the original)
data = data.assign(hour=data["ts"].dt.floor("h"))

# .map() — translate values through a dict
ROLE = {
    "LoRaWAN Dragino-S31-LB": "food_chamber",
    "LoRaWAN Dragino-D23-LB": "brood_chamber",
    "LoRaWAN SenseCAP-S2120": "weather",
}
sensors = sensors.assign(
    role=sensors["sensor_type"].map(ROLE)
)
```

</div>
<div>

```python
features = features.rename(columns={
    "tempC1": "brood_temp_c1",
    "temperature": "food_temp",
    "relativeHumidity": "food_humidity",
})
```

<div class="bh-out-label mt-3">sensors after .map()</div>
<pre class="bh-out">   sensor_id  beehive_id      sensor_type           role
0          3           1  Dragino-D23-LB  brood_chamber
1          4           1  Dragino-S31-LB   food_chamber
2          7           1  SenseCAP-S2120        weather
</pre>

<div class="bh-note mt-3">
A key missing from the dict becomes <code>NaN</code> — so <code>sensors["role"].isna().sum()</code> is a free check that your mapping covered everything.
</div>

</div>
</div>

---

# Working with time: the `.dt` accessor

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

`.dt` unlocks datetime methods on a whole column at once.

```python
ts = data["ts"]

ts.dt.floor("h")      # 04:11:02 -> 04:00:00
ts.dt.date            # 2025-08-01
ts.dt.hour            # 4
ts.dt.month           # 8
ts.dt.dayofweek       # 0 = Monday
ts.dt.strftime("%Y-%m")

ts.min(), ts.max()    # the period you actually have
ts.diff()             # gap to previous row (Timedelta)
ts.diff().dt.total_seconds() / 3600   # ...in hours
```

<div class="bh-small mt-2">
If <code>.dt</code> raises <em>"Can only use .dt accessor with datetimelike values"</em>, your column is a string. <code>pd.to_datetime(col)</code> fixes it.
</div>

</div>
<div>

### Time zones

```python
# ts is *naive* — no zone attached — but holds UTC
local = (features["hour"]
         .dt.tz_localize("UTC")       # declare: UTC
         .dt.tz_convert("Europe/Berlin"))   # shift it

features["hour_local"] = local.dt.hour
features["month"]      = local.dt.month
features["dayofweek"]  = local.dt.dayofweek
```

<div class="bh-warn mt-3">
<code>tz_localize</code> <strong>attaches</strong> a zone without moving the clock.
<code>tz_convert</code> <strong>moves</strong> the clock. Getting these the wrong way round shifts every local-time feature by two hours and nothing will complain.
</div>

<div class="bh-note mt-3">
Germany changes its clocks. The offset is +01:00 or +02:00 depending on the date — never hardcode it, let the zone database do it.
</div>

</div>
</div>

---

# Building a complete index: `date_range` + `reindex`

```python
hours = pd.date_range("2025-06-18", "2025-09-17", freq="h")      # every hour, no gaps
grid  = pd.MultiIndex.from_product([[1, 2, 3], hours],
                                   names=["beehive_id", "hour"])  # every hive × every hour

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
This is the whole idea of Exercise 4. <code>reindex</code> aligns your data to an index <em>you</em> define — and every row you expected but do not have turns into a <code>NaN</code> you can count.
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
<code>join</code> is <code>merge</code>'s index-aware cousin: it lines the right frame's <em>index</em> up against a column or index level on the left. Perfect for attaching one weather table to every hive.
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

---

# Checking your own work: `assert`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

An `assert` is a claim about your data that stops the notebook if it is false. Write them as you go.

```python
# the grain: one row per hive per hour, no repeats
assert not features.duplicated(
    subset=["beehive_id", "hour"]).any()

# the table is a complete rectangle
assert len(features) == (
    features["beehive_id"].nunique()
    * features["hour"].nunique()
)

# ranges that physics allows
assert features["food_humidity"].between(0, 100).all()

# nothing lost in a join
assert len(after) == len(before), (
    f"join changed rows: {len(before)} -> {len(after)}"
)
```

</div>
<div>

<div class="bh-note">
An assertion that has never failed still earns its place: it is documentation that <em>executes</em>. Six months later it tells the next person what you believed about this table.
</div>

<div class="bh-out-label mt-4">when one fails</div>
<pre class="bh-out">AssertionError: join changed rows: 939523 -> 1142006
</pre>

<div class="mt-4">

Useful companions:

```python
df.duplicated(subset=[...]).any()
df["col"].between(lo, hi).all()
df["col"].notna().all()
set(a["id"]) - set(b["id"])      # what failed to match
```

</div>

</div>
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
<div class="bh-card-h">2 · Copy vs. view</div>

```python
sub = df[df["x"] > 0]
sub["y"] = 1     # SettingWithCopyWarning
```
Take an explicit copy — `df[mask].copy()` — or build new frames with `.assign()` instead of mutating slices.
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

---

# The toolkit, mapped to the day

| Exercise | The functions you will reach for |
|---|---|
| **0 · Extract** | `pd.DataFrame(...)`, `to_parquet`, `read_parquet`, `len`, `.min()` / `.max()` |
| **1 · Profile** | `.head()`, `.shape`, `.dtypes`, `value_counts`, `nunique`, `isna().sum()` |
| **2 · Deduplicate** | `duplicated`, `drop_duplicates(subset=)`, `groupby().size()`, `nunique`, `idxmax` |
| **3 · Reshape & join** | `.map()`, `.assign()`, boolean filtering, `merge(on=, how=)`, `groupby().mean()`, `unstack`, `add_prefix` |
| **4 · Align & gaps** | `.dt.floor("h")`, `date_range`, `MultiIndex.from_product`, `reindex`, `join`, `diff`, `interpolate`, `isna().mean()` |
| **5 · Validate** | `tz_localize` / `tz_convert`, `.dt.hour/month/dayofweek`, `rename`, `assert`, `to_parquet` |

<div class="bh-note mt-5">
Nothing else. If you find yourself writing a <code>for</code> loop over rows, there is a pandas function for it — ask.
</div>

---

# Getting unstuck

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

### When something looks wrong

1. `print(len(df))` — did the row count move?
2. `df.dtypes` — is that column still a timestamp?
3. `df.head()` — look at actual rows, not just shapes
4. `df.index` — are the two frames indexed the same way?
5. Re-run from a clean kernel

<div class="bh-note mt-4">
<kbd>Shift</kbd>+<kbd>Tab</kbd> inside any function call shows the docstring. <code>df.merge?</code> in a cell does the same.
</div>

</div>
<div>

### The rules for today

<div class="mt-3">

- **Hit the database once.** If you are re-running a query to get a dataframe back, Exercise 0 is not finished.
- **Check the row count after every join and reshape.**
- **Write down every decision** as you make it — what you dropped, what you filled, what you left empty and why. That becomes `DATA_DICTIONARY.md`.
- **A number you cannot explain is a bug**, even if the validator is green.

</div>

</div>
</div>

---
layout: center
class: text-center bh-cover
---

<div class="bh-kicker">Now open the notebook</div>

# Let's go 🐝

```bash
uv sync
cp .env.example .env      # paste in your connection string
uv run jupyter lab workshop/notebooks/workshop.ipynb
```

<div class="mt-8 max-w-2xl mx-auto text-left">

> You are not told what is wrong with this data, because finding out is the exercise.

</div>

<div class="mt-6 bh-small">
Exercise 0 starts on the next cell of <code>workshop.ipynb</code>.
</div>
