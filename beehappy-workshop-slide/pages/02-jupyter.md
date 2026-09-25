---
layout: center
class: bh-section
---

# 2 · Your toolbox

Jupyter in five minutes, then pandas and matplotlib

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
| <kbd>Shift</kbd>+<kbd>Tab</kbd> | show the docstring |

</div>
</div>

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
data["temp"].mean() # 347.0  — sensor sends deci-degrees
```

```python
# cell 2 — fix the scale
data["temp"] = data["temp"] / 10
data["temp"].mean() # 34.7 °C  ✅
```

```python
# cell 2 again (you re-ran it)
data["temp"] = data["temp"] / 10
data["temp"].mean() # 3.47 °C  — ❌ no error, no warning 
```

</div>
<div>

Anything that *transforms a column in place*, *appends*, or *merges* is unsafe to re-run.

<div class="bh-note mt-4">
Fix: <strong>Kernel → Restart Kernel and Run All Cells</strong> before you trust a result. If your notebook does not survive that, it is not reproducible.
</div>

<div class="mt-4 bh-small">
The number in <code>[12]</code> beside a cell is its execution order, not its position. If those numbers are not ascending down the page, be suspicious.
</div>

</div>
</div>
