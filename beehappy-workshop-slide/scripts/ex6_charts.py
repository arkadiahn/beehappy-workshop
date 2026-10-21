"""Render the Ex 6 slide charts by running the solution notebook's own plotting cells.

Each code cell under "## Exercise 6" in solutions.ipynb that draws a figure becomes
one PNG, so the slides always show exactly what the solution produces.

Run from the repo root after a fresh extract + solution run (it reads
workshop/out/features_hourly.parquet):
    uv run python beehappy-workshop-slide/scripts/ex6_charts.py
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

NOTEBOOK = "workshop/notebooks/solutions.ipynb"
OUT = "beehappy-workshop-slide/public/charts"
NAMES = ["ex6-1-plt-plot", "ex6-2-window", "ex6-3-df-plot", "ex6-4-sns-hue", "ex6-5-subplots"]

cells = json.load(open(NOTEBOOK, encoding="utf-8"))["cells"]
start = next(i for i, c in enumerate(cells)
             if c["cell_type"] == "markdown" and "".join(c["source"]).startswith("## Exercise 6"))
code = ["".join(c["source"]) for c in cells[start:] if c["cell_type"] == "code"]

scope = {"pd": pd, "features": pd.read_parquet("workshop/out/features_hourly.parquet")}
names = iter(NAMES)
for src in code:
    exec(src, scope)
    if plt.get_fignums():  # the cell drew something
        name = next(names)
        plt.gcf().savefig(f"{OUT}/{name}.png", dpi=110, bbox_inches="tight", facecolor="white")
        plt.close("all")
        print("wrote", name)
