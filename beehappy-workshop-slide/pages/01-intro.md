---
class: bh-cover
---

<div class="bh-kicker">Bildungscampus Heilbronn · Live LoRaWAN data</div>

# <span class="bh-brand">BeeHappy</span> — Data Foundation


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

1. This data is real and nobody has cleaned it. Every problem you hit today is a problem that actually exists in a production database right now.
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

**Three beehives** at Bildungscampus Heilbronn, wired with **LoRaWAN sensors**, reporting continuously since **2025**. Each hive is wrapped in a different material.

<div class="grid grid-cols-3 gap-6 mt-5 max-w-3xl mx-auto">
  <figure class="m-0">
    <img src="/images/hives/beehive1.jpg" class="w-full h-60 object-cover rounded-lg shadow-lg" alt="Beehive 1, wrapped in plastic film" />
    <figcaption class="mt-2 text-sm"><strong>Hive 1</strong> · plastic film</figcaption>
  </figure>
  <figure class="m-0">
    <img src="/images/hives/beehive2.jpg" class="w-full h-60 object-cover rounded-lg shadow-lg" alt="Beehive 2, wrapped in thermal foil" />
    <figcaption class="mt-2 text-sm"><strong>Hive 2</strong> · thermofolie</figcaption>
  </figure>
  <figure class="m-0">
    <img src="/images/hives/beehive3.jpg" class="w-full h-60 object-cover object-top rounded-lg shadow-lg" alt="Beehive 3, covered with cotton fabric" />
    <figcaption class="mt-2 text-sm"><strong>Hive 3</strong> · cotton</figcaption>
  </figure>
</div>

<!--
These are the three hives the data comes from. Which material works best is the
question the data answers today.
-->

---

# 📡 What sensors do the hives carry?

<div class="grid grid-cols-2 gap-6 mt-4">
<div>

Each hive carries devices that measure what is happening inside and around it:

- **Three probes** — C1 brood, C2 food, C3 empty top
- **Brood sensor** — temperature + humidity
- **Weather station** — temperature, humidity, wind, UV, pressure, light, rain

<figure class="m-0 mt-4">
  <img src="/images/hives/sensor-on-hive.jpg" class="h-36 rounded-lg shadow" alt="A LoRaWAN sensor mounted on the side of an open hive" />
  <figcaption class="bh-small mt-1">A LoRaWAN sensor mounted on a hive</figcaption>
</figure>

</div>
<div>

<svg viewBox="0 -24 470 344" class="w-full" role="img" aria-label="Cross-section of one hive: an empty top level, a food level with sugar, and a brood level at the bottom. A probe device on the side has one probe in each level (C3 top, C2 food, C1 brood). A temperature and humidity sensor sits in the brood level. A weather station stands on a pole beside the hive.">
  <g font-family="Inter, sans-serif" fill="#92400e">
    <line x1="10" y1="312" x2="460" y2="312" stroke="#d6c7a1" stroke-width="2"/>
    <line x1="62" y1="96" x2="62" y2="312" stroke="#a16207" stroke-width="4"/>
    <rect x="38" y="76" width="48" height="26" rx="4" fill="#fde68a" stroke="#d97706" stroke-width="1.5"/>
    <line x1="62" y1="76" x2="62" y2="58" stroke="#a16207" stroke-width="2"/>
    <line x1="46" y1="58" x2="78" y2="58" stroke="#a16207" stroke-width="2"/>
    <circle cx="46" cy="58" r="5" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
    <circle cx="78" cy="58" r="5" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
    <text x="62" y="-10" text-anchor="middle" style="font-size:13px;font-weight:700">Weather station</text>
    <text x="62" y="4" text-anchor="middle" style="font-size:10px">SenseCAP S2120</text>
    <text x="62" y="18" text-anchor="middle" style="font-size:9.5px" fill="#78350f">temp · humidity</text>
    <text x="62" y="30" text-anchor="middle" style="font-size:9.5px" fill="#78350f">wind · UV · light</text>
    <text x="62" y="42" text-anchor="middle" style="font-size:9.5px" fill="#78350f">pressure · rain</text>
    <polygon points="160,74 340,74 352,92 148,92" fill="#d97706"/>
    <rect x="156" y="92" width="188" height="62" fill="#fffbeb" stroke="#d97706" stroke-width="2"/>
    <rect x="156" y="154" width="188" height="62" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
    <rect x="156" y="216" width="188" height="70" fill="#fde68a" stroke="#d97706" stroke-width="2"/>
    <rect x="166" y="286" width="12" height="26" fill="#a16207"/>
    <rect x="322" y="286" width="12" height="26" fill="#a16207"/>
    <text x="170" y="128" style="font-size:13px;font-weight:700">Top</text>
    <text x="170" y="143" style="font-size:10px" fill="#78350f">empty</text>
    <text x="170" y="190" style="font-size:13px;font-weight:700">Food</text>
    <text x="170" y="205" style="font-size:10px" fill="#78350f">sugar</text>
    <text x="170" y="250" style="font-size:13px;font-weight:700">Brood</text>
    <text x="170" y="265" style="font-size:10px" fill="#78350f">~35 °C</text>
    <rect x="214" y="234" width="62" height="34" rx="4" fill="#ffffff" stroke="#b45309" stroke-width="1.5"/>
    <text x="245" y="249" text-anchor="middle" style="font-size:10px;font-weight:700">S31</text>
    <text x="245" y="262" text-anchor="middle" style="font-size:8.5px" fill="#78350f">temp + hum.</text>
    <path d="M384 176 C 360 176, 352 123, 320 123" fill="none" stroke="#b45309" stroke-width="1.5"/>
    <path d="M384 184 C 362 184, 352 185, 320 185" fill="none" stroke="#b45309" stroke-width="1.5"/>
    <path d="M384 192 C 360 192, 352 250, 320 250" fill="none" stroke="#b45309" stroke-width="1.5"/>
    <circle cx="316" cy="123" r="6" fill="#b45309"/>
    <circle cx="316" cy="185" r="6" fill="#b45309"/>
    <circle cx="316" cy="250" r="6" fill="#b45309"/>
    <text x="300" y="127" text-anchor="end" style="font-size:11px;font-weight:700">C3</text>
    <text x="300" y="189" text-anchor="end" style="font-size:11px;font-weight:700">C2</text>
    <text x="300" y="254" text-anchor="end" style="font-size:11px;font-weight:700">C1</text>
    <rect x="384" y="166" width="52" height="36" rx="4" fill="#ffffff" stroke="#b45309" stroke-width="1.5"/>
    <text x="410" y="188" text-anchor="middle" style="font-size:11px;font-weight:700">D23</text>
    <text x="410" y="222" text-anchor="middle" style="font-size:10px" fill="#78350f">three probes,</text>
    <text x="410" y="235" text-anchor="middle" style="font-size:10px" fill="#78350f">one per level</text>
  </g>
