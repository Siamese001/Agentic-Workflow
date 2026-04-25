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
# Interactive / stdin-blocking commands that hang Cascade's turn forever.
# Cascade's terminal cannot send keystrokes, so any command that waits for
# keyboard input (pagers, editors, watchers, REPLs) blocks indefinitely.
# Constitutional §14 (`subprocess.run` timeout=) covers Python invocations,
# but the shell pipeline itself is the blocking entity here — a Python-level
# timeout cannot save the turn. This gate closes that gap at exec time.
#
# Categories blocked:
#   1) Pipe targets:    `<anything> | more`, `| less`, `| most`, `| bat`
#   2) Leading pagers:  `more file.json`, `less foo`, `most bar`
#   3) Editors:         `vi`, `vim`, `nvim`, `nano`, `pico`, `emacs`, `ed`
#   4) Live watchers:   `top`, `htop`, `btop`, `watch ...`, `tail -f`, `tail --follow`
#   5) Bare REPLs:      `python` / `python3` / `node` / `irb` / `ipython` with no script
#
# Recovery patterns:
#   - Redirect to file (`> out.txt`) and read it back via read_file
#   - Use `head -n N` / `Get-Content -TotalCount N` for long output
#   - Use `Blocking=false` + `WaitMsBeforeAsync` for genuine long-runners

# Pagers piped to: `... | more`, `... | less`, etc.
_INTERACTIVE_PAGER_PIPE_RE = re.compile(
    r"\|\s*\"?(?:more(?:\.com)?|less|most|bat)\"?(?:\.exe)?(?:\s|$|\|)",
    re.IGNORECASE,
)

# Pagers as leading executable: `more file`, `less file`, etc.
# Anchored to start-of-string OR after a separator (; & && || |).
_INTERACTIVE_PAGER_LEAD_RE = re.compile(
    r"(?:^|[;&|])\s*\"?(?:more(?:\.com)?|less|most)\"?(?:\.exe)?\s+\S",
    re.IGNORECASE,
)

# Editors that take over the terminal. Match as leading executable only
# (not as substring — `vim` could appear in a file path otherwise).
# Includes both bare invocations (`vim`) and with-args (`vim file.txt`).
_INTERACTIVE_EDITOR_RE = re.compile(
    r"(?:^|[;&|])\s*\"?(?:vi|vim|nvim|nano|pico|emacs|ed|view)\"?(?:\.exe)?(?:\s|$)",
    re.IGNORECASE,
)

# Live-watch commands: `top`, `htop`, `btop`, `watch <cmd>`, `tail -f|--follow`.
# `tail` without -f is allowed (bounded output).
_INTERACTIVE_WATCHER_RE = re.compile(
    r"(?:^|[;&|])\s*\"?(?:top|htop|btop|watch)\"?(?:\.exe)?(?:\s|$)",
    re.IGNORECASE,
)
_TAIL_FOLLOW_RE = re.compile(
    r"(?:^|[;&|])\s*\"?tail\"?(?:\.exe)?\s+(?:[^|;&]*\s)?(?:-f|--follow)\b",
    re.IGNORECASE,
)

# Bare REPLs (no script argument). `python script.py` is fine; bare `python`
# is not. Match: command at start-of-string or after separator, followed by
# end-of-string, whitespace+separator, or whitespace+only-flags-no-script.
# We treat `-i` (interactive) as always-blocking even with a script.
_BARE_REPL_RE = re.compile(
    r"(?:^|[;&|])\s*\"?(?:python|python3|node|irb|ipython|bash|sh)\"?(?:\.exe)?\s*(?:$|[;&|])",
    re.IGNORECASE,
)
_INTERACTIVE_FLAG_RE = re.compile(
    r"(?:^|[;&|])\s*\"?(?:python|python3|node|bash|sh)\"?(?:\.exe)?\s+(?:[^|;&]*\s)?-i(?:\s|$)",
    re.IGNORECASE,
)


def _check_interactive(command_line: str) -> str | None:
    """Return a category label if `command_line` will block on stdin, else None."""
    if _INTERACTIVE_PAGER_PIPE_RE.search(command_line):
        return "pager (piped)"
    if _INTERACTIVE_PAGER_LEAD_RE.search(command_line):
        return "pager (leading)"
    if _INTERACTIVE_EDITOR_RE.search(command_line):
        return "editor"
    if _INTERACTIVE_WATCHER_RE.search(command_line):
        return "live watcher"
    if _TAIL_FOLLOW_RE.search(command_line):
        return "tail --follow"
    if _BARE_REPL_RE.search(command_line):
        return "bare REPL"
    if _INTERACTIVE_FLAG_RE.search(command_line):
        return "interactive flag (-i)"
    return None


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

    interactive_kind = _check_interactive(command_line)
    if interactive_kind is not None:
        return _exit_block(
            f"Interactive / stdin-blocking command detected ({interactive_kind}). "
            "Cascade's terminal cannot send keystrokes, so the command will hang "
            "the turn forever. Recovery: (a) redirect output to a file with `> out.txt` "
            "and read it back via read_file; (b) use `head -n N` for long output; "
            "(c) for genuine long-runners, set Blocking=false + WaitMsBeforeAsync. "
            "Constitutional §27.",
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
