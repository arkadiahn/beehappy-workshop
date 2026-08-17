# the_bees

ETL pipeline that loads the [Bildungscampus Digital Beehive](https://apis.smartcity.hn/bildungscampus/iotplatform/digitalbeehive/v1/)
IoT API into PostgreSQL.

Seven LoRaWAN devices at Bildungscampus Heilbronn, building 42:

| Device type | Count | Measures | Lands in |
|---|---|---|---|
| SenseCAP S2120 | 1 | temperature, humidity, wind speed/direction, UV, pressure, light, rain | `weather` |
| Dragino S31-LB | 3 | in-hive temperature + humidity | `hive_measurements` |
| Dragino D23-LB | 3 | three-probe temperature (brood / food / hive) | `hive_measurements` |

## Setup

```bash
uv sync --extra analysis   # omit --extra analysis for the ETL alone
createdb bees
```

The `analysis` extra holds the notebook stack (jupyter, pandas, matplotlib,
seaborn) used by `bees.ipynb`. It is deliberately kept out of the core
dependencies so the deployed cron container stays small.

`.env` (gitignored) needs:

```
BILDUNGSCAMPUS_API_KEY=...          # https://data-library.smartcity.hn/my-apps/new-app
DATABASE_URL=postgresql://user@localhost:5432/bees
```

`DATABASE_URL` is optional — without it the standard `PGUSER`/`PGHOST`/`PGPORT`/`PGDATABASE`
variables are used instead.

## Usage

```bash
uv run main.py --init-schema     # create tables, then load
uv run main.py                   # incremental load — run this on a schedule
uv run main.py --discover-only   # print the API's devices and keys, touch nothing
uv run main.py --dry-run         # fetch and transform, write nothing
uv run main.py --backfill-days 7 # override the 90-day backfill window
```

The first run backfills 90 days (~53k rows, ~75s). Later runs only fetch what
changed. Re-running is always safe: `UNIQUE (sensor_id, recorded_at)` plus
`ON CONFLICT DO NOTHING` means overlapping windows and crashed runs converge to
the same table.

## Deploying to Railway

Two services in one Railway project: a **Postgres** database and a **cron**
service running this pipeline hourly.

### 1. Create the database

In the Railway dashboard: **New Project → Deploy PostgreSQL**. Nothing to
configure; the schema creates itself on the first run.

### 2. Deploy the ETL as a cron service

Push this repo to GitHub, then in the same Railway project: **New → GitHub
Repo** and pick it. `railway.json` is detected automatically and sets the
Dockerfile build, the hourly schedule and `restartPolicyType: NEVER` (without
that last one Railway would restart the finished job in a loop).

On the new service's **Variables** tab add:

| Variable | Value |
|---|---|
| `BILDUNGSCAMPUS_API_KEY` | your key |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |

That `${{Postgres.DATABASE_URL}}` is a Railway *reference variable*, not a
literal — it resolves to the private-network address, so traffic never leaves
Railway and costs no egress. Type it exactly as shown.

The first run backfills 90 days and then exits; every later run takes a few
seconds. Change the cadence via `cronSchedule` in `railway.json` (readings
arrive every ~20 min, so hourly loses nothing).

### 3. Connecting from your laptop

For `psql` or the notebook, use the Postgres service's **`DATABASE_PUBLIC_URL`**
(Variables tab) — the internal `*.railway.internal` host does not resolve
outside Railway. Put it in `.env` as either name; `DATABASE_URL` wins if both
are set:

```
DATABASE_PUBLIC_URL=postgresql://postgres:...@turntable.proxy.rlwy.net:12345/railway
```

`sslmode=require` is appended automatically for any non-local host, so
credentials are never sent over the public internet in the clear. Set
`sslmode=` explicitly in the URL to override.

Note the public proxy **does** bill egress, so prefer keeping bulk loads on the
cron service and using the public URL for queries.

## Hive topology

The API says which devices exist, but **not which device sits in which hive** —
every device reports `location = "42"`. That mapping lives in `hives.toml`, and
the current grouping is a **guess** (S31-LB paired with D23-LB in API order).

Confirm it with the beekeeper and edit `sensors = [...]`; the next run moves the
sensors. A device present in the API but absent from `hives.toml` is still
loaded, with `hive_id = NULL` and a warning.

## Layout

```
main.py            CLI: argument parsing, run report
bees/config.py     settings from .env; topology from hives.toml
bees/api.py        API client, retries, backwards timeseries pagination
bees/transform.py  API key -> column mapping, pivot to rows
bees/db.py         schema, dimension upserts, batched fact inserts
bees/etl.py        orchestration: discover -> seed -> load
data_schema.sql    tables (idempotent, applied by --init-schema)
hives.toml         hive <-> sensor topology (hand-maintained)
bees.ipynb         notebook for data analysis
Dockerfile         ETL-only image for the Railway cron service
railway.json       Railway build + hourly cron configuration
```

## Notes on the API

Two behaviours differ from the published OpenAPI spec, and the client handles both:

- The 500-point response cap is **per key**, and truncates from the *newest*
  end. `iter_timeseries` therefore pages *backwards* from `endTs`.
- Points arrive **newest first**, not "oldest to newest" as documented.

Also worth knowing:

- Requesting a key outside a group's `valueType` list fails the *whole* request
  with `400 Forbidden keys used`, so keys are always taken from the live list.
- `latitude`/`longitude` are empty for every device; coordinates fall back to
  `[defaults]` in `hives.toml`.
- `air_pressure` is stored in **pascals**, exactly as reported (~100000, not ~1000).
- Multi-hour gaps in the data are genuine device outages — verified against the
  API, which returns an empty series for those windows.
