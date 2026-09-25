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

<span class="bh-small">

`load_dotenv` reads `.env` into the environment — the connection string stays out of your notebook.

`psycopg.connect` opens the connection. `with` closes it for you, even if a cell raises.

`cur.execute` sends the SQL, `cur.fetchall` pulls the rows back as a list of tuples, and `cur.description` carries the column names.

</span>

<div class="bh-warn mt-3">
Copy <code>.env.example</code> to <code>.env</code> — connection strings belong in <code>.env</code>, never in a committed notebook. Keep <code>sslmode=require</code>: this is the <strong>production</strong> database, over the public internet.
</div>

</div>
</div>

<!--
Wait until everyone's cell 1 prints the host before moving on. Nobody gets further
without a working connection.

Why the read-only role (grafana_ro): the superuser can DROP the live tables, and this is
the real database, not a copy.

The .env habit is the point even though today's URL is not a secret — the next one will be.

If someone hangs on connect, it is almost always corporate wifi blocking port 45838 —
have them tether to a phone.
-->

---

# The SQL you need today

<div class="grid grid-cols-2 gap-6 mt-3">
<div>

```sql
SELECT * FROM beehives
```

<span class="bh-small">

`SELECT` — which columns you want. `*` means **all of them**.

`FROM beehives` — which table to read.

That is the whole statement: *give me every column of every row in `beehives`*.

</span>

<div class="bh-note mt-3">
Fine for <code>beehives</code> and <code>sensors</code> — three and nine rows. Not fine for <code>data</code>.
</div>

</div>
<div>

```sql
SELECT * FROM data
WHERE ts >= (now() AT TIME ZONE 'UTC')
            - INTERVAL '3 months'
```

<span class="bh-small">

`WHERE` keeps only the rows matching a condition — here, the last three months.

`data` is millions of rows. The filter belongs **in SQL**, so the rest never crosses the network.

</span>

<div class="bh-warn mt-3">
<code>ts</code> is <code>timestamp without time zone</code> holding UTC — so compare against UTC, not the server's local clock.
</div>

</div>
</div>

<!--
Three queries in total, one per table — a dict of {name: sql} that you loop over.

If someone asks "why not SELECT the columns by name": you can, and in production you
should. Today `*` is honest — part of the exercise is discovering what is in there.
-->

---

# Reading and writing files

<div class="grid grid-cols-2 gap-6 mt-3">

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

<div>

```python
frames[name] = pd.DataFrame(
    cur.fetchall(),
    columns=[c.name for c in cur.description],
)
frames[name].to_parquet(
    RAW / f"{name}.parquet", index=False)

data = pd.read_parquet(RAW / "data.parquet")
```

<div class="bh-note mt-4">
<code>index=False</code> on write: your row index is usually just 0,1,2… — do not save it as a column.
</div>

</div>

</div>
