---
description: Scaffold a new data source end to end
argument-hint: <source_name> <file|jdbc|api>
---

Add a new source named `$1` of type `$2` to the pipeline.

Read the `medallion-layers` and `ops-logging` skills first.

The expandability contract says a new source is **one YAML entry and one
subclass**. Work in these numbered steps and STOP after each:

1. Add the `$1` entry to `conf/sources.yml`: name, type, schedule,
   landing path, bronze table. Show me the entry.
2. Create the extractor subclass implementing `discover() → fetch() →
   land()`. Show me the file before writing it.
3. Create the bronze table DDL — all STRING plus load metadata.
4. Add a test that running the same window twice produces the same row
   count.

If any step requires editing code outside `conf/sources.yml` and the new
subclass, stop and tell me. That means the abstraction is wrong, and
working around it is worse than fixing it.
