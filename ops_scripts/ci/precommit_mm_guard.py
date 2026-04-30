#!/usr/bin/env python3
"""Gate G-PRECOMMIT-MM-DUAL-STATE — block silent commit rollback on dual-state files.

Plan: ``.windsurf/plans/adg-three-bucket-unified-c4f8e2.md`` (W4 P4.1).

The bug
-------
When a file is in **MM dual state** (modified in BOTH the index AND the
working tree), ``pre-commit`` stashes the unstaged half via ``git stash -k``,
runs hooks, then pops the stash. If any hook (e.g. ``ruff-format``) modifies
the file, the stash pop hits a conflict — pre-commit silently resolves it
with the worktree version, ate the staged half, and the user sees
``"Everything up-to-date"`` from ``git commit`` despite having genuine
staged changes.

The fix
-------
Run this guard **first** in the pre-commit chain. If any staged file also
has unstaged modifications, abort with a clear error explaining the two
recovery paths (stage everything OR stash the unstaged half).

Detection
---------
Parse ``git status --porcelain`` for status codes where:
  * column 0 (index) ∈ ``{M, A, D, R, C}`` — staged change
  * column 1 (worktree) ∈ ``{M, D}``       — unstaged change exists

Common dual states: ``MM`` ``AM`` ``DM`` ``RM`` ``CM`` ``MD`` ``AD``
``DD`` ``RD`` ``CD``.

Bypass
------
``PRECOMMIT_MM_GUARD_BYPASS=1`` — logged stderr warning + exit 0. Use only
when you accept the risk of silent staged-change loss (e.g., scripted
batch commits where you reset+restage on failure).

Usage
-----

::

    python ops_scripts/ci/precommit_mm_guard.py
    python ops_scripts/ci/precommit_mm_guard.py --status-text "MM agentic_core/x.py"  # for tests
"""

from __future__ import annotations

# This guard inspects git status — does not consume ADG views.
__adg_consumer_mode__ = "inventory"

import argparse
import os
import subprocess
import sys
from typing import Final

# Status-code semantics per ``git status --porcelain`` (man pages).
INDEX_STAGED_CODES: Final[frozenset[str]] = frozenset({"M", "A", "D", "R", "C"})
WORKTREE_DIRTY_CODES: Final[frozenset[str]] = frozenset({"M", "D"})


def parse_porcelain(text: str) -> list[tuple[str, str, str]]:
    """Parse ``git status --porcelain`` output into ``(index_code, worktree_code, path)``.

    Skips untracked files (``??``) and ignored files (``!!``). Handles renames
    (``R orig -> new``) by reporting the destination path.
    """
    rows: list[tuple[str, str, str]] = []
    for raw in text.splitlines():
        if not raw or len(raw) < 3:
            continue
        idx_code = raw[0]
        wt_code = raw[1]
        if idx_code == "?" or idx_code == "!":
            continue
        rest = raw[3:]
        # Renames look like: "R  oldpath -> newpath"
        path = rest
        if " -> " in rest:
            path = rest.split(" -> ", 1)[1]
        rows.append((idx_code, wt_code, path))
    return rows


def find_dual_state(rows: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """Return the subset of rows in dual state (staged + worktree-dirty)."""
    return [
        (i, w, p)
        for (i, w, p) in rows
        if i in INDEX_STAGED_CODES and w in WORKTREE_DIRTY_CODES
    ]


def _git_status_porcelain() -> str:
    """Return ``git status --porcelain`` output. Empty string on git failure."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"[precommit_mm_guard] WARNING: git status failed: {exc}", file=sys.stderr)
        return ""
    if result.returncode != 0:
        print(
            f"[precommit_mm_guard] WARNING: git status exited {result.returncode}: "
            f"{result.stderr.strip()[:200]}",
            file=sys.stderr,
        )
        return ""
    return result.stdout


def format_violation_message(violations: list[tuple[str, str, str]]) -> str:
    """Format a clear, actionable error message for the user."""
    lines = [
        "",
        "=" * 72,
        "[precommit_mm_guard] COMMIT BLOCKED — dual-state files detected",
        "=" * 72,
        "",
        "The following files are staged AND have unstaged modifications:",
        "",
    ]
    for idx, wt, path in violations:
        lines.append(f"  {idx}{wt}  {path}")
    lines += [
        "",
        "Why this blocks the commit",
        "--------------------------",
        "Pre-commit stashes unstaged changes (`git stash -k`) before running",
        "hooks. If any hook (ruff-format, guardian-comment-fixer, ...) modifies",
        "the file, the stash pop hits a conflict — pre-commit silently resolves",
        "it with the worktree version, eats the staged half, and your commit",
        "shows 'Everything up-to-date' despite real staged changes.",
        "",
        "Recovery — pick one",
        "-------------------",
        "  (a) Stage everything:    git add <files>",
        "  (b) Stash the unstaged:  git stash --keep-index",
        "  (c) Commit just the staged half explicitly:",
        "        git stash --keep-index && git commit && git stash pop",
        "",
        "Bypass (accept risk of silent staged-change loss):",
        "  PRECOMMIT_MM_GUARD_BYPASS=1 git commit ...",
        "",
        "Plan: .windsurf/plans/adg-three-bucket-unified-c4f8e2.md (W4 P4.1)",
        "=" * 72,
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status-text",
        type=str,
        default=None,
        help="Inject porcelain text instead of running git (for tests)",
    )
    args = parser.parse_args(argv)

    if os.environ.get("PRECOMMIT_MM_GUARD_BYPASS") == "1":
        print(
            "[precommit_mm_guard] BYPASS active — silent-rollback risk accepted by operator",
            file=sys.stderr,
        )
        return 0

    text = args.status_text if args.status_text is not None else _git_status_porcelain()
    if not text.strip():
        # No staged changes (or git unreachable) — let pre-commit handle it.
        return 0

    rows = parse_porcelain(text)
    violations = find_dual_state(rows)
    if not violations:
        return 0

    print(format_violation_message(violations), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
