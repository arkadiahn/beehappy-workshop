---
layout: center
class: bh-section
---

# 3 · pandas 101

The functions you need

---

# Why pandas?

<div class="grid grid-cols-4 gap-3 mt-4">

<div v-click="1" class="bh-card">
<div class="bh-card-h">Built for exactly this job</div>
<span class="bh-small">Missing values, duplicates, time zones, joins, reshaping.</span>
</div>

<div v-click="2" class="bh-card">
<div class="bh-card-h">The lingua franca</div>
<span class="bh-small">scikit-learn, matplotlib, seaborn, plotly all take a <code>DataFrame</code> directly.</span>
</div>

<div v-click="3" class="bh-card">
<div class="bh-card-h">Reads everything</div>
<span class="bh-small"><code>read_sql</code>, <code>read_parquet</code>, <code>read_csv</code>, <code>read_excel</code> — and a <code>to_*</code> for each.</span>
</div>

<div v-click="4" class="bh-card">
<div class="bh-card-h">Fifteen years of answers</div>
<span class="bh-small">Whatever you get stuck on, someone already asked it.</span>
</div>

</div>

<div v-click="5" class="bh-note mt-5">
Three months of readings is about half a million rows — it fits in memory, so the simplest tool is also the right one.
</div>

<!--

- Interactive by design. Every line runs immediately and shows you the table. You look,
  react, adjust — which is what cleaning actually *is*. A compiled batch job cannot do that.
- It is the default. Being the thing everyone already knows is itself a feature: the person
  who picks up your notebook next year will read it without a manual.
-->


---

# What pandas is

<div class="grid gap-6 mt-3" style="grid-template-columns: 3fr 2fr">
<div>

<JupyterCell n="1" label="a DataFrame">

```python
import pandas as pd

df = pd.DataFrame({
    "sensor_id": [8, 8, 6],
    "unit": ["tempC1", "tempC2", "temperature"],
    "value": [35.5, 35.7, 35.6],
})
df
```

<template #output>
<pre>   sensor_id         unit  value
0          8       tempC1   35.5
1          8       tempC2   35.7
2          6  temperature   35.6</pre>
</template>
</JupyterCell>

</div>
<div>

<JupyterCell n="2" label="one column: a Series">

```python
df["value"]
```

<template #output>
<pre>0    35.5
1    35.7
2    35.6
Name: value, dtype: float64</pre>
</template>
</JupyterCell>

<JupyterCell n="3">

```python
type(df["value"])
```

<template #output>
<pre>pandas.Series</pre>
</template>
</JupyterCell>

</div>
</div>

<div v-click="4" class="grid grid-cols-2 gap-4 mt-4">
<div class="bh-card">
<div class="bh-card-h">Row-oriented · transactional</div>
<span class="bh-small">Postgres stores each reading as a whole row. Fast to <strong>write</strong> one reading at a time.</span>
</div>
<div class="bh-card">
<div class="bh-card-h">Column-oriented · analytical</div>
<span class="bh-small">pandas and Parquet store each column together. Fast to <strong>analyse</strong>: <code>df["value"].mean()</code> reads one column.</span>
</div>
</div>

<!--

**`DataFrame`** — a table. Named columns, a row **index**, and a `dtype` per column.

**`Series`** — one column. A 1-D array with an index attached.

A DataFrame is essentially a dict of Series that share an index.

The bold left-hand column is the <strong>index</strong>, not data. It comes back to matter in Exercise 4.

Row vs column: the sensors write into Postgres (OLTP) one reading at a time, so each row
is stored together. Analysis asks "average of this column over half a million rows", so
pandas keeps each column as one contiguous typed array. That is why column operations are
fast and looping over rows is slow. Exercise 0 is the bridge: read from the row store
once, then work in columns.
-->

