---
layout: center
class: bh-section
---

# Exercise 6 · Look at what you built

A line chart is how you check the table with your eyes, and how you answer the materials question.

<div class="mt-8 bh-small">
<code>df.plot</code> · <code>ax.axhline</code> · <code>pd.Timedelta</code> · <code>plt.subplots</code> · <code>sns.lineplot</code>
</div>

---

# One hive: brood vs outside

Three months of hourly points is a scribble, so zoom to a few days.

```python
import matplotlib.pyplot as plt

OPTIMAL_C = 35  # brood-nest target, not a data series
DAYS = 7        # try 3; comment out the window line for the full extract

one = features[features["beehive_id"] == 1]
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
- Breaks in the line are leftover gaps, not a plotting bug. pandas skips `NaN`.
- Try `DAYS = 7`, then `3`. Comment out the window line to see the whole extract. It should look like a scribble.

</div>
<div>

**If it looks wrong**

<div class="bh-warn">
If the two traces sit on top of each other, you plotted the same column twice or joined weather onto brood by mistake.
</div>

<div class="bh-note mt-4">
If there is no dashed line, <code>axhline</code> was never called. The 35 °C line is the point of the chart. Without it you cannot tell whether brood is doing its job.
</div>

</div>
</div>

---

# All three hives: the materials question

<div class="grid grid-cols-5 gap-6 mt-2">
<div class="col-span-3">

```python
import seaborn as sns

temp = features[["beehive_id", "hour", "brood_temp_c1",
                 "brood_temp_c2", "brood_temp_c3", "outside_temp"]]
temp_7_days = temp[temp["hour"] >= temp["hour"].max()
                                   - pd.Timedelta(days=DAYS)]

fig, axes = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
probes = ["brood_temp_c1", "brood_temp_c2", "brood_temp_c3"]
for ax, col in zip(axes, probes):
    sns.lineplot(data=temp_7_days, x="hour", y=col,
                 hue="beehive_id", palette="pastel", ax=ax,
                 legend=(ax is axes[-1]))
    ax.axhline(OPTIMAL_C, linestyle="--")
    ax.set_ylabel(col)

fig.suptitle(f"Brood vs 35 °C by hive — last {DAYS} days")
```

</div>
<div class="col-span-2">

<div class="bh-note">
<code>plt.subplots(3, 1)</code> gives one figure and a list of three <strong>axes</strong>, one per panel. <code>zip</code> pairs each panel with one probe column.
</div>

<div class="bh-small mt-2">
<code>hue="beehive_id"</code> draws one line per hive on the same axes.
</div>

<div class="mt-2 font-semibold">Questions to answer</div>

<span class="bh-small">

1. Which hive stays closest to 35 °C on each probe?
2. Do the three probes in one hive agree, or does one wander?
3. Does one hive go silent while the others do not?
4. Which material looks best? What would you want to see in winter before you trust that?

</span>

</div>
</div>

<!--
The hive whose brood stays closest to 35 °C, with the fewest long holes, is the one
the data currently supports. Two caveats to say out loud: the hive-to-material mapping
must be confirmed, and a summer week tells you nothing about winter.
-->
