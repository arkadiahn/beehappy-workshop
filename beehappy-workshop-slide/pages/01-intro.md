---
class: bh-cover
---

<div class="bh-kicker">Bildungscampus Heilbronn · Live LoRaWAN data</div>

# <span class="bh-brand">BeeHappy</span> — Data Foundation

Real beehive sensor data.<br>
**Analyze what material works best** for the bees.

<div class="mt-10 flex gap-3 items-center">
  <span class="bh-pill">~4 hours</span>
  <span class="bh-pill">7 exercises</span>
  <span class="bh-pill">pandas + matplotlib + Jupyter</span>
</div>

<div @click="$slidev.nav.next" class="mt-12 py-1 cursor-pointer text-amber-700">
  Press Space to start <carbon:arrow-right class="inline" />
</div>

<!--
Welcome. Two things to say out loud before we begin:

1. This data is real and nobody has cleaned it. Every problem you hit today is a
   problem that actually exists in a production database right now.
2. You do not need to know pandas. We teach each function in the exercise
   that uses it.
-->

---
layout: center
class: bh-section
---

# 1 · Intro

What the data is, where it comes from, and why cleaning it is the job

---

# 🐝 What is BeeHappy?

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

**Three beehives** at Bildungscampus Heilbronn, wired with **LoRaWAN sensors**, reporting continuously since **2025**.

Each hive carries devices that measure what is happening inside and around it:

- **Brood chamber** — three temperature probes (`tempC1/C2/C3`)
- **Food chamber** — temperature + humidity
- **Weather station** — temperature, humidity, wind, UV, pressure, light, rain

</div>
<div>

```mermaid {scale: 0.62, theme: 'base', themeVariables: {primaryColor: '#fef3c7', primaryBorderColor: '#f59e0b', primaryTextColor: '#92400e', lineColor: '#d97706', secondaryColor: '#fde68a', tertiaryColor: '#fffbeb', fontFamily: 'Inter, sans-serif'}}
graph TD
  A[Brood sensor<br/>Dragino D23-LB] --> G[LoRaWAN<br/>gateway]
  B[Food sensor<br/>Dragino S31-LB] --> G
  C[Weather station<br/>SenseCAP S2120] --> G
  G --> D[ChatBotCollector<br/>service]
  D --> E[(PostgreSQL)]
```

<div class="bh-note mt-3">
The collector is a service with bugs. <br>
</div>

</div>
</div>

<!--
The hardware detail is not trivia. Knowing that three *different device types* report
on three *different schedules* is what makes Exercise 4 make sense.
-->

---

# Why are we collecting this data?

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-kicker">Today · questions the data can answer</div>

We wrapped the three hives in three different materials: **thermofolie**, **cotton** and **plastic**.

<div class="bh-card mt-3">
<div class="bh-card-h">🐝 Which material is best for the colony?</div>

<span class="bh-small">

- Which hive keeps its brood closest to **35 °C**?
- Does brood stay steadier than the outside temperature?
- Do the three brood probes in one hive agree?
- Does one hive go silent more often than the others?

</span>
</div>

</div>
<div>

<div class="bh-kicker">Later · machine learning</div>

<div class="bh-card mt-3">
<div class="bh-card-h">🌡️ Colony health</div>
<span class="bh-small">The bees hold brood at ~35 °C. When it drifts, something is wrong, and it drifts <em>before</em> the beekeeper can see it. A model could raise the alarm.</span>
</div>

<div class="bh-card mt-3">
<div class="bh-card-h">❄️ Overwintering</div>
<span class="bh-small">Most colonies are lost in winter. Temperature and humidity history could flag the hives at risk while there is still time to act.</span>
</div>

</div>
</div>

<div class="bh-note mt-5">
The question we answer today and the model we might train later need the same input: <strong>one clean row per hive per hour</strong>. That table is what we build today.
</div>

<!--
Pull the group toward the framing: we are not cleaning data for its own sake.

There is no ML problem to solve yet, so today ends with a plot that answers the
materials question. The same table is the input a model would need later, so none
of the work is wasted.
-->

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

# The data · two small lookup tables

<div class="bh-out-label mt-2">beehives · 3 rows · the hives</div>
<pre class="bh-out">   beehive_id          name                                           notes
0           1  Beehive No.1  Larry is standing alone, he needs some friends
1           2  Beehive No.2            TamTam is the middle Sandwhich child
2           3  Beehive No.3          BonBon is the smallest yet most active
</pre>
<div class="bh-small mt-1">+ <code>location</code>, <code>installation_date</code>, <code>last_inspection_date</code></div>