</svg>

</div>
</div>

<!--
The hive has three levels: brood at the bottom, food (sugar) in the middle, an empty top.
The D23 device has one probe per level: C1 brood, C2 food, C3 top. The S31 temperature and
humidity sensor also sits in the brood level. The empty top mostly follows the outside air.

The hardware detail is not trivia. Knowing that three *different device types* report
on three *different schedules* is what makes Exercise 4 make sense.
-->

---

# Why and how we are collecting this data

<div class="grid grid-cols-2 gap-6 mt-2">
<div>

<div class="bh-kicker">Today</div>

<div class="bh-card mt-2">
<div class="bh-card-h">🐝 Which material is best for the colony?</div>

<span class="bh-small">

- Whose brood stays closest to **35 °C**?
- Whose brood stays steadiest?

</span>
</div>

<div class="bh-kicker mt-4">Later · machine learning</div>

<div class="bh-card mt-2">
<div class="bh-card-h">🌡️ Colony health</div>
<span class="bh-small">Alert when brood temperature drifts.</span>
</div>

<div class="bh-card mt-2">
<div class="bh-card-h">❄️ Overwintering</div>
<span class="bh-small">Flag hives at risk before winter losses.</span>
</div>

<div class="bh-note mt-5">
Both need the same input: <strong>one clean row per hive per hour</strong>. That's what we build today.
</div>
</div>
<div>

<div class="bh-kicker">How</div>

```mermaid {scale: 0.62, theme: 'base', themeVariables: {primaryColor: '#fef3c7', primaryBorderColor: '#f59e0b', primaryTextColor: '#92400e', lineColor: '#d97706', secondaryColor: '#fde68a', tertiaryColor: '#fffbeb', fontFamily: 'Inter, sans-serif'}}
graph TD
  A[Three probes<br/>Dragino D23-LB] --> G[LoRaWAN<br/>gateway]
  B[Brood sensor<br/>Dragino S31-LB] --> G
  C[Weather station<br/>SenseCAP S2120] --> G
  G --> D[ChatBotCollector<br/>service]
  D --> E[(PostgreSQL)]
```

<div class="bh-note mt-2">
The collector is a service with bugs. <br>
</div>

</div>
</div>


<!--
Pull the group toward the framing: we are not cleaning data for its own sake.

Today: the three hives are wrapped in thermofolie, cotton and plastic. Other questions
the data can answer: does the empty top level follow the outside temperature? Does one hive go
silent more often than the others?

