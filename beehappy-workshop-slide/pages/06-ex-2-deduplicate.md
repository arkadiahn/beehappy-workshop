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
KEY = ["sensor_id", "measurement_unit", "ts"]

# how many copies does each key have?
data.groupby(KEY).size()
data.groupby(KEY).size().max()     # worst multiplicity

# the index label of the worst key
worst = data.groupby(KEY).size().idxmax()
```

<div class="bh-out-label mt-3">groupby(KEY).size()</div>
<pre class="bh-out">sensor_id  measurement_unit  ts
3          tempC1            2025-08-01 04:11    4
                             2025-08-01 04:31    1
7          temperature       2025-08-01 04:17    3
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
    <span class="arr">→</span><span class="box">size() 4</span>
    <span class="box">size() 1</span><span class="box">size() 3</span></div>
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
