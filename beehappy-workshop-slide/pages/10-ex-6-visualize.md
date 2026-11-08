---
layout: center
class: bh-section
---

# Exercise 6 · Look at what you built

Check the table with your eyes. Answer the materials question.

<div class="mt-8 bh-small">
<code>plt.plot</code> · <code>plt.subplots</code> · <code>df.plot</code> · <code>ax.axhline</code> · <code>sns.lineplot(hue=)</code> · <code>sns.set_palette</code>
</div>

<!--
Five small steps, each one adds a single idea:
1 plt.plot  2 a time window + fig, ax  3 df.plot + reference line
4 seaborn hue  5 one panel per level (brood, food, empty top).
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
plt.plot(one["hour"], one["brood_probe_temp"])
plt.xticks(rotation=45)  # tilt the dates
plt.show()
```

<div class="bh-note mt-3">
<code>plt.plot</code> takes an <strong>x</strong> and a <strong>y</strong>, both columns of the same length. One hive, one probe, the whole extract.
</div>

</div>
<div class="col-span-3">

<img src="/charts/ex6-1-plt-plot.png" class="max-h-96 mx-auto" alt="Hive 1 brood probe over three months: dense zig-zag between about 11 and 37 °C, trending down from August to late October" />

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
ax.plot(window["hour"], window["brood_probe_temp"])
ax.set_ylabel("°C")
```

<div class="grid grid-cols-3 gap-6 mt-3">
<div class="col-span-2">

<img src="/charts/ex6-2-window.png" class="w-full" alt="Hive 1 brood probe over the last seven days: a daily cycle between about 11 and 20 °C" />

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
    y=["brood_probe_temp", "outside_temp"],
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

<img src="/charts/ex6-3-df-plot.png" class="w-full" alt="Hive 1 over seven days: brood probe between 11 and 20 °C, outside between 7 and 20 °C, black dashed 35 °C line far above both" />

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
temperature every day. That is late October. It is a finding, not a bug: let them
say it out loud before you explain it.
-->

---

# Step 4 · seaborn: one line per hive with `hue`

<div class="grid grid-cols-5 gap-6 mt-2">
<div class="col-span-2">

```python
temp = features[[
    "beehive_id", "hour", "brood_probe_temp",
    "food_probe_temp", "top_probe_temp",
    "outside_temp"]]
temp_7_days = temp[temp["hour"] >=
                   temp["hour"].max()
                   - pd.Timedelta(days=DAYS)]

ax = sns.lineplot(data=temp_7_days,
                  x="hour",
                  y="brood_probe_temp",
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

<img src="/charts/ex6-4-sns-hue.png" class="max-h-100 mx-auto" alt="Brood probe for hives 1, 2 and 3 over the last seven days: hive 2 runs about 8 °C warmer than hives 1 and 3; all stay below the 35 °C line" />

</div>
</div>

---

# Step 5 · One panel per level: `plt.subplots`

<div class="grid grid-cols-2 gap-6 mt-2">
<div>

```python
PROBES = ["brood_probe_temp", "food_probe_temp",
          "top_probe_temp"]   # bottom to top
fig, axes = plt.subplots(3, 1, figsize=(9, 9),
                         sharex=True)

# axes: three plots. enumerate: 0, 1, 2
for i, ax in enumerate(axes):
    sns.lineplot(
        data=temp_7_days, x="hour",
        y=PROBES[i],
        hue="beehive_id", palette="colorblind",
        ax=ax,
        legend=(i == 0),  # top panel only
    )
    ax.axhline(OPTIMAL_C, color="black",
               linestyle="--")
    ax.set_ylabel(f"{PROBES[i]} (°C)")

fig.suptitle(f"Probes bottom to top, last {DAYS} days "
             f"(dashed: {OPTIMAL_C} °C target)")
fig.tight_layout()
```

</div>
<div>

<img src="/charts/ex6-5-subplots.png" class="max-h-90 mx-auto" alt="Three stacked panels, the brood, food and top probes for all three hives over seven days, each with a black dashed 35 °C line and one shared legend on the top panel" />

<div class="bh-small mt-1">
<code>ax=ax</code> picks the panel. <code>legend=(i == 0)</code> keeps one legend instead of three.
</div>

</div>
</div>

<!--
legend=False on every panel plus fig.legend does NOT work: seaborn then gives the
hive lines no labels and the shared legend comes out empty.
-->

---

# Step 6 · How far from 35 °C?

<div class="grid grid-cols-2 gap-6 mt-2">
<div>

<div class="relative">
<div v-click.hide="1">

```python
deviation = features.assign(
    deviation=features[...] - OPTIMAL_C,
    day=features["hour"].dt.floor("D"),
)
daily_dev = (deviation
             .groupby([...])["deviation"]
             .mean().reset_index())

fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=..., x="...", y="...",
             hue="...", palette="colorblind",
             ax=ax)
ax.axhline(0, color="black", linestyle="--")
```

</div>
<div v-click="1" class="absolute inset-0">

```python
deviation = features.assign(
    deviation=features["brood_temp"] - OPTIMAL_C,
    day=features["hour"].dt.floor("D"),
)
daily_dev = (deviation
             .groupby(["beehive_id", "day"])["deviation"]
             .mean().reset_index())

fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=daily_dev, x="day", y="deviation",
             hue="beehive_id", palette="colorblind",
             ax=ax)
ax.axhline(0, color="black", linestyle="--")
```

</div>
</div>

<div class="bh-note mt-3">
<code>brood_temp</code> is the sensor in the brood level. Subtract 35: <strong>0</strong> is perfect, below 0 is too cold.
</div>

</div>
<div v-click="2">

<img src="/charts/ex6-6-deviation.png" class="w-full" alt="Daily mean of brood_temp minus 35 °C per hive, mid August to early November. All three hives stay below zero. Hive 3 is closest until early October; hive 2 drops to about -15 in late September, then stays near -2 to -8 through October while hives 1 and 3 fall to -20 to -25; in November all three fall to about -30." />

<div class="bh-small mt-2">Every line stays below 0: no hive reaches 35 °C. Which one stays <strong>closest</strong> changes over the season.</div>

</div>
</div>

<!--
Ask for the column and the groupby keys before the reveal click.

On the current extract (7 Aug - 7 Nov): hive 3 is closest until early October. Hive 2 is the
coldest in late September (about -15), then holds near -2 to -8 through October while hives 1
and 3 drop to -20 to -25. In November all three fall to about -30.
-->

---

# Step 7 · One number per hive

<div class="grid grid-cols-2 gap-6 mt-2">
<div>

<div class="relative">
<div v-click.hide="1">

```python
mae = (deviation
       .assign(abs_dev=...)
       .groupby(...)["abs_dev"].mean()
       .round(2)
       .sort_values())
mae
```

</div>
<div v-click="1" class="absolute inset-0">

```python
mae = (deviation
       .assign(abs_dev=deviation["deviation"].abs())
       .groupby("beehive_id")["abs_dev"].mean()
       .round(2)
       .sort_values())