<div class="bh-out-label mt-4">sensors · 9 rows · the devices, and which hive each belongs to</div>
<pre class="bh-out">   sensor_id  beehive_id            sensor_name             sensor_type             measurement_units
0          1           1  LoRa-2CF7F1C0613005BC  LoRaWAN SenseCAP-S2120  lightIntensity,rainGauge,...
1          2           2  LoRa-2CF7F1C0613005BC  LoRaWAN SenseCAP-S2120  lightIntensity,rainGauge,...
2          3           3  LoRa-2CF7F1C0613005BC  LoRaWAN SenseCAP-S2120  lightIntensity,rainGauge,...
3          4           1  LoRa-A840411F645AE815  LoRaWAN Dragino-S31-LB  temperature,relativeHumidity
4          5           3  LoRa-A8404138A188669C  LoRaWAN Dragino-S31-LB  temperature,relativeHumidity
5          6           2  LoRa-A84041CC625AE81E  LoRaWAN Dragino-S31-LB  temperature,relativeHumidity
6          7           3  LoRa-A8404160C85A7A7B  LoRaWAN Dragino-D23-LB          tempC3,tempC1,tempC2
7          8           1  LoRa-A84041892E5A7A68  LoRaWAN Dragino-D23-LB          tempC3,tempC1,tempC2
8          9           2  LoRa-A840419521864618  LoRaWAN Dragino-D23-LB          tempC3,tempC1,tempC2
</pre>
<div class="bh-small mt-1">+ <code>installation_date</code>, <code>last_seen</code>, <code>is_active</code> · one weather station, one food sensor and one brood sensor per hive</div>

<!--
Real rows from the database. Read the sensor_type column out loud: SenseCAP is the
weather station, S31 is the food chamber, D23 is the brood chamber.

Do not point out that sensors 1–3 share a sensor_name. That is Exercise 3's discovery.
-->

---

# The data · one big table of readings

<div class="bh-out-label mt-2">data · ~500k rows for three months · millions in total</div>
<pre class="bh-out">   reading_id  sensor_id  beehive_id  measurement_unit                      ts  value
0     2072737          8           1            tempC3 2026-06-28 12:22:52.471   37.3
1     2072738          8           1            tempC1 2026-06-28 12:22:52.471   35.5
2     2072739          8           1            tempC2 2026-06-28 12:22:52.471   35.7
3     2072776          8           1            tempC3 2026-06-28 12:22:52.471   37.3
4     2072777          8           1            tempC1 2026-06-28 12:22:52.471   35.5
5     2072778          8           1            tempC2 2026-06-28 12:22:52.471   35.7
6     2072732          6           2       temperature 2026-06-28 12:23:27.991   35.6
7     2072733          6           2  relativeHumidity 2026-06-28 12:23:27.991   65.8
</pre>

<div class="bh-small mt-2">
<strong>Long</strong> format: one row per <em>measurement</em>. A single uplink from brood sensor 8 writes three rows: <code>tempC1</code>, <code>tempC2</code>, <code>tempC3</code>.
</div>

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

<div class="bh-out-label">how the tables connect</div>
<div class="space-y-2 mt-1">
  <div class="bh-flow"><span class="box">data</span><span class="arr">— sensor_id →</span><span class="box">sensors</span><span class="bh-small">which device, what type</span></div>
  <div class="bh-flow"><span class="box">data</span><span class="arr">— beehive_id →</span><span class="box">beehives</span><span class="bh-small">which hive</span></div>
  <div class="bh-flow"><span class="box">sensors</span><span class="arr">— beehive_id →</span><span class="box">beehives</span></div>
</div>

</div>
<div>

<div class="bh-note">
You pull <strong>the last three months</strong> of <code>data</code>, filtered in SQL rather than in pandas. The full history is too big to be worth moving.
</div>

</div>
</div>

<!--
Rows 0–2 and 3–5 are worth a second look later. Do not explain them now: Exercise 2
is where they find out why.
-->

---

# The target

One row per hive per hour. `validate_features.py` enforces exactly these names.

<div class="grid grid-cols-2 gap-6 mt-3 text-sm">
<div>

| Column | Meaning |
|---|---|
| `beehive_id`| which hive |
| `hour` | the hour, **UTC** |
| `brood_temp_c1/c2/c3` | brood chamber, three probes |
| `food_temp`, `food_humidity` | food chamber |
| `hour_local`, `month`, `dayofweek` | calendar, **Europe/Berlin** |

</div>
<div>

| Column | Meaning |
|---|---|
| `outside_temp`, `outside_humidity` | ambient |
| `outside_wind_speed`, `outside_wind_dir` | ambient |
| `outside_uv_index`, `outside_pressure_pa` | ambient |
| `outside_light`, `outside_rain` | ambient |

</div>
</div>

```bash
uv run python workshop/validate_features.py workshop/out/features_hourly.parquet
```

<!--
Green is not the goal. A table that passes but whose gap policy you cannot defend is worse than one that fails honestly.
-->

---

# The exercises

| # | Exercise | What you produce | Time |
|---|---|---|---|
| **0** | **Extract** | Three months of `data` + both lookup tables, pulled once, saved to disk | 30 min |
| **1** | **Profile** | A written description of what is actually in there | 30 min |
| **2** | **Deduplicate** | `data` at one row per real measurement, and a number for what you removed | 30 min |
| **3** | **Reshape & join** | A hive frame and a weather frame, each with a grain you can state out loud | 60 min |
| **4** | **Align time & gaps** | One row per hive-hour, with a written gap policy | 60 min |
| **5** | **Validate & document** | `features_hourly.parquet` + `DATA_DICTIONARY.md` that pass the validator | 30 min |
| **6** | **Look at what you built** | One chart of brood vs outside on a short window | 10 min |

<!--
Each exercise says **what to produce, not how**. The exercises build on each other, so do them in order.
-->
