# BeeHappy — Data Foundation workshop

A half-day, hands-on workshop. You start with three raw tables from the BeeHappy
beehive monitoring database and finish with **one dataframe fit to train a model on** —
one row per hive per hour, every cleaning decision written down and checked.

The data is real: 2.36 million readings from seven LoRaWAN devices on three beehives
at Bildungscampus Heilbronn, collected over 14 months. So are its problems. Nothing
here has been tidied up or seeded with artificial mistakes.

## Setup

```bash
uv sync
uv run jupyter lab workshop/notebooks/workshop.ipynb
```

That is the whole setup. No database, no credentials, no network — the data ships
with the repo as Parquet.

## What you are given

| File | Rows | What it is |
|---|---|---|
| `workshop/data/beehives.parquet` | 3 | The hives |
| `workshop/data/sensors.parquet` | 9 | The devices, and which hive each belongs to |
| `workshop/data/data.parquet` | 2,355,297 | Every reading, one row per measurement |

`workshop/data/MANIFEST.md` records exactly when the snapshot was taken and the
numbers your answers should reproduce.

Note the shape of `data`: it is **long**, one row per *measurement*, not per reading
event. A single device uplink writes several rows, one for each thing it measured.
Getting from that to a table with one column per measurement is the first real task.

## The exercises

| # | | Time |
|---|---|---|
| 0 | **Profile** — what is actually in here? | 30 min |
| 1 | **Deduplicate** — find the real grain of the table | 30 min |
| 2 | **Reshape and join** — long to wide, then attach the hive and weather context | 60 min |
| 3 | **Align time and handle gaps** — put everything on one clock | 60 min |
| 4 | **Validate and document** — prove it, then describe it | 30 min |

Work through `workshop/notebooks/workshop.ipynb`. Each exercise says what to produce,
not how. When you have a candidate feature table:

```bash
uv run python workshop/validate_features.py workshop/out/features_hourly.parquet
```

It grades your output and tells you what is wrong, not just that something is.

## A word of warning

You are not told what is wrong with this data, because finding out is the exercise.
One habit will save you more than any other:

> **Check your row count after every join.**

If a join changes the number of rows and you cannot say exactly why, stop and find out.
That single reflex catches the most expensive mistake in this dataset.

## For instructors

`workshop/notebooks/solutions.ipynb` is a full worked solution. Do not hand it out;
it names every defect on sight and there is nothing left to discover afterwards.

To re-cut the snapshot from the live database:

```bash
uv sync --extra export
CHATBOTDB_URL='postgresql://grafana_ro:...@host:port/railway' \
  uv run python workshop/scripts/export_snapshot.py
```

Use the read-only `grafana_ro` role, never the superuser. Be aware that re-cutting
may *lose* teaching material: the largest defect in this data is a live bug in the
upstream collector, and if it is ever fixed a fresh export will be cleaner and several
exercises will fall flat. The committed snapshot is deliberately frozen.

## History

This repository previously held an ETL pipeline that loaded the Bildungscampus
Digital Beehive API into a separate PostgreSQL database, plus Grafana and Metabase
dashboards built on it. That database has been retired — the BeeHappy project already
had a live one with more history — and the Grafana dashboard now lives in the
`beehappy` repository under `grafana/`.

None of it is related to the data in this workshop, so it has been removed to avoid
confusion. It remains in the git history at commit `6b8ca1d` if it is ever needed,
including its notes on the source API's quirks.
