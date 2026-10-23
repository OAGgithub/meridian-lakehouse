---
paths:
  - "**/*.sql"
  - "notebooks/**"
---

# SQL on Databricks

- Three-level names always: `meridian.bronze.transactions`, never a bare
  table name that depends on the session's current catalog.
- Keywords uppercase, identifiers lowercase_snake.
- Every CREATE carries a COMMENT on the table and on every column. The
  catalog is documentation that cannot go stale.
- `CREATE TABLE IF NOT EXISTS` — scripts must be re-runnable.
- MERGE on the natural key, never blind INSERT, anywhere re-running the
  same window is possible.
- All timestamps stored UTC, typed `TIMESTAMP`, named `*_at` or `*_ts`.
- No `SELECT *` outside ad-hoc exploration.
