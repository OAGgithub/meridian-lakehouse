"""Flag credentials written into a file.

Wired as a PostToolUse hook on Edit|Write. The write has already happened,
so this reports rather than prevents: it blocks the turn and tells Claude
to remove the value and move it to .env.
"""

import json
import re
import sys
from pathlib import Path

SECRETS: list[tuple[str, str]] = [
    (r"\bdapi[0-9a-f]{32}\b", "Databricks personal access token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "private key"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "GitHub token"),
    (r"\bsk-[A-Za-z0-9]{32,}\b", "API secret key"),
    (r"(?i)\b(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
     "hardcoded credential"),
]

ALLOWED = {".env.example"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    raw_path = (payload.get("tool_input") or {}).get("file_path")
    if not raw_path:
        return 0

    path = Path(raw_path)
    if path.name in ALLOWED:
        return 0

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0

    for pattern, label in SECRETS:
        match = re.search(pattern, text)
        if match:
            line = text[: match.start()].count("\n") + 1
            print(
                f"Possible {label} written to {path.name} line {line}. "
                "Remove the literal value, read it from os.environ instead, "
                "and add the key to .env.example with an empty value.",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
