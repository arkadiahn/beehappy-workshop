# Container for the Railway cron service.
#
# Only the ETL dependencies are installed -- the `analysis` extra (jupyter,
# pandas, matplotlib, seaborn) is for the notebook and would roughly quadruple
# the image for no benefit here.

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependency layer first: rebuilt only when the lockfile changes, so ordinary
# code edits redeploy in seconds.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Application code. hives.toml and data_schema.sql are runtime inputs, not
# just docs -- the container reads both on every run.
COPY bees/ ./bees/
COPY main.py data_schema.sql hives.toml ./

ENV PATH="/app/.venv/bin:$PATH"

# --init-schema is idempotent (CREATE TABLE IF NOT EXISTS), so a fresh Railway
# database bootstraps itself on the first scheduled run.
CMD ["python", "main.py", "--init-schema"]
