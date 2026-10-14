# ops-console

A data platform for a multi-store retail chain. Portfolio project,
held to production standards — the code is the deliverable.

## What it does
Ingests three kinds of source into BigQuery, models them with dbt,
and runs the whole thing on a schedule in Airflow.

Sources:
1. Daily inventory export  — messy CSV dropped to GCS
2. Ops app database        — incremental pull from Postgres
3. Stripe (test mode)      — paginated REST API

## Architecture
GCS landing zone -> BigQuery raw -> dbt -> BigQuery marts

BigQuery datasets:
- `raw_*`     — landed source data, all columns STRING, never modified
- `staging_*` — dbt: typed, renamed, deduplicated (views)
- `marts`     — dbt: dims and facts, the only layer anything reads

## Stack
Python 3.12 · uv · BigQuery · GCS · dbt (Fusion) · Airflow (local Docker)
Terraform · Postgres/Neon (app source only) · pytest · ruff · GH Actions

## Rules
- Never mutate raw. Fix the transform and re-run it.
- Extraction is idempotent: re-running the same window produces the
  same rows. Upsert on natural keys; never blind INSERT.
- Every pipeline run writes to `ops.load_run` with counts and status,
  success or failure.
- All modeling happens in dbt, not in Python. Python extracts and
  loads; dbt transforms. Do not blur this.
- Every dbt model has tests. At minimum not_null and unique on the
  key. Freshness checks on every source.
- A failed critical test fails the DAG. A silent bad load is the worst
  outcome in this codebase.
- All BigQuery infrastructure is declared in Terraform.
- Type hints on every function. No secrets in code or committed files.

## Cost discipline
The sandbox gives 1 TiB of query processing a month. Partition fact
tables on date, cluster on store. Never `SELECT *` in a model. Treat
cost as a design constraint and note the reasoning in the model's
description — this is half of what the job is.

## Conventions
- `uv run` for everything; never invoke pip.
- Line length 100, ruff defaults.
- Conventional commits (`feat:`, `fix:`, `chore:`).

## Definition of done
Terraform change if infra moved + implementation + dbt tests +
pytest + a README line if the run instructions changed.

## Current state
Session 0 complete. GCP project, bucket, service account, and ADC all
working; smoke test passes. No BigQuery datasets exist yet. Next:
Terraform to create them.