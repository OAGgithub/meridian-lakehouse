---
name: medallion-layers
description: Rules for what belongs in the bronze, silver, and gold layers of the meridian lakehouse, and the schema-drift contract between them. Use when creating or modifying any table, transform, or Lakeflow pipeline, or when deciding which layer a piece of logic belongs in.
---

# Medallion layers

## bronze — landed exactly as received

- **Every column STRING.** No exceptions, no "but this one is obviously
  an int". Typing is silver's job.
- Plus load metadata: `_run_id`, `_source_file`, `_ingested_at`.
- **Append only. Never modified.** A bad transform is fixed by re-running
  the transform, not by editing bronze.
- Schema drift must not break a load. A source that gains, loses, or
  retypes a column still lands. The failure surfaces in silver, where it
  can be reasoned about, instead of killing ingestion at 2am.

This is the single most load-bearing rule in the project. If you are
about to cast something in bronze, stop.

## silver — typed, deduplicated, conformed

- One model per source. No cross-source joins here.
- Cast explicitly; a failed cast is a `dq_result` row, not an exception.
- Deduplicate on the natural key, keeping the latest by source timestamp.
- Conform keys across sources to the same format and type.
- SCD2 where history matters (account master), SCD1 where it does not.

## gold — business marts

- The only layer anything outside the pipeline queries.
- Cross-source joins live here.
- Fraud and AML detection will be gold tables. They read silver; they
  never read bronze and never write back down.

## Direction

Data moves bronze → silver → gold and never the other way. A gold table
that writes to silver, or a silver model that reads gold, is a bug
regardless of how convenient it is.

Worked table definitions: `reference/patterns.md`.
