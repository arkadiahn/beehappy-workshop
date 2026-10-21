---
layout: center
class: bh-section
---

# Exercise 6 · Look at what you built

A line chart is how you check the table with your eyes, and how you answer the materials question.

<div class="mt-8 bh-small">
<code>plt.plot</code> · <code>plt.subplots</code> · <code>df.plot</code> · <code>ax.axhline</code> · <code>sns.lineplot(hue=)</code> · <code>sns.set_palette</code>
</div>

<!--
Five small steps, each one adds a single idea:
1 plt.plot  2 a time window + fig, ax  3 df.plot + reference line
4 seaborn hue  5 one panel per probe.
Every chart on the next slides is the real output of that cell on the current extract.
-->

---

# Step 1 · Your first plot: `plt.plot(x, y)`

<div class="grid grid-cols-5 gap-6 mt-2">
<div class="col-span-2">

```python
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_palette("colorblind")
OPTIMAL_C = 35
DAYS = 7
HIVE = 1

one = features[
    features["beehive_id"] == HIVE]
plt.plot(one["hour"], one["brood_temp_c1"])
plt.xticks(rotation=45)  # tilt the dates
```

<div class="bh-note mt-3">
<code>plt.plot</code> takes an <strong>x</strong> and a <strong>y</strong>, both columns of the same length. One hive, one probe, the whole extract.
</div>

</div>
<div class="col-span-3">

<img src="/charts/ex6-1-plt-plot.png" class="max-h-96 mx-auto" alt="Hive 1 brood probe C1 over three months: dense zig-zag between about 17 and 37 °C, trending down from August to late September" />

<div class="bh-small mt-1">Three months of hourly points is a <strong>scribble</strong>. You see the trend, but not a single day.</div>

</div>
</div>

<!--
sns.set_palette("colorblind") changes the colours for matplotlib and pandas too, so
every chart today uses the same high-contrast palette. "pastel" is too light for a
projector.
-->

---

# Step 2 · Zoom in: a time window and `fig, ax`

```python
window = one[one["hour"] >= one["hour"].max() - pd.Timedelta(days=DAYS)]
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(window["hour"], window["brood_temp_c1"])
ax.set_ylabel("°C")
```

<div class="grid grid-cols-3 gap-6 mt-3">
<div class="col-span-2">

<img src="/charts/ex6-2-window.png" class="w-full" alt="Hive 1 brood probe C1 over the last seven days: a clear daily cycle between about 17 and 33 °C" />

</div>
<div>

<div class="bh-note">
<code>plt.subplots()</code> returns the <strong>figure</strong> (the whole picture) and an <strong>axes</strong> (one plot inside it). From now on you draw on <code>ax</code>.
</div>

<div class="bh-small mt-3">
The window is the same boolean filter as Exercise 3, using a time: "everything after the last hour minus 7 days". Now each day is visible.
</div>

</div>
</div>

---

# Step 3 · Let pandas draw, then add a reference line

<div class="grid grid-cols-5 gap-5 mt-2">
<div class="col-span-2">

```python
ax = window.plot(
    x="hour",
    y=["brood_temp_c1", "outside_temp"],
    figsize=(10, 4))
ax.axhline(OPTIMAL_C, color="black",
           linestyle="--",
           label=f"optimal {OPTIMAL_C}°C")
ax.set_ylabel("°C")
ax.legend()
```

<div class="bh-small mt-3">
Same hive, same window: the only new thing is the code.
</div>

</div>
<div class="col-span-3">

<img src="/charts/ex6-3-df-plot.png" class="w-full" alt="Hive 1 over seven days: brood C1 between 17 and 33 °C, outside between 5 and 33 °C, black dashed 35 °C line above both" />

<div class="bh-note mt-3">
<code>df.plot</code> is matplotlib underneath: two columns become two lines, with a legend and formatted dates. It <strong>returns the axes</strong>, so <code>axhline</code> can draw the target on it. Make the line <strong>black</strong>: left at the default it takes the first palette colour, the same blue as brood.
</div>

</div>
</div>

---

# How to read the chart

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

**What to look for**

