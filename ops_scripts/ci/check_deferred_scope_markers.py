#!/usr/bin/env python3
"""
check_deferred_scope_markers.py — pre-commit gate for DEFERRED_SCOPE marker contract.

Scans staged plan files (`.windsurf/plans/*.md`) for added lines containing
prose deferred-scope language. If any are present AND the file lacks a
matching `DEFERRED_SCOPE:` marker, the commit is blocked.

Policy: `.windsurf/rules/deferred-scope-capture.md`

Scoped narrowly to avoid false positives:
  - Only .windsurf/plans/*.md files (where backlog is recorded)
  - Only added lines (`+` in unified diff), not existing prose
  - Only if file lacks ANY DEFERRED_SCOPE: marker
  - Rule / doc files with meta-discussion are NOT scanned

Usage (from pre-commit):
    python ops_scripts/ci/check_deferred_scope_markers.py

Exit codes:
    0 — no violations (or no plan files staged)
    1 — violations found (commit blocked)

Bypass: DEFERRED_SCOPE_GATE_BYPASS=1  (logged when used).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Phrases that suggest deferred scope without a marker
PROSE_PATTERNS = [
    re.compile(
        r"\bdeferred\s+to\s+(?:a\s+)?(?:future|later|next)\s+(?:wave|phase|session|sprint)\b", re.IGNORECASE
    ),
    re.compile(r"\bout\s+of\s+scope\s+for\s+this\s+(?:wave|phase|plan|session)\b", re.IGNORECASE),
    re.compile(r"\bfuture\s+work\b", re.IGNORECASE),
    re.compile(r"\bwill\s+be\s+done\s+(?:later|next|in\s+a\s+future)\b", re.IGNORECASE),
    re.compile(r"\bparked\s+indefinitely\b", re.IGNORECASE),
    re.compile(r"\bnot\s+yet\s+tackled\b", re.IGNORECASE),
    re.compile(r"\baddressed\s+in\s+a\s+later\s+(?:wave|phase|plan)\b", re.IGNORECASE),
]
MARKER_RE = re.compile(r"^\s*DEFERRED_SCOPE:\s*", re.IGNORECASE | re.MULTILINE)

# Files scoped to this gate
PLAN_GLOB_RE = re.compile(r"^\.windsurf/plans/.+\.md$")


def _run(argv: list[str]) -> str:
    try:
        result = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            shell=False,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout or ""


def _staged_plan_files() -> list[str]:
    out = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
    return [line for line in out.splitlines() if PLAN_GLOB_RE.match(line)]


def _staged_added_lines(path: str) -> list[tuple[int, str]]:
    """Return (line_no, text) for added lines in the staged diff of `path`."""
    out = _run(["git", "diff", "--cached", "--unified=0", "--", path])
    added: list[tuple[int, str]] = []
    current_line = 0
    for raw in out.splitlines():
        # Hunk header: @@ -a,b +c,d @@
        if raw.startswith("@@"):
            m = re.match(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@", raw)
            if m:
                current_line = int(m.group(1))
            continue
        if raw.startswith("+++") or raw.startswith("---"):
            continue
        if raw.startswith("+"):
            added.append((current_line, raw[1:]))
            current_line += 1
        elif raw.startswith("-"):
            pass
        else:
            current_line += 1
    return added


def _file_has_marker(path: str) -> bool:
    """Check whether the staged (post-commit) version of the file has a marker."""
    content = _run(["git", "show", f":{path}"])
    return bool(MARKER_RE.search(content))


def main() -> int:
    if os.environ.get("DEFERRED_SCOPE_GATE_BYPASS") == "1":
        print("[deferred_scope_gate] BYPASS engaged", file=sys.stderr)
        return 0

    plan_files = _staged_plan_files()
    if not plan_files:
        return 0

    violations: list[tuple[str, int, str, str]] = []
    for path in plan_files:
        if _file_has_marker(path):
            continue  # file has at least one marker — assumed compliant
        added = _staged_added_lines(path)
        for line_no, text in added:
            for pattern in PROSE_PATTERNS:
                m = pattern.search(text)
                if m:
                    violations.append((path, line_no, m.group(0), text.strip()))
                    break

    if not violations:
        return 0

    print("", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print("BLOCKED: deferred-scope prose without DEFERRED_SCOPE marker", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print(
        "The following staged plan files introduce deferred-scope prose "
        "without emitting a DEFERRED_SCOPE: marker. This violates the "
        "deferred-scope-capture rule.",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    for path, line_no, phrase, full_line in violations:
        snippet = full_line[:100] + ("..." if len(full_line) > 100 else "")
        print(
            f"  {path}:{line_no}  phrase='{phrase}'\n    {snippet}",
            file=sys.stderr,
        )
    print("", file=sys.stderr)
    print("Fix options:", file=sys.stderr)
    print(
        "  1. Add a DEFERRED_SCOPE: marker line to the same file (see "
        ".windsurf/rules/deferred-scope-capture.md for schema).",
        file=sys.stderr,
    )
    print(
        "  2. Rephrase the prose to remove deferred-scope language if this is "
        "historical commentary, not a new deferred item.",
        file=sys.stderr,
    )
    print(
        "  3. Emergency bypass: DEFERRED_SCOPE_GATE_BYPASS=1 git commit ...",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
