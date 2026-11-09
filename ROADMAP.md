# Roadmap

Six sessions to a complete platform, then the fraud/AML road.

One session = one Claude Code conversation = one commit. If a session
is running long, stop and commit what works. A half-finished session is
a worse starting point than a smaller finished one.

---

## 1. Foundation — **done**

Catalog `meridian`, schemas `bronze`/`silver`/`gold`/`ops`, volume
`meridian.bronze.landing`, tables `ops.load_run` and `ops.dq_result`.

---

## 2. Synthetic data generator — **next**

A CLI that writes realistic dirty core-banking CSVs to `data/`.

- Full fraud-ready transaction schema (see `.claude/rules/transaction-schema.md`)
- Realistic distributions: amounts log-normal, not uniform; weekday and
  business-hour weighting; a few high-volume accounts
- Deliberate dirt: inconsistent date formats, whitespace, missing
  counterparty names, occasional duplicate `txn_id`, one malformed row
  per file. Clean data proves nothing.
- `--seed` makes every run reproducible
- pytest: same seed → identical output; dirt actually appears

**Done when:** `uv run python -m meridian_lakehouse.generate --seed 42
--days 90` writes CSVs you can open, and the tests pass. Nothing touches
Databricks this session.

---

## 3. Bronze ingestion

`conf/sources.yml` + `ingest/base.py` (`discover()` → `fetch()` →
`land()`) + the core banking subclass. Upload to the volume, land into
`meridian.bronze.core_banking_transactions`, all STRING.

Every run opens a `load_run` row before doing work. Re-running the same
day must not duplicate rows.

**Done when:** running it twice leaves the same row count and two rows
in `ops.load_run`.

---

## 4. Silver

Type, deduplicate, conform. Casts that fail become `dq_result` rows, not
exceptions. `severity='error'` leaves silver untouched.

**Done when:** the malformed rows the generator injected are visible in
`ops.dq_result` and absent from silver.

---

## 5. Second source — account master

Azure SQL with an incremental watermark. This is the session that tests
the expandability contract: one YAML entry, one subclass, nothing else
edited. If it needs more, the abstraction was wrong and we fix it here.

Requires an Azure free account and a $5 budget alert first.

---

## 6. Gold + orchestration

Cross-source marts. A Databricks Job running the whole chain on a
schedule. A README section a stranger could follow.

**Done when:** it runs overnight without you.

---

## Then: the fraud/AML road

Not scheduled. Each is a gold layer on data that already exists —
no re-ingestion, which is the whole point of the wide schema.

- **B1** Structuring detection — amounts clustering under reporting limits
- **B2** Velocity and rapid pass-through — in-then-out within a window
- **B3** Sanctions screening — fuzzy match `counterparty_name` to OFAC SDN
- **B4** Case management — alerts, dispositions, SAR-shaped output

Later, once the platform is boring: FRED API as a third source, ADLS
Gen2 migration, dbt migration, OCR on scanned PDF statements.
