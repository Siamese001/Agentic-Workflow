"""Tests for scripts/governance/worktree_hygiene.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import worktree_hygiene as mod  # noqa: E402


def test_parse_worktrees_includes_detached_rows() -> None:
    parsed = mod.parse_worktrees(
        "worktree /repo\nHEAD abc\nbranch refs/heads/main\n\n"
        "worktree /tmp/wt\nHEAD def\ndetached\n\n"
    )

    assert parsed == [
        {"path": "/repo", "head": "abc", "branch": "main"},
        {"path": "/tmp/wt", "head": "def", "branch": "DETACHED"},
    ]


def test_dirty_protected_worktree_summary() -> None:
    issue = mod.WorktreeHygieneIssue(
        branch="main",
        worktree=Path("/repo"),
        dirty_files=("M docs/a.md", "M docs/b.md", "M docs/c.md"),
    )

    summary = mod.summarize_dirty_worktrees([issue], max_files_per_worktree=2)

    assert summary.startswith("- main @ ")
    assert summary.endswith(": M docs/a.md, M docs/b.md (+1 more)")
