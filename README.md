# meridian-lakehouse

A retail bank data platform built on Databricks. Portfolio project held to
production standards: every load is logged, every transform is tested, and
the transaction schema is wide enough to support fraud and AML detection
without re-ingesting anything.

## Architecture

```
sources            bronze              silver            gold
---------------    ----------------    --------------    ----------------
core banking CSV   as received,        typed, deduped,   business marts
account master     all STRING,         conformed keys    (fraud/AML later)
FRED API           append-only
                        |
                        +--> ops.load_run    every run, win or lose
                             ops.dq_result   every quality check
```

Three sources land in a Unity Catalog volume, move through bronze → silver →
gold, run on a Databricks Job, and report on their own health in `ops`.

## Platform

Databricks Free Edition (serverless) · Unity Catalog · PySpark + SQL ·
Lakeflow Declarative Pipelines · Databricks Jobs · Python 3.12 via `uv`.

Decisions and the reasoning behind them: [DECISIONS.md](DECISIONS.md).
Working agreements for AI-assisted development: [CLAUDE.md](CLAUDE.md).

## Status

| Piece | State |
| --- | --- |
| Catalog `meridian`, schemas `bronze`/`silver`/`gold`/`ops` | done |
| Volume `meridian.bronze.landing` | done |
| `ops.load_run`, `ops.dq_result` | done |
| Synthetic source data generator | in progress |
| Bronze ingestion | not started |
| Silver models | not started |
| Gold marts | not started |

## Running it

```bash
uv sync
uv run pytest
uv run python -m meridian_lakehouse.generate --seed 42 --days 90
```

Secrets live in `.env` (never committed). See `.env.example` for the keys.
