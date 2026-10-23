# Decisions

Short records of choices that would otherwise be invisible later.

## 1. Azure + Databricks over GCP
GCP was chosen first for BigQuery's no-credit-card sandbox — a
convenience argument, not a market one. An analysis of 22,000 data
engineering job ads shows two dominant stacks: Spark+Databricks+Azure
and Spark+Snowflake+dbt+AWS. GCP appears in neither. Databricks also
matches existing PySpark experience.

Cost: roughly two hours of Terraform rewritten. Concepts transferred
unchanged — buckets→volumes, service accounts→service principals,
IAM→RBAC, raw/staging/marts→bronze/silver/gold.

## 2. Unity Catalog volume as the landing zone, not ADLS Gen2
Free Edition supports external locations, so ADLS was possible. It was
deferred because it requires a service principal, RBAC assignment,
storage credential and external location — an hour of plumbing before
any data moves.

Planned as a later migration instead. Moving a landing zone from
managed storage to customer-managed storage is what teams actually do
when they outgrow a default, and doing it as a migration demonstrates
more than doing it on day one.

## 3. Lakeflow Declarative Pipelines, not dbt (yet)
dbt is the stronger résumé keyword but belongs to the Snowflake path.
Lakeflow is native, included in Free Edition, and one tool fewer while
learning the platform.

dbt-databricks is planned as a later migration. 

## 4. Databricks Jobs, not Azure Data Factory
ADF bills per pipeline run and adds nothing this project needs.
Databricks Jobs is included.

## 5. Retail banking over healthcare
Finance was chosen for domain leverage: a year of transactional,
marketing and risk data at a national bank. Synthetic data is credible
because the patterns come from having seen real exports. 

## 6. Bronze is all STRING
Typing happens in silver. A source that gains, loses or retypes a
column can never break a bronze load — the failure surfaces in silver
where it can be reasoned about, instead of killing ingestion.
## 7. Claude Code setup: rules path-scoped, patterns in skills
CLAUDE.md is loaded in full at the start of every session, so everything
in it is paid for on every message whether or not it is relevant. The
docs put the target at under 200 lines.

So the split is by *when the content matters*:

- **CLAUDE.md** — true in every session: what the project is, what
  exists, commands, how to work. ~75 lines.
- **`.claude/rules/*.md`** — `verification.md` loads always; the rest
  carry `paths:` frontmatter and load only when a matching file is
  touched. Python conventions cost nothing while writing SQL.
- **`.claude/skills/*/SKILL.md`** — loaded only when relevant to the
  prompt. Detail goes in `reference/`, loaded only when the skill is.
- **`.claude/hooks/*.py`** — rules are context, not enforcement. The
  destructive-command guard is a PreToolUse hook because "never run
  DROP" in CLAUDE.md is a wish, not a control.

Written in Python rather than bash: this is a Windows machine, and shell
hooks fall back to PowerShell when Git Bash isn't found. Python is
already a hard dependency of the project.
