# Layer patterns

## Naming

| layer | pattern | example |
| --- | --- | --- |
| bronze | `<source>_<object>` | `core_banking_transactions` |
| silver | `<entity>` | `transactions`, `accounts`, `customers` |
| gold | `<fact\|dim>_<grain>` | `fact_daily_account_activity` |

## Bronze table shape

```sql
CREATE TABLE IF NOT EXISTS meridian.bronze.core_banking_transactions (
  txn_id            STRING COMMENT 'As received; not validated here.',
  account_id        STRING COMMENT 'As received.',
  amount            STRING COMMENT 'STRING on purpose — typed in silver.',
  `timestamp`       STRING COMMENT 'STRING on purpose — parsed in silver.',
  _run_id           STRING    COMMENT 'FK to meridian.ops.load_run.',
  _source_file      STRING    COMMENT 'Volume path this row came from.',
  _ingested_at      TIMESTAMP COMMENT 'UTC landing time.'
)
COMMENT 'Raw core banking export. Append only, never modified.';
```

## Schema drift

Read the source with a permissive reader, then select the columns the
bronze table declares. New source columns are ignored by bronze and
reported as a `warn` in `dq_result`. Missing source columns land as NULL
and are reported as a `warn`. Neither stops the load.

A `warn` that nobody reads is still better than a 2am failure that stops
tomorrow's data arriving.

## Silver cast pattern

Cast into a nullable column, then count the nulls that were not null in
bronze. That count is the `dq_result` row. Never let a cast throw —
a single malformed row must not discard the other 400,000.

## Idempotency

Every silver and gold write is a MERGE on the natural key. Re-running
yesterday's load must produce the same table, not duplicates. Test this
explicitly: run the load twice in a test and assert the row count is
unchanged.
