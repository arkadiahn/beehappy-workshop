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
