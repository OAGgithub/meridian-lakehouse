---
description: Orient at the start of a work session without reading the whole repo
---

Do exactly this, nothing more:

1. `git log --oneline -5` and `git status --short`
2. Read the Status table in README.md

Then tell me in three lines: what the last commit did, what is unfinished,
and what the next single task should be.

Do not read source files, do not explore the repo, do not propose a plan
beyond the next one task. I will tell you which task to start.
