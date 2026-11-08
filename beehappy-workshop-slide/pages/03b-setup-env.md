# Get, set, go.

<div class="grid gap-6 mt-2" style="grid-template-columns: 7fr 5fr">
<div>

**1 · Install uv** if you have not yet

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2 · Create `.env`** in the repo root, then replace `password` with the one we sent on Slack

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows
```

**3 · Open the notebook** from the repo root

```bash
uv run jupyter notebook workshop/notebooks/workshop.ipynb
```

**4 · Run the first cell.** It prints your database URL.

</div>
<div>

<div class="bh-out-label">.env</div>
<pre class="bh-out" style="white-space: pre-wrap; word-break: break-all">DATABASE_URL=postgresql://postgres:<strong>password</strong>@crossover.proxy.rlwy.net:45838/railway</pre>

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

After installing uv, students may need to open a new terminal so `uv` is on their PATH.
The first `uv run` creates the environment and installs everything, so it takes a minute.

Only the word `password` changes: keep the rest of the URL as it is.
-->
