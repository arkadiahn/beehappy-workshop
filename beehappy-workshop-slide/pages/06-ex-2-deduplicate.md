---
layout: center
class: bh-section
---

# Exercise 2 · Deduplicate

Name the grain. Then let pandas tell you whether it holds.

<div class="mt-8 bh-small">
<code>duplicated</code> · <code>drop_duplicates(subset=)</code> · <code>groupby().size()</code> · <code>nunique</code>
</div>

---

# Duplicates: `duplicated` and `drop_duplicates`

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
KEY = ["sensor_id", "measurement_unit", "ts"]

# How many rows share a key?
data.duplicated(subset=KEY).sum()       # 119593

before = len(data)
distinct = len(data.drop_duplicates(subset=KEY))
pct = 100 * (1 - distinct / before)
print(f"{before:,} rows -> {distinct:,} distinct keys "
      f"({pct:.1f}% redundant)")
```

<pre class="bh-out mt-2">511,937 rows -> 392,344 distinct keys (23.4% redundant)
</pre>

```python
# keep one row per key, renumber the index 0, 1, 2, ...
data = data.drop_duplicates(subset=KEY)
data = data.reset_index(drop=True)
```

</div>
<div>

<div class="bh-note">
<code>subset=</code> is the important argument. Without it, pandas compares <em>whole rows</em> — and <code>reading_id</code> is unique on every row, so nothing is ever a duplicate.
</div>

Before you drop, ask whether the copies **agree**:

```python
# do copies of one key disagree on value?
(data.groupby(KEY)["value"].nunique() > 1).sum()
# 0 -> exact copies, safe to drop
# >0 -> you must arbitrate

# different reading_ids for one key?
data.groupby(KEY)["reading_id"].nunique().max()
# 70 -> real INSERTs, not your query
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
KEY = ["sensor_id", "measurement_unit", "ts"]

# how many copies does each key have?
data.groupby(KEY).size()
data.groupby(KEY).size().max()     # worst multiplicity

# the index label of the worst key
worst = data.groupby(KEY).size().idxmax()
```

<div class="bh-out-label mt-3">groupby(KEY).size()</div>
<pre class="bh-out">sensor_id  measurement_unit  ts
1          lightIntensity    2026-06-28 12:24:36.630     1
                             2026-06-28 14:16:39.427     2
...
6          relativeHumidity  2026-08-13 03:58:33.810    70
...
dtype: int64
</pre>

</div>
<div>

The mental model:

<div class="mt-2 space-y-2">
  <div class="bh-flow"><span class="bh-pill">1 · split</span>
    <span class="arr">→</span><span class="box">rows where key = A</span>
    <span class="box">key = B</span><span class="box">key = C</span></div>
  <div class="bh-flow"><span class="bh-pill">2 · apply</span>
    <span class="arr">→</span><span class="box">size() 1</span>
    <span class="box">size() 2</span><span class="box">size() 70</span></div>
  <div class="bh-flow"><span class="bh-pill">3 · combine</span>
    <span class="arr">→</span><span class="box">one row per group, key as the index</span></div>
</div>

<div class="bh-note mt-2">
The group keys become the <strong>index</strong> of the result. Several keys give a <strong>MultiIndex</strong> — a tuple per row. <code>.reset_index()</code> turns them back into ordinary columns.
</div>

<div class="bh-small mt-2">
Same pattern, different verb: Exercise 4 will <code>groupby(...).mean()</code> instead of <code>.size()</code>.
</div>

</div>
</div>

<!--
The duplicates come from a live bug in the ChatBotCollector service. They run at
21–27% per month and the rate is uneven, so they skew any mean weighted by row count.
Dropping them is not just cosmetic.

If the redundancy prints near zero, the bug was fixed upstream. Say so and teach it as
"here is how you would have caught it".
-->