mae
```

</div>
</div>

<div class="bh-small mt-3"><code>.abs()</code> makes every distance positive, so too cold and too hot both count. The mean of that is the <strong>mean absolute deviation</strong>: lower is better.</div>

</div>
<div>

<div v-click="2">
<div class="bh-out-label">output</div>
<pre class="bh-out">beehive_id
2     7.37
3     9.29
1    11.43
Name: abs_dev, dtype: float64</pre>
</div>

<div v-click="3" class="bh-warn mt-4">
Hive 2 (thermofolie) is closest <strong>on average</strong>. The Step 6 chart shows it wins only from October on. One number hides <em>when</em>.
</div>

</div>
</div>

<!--
Hive 2 7.37, hive 3 9.29, hive 1 11.43 on the current extract (7 Aug - 7 Nov).
Good closing question: is one number enough to answer the materials question?
-->

---

# Answering the materials question

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

**Read the Step 5 – 7 charts**

1. The top level is empty. Does it follow the brood or the outside?
2. Did one hive's sensors stop sending data for a while, while the other hives kept reporting? <span class="bh-small">Hint: the daily means hide gaps. Plot the full extract hourly, or count the missing hours per hive with <code>.isna().sum()</code>.</span>
3. The data covers August to November. Would the same hive still be best in the cold of winter? What data would you need to be sure?

</div>
<div>

<div class="bh-warn">
A chart shows a pattern, not a verdict. One week of late October is one week. Say what the data supports <em>and</em> what it cannot tell you yet.
</div>

<div class="flex items-center gap-4 mt-4">
<img src="/images/Feedback%20Bee%20Data%20Foundation%20Workshop.png" class="w-28 h-28" alt="QR code linking to the workshop feedback form" />
<div class="bh-small"><strong>Done? Tell us how it went.</strong><br>Scan to leave feedback on the workshop.</div>
</div>

</div>
</div>

<!--
On the current extract (21-28 October) hive 2's brood probe runs about 8 °C warmer
than hives 1 and 3 (about 22 °C against 14 and 12), and all three stay well below 35 °C.
The top probes of all three hives sit close together and follow the outside air.
Two caveats to say out loud: the hive-to-material mapping must be confirmed, and one
October week tells you nothing about winter.
-->

---

# Optional · six more kinds of plot

<div class="bh-small">Done early? The end of the notebook has one cell per plot type, already working. Run them and read each chart.</div>

<div class="grid grid-cols-3 gap-3 mt-3">

<div v-click="1" class="bh-card" style="padding:0.5rem 0.7rem">
<img src="/charts/opt-scatter.png" class="h-28 w-full object-contain" alt="Outside temperature against humidity, one dot per hour, coloured by month" />
<div style="font-size:0.72rem;font-weight:700;color:var(--bh-honey-700)" class="mt-1">Scatter · <code>sns.scatterplot</code></div>
<div style="font-size:0.66rem;line-height:1.3" class="text-gray-500">Two columns against each other: hot hours are dry.</div>
</div>

<div v-click="2" class="bh-card" style="padding:0.5rem 0.7rem">
<img src="/charts/opt-lmplot.png" class="h-28 w-full object-contain" alt="Brood probe against outside temperature with one fitted line per hive; hive 2's line is flattest" />
<div style="font-size:0.72rem;font-weight:700;color:var(--bh-honey-700)" class="mt-1">Scatter + line · <code>sns.lmplot</code></div>
<div style="font-size:0.66rem;line-height:1.3" class="text-gray-500">Flatter line per hive = better insulated.</div>
</div>

<div v-click="3" class="bh-card" style="padding:0.5rem 0.7rem">
<img src="/charts/opt-boxplot.png" class="h-28 w-full object-contain" alt="Brood probe temperature per month and hive as boxes, falling from August to November" />
<div style="font-size:0.72rem;font-weight:700;color:var(--bh-honey-700)" class="mt-1">Boxplot · <code>sns.boxplot</code></div>
<div style="font-size:0.66rem;line-height:1.3" class="text-gray-500">Median and spread per group: the brood cools month by month.</div>
</div>

<div v-click="4" class="bh-card" style="padding:0.5rem 0.7rem">
<img src="/charts/opt-dailycycle.png" class="h-28 w-full object-contain" alt="The average day per local hour for each hive and outside, with shaded uncertainty bands" />
<div style="font-size:0.72rem;font-weight:700;color:var(--bh-honey-700)" class="mt-1">Line with a band · <code>sns.lineplot</code></div>
<div style="font-size:0.66rem;line-height:1.3" class="text-gray-500">The average day: the mean plus its uncertainty.</div>
</div>

<div v-click="5" class="bh-card" style="padding:0.5rem 0.7rem">
<img src="/charts/opt-heatmap.png" class="h-28 w-full object-contain" alt="Correlation matrix of six weather columns; light and UV at 0.98, temperature and humidity at -0.81" />
<div style="font-size:0.72rem;font-weight:700;color:var(--bh-honey-700)" class="mt-1">Heatmap · <code>sns.heatmap</code></div>
<div style="font-size:0.66rem;line-height:1.3" class="text-gray-500">Which columns move together: light and UV almost the same.</div>
</div>

<div v-click="6" class="bh-card" style="padding:0.5rem 0.7rem">
<img src="/charts/opt-histogram.png" class="h-28 w-full object-contain" alt="Hours per 45 degree wind direction sector, peaking between 180 and 225 degrees" />
<div style="font-size:0.72rem;font-weight:700;color:var(--bh-honey-700)" class="mt-1">Histogram · <code>sns.histplot</code></div>
<div style="font-size:0.66rem;line-height:1.3" class="text-gray-500">How often each value occurs: wind mostly from the south-west.</div>
</div>

</div>

<!--
These are EXECUTE cells: nothing to fill in. The point is the vocabulary: which plot
answers which kind of question. Each one comes with two or three questions in the notebook.
-->
