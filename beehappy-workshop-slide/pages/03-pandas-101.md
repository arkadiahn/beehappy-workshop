---
layout: center
class: bh-section
---

# 3 · pandas 101

The functions you need

---

# Why pandas?

<div class="grid grid-cols-4 gap-3 mt-4">

<div class="bh-card">
<div class="bh-card-h">The lingua franca</div>
<span class="bh-small">scikit-learn, matplotlib, seaborn, plotly all take a <code>DataFrame</code> directly.</span>
</div>

<div class="bh-card">
<div class="bh-card-h">Built for exactly this job</div>
<span class="bh-small">Missing values, duplicates, time zones, joins, reshaping.</span>
</div>

<div class="bh-card">
<div class="bh-card-h">Reads everything</div>
<span class="bh-small"><code>read_sql</code>, <code>read_parquet</code>, <code>read_csv</code>, <code>read_excel</code> — and a <code>to_*</code> for each.</span>
</div>

<div class="bh-card">
<div class="bh-card-h">Fifteen years of answers</div>
<span class="bh-small">Whatever you get stuck on, someone already asked it.</span>
</div>

</div>

<div class="bh-note mt-5">
Three months of readings is a few hundred MB — it fits in memory, so the simplest tool is also the right one.
</div>

<!--

- Interactive by design. Every line runs immediately and shows you the table. You look,
  react, adjust — which is what cleaning actually *is*. A compiled batch job cannot do that.
- It is the default. Being the thing everyone already knows is itself a feature: the person
  who picks up your notebook next year will read it without a manual.
-->

---

# When pandas is *not* the right tool

<div class="grid gap-6 mt-4">
<div>

| Your data | Reach for |
|---|---|
| fits in RAM (**today**) | **pandas** |
| 10–100 GB, one machine | **Polars**, **DuckDB** |
| still in a database | **SQL** — aggregate first |

<div class="bh-small mt-4">
The four ideas — <code>filter</code>, <code>groupby</code>, <code>join</code>, <code>pivot</code> — are the same in all of them.
</div>

</div>
</div>

<!--
The two alternatives, if anyone asks:

- Polars — same DataFrame idea, written in Rust, multi-threaded and lazy. Often 5–30x
  faster with a very similar API. The natural next step when pandas starts to hurt.
- DuckDB — runs SQL straight over Parquet files or over a DataFrame, handles
  larger-than-memory, no server to set up.

The warning to say out loud: pulling millions of rows over the network only to `.head()`
them is the most common way to make a laptop unusable. If the answer is an average,
compute the average in the database.
-->

---

# What pandas is

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
import pandas as pd

df = pd.DataFrame({
    "sensor_id": [3, 3, 7],
    "unit": ["tempC1", "tempC2", "temperature"],
    "value": [34.9, 35.2, 21.3],
})
df
```

<div class="bh-out-label">output</div>
<pre class="bh-out">   sensor_id         unit  value
0          3       tempC1   34.9
1          3       tempC2   35.2
2          7  temperature   21.3
</pre>
</div>

<div>

```python
df["value"]           # a Series
type(df["value"])     # pandas.core.series.Series
```

<div class="bh-out-label">output</div>
<pre class="bh-out">0    34.9
1    35.2
2    21.3
Name: value, dtype: float64
</pre>

</div>
</div>

<!--

**`DataFrame`** — a table. Named columns, a row **index**, and a `dtype` per column.

**`Series`** — one column. A 1-D array with an index attached.

A DataFrame is essentially a dict of Series that share an index.

The bold left-hand column is the <strong>index</strong>, not data. It comes back to matter in Exercise 4.
-->