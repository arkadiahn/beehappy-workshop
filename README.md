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

**The service must be connected to a GitHub repo, not uploaded with `railway
up`.** A CLI upload is a one-off snapshot: Railway reports `canRedeploy: false`
on it and the cron scheduler has nothing to re-run, so the job builds, runs
once, and then never fires again. This is silent — the deployment still says
SUCCESS. Connect the repo instead:

In the project: **New → GitHub Repo**, pick the repo and branch. On the
service's **Variables** tab add:

| Variable | Value |
|---|---|
| `BILDUNGSCAMPUS_API_KEY` | your key |
| `DATABASE_URL` | `${{beehive-db.DATABASE_URL}}` |

That `${{beehive-db.DATABASE_URL}}` is a Railway *reference variable*, not a
literal — it resolves to the private-network address, so traffic never leaves
Railway and costs no egress. Substitute your Postgres service's name.

`railway.json` sets the Dockerfile build, the hourly schedule and
`restartPolicyType: NEVER` (without that last one Railway restarts the finished
job in a loop). Note it is **only read on GitHub-sourced deploys** — a `railway
up` upload ignores it, in which case set the schedule and restart policy on the
service directly:

```bash
railway api "mutation { serviceInstanceUpdate(
  serviceId: \"<id>\", environmentId: \"<id>\",
  input: { cronSchedule: \"17 * * * *\", restartPolicyType: NEVER }) }"
```

The first run backfills 90 days and then exits; later runs take seconds. Change
the cadence via `cronSchedule` (readings arrive every ~20 min, so hourly loses
nothing). Railway skips a scheduled run if the previous one is still going.

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

## Dashboard (Metabase)

`metabase/queries.sql` holds one SQL block per dashboard card, each verified
against the live database. `metabase/00_readonly_role.sql` creates the
`metabase_ro` role — Metabase only needs `SELECT`, and this dashboard is shown
to students, so it should not connect as the superuser.

Connect Metabase over the **private network** (no egress, database stays off the
public internet for this path):

| Field | Value |
|---|---|
| Host | `postgres-nnqo.railway.internal` |
| Port | `5432` · Database `railway` · User `metabase_ro` |

Two conventions the cards depend on:

- **Fixed hive colors.** Set each hive's hue once in Metabase's series settings.
  A filter that hides one hive must not repaint the others. Outside/ambient is
  always neutral gray — it is context, not a fourth hive.
- **No dual-axis charts.** Temperature and humidity are deliberately separate
  cards. Two y-scales on one plot makes both unreadable.

### What the experiment cards measure

The project is comparing three cover materials for microclimate stability, so
the dashboard reports three things, not one:

| Card | Measure | Reading |
|---|---|---|
| Stability | `stddev_samp(temperature)` | how much the hive wanders |
| Accuracy | `avg(abs(temperature - 35))` | how far it sits from the ideal |
| Buffering | `regr_slope(hive_c, outside_c)` | °C the hive moves per 1 °C outside |

Stability alone is not enough — **a hive can be perfectly stable at the wrong
temperature**, and the current data contains exactly that case, so ranking on
standard deviation alone picks the wrong material.

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
