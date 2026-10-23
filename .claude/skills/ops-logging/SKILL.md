---
name: ops-logging
description: How to write run history and data-quality results to meridian.ops.load_run and meridian.ops.dq_result. Use whenever writing, reviewing, or debugging any extractor, ingestion job, transform, or data-quality check — every piece of pipeline code in this project must log through these two tables.
---

# Pipeline observability

Two tables carry every claim this project makes about itself. If a run
is not in `ops.load_run`, it did not happen. If a check is not in
`ops.dq_result`, it was not checked.

## The non-negotiable order

1. **Before any work**, INSERT a row into `ops.load_run` with
   `status='running'`, `started_at` set, `finished_at` NULL.
2. Do the work.
3. UPDATE that row: `status`, `finished_at`, row counts, and
   `error_message` if it failed.

A crashed run must leave evidence. A row stuck at `'running'` with an old
`started_at` is a *successful* detection of a crash, not a bug.

Never write the `load_run` row at the end. Never write it only on success.

## Status values

`running` → `succeeded` | `failed` | `partial`

`partial` means rows landed but `rows_rejected > 0`. It is not a failure
and must not be reported as one.

## Data quality

Every check writes to `ops.dq_result`, pass or fail. A check that only
records failures cannot distinguish "clean" from "never ran".

- `severity='error'` → fail the run, leave the target layer untouched
- `severity='warn'` → record it, continue

A silent bad load is the worst possible outcome in this codebase.

## Source-agnostic

No column in `ops` may name a specific source. Source identity lives in
the `source_name` **value**, never in a column name. Adding a fourth
source must not alter the ops schema.

Full column list and worked examples: `reference/schema.md`.
