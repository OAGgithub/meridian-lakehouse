"""Block destructive shell/SQL commands before they run.

Wired as a PreToolUse hook on Bash in .claude/settings.json.
Exit 0 with no output = allow. Deny is expressed as JSON on stdout.

If this ever blocks something you legitimately need, run the command
yourself in a terminal rather than loosening the pattern list.
"""

import json
import re
import sys

# (pattern, why) — matched case-insensitively against the whole command
PATTERNS: list[tuple[str, str]] = [
    (r"\bdrop\s+(table|schema|catalog|volume|view|database)\b",
     "DROP would destroy a Unity Catalog object"),
    (r"\btruncate\s+table\b",
     "TRUNCATE would empty a table"),
    (r"\bdelete\s+from\b",
     "DELETE FROM mutates data; bronze is append-only and silver is rebuilt, not edited"),
    (r"\bvacuum\b.*\bretain\s+0\b",
     "VACUUM RETAIN 0 destroys Delta time-travel history"),
    (r"\brm\s+-[a-z]*[rf]",
     "recursive/forced delete"),
    (r"\bgit\s+push\b.*(--force|-f)\b",
     "force push rewrites published history"),
    (r"\bgit\s+reset\s+--hard\b",
     "git reset --hard discards uncommitted work"),
    (r"\bgit\s+clean\s+-[a-z]*f",
     "git clean -f deletes untracked files"),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # nothing to inspect; don't get in the way

    command = (payload.get("tool_input") or {}).get("command", "")
    if not command:
        return 0

    for pattern, why in PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            json.dump(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f"Blocked by guard_destructive.py: {why}. "
                            "Show me the statement and explain what it would "
                            "affect; I will run it myself if it is right."
                        ),
                    }
                },
                sys.stdout,
            )
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
