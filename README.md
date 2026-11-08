# BeeHappy — Data Foundation workshop

A half-day (~4 hours), hands-on workshop. You start with three raw tables in the
BeeHappy beehive monitoring database and finish with **one dataframe fit to train a
model on** — one row per hive per hour, every cleaning decision written down and
checked. Plots at the end answer the question the data was collected for: **which hive
wrapping material is best for the colony?**

The data is real: LoRaWAN devices on three beehives at Bildungscampus Heilbronn,
reporting continuously since 2025. So are its problems. Nothing here has been tidied
up or seeded with artificial mistakes.

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you do not have it yet:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh                 # macOS / Linux
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"     # Windows
   ```

2. Create `.env` in the repo root, then replace `password` in `DATABASE_URL` with the
   password you were sent on Slack:

   ```bash
   cp .env.example .env        # macOS / Linux
   copy .env.example .env      # Windows
   ```

3. Open the notebook from the repo root. The first `uv run` installs everything:

   ```bash
   uv run jupyter notebook workshop/notebooks/workshop.ipynb
   ```

4. Run the first cell. It prints the database URL it found.

No data ships with this repo. Exercise 0 is going and getting it, so you need a network
connection and a working `DATABASE_URL`.

## The hives and their sensors

Three hives, each wrapped in a different material: **hive 1** plastic film, **hive 2**
thermofolie, **hive 3** cotton. Each hive has three levels: brood at the bottom, food
(sugar) in the middle, and an empty top.

| Device | Where | Measures | Columns in the final table |
|---|---|---|---|
| Dragino D23-LB | one probe per level | `tempC1` brood, `tempC2` food, `tempC3` top | `brood_probe_temp`, `food_probe_temp`, `top_probe_temp` |
| Dragino S31-LB | brood level | temperature, humidity | `brood_temp`, `brood_humidity` |
| SenseCAP S2120 | weather station beside the hives | temperature, humidity, wind, UV, pressure, light, rain | `outside_*` |

The bees keep the brood at about 35 °C. The empty top level mostly follows the outside air.

## What you are given

Three tables in Postgres:

| Table | What it is |
|---|---|
| `beehives` | the hives |
| `sensors` | the devices, and which hive each belongs to |
| `data` | every reading, one row per measurement |

You pull the **last three months** of `data` yourself, save it, and work from your
saved copy. `data` runs to millions of rows over the full history, so the window is
not a formality.

Note its shape: it is **long**, one row per *measurement*, not per reading event. A
single device uplink writes several rows, one for each thing it measured. Getting from
that to a table with one column per measurement is the main reshaping task.

## The exercises

| # | | Time |
|---|---|---|
| 0 | **Extract** — pull three months out of Postgres, once, and save to Parquet | 30 min |
| 1 | **Profile** — what is actually in here? | 30 min |
| 2 | **Deduplicate** — find the real grain of the table | 30 min |
| 3 | **Reshape and join** — attach each sensor's role, split hive from weather, collapse the weather station | 60 min |
| 4 | **Align time and handle gaps** — one clock, long to wide, every hive-hour, weather attached | 60 min |
| 5 | **Validate and document** — local time, target names, assertions, save and validate | 30 min |
| 6 | **Look at what you built** — plots, and a number for how far each hive is from 35 °C | 30 min |

Work through [`workshop/notebooks/workshop.ipynb`](workshop/notebooks/workshop.ipynb).
Cells marked `# EXECUTE` are working code: just run them. Cells marked `# TODO` are
yours: replace the `...` and run. When you have a feature table:

```bash
uv run python workshop/validate_features.py workshop/out/features_hourly.parquet
```

It grades your output and tells you what is wrong, not just that something is.

Homework: write `DATA_DICTIONARY.md` — every column, its unit, and every decision you
made. The optional seaborn plots at the end of the notebook are extra practice.

## A word of warning

You are not told what is wrong with this data, because finding out is the exercise.
One habit will save you more than any other:

> **Check your row count after every join.**

If a join changes the number of rows and you cannot say exactly why, stop and find out.
That single reflex catches the most expensive mistake in this dataset.

## For instructors

### Slides

The deck in `beehappy-workshop-slide/` is a [Slidev](https://sli.dev) project. It mirrors
the notebook cell by cell, with real outputs, and hides each `TODO` answer until a click.

```bash
cd beehappy-workshop-slide
npm install
npm run dev
```

The slides open in the browser. For speaker notes, open `/presenter` on the same address
(e.g. `http://localhost:3030/presenter`) on your laptop and put the normal window on the
projector; the two stay in sync.

The Exercise 6 charts in `public/charts/` are rendered from the current extract. After a
fresh extract, regenerate them with `uv run python beehappy-workshop-slide/scripts/ex6_charts.py`.

### Solutions

`workshop/notebooks/solutions.ipynb` is a full worked solution. Do not hand it out;
it names every defect on sight and there is nothing left to discover afterwards.

Students read the live database rather than a frozen snapshot, so **run the solutions
notebook the week before you teach** and check the numbers on the slides still hold.
The largest defect in this data is a live bug in the upstream collector; if it is ever
fixed, a fresh pull will be cleaner and Exercise 2 will fall flat. The solutions also
show whether the current three-month window crosses a daylight saving change.

**Clear the outputs before you commit a notebook.** The first cell prints `DATABASE_URL`,
password included, and a saved output would publish it.

### Database access

Students connect as the `postgres` user. This is the BeeHappy **production** database, not a copy, and that role can drop the live tables.
Send the password privately (e.g. on Slack), never in the repo,
and rotate it after the workshop.

A frozen 14-month Parquet snapshot of all three tables is preserved in git history at
commit `cc8bbd1` (`workshop/data/`), together with the `export_snapshot.py` script that
cut it and a manifest of its numbers. Restore it if you ever need a workshop that runs
offline or a known-good copy of the defects.

## History

This repository previously held an ETL pipeline that loaded the Bildungscampus
Digital Beehive API into a separate PostgreSQL database, plus Grafana and Metabase
dashboards built on it. That database has been retired — the BeeHappy project already
had a live one with more history — and the Grafana dashboard now lives in the
`beehappy` repository under `grafana/`.

None of it is related to the data in this workshop, so it has been removed to avoid
confusion. It remains in the git history at commit `6b8ca1d` if it is ever needed,
including its notes on the source API's quirks.
