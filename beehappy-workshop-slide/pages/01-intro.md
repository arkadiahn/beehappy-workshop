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

<div class="grid grid-cols-2 gap-4 mt-6">

<div class="bh-card">
<div class="bh-card-h">🌡️ Colony health</div>
Brood temperature is tightly regulated by the bees at ~35 °C. When it drifts, something is wrong — and it drifts <em>before</em> the beekeeper can see it.
</div>

<div class="bh-card">
<div class="bh-card-h">❄️ Overwintering</div>
Most colony losses happen in winter. Humidity and temperature history tell you which hives are at risk while you can still act.
</div>

</div>

<div class="mt-8">
We used 3 different materials for each hive: thermofolie, cotton and plastic. <br>
We would like to figure out which material is the best one for the bee colony.

</div>

<!--
Pull the group toward the framing: we are not doing data cleaning as an end in itself.
We are building the input a model needs.
-->

---
layoutClass: gap-10
---

# The data

<div class="bh-out-label mt-2">data (long, one row per measurement)</div>
<pre class="bh-out">reading_id  sensor_id  measurement_unit  ts                value
   9182344          3  tempC1            2025-08-01 04:11   34.9
   9182345          3  tempC2            2025-08-01 04:11   35.2
   9182346          3  tempC3            2025-08-01 04:11   34.7
   9182347          7  temperature       2025-08-01 04:17   21.3
   9182348          7  relativeHumidity  2025-08-01 04:17   63.0
   9182349          3  tempC1            2025-08-01 04:11   34.9
</pre>

<div class="bh-note mt-6">
Everything in between is pandas.
</div>

---

# The data

<div class="grid grid-cols-3 gap-4 mt-6">

<div class="bh-card">
<div class="bh-card-h">beehives</div>
<span class="bh-small">~3 rows</span>

The hives themselves — id and name.
</div>

<div class="bh-card">
<div class="bh-card-h">sensors</div>
<span class="bh-small">~9 rows</span>

The devices: `sensor_id`, `sensor_type`, `sensor_name`, and which `beehive_id` each belongs to.
</div>

<div class="bh-card">
<div class="bh-card-h">data</div>
<span class="bh-small">millions of rows</span>

Every reading: `reading_id`, `sensor_id`, `measurement_unit`, `ts`, `value`.
</div>

</div>

<div class="mt-6">

You pull **the last three months** of `data` — filtered in SQL, not in pandas afterwards. The full history is far too big to be worth moving.

</div>

---

# The target

One row per hive per hour. `validate_features.py` enforces exactly these names.

<div class="grid grid-cols-2 gap-6 mt-3 text-sm">
<div>

| Column | Meaning |
|---|---|
| `beehive_id`, `hive_name` | which hive |
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
