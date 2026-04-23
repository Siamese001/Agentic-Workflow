#!/usr/bin/env python3
"""
pre_run_gate.py — Windsurf pre_run_command hard gate (Phase 1.1).

Reads JSON payload from stdin. Blocks (exit 2) on:
  - PowerShell commands (powershell, pwsh — case-insensitive, any path prefix, .exe suffix)
  - Full test-suite run during ADG repair (ADG_REPAIR_ACTIVE env var)

SSOT for PowerShell ban enforcement (2026-04-08):
  Pre-commit T7.8 file scanner (check_powershell_ban.py) was archived because
  retroactive file scanning caused 7,244 false positives. This hook is the
  single enforcement point — blocks Cascade from running pwsh/powershell at
  execution time, which is where the actual hang risk exists.

Fail policy: CLOSED — malformed/missing JSON → exit 2 with diagnostic.
Zero hardcoded paths.
"""

import json
import os
import re
import sys

fail_policy = "closed"

powershell_patterns = ("powershell", "pwsh")

# Matches pytest invocations that run the full unit test suite.
# Handles: trailing slash, Windows backslash, optional trailing args.
_FULL_SUITE_RE = re.compile(r"pytest\s+tests[/\\]unit[/\\]?(\s|$)")

# Script paths that are allowed to reference "powershell" in their name
# because they are *about* PowerShell (checkers, RCA docs, etc.)
_allowed_script_suffixes = (
    "check_powershell_ban.py",
    "pre_run_gate.py",
)

# Match powershell/pwsh as the leading executable in a command line.
# Handles: bare name, .exe suffix, Unix paths (/usr/bin/pwsh),
# Windows paths with or without spaces (C:/Program Files/PowerShell/7/pwsh.exe).
# The pattern anchors to start of string and allows an optional path prefix
# containing any chars except spaces — OR a quoted path.
_POWERSHELL_EXEC_RE = re.compile(
    r"""
    (?:^|(?<=\s))           # start of string or preceded by whitespace
    (?:
        "(?:[^"]*[/\\])?    # optional quoted path prefix
        (powershell|pwsh)   # executable name (group 1)
        (?:\.exe)?          # optional .exe
        "                   # closing quote
      |
        (?:[^\s]*[/\\])?    # optional unquoted path prefix (no spaces)
        (powershell|pwsh)   # executable name (group 2)
        (?:\.exe)?          # optional .exe
    )
    (?:\s|$)                # followed by space or end-of-string
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _exit_block(reason: str) -> int:
    print(f"[pre_run_gate] BLOCKED: {reason}", file=sys.stderr)
    return 2


def check_command(command_line: str) -> int:
    """Return 0 (allow) or 2 (block). command_line must be a non-empty string."""
    lower = command_line.lower()

    # Always check for powershell/pwsh as the leading executor first.
    # The allowlist exempts scripts whose *path* contains a known suffix
    # (e.g. check_powershell_ban.py) but ONLY when powershell is not the
    # executor itself — "powershell check_powershell_ban.py" must still block.
    if _POWERSHELL_EXEC_RE.search(command_line):
        leading_token = lower.lstrip().split()[0] if lower.strip() else ""
        is_allowed_script = any(
            lower.endswith(s) or ("/" + s) in lower or ("\\" + s) in lower for s in _allowed_script_suffixes
        )
        # Exempt only when the leading token is NOT powershell/pwsh itself,
        # i.e. a python invocation of a checker that mentions powershell by name.
        if is_allowed_script and not any(pat in leading_token for pat in powershell_patterns):
            pass  # allowed: python script whose path references powershell
        else:
            matched = next(pat for pat in powershell_patterns if pat in command_line.lower())
            return _exit_block(
                f"PowerShell is forbidden (matched '{matched}'). "
                "Use argv list with shell=False per constitutional §0.",
            )

    if _FULL_SUITE_RE.search(command_line) and os.environ.get("ADG_REPAIR_ACTIVE"):
        return _exit_block(
            "Full test-suite run blocked during ADG repair (ADG_REPAIR_ACTIVE is set). "
            "Run scoped cluster tests only per constitutional ADG repair discipline.",
        )

    return 0


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
    raw = sys.stdin.read()
    if not raw.strip():
        if fail_policy == "closed":
            print("[pre_run_gate] BLOCKED: empty stdin payload.", file=sys.stderr)
            return 2
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        if fail_policy == "closed":
            print(f"[pre_run_gate] BLOCKED: malformed JSON payload — {exc}", file=sys.stderr)
            return 2
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return 0

    command_line = tool_info.get("command_line", "")

    # Only process string command lines — non-string types are ignored (fail-open)
    if not isinstance(command_line, str) or not command_line:
        return 0

    return check_command(command_line)


if __name__ == "__main__":
    sys.exit(main())
