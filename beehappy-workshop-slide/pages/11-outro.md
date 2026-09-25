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

# Getting unstuck

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

### When something looks wrong

1. `print(len(df))` — did the row count move?
2. `df.dtypes` — is that column still a timestamp?
3. `df.head()` — look at actual rows, not just shapes
4. `df.index` — are the two frames indexed the same way?
5. Re-run from a clean kernel
6. Does the plot window actually show anything? Try `DAYS = 7` then `3`.

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

---

# Why data cleaning comes first

<div class="mt-8 text-left max-w-3xl mx-auto">

> An AI/ML model cannot tell the difference between a signal and a mistake in your table.<br>
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
The usual industry estimate is that 60–80% of any data science project is this step.
</div>

<!--
Do not moralise for too long. One sentence per card and move on — they will meet all
three of these for real within the hour.
-->

---

# Let's go 🐝

```bash
uv sync
cp .env.example .env      # paste in your connection string
uv run jupyter notebook workshop/notebooks/workshop.ipynb
```

<div class="mt-8 max-w-2xl mx-auto text-left">

> You are not told what is wrong with this data, because finding out is the exercise.

</div>

<div class="mt-6 bh-small">
Exercise 0 starts on the next cell of <code>workshop.ipynb</code>.
</div>
