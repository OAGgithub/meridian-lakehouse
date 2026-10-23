# meridian-lakehouse

A retail bank data platform. Portfolio project held to production
standards — the code is the deliverable.

## What it does
Ingests three kinds of source into a Databricks lakehouse, models them
through bronze → silver → gold, runs on a schedule, and reports on its
own health.

Sources:
1. Core banking export — daily CSV into a Unity Catalog volume
2. Customer/account master — Azure SQL, incremental watermark   (later)
3. FRED API — Federal Reserve economic data                     (later)

## Platform
Databricks Free Edition, serverless compute. Unity Catalog.
PySpark + SQL. Lakeflow Declarative Pipelines for transforms.
Databricks Jobs for orchestration. Python 3.12 managed with uv.
No dbt yet — deliberate, see DECISIONS.md.

## What already exists
- Catalog `meridian`, schemas `bronze` `silver` `gold` `ops`
- Volume `meridian.bronze.landing`
  → path /Volumes/meridian/bronze/landing/
- Tables `ops.load_run` and `ops.dq_result`, with smoke-test rows

Nothing else. No extractors, no bronze tables, no pipelines yet.

## Layer rules
- bronze — landed exactly as received. Every column STRING, plus load
  metadata. Append only. NEVER modified: a bad transform is fixed by
  re-running the transform, not by editing bronze.
- silver — typed, deduplicated, conformed keys. One model per source.
- gold — business marts, cross-source. The only layer anything outside
  the pipeline queries.
- ops — run history and data quality. Source-agnostic: no column in
  ops may name a specific source.

## Pipeline rules
- Every run INSERTs into ops.load_run with status='running' BEFORE
  doing any work, then UPDATEs it at the end. A crashed run must leave
  evidence.
- Extraction is idempotent: re-running the same window produces the
  same rows. Upsert on natural keys, never blind INSERT.
- Every data-quality check writes to ops.dq_result.
  severity='error' fails the run and leaves silver untouched.
  severity='warn' is recorded and the run continues.
- A silent bad load is the worst possible outcome in this codebase.
- All timestamps are UTC.

## The transaction schema is fraud-ready — do not trim it
Transactions always carry: txn_id, account_id, counterparty_id,
counterparty_name, amount, currency, timestamp (tz-aware), channel,
direction, merchant_category, country, branch_id, device_id,
ip_address.

These exist so fraud and AML detection can be added as a gold layer
later without regenerating or re-ingesting anything. Never drop one
to simplify.

## Expandability contract
Adding a fourth source must not require editing existing code.
- conf/sources.yml declares every source: name, type, schedule,
  landing path, bronze table
- ingest/base.py defines the contract: discover() → fetch() → land()
- A new source = one YAML entry + one subclass

If a change would require editing more than those two things, the
abstraction is wrong. Say so instead of working around it.

## Conventions
- `uv run` for everything. Never invoke pip.
- Type hints on every function. Line length 100, ruff defaults.
- Conventional commits: feat:, fix:, chore:, docs:, test:
- No secrets in code or in committed files.

## Definition of done
Implementation + a test + rows written to ops + a README line if the
run instructions changed.

## How to work with me
- Build in numbered steps and STOP after each for review.
- Never run DROP, DELETE, or anything destructive without showing me
  the statement first.
- I am learning this stack. Explain non-obvious choices in one or two
  sentences as you make them — not a tutorial, just the reasoning.
- If a decision isn't covered here, ask rather than assume, then
  propose adding it to this file.