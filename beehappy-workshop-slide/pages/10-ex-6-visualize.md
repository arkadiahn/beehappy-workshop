---
layout: center
class: bh-section
---

# Exercise 6 · Look at what you built

A line chart is how you check the table with your eyes.

<div class="mt-8 bh-small">
<code>df.plot</code> · <code>ax.axhline</code> · <code>pd.Timedelta</code>
</div>

---

# Plot brood vs outside

Three months of hourly points is a scribble — zoom to a few days.

```python
import matplotlib.pyplot as plt

OPTIMAL_C = 35  # brood-nest target, not a data series
DAYS = 7        # try 3; comment out the window line for the full extract

one = features[features["hive_name"] == "Beehive No.1"]
window = one[one["hour"] >= one["hour"].max() - pd.Timedelta(days=DAYS)]

ax = window.plot(x="hour", y=["brood_temp_c1", "outside_temp"],
                 figsize=(10, 4))
ax.axhline(OPTIMAL_C, linestyle="--", label=f"optimal {OPTIMAL_C}°C")
ax.set_ylabel("°C")
ax.legend()
```

<div class="bh-note mt-3">
<code>DataFrame.plot</code> is matplotlib underneath. You do not need to import pyplot to draw, but you do need the axes object to add the 35 °C line.
</div>

---

# How to read the chart

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

**What to look for**

- Brood should hug 35 °C more tightly than outside does.
- Breaks in the line are leftover gaps, not a plotting bug — pandas skips `NaN`.
- Try `DAYS = 7` then `3`. Comment out the window line to see the whole extract; it should look like a scribble.

</div>
<div>

**If it looks wrong**

<div class="bh-warn">
If the two traces sit on top of each other, you plotted the same column twice or joined weather onto brood by mistake.
</div>

<div class="bh-note mt-4">
If there is no dashed line, <code>axhline</code> was never called. The 35 °C line is the point of the chart — without it you cannot tell whether brood is doing its job.
</div>

</div>
</div>
