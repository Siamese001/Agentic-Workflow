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


def test_single_main_worktree_passes_when_clean(monkeypatch, tmp_path: Path) -> None:
    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command == ("rev-parse", "--verify", "HEAD"):
            return 0, "abc", ""
        if command == ("rev-parse", "--verify", "origin/main"):
            return 0, "abc", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod, "run_git", fake_git)

    assert mod.verify_single_main_worktree(tmp_path) == []


def test_single_main_worktree_reports_topology_and_dirty_issues(monkeypatch, tmp_path: Path) -> None:
    other = tmp_path / "other"

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return (
                0,
                f"worktree {tmp_path}\nHEAD abc\ndetached\n\n"
                f"worktree {other}\nHEAD def\nbranch refs/heads/main\n\n",
                "",
            )
        if command == ("status", "--short", "--branch"):
            return 0, "## HEAD (no branch)\n M docs/a.md", ""
        if command == ("diff", "--quiet"):
            return 1, "", ""
        if command == ("diff", "--cached", "--quiet"):
            return 1, "", ""
        if command == ("rev-parse", "--verify", "HEAD"):
            return 0, "abc", ""
        if command == ("rev-parse", "--verify", "origin/main"):
            return 0, "def", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "codex/leftover", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod, "run_git", fake_git)

    issues = mod.verify_single_main_worktree(tmp_path)
    codes = {issue.code for issue in issues}

    assert {
        "worktree_count",
        "worktree_branch",
        "dirty_status",
        "unstaged_diff",
        "staged_diff",
        "head_not_base_ref",
        "unmerged_branches",
    } <= codes


def test_single_main_worktree_reports_wrong_path(monkeypatch, tmp_path: Path) -> None:
    actual = tmp_path / "actual"
    expected = tmp_path / "expected"

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {actual}\nHEAD abc\nbranch refs/heads/main\n\n", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod, "run_git", fake_git)

    issues = mod.verify_single_main_worktree(tmp_path, expected_path=expected)

    assert any(issue.code == "worktree_path" for issue in issues)