Later: bees hold brood at ~35 °C, and it drifts *before* the beekeeper can see a
problem, so a model could raise the alarm. Most colonies are lost in winter;
temperature and humidity history could flag the hives at risk while there is still
time to act.

There is no ML problem to solve yet, so today ends with a plot that answers the
materials question. The same table is the input a model would need later, so none
of the work is wasted.
-->

---

# Why data cleaning comes first

<div class="mt-8 text-left max-w-3xl mx-auto">

> A model can't tell a signal from a mistake. It will happily learn the mistake.

</div>

<div class="grid grid-cols-2 gap-4 mt-10 text-left max-w-3xl mx-auto">
<div class="bh-card">
<div class="bh-card-h">Duplicates</div>
<span class="bh-small">Rows inserted twice silently skew every average.</span>
</div>
<div class="bh-card">
<div class="bh-card-h">Silent gaps</div>
<span class="bh-small">A missing row isn't a <code>NaN</code>. It's nothing, and nothing is hard to notice.</span>
</div>
</div>

<div class="mt-8 bh-small">
Typically 60–80% of a data science project is this step.
</div>

<!--
Do not moralise for too long. One sentence per card and move on — they will meet both
of these for real within the hour.

Duplicates: the "average temperature" becomes a weighted average, weighted by how many
times the collector happened to insert the same row.
-->

---

# The data · two small lookup tables

<div class="bh-out-label mt-2">beehives · 3 rows · the hives</div>
<pre class="bh-out">   beehive_id          name
0           1  Beehive No.1
1           2  Beehive No.2
2           3  Beehive No.3
</pre>
<div class="bh-small mt-1">+ <code>notes</code>, <code>location</code>, <code>installation_date</code>, <code>last_inspection_date</code></div>

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
<div class="bh-small mt-1">+ <code>installation_date</code>, <code>last_seen</code>, <code>is_active</code> · one weather station, one brood sensor and one three-probe device per hive</div>

<!--
Real rows from the database. Read the sensor_type column out loud: SenseCAP is the
weather station, S31 is the brood temperature and humidity sensor, D23 holds the three probes (C1 brood, C2 food, C3 empty top).

Do not point out that sensors 1–3 share a sensor_name. That is Exercise 3's discovery.
-->

---

# The data · one big table of readings

<div class="bh-out-label mt-2">data · ~500k rows for three months · millions in total</div>
<pre class="bh-out">   reading_id  sensor_id  beehive_id  measurement_unit                      ts  value
0     2293351          8           1            tempC3 2026-08-07 13:11:37.873   32.6
1     2293352          8           1            tempC1 2026-08-07 13:11:37.873   34.6
2     2293353          8           1            tempC2 2026-08-07 13:11:37.873   31.0
3     2293390          8           1            tempC3 2026-08-07 13:11:37.873   32.6
4     2293391          8           1            tempC1 2026-08-07 13:11:37.873   34.6
5     2293392          8           1            tempC2 2026-08-07 13:11:37.873   31.0
6     2293385          6           2       temperature 2026-08-07 13:19:12.026   33.8
7     2293386          6           2  relativeHumidity 2026-08-07 13:19:12.026   65.4
</pre>

<div class="bh-small mt-2">
<strong>Long</strong> format: one row per <em>measurement</em>. A single uplink from probe device 8 writes three rows: <code>tempC1</code>, <code>tempC2</code>, <code>tempC3</code>.
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

One row per hive per hour.

<div class="grid grid-cols-2 gap-6 mt-3 text-sm">
<div>

| Column | Meaning |
|---|---|
| `beehive_id`| which hive |
| `hour` | the hour, **UTC** |
| `brood_probe_temp`, `food_probe_temp`, `top_probe_temp` | three probes, one per level: brood (C1), food (C2), empty top (C3) |
| `brood_temp`, `brood_humidity` | temperature and humidity sensor in the brood level |
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


<!--
Green is not the goal. A table that passes but that you cannot explain is worse than one that fails honestly.
-->

---

# The exercises

| # | Exercise | What you produce | Time |
|---|---|---|---|
| **0** | **Extract** | Three tables, saved to disk | 10 min |
| **1** | **Profile** | What is in the data | 30 min |
| **2** | **Deduplicate** | One row per real reading | 15 min |
| **3** | **Reshape & join** | A hive frame and a weather frame | 60 min |
| **4** | **Align time & gaps** | One row per hive-hour | 30 min |
| **5** | **Validate & document** | A validated file | 10 min |
| **6** | **Look at what you built** | Plots that answer the question | 30 min |

<!--
Each exercise says **what to produce, not how**. The exercises build on each other, so do them in order.
-->