- Brood should hug 35 °C more tightly than outside does.
- Breaks in the line are leftover gaps, not a plotting bug. Matplotlib skips `NaN`.
- Try `DAYS = 7`, then `3`. Comment out the window line to see the whole extract again.

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

<!--
On the current extract brood stays well below 35 °C and swings with the outside
temperature every day. That is late September. It is a finding, not a bug: let them
say it out loud before you explain it.
-->

---

# Step 4 · seaborn: one line per hive with `hue`

<div class="grid grid-cols-5 gap-6 mt-2">
<div class="col-span-2">

```python
temp = features[[
    "beehive_id", "hour", "brood_temp_c1",
    "brood_temp_c2", "brood_temp_c3",
    "outside_temp"]]
temp_7_days = temp[temp["hour"] >=
                   temp["hour"].max()
                   - pd.Timedelta(days=DAYS)]

ax = sns.lineplot(data=temp_7_days,
                  x="hour",
                  y="brood_temp_c1",
                  hue="beehive_id",
                  palette="colorblind")
ax.axhline(OPTIMAL_C, color="black",
           linestyle="--")
plt.xticks(rotation=45)
```

<div class="bh-note mt-2">
seaborn takes the <strong>long</strong> frame, and <code>hue=</code> splits it into one coloured line per hive. No filtering per hive.
</div>

</div>
<div class="col-span-3">

<img src="/charts/ex6-4-sns-hue.png" class="max-h-100 mx-auto" alt="Brood probe C1 for hives 1, 2 and 3 over seven days; hive 2 runs a few degrees colder than hives 1 and 3; all stay below the 35 °C line" />

</div>
</div>

---

# Step 5 · One panel per probe: `plt.subplots`

<div class="grid grid-cols-2 gap-6 mt-2">
<div>

```python
fig, axes = plt.subplots(3, 1, figsize=(9, 9),
                         sharex=True)

# axes: three plots. enumerate: 1, 2, 3
for i, ax in enumerate(axes, start=1):
    sns.lineplot(
        data=temp_7_days, x="hour",
        y=f"brood_temp_c{i}",
        hue="beehive_id", palette="colorblind",
        ax=ax,
        legend=(i == 1),  # top panel only
    )
    ax.axhline(OPTIMAL_C, color="black",
               linestyle="--")
    ax.set_ylabel(f"brood C{i} (°C)")

fig.suptitle(f"Brood by hive, last {DAYS} days "
             f"(dashed: {OPTIMAL_C} °C target)")
fig.tight_layout()
```

</div>
<div>

<img src="/charts/ex6-5-subplots.png" class="max-h-90 mx-auto" alt="Three stacked panels, brood probes C1, C2 and C3 for all three hives over seven days, each with a black dashed 35 °C line and one shared legend on the top panel" />

<div class="bh-small mt-1">
<code>ax=ax</code> picks the panel. <code>legend=(i == 1)</code> keeps one legend instead of three.
</div>

</div>
</div>

<!--
legend=False on every panel plus fig.legend does NOT work: seaborn then gives the
hive lines no labels and the shared legend comes out empty.
-->

---

# Answering the materials question

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

**Read the Step 5 chart**

1. Which hive stays closest to 35 °C on each probe?
2. Do the three probes in one hive agree, or does one wander?
3. Does one hive go silent while the others do not?
4. Which material looks best? What would you want to see in winter before you trust that answer?

</div>
<div>

<div class="bh-note">
Write your reading in the markdown cell under the chart: two or three sentences, and the evidence for each.
</div>

<div class="bh-warn mt-4">
A chart shows a pattern, not a verdict. One week of late September is one week. Say what the data supports <em>and</em> what it cannot tell you yet.
</div>

<div class="flex items-center gap-4 mt-4">
<img src="/images/Feedback%20Bee%20Data%20Foundation%20Workshop.png" class="w-28 h-28" alt="QR code linking to the workshop feedback form" />
<div class="bh-small"><strong>Done? Tell us how it went.</strong><br>Scan to leave feedback on the workshop.</div>
</div>

</div>
</div>

<!--
The hive whose brood stays closest to 35 °C, with the fewest long holes, is the one
the data currently supports. Two caveats to say out loud: the hive-to-material mapping
must be confirmed, and a late-summer week tells you nothing about winter.
-->
