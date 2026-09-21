# BeeHappy — Data Foundation workshop

A half-day (~4 hours), hands-on workshop. You start with three raw tables in the
BeeHappy beehive monitoring database and finish with **one dataframe fit to train a
model on** — one row per hive per hour, every cleaning decision written down and
checked. A short plot at the end is how you look at what you built.

The data is real: LoRaWAN devices on three beehives at Bildungscampus Heilbronn,
reporting continuously since 2025. So are its problems. Nothing here has been tidied
up or seeded with artificial mistakes.

## Setup

```bash
uv sync
cp .env.example .env    # then paste in the connection string you were given
uv run jupyter lab workshop/notebooks/workshop.ipynb
```

No data ships with this repo. Exercise 0 is going and getting it, which means you need
a network connection and a `DATABASE_URL` in `.env`. The database is hosted on Railway;
your connection string needs `?sslmode=require` on the end, or the password crosses the
public internet in plaintext. The role you are given is read-only: you cannot damage
anything.

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
that to a table with one column per measurement is the first real reshaping task.

## The exercises

| # | | Time |
|---|---|---|
| 0 | **Extract** — pull three months out of Postgres, once | 30 min |
| 1 | **Profile** — what is actually in here? | 30 min |
| 2 | **Deduplicate** — find the real grain of the table | 30 min |
| 3 | **Reshape and join** — attach hive and role, then split hive vs weather (wide reshape is Ex 4) | 60 min |
| 4 | **Align time and handle gaps** — one clock, long to wide, complete hours, weather | 60 min |
| 5 | **Validate and document** — prove it, then describe it | 30 min |
| 6 | **Look at what you built** — plot brood vs outside on a short window | 10 min |

Work through [`workshop/notebooks/workshop.ipynb`](workshop/notebooks/workshop.ipynb).
Each exercise has a starter in the code cell — fill the blanks and run it. The
markdown still says the deliverable and what to watch for. When you have a candidate
feature table:

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

Students now read the live database rather than a frozen snapshot, so **run the
solutions notebook the week before you teach**. The largest defect in this data is a
live bug in the upstream collector; if it is ever fixed, a fresh pull will be cleaner
and Exercise 2 will fall flat. The solutions notebook flags what to check, including
whether the current three-month window happens to cross a DST change.

A frozen 14-month Parquet snapshot of all three tables is preserved in git history at
commit `cc8bbd1` (`workshop/data/`), together with the `export_snapshot.py` script that
cut it and a manifest of its numbers. Restore it if you ever need a workshop that runs
offline or a known-good copy of the defects.

Hand out credentials for the read-only `grafana_ro` role, never the `postgres`
superuser. This is the BeeHappy **production** database, not a copy — a student who
mistypes a query under a superuser role can drop the live tables, and Exercise 0's
`SELECT *` habit makes that an easy mistake to make. `grafana_ro` already exists on the
instance; only its password needs distributing.

## History

This repository previously held an ETL pipeline that loaded the Bildungscampus
Digital Beehive API into a separate PostgreSQL database, plus Grafana and Metabase
dashboards built on it. That database has been retired — the BeeHappy project already
had a live one with more history — and the Grafana dashboard now lives in the
`beehappy` repository under `grafana/`.

None of it is related to the data in this workshop, so it has been removed to avoid
confusion. It remains in the git history at commit `6b8ca1d` if it is ever needed,
including its notes on the source API's quirks.
