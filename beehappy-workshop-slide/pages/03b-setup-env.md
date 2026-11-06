# Get, set, go.

<div class="grid grid-cols-2 gap-6 mt-6">
<div>

**1 · Copy the template** in the repo root

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows
```

**2 · Open `.env`** and check `DATABASE_URL` is filled in. Still says `PASSWORD`? Ask us.

**3 · Notebook already open?** Re-run its first cell.

</div>
<div>

<div class="bh-out-label">.env</div>
<pre class="bh-out">DATABASE_URL=postgresql://user:password@host:port/railway</pre>

<div v-click class="mt-6">

**Two kinds of cells** in the notebook

```python
# EXECUTE: working code, just run it
sensors
```

```python
# TODO: your turn, replace the ...
raw_sensor_readings = ...
```

</div>

</div>
</div>

<!--
Do this together, before anyone opens Exercise 0. Walk the room: the usual
failures are a file saved as `.env.txt` (Windows hides extensions) or `.env`
created in workshop/notebooks/ instead of the repo root.
-->
