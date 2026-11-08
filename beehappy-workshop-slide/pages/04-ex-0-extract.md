---
layout: center
class: bh-section
---

# Exercise 0 · Extract

Pull once. Save. Work from your copy.

<div class="mt-8 bh-small">
<code>pd.DataFrame</code> · <code>to_parquet</code> · <code>read_parquet</code>
</div>

---

# Connecting to the database

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```python
import os, psycopg
from dotenv import load_dotenv

load_dotenv(REPO / ".env")
DATABASE_URL = os.environ["DATABASE_URL"]

with psycopg.connect(DATABASE_URL,
                     connect_timeout=30) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM beehives")
        rows = cur.fetchall()
        cols = [c.name for c in cur.description]
```

</div>
<div>

<span class="bh-small" v-click="1">`load_dotenv` reads `.env` into the environment.</span>

<span class="bh-small" v-click="2">`psycopg.connect` opens the connection. `with` closes it for you, even if a cell raises.</span>

<span class="bh-small" v-click="3">`cur.execute` sends the SQL, `cur.fetchall` pulls the rows back as a list of tuples, and `cur.description` carries the column names.</span>

<div v-click="4" class="mt-4">

```sql
SELECT *       -- which columns: all
FROM data      -- which table
WHERE ts >= now() - INTERVAL '3 months'
               -- which rows: the last 3 months
```

<span class="bh-small">Filter in SQL, so only three months cross the network.</span>

</div>

</div>
</div>

<!--
Wait until everyone's first cell prints the database URL before moving on. Nobody gets further
without a working connection.

Today's role is the postgres superuser (grafana_ro does not work), and this is the real
database, not a copy. Only run the SELECTs in the notebook.

The .env habit is the point: the password stays out of the notebook and out of git.

SQL in ten seconds: SELECT picks columns, FROM picks the table, WHERE picks rows.

If someone hangs on connect, it is almost always corporate wifi blocking port 45838 —
have them tether to a phone.
-->

---

# Read it back from disk

<JupyterCell n="1" at="2">

<div class="relative">
<div v-click.hide="1">

```python
beehives = pd.read_parquet(...)
sensors  = ...
raw_sensor_readings = ...
```

</div>
<div v-click="1" class="absolute inset-0">

```python
beehives = pd.read_parquet(RAW / "beehives.parquet")
sensors  = pd.read_parquet(RAW / "sensors.parquet")
raw_sensor_readings = pd.read_parquet(RAW / "data.parquet")
```

</div>
</div>

</JupyterCell>

<div v-click="3" class="bh-note mt-4">
<code>data.parquet</code> becomes <code>raw_sensor_readings</code>: the name says it is raw and not yet cleaned. Everything from Exercise 1 on starts from these three dataframes.
</div>

<!--
Ask the room for the three lines before the reveal click. RAW is defined in the setup
cell: workshop/out/raw/. Reading back from Parquet keeps every dtype, so ts is still a
timestamp.
-->

---

# Reading and writing files

<div>

### Why Parquet, not CSV?

| | CSV | Parquet |
|---|---|---|
| dtypes | **lost** | preserved |
| timestamps | become strings | stay timestamps |
| size | large | compressed |
| speed | slow | fast |

<div class="bh-warn mt-4">
Save <code>ts</code> to CSV and read it back and it is a <strong>string</strong>. Then <code>.dt.floor("h")</code> fails in Exercise 4 with an error message that never mentions CSV.
</div>


</div>
