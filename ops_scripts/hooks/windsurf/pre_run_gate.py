#!/usr/bin/env python3
"""
pre_run_gate.py — Windsurf pre_run_command hard gate (Phase 1.1).

Reads JSON payload from stdin. Blocks (exit 2) on:
  - PowerShell commands (powershell, pwsh — case-insensitive)
  - Full test-suite run during ADG repair (ADG_REPAIR_ACTIVE env var)

Fail policy: CLOSED — malformed/missing JSON → exit 2 with diagnostic.
Zero hardcoded paths.
"""

import json
import os
import re
import sys

FAIL_POLICY = "closed"

POWERSHELL_PATTERNS = ("powershell", "pwsh")
_FULL_SUITE_RE = re.compile(r"pytest\s+tests/unit(\s|$)")

# Script paths that are allowed to reference "powershell" in their name
# because they are *about* PowerShell (checkers, RCA docs, etc.)
_ALLOWED_SCRIPT_SUFFIXES = (
    "check_powershell_ban.py",
    "pre_run_gate.py",
)


def _exit_block(reason: str) -> int:
    print(f"[pre_run_gate] BLOCKED: {reason}", file=sys.stderr)
    return 2


def check_command(command_line: str) -> int:
    """Return 0 (allow) or 2 (block)."""
    lower = command_line.lower()

    # Allow commands that are invoking the powershell-ban checker itself
    # or this gate — they reference "powershell" in path, not as execution target
    if any(lower.endswith(s) or ("/" + s) in lower or ("\\" + s) in lower
           for s in _ALLOWED_SCRIPT_SUFFIXES):
        pass
    else:
        for pat in POWERSHELL_PATTERNS:
            # Match powershell/pwsh only as the executable (first token) or
            # as an explicit argument value — not inside a file path
            tokens = command_line.split()
            executable = tokens[0].lower() if tokens else ""
            if pat == executable or executable.endswith(pat + ".exe"):
                return _exit_block(
                    "PowerShell is forbidden (matched '{}'). ".format(pat)
                    + "Use subprocess.run(argv, shell=False) per constitutional §0.",
                )

    if _FULL_SUITE_RE.search(command_line) and os.environ.get("ADG_REPAIR_ACTIVE"):
        return _exit_block(
            "Full test-suite run blocked during ADG repair (ADG_REPAIR_ACTIVE is set). "
            + "Run scoped cluster tests only per constitutional ADG repair discipline.",
        )

    return 0


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        if FAIL_POLICY == "closed":
            print("[pre_run_gate] BLOCKED: empty stdin payload.", file=sys.stderr)
            return 2
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        if FAIL_POLICY == "closed":
            print(f"[pre_run_gate] BLOCKED: malformed JSON payload — {exc}", file=sys.stderr)
            return 2
        return 0

    tool_info = payload.get("tool_info", payload)
    command_line = tool_info.get("command_line", "")

    if not command_line:
        return 0

    return check_command(command_line)


if __name__ == "__main__":
    sys.exit(main())
