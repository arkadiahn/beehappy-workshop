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

- A notebook is a list of **cells**: Markdown or Code.
- Run a cell → output appears below it.
- Variables **persist** between cells (the *kernel*).

<div class="bh-note mt-4">
The last line is shown automatically: <code>df.head()</code> → a table.
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

<div class="grid grid-cols-5 gap-6 mt-4">
<div class="col-span-3">

<JupyterCell n="1" at="1">

```python
data = pd.read_parquet("data.parquet")
data["temp"].mean()
```

<template #output>
<pre>347.0</pre>
</template>
</JupyterCell>

<JupyterCell n="2" at="2" rerun="3" rerun-n="3" label="fix the scale, then run the same cell again">

```python
data["temp"] = data["temp"] / 10
data["temp"].mean()
```

<template #output>
<pre>34.7  ✅</pre>
</template>
<template #rerun-output>
<pre>3.47  ❌ no error, no warning</pre>
</template>
</JupyterCell>

</div>
<div class="col-span-2">

<div class="bh-warn">
<strong>Cells remember.</strong> Re-running a cell that changes data changes it again.
</div>

<div v-click="4" class="bh-note mt-4">
Fix: <strong>Restart Kernel and Run All</strong> before you trust a result.
</div>

</div>
</div>

<!--
The sensor sends deci-degrees, so cell 1 shows 347.0. Click 2 runs the fix; click 3 runs
the same cell again, which divides by 10 a second time.

Anything that transforms a column in place, appends, or merges is unsafe to re-run.

The number in [3] beside a cell is its execution order, not its position. If those
numbers are not ascending down the page, be suspicious.
-->
