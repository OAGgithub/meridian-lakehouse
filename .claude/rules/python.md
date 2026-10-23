---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Python

- `uv run` for everything. Never invoke `pip` or activate the venv by hand.
- Type hints on every function signature, including `-> None`.
- Line length 100. `uv run ruff check --fix` before claiming done.
- Pure functions where possible: a function that both computes and writes
  is two functions.
- No bare `except:`. Catch the specific error or let it crash — a pipeline
  that swallows an error is worse than one that stops.
- Paths with `pathlib`, never string concatenation.
- Randomness in generators must take an explicit seed. Determinism is the
  whole reason the generator is testable.
