# meridian-lakehouse

A retail bank data platform. Portfolio project held to production
standards — the code is the deliverable.

## What it does

Ingests three sources into a Databricks lakehouse, models them through
bronze → silver → gold, runs on a schedule, and reports on its own health.

1. Core banking export — daily CSV into a Unity Catalog volume
2. Customer/account master — Azure SQL, incremental watermark  *(later)*
3. FRED API — Federal Reserve economic data                    *(later)*

## Platform

Databricks Free Edition, serverless. Unity Catalog. PySpark + SQL.
Lakeflow Declarative Pipelines for transforms. Databricks Jobs for
orchestration. Python managed with uv. No dbt yet — see DECISIONS.md.

## What already exists

- Catalog `meridian`, schemas `bronze` `silver` `gold` `ops`
- Volume `meridian.bronze.landing` → `/Volumes/meridian/bronze/landing/`
- Tables `ops.load_run`, `ops.dq_result`, with smoke-test rows

Nothing else. No extractors, no bronze tables, no pipelines yet.
The Status table in README.md is the current truth — read that, not the
repo, when you need to know what is built.

## Commands

```bash
uv sync                  # install
uv run pytest            # tests
uv run ruff check --fix  # lint
```

## Architecture rules live in skills

- `medallion-layers` — what belongs in bronze/silver/gold, schema drift
- `ops-logging` — the `load_run` / `dq_result` contract

Read the relevant skill before writing pipeline code. Do not restate
their contents here; this file stays short on purpose.

## Expandability contract

Adding a fourth source must not require editing existing code.

- `conf/sources.yml` declares every source: name, type, schedule,
  landing path, bronze table
- `ingest/base.py` defines the contract: `discover()` → `fetch()` → `land()`
- A new source = one YAML entry + one subclass

If a change would require editing more than those two things, the
abstraction is wrong. Say so instead of working around it.

## Conventions

- `uv run` for everything. Never invoke pip.
- Conventional commits: `feat:` `fix:` `chore:` `docs:` `test:`
- No secrets in code or committed files. `.env` only.
- **Definition of done:** implementation + a test + rows written to `ops`
  + a README line if the run instructions changed.

## How to work with me

- Build in numbered steps and STOP after each for review.
- Never run DROP, DELETE, or anything destructive. A hook blocks these;
  if you hit it, show me the statement instead of working around it.
- I am learning this stack. Explain non-obvious choices in one or two
  sentences as you make them — not a tutorial, just the reasoning.
- If a decision isn't covered here, ask rather than assume, then propose
  adding it to DECISIONS.md.
