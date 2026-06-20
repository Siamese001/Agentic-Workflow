"""Tests for scripts/governance/codex_publication_audit.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import codex_publication_audit as mod  # noqa: E402
from worktree_hygiene import WorktreeHygieneIssue  # noqa: E402


def test_publication_audit_reports_patch_unique_and_equivalent(monkeypatch, tmp_path: Path) -> None:
    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("fetch", "origin", "--prune"):
            return 0, "", ""
        if command == ("rev-parse", "--verify", "origin/main"):
            return 0, "abc", ""
        if command == ("ls-remote", "origin", "refs/heads/main"):
            return 0, "abc\trefs/heads/main", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## codex/test...origin/main", ""
        if command == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/codex/test\n\n", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "codex/one\n", ""
        if command == ("cherry", "-v", "origin/main", "codex/one"):
            return 0, "+ 111 unique work\n- 222 equivalent work\n", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod, "run_git", fake_git)
    monkeypatch.setattr(mod, "find_dirty_protected_worktrees", lambda root, skip_paths=(): [])

    report = mod.build_publication_audit(tmp_path)

    assert report["status"] == "PASS"
    branch = report["unmerged_branches"][0]
    assert branch["patch_unique_commits"] == ["+ 111 unique work"]
    assert branch["patch_equivalent_commits"] == ["- 222 equivalent work"]


def test_publication_audit_warns_dirty_protected_worktree(monkeypatch, tmp_path: Path) -> None:
    issue = WorktreeHygieneIssue("main", tmp_path / "main", ("M docs/a.md",))

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("fetch", "origin", "--prune"):
            return 0, "", ""
        if command == ("rev-parse", "--verify", "origin/main"):
            return 0, "abc", ""
        if command == ("ls-remote", "origin", "refs/heads/main"):
            return 0, "abc\trefs/heads/main", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## codex/test", ""
        if command == ("worktree", "list", "--porcelain"):
            return 0, "", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod, "run_git", fake_git)
    monkeypatch.setattr(mod, "find_dirty_protected_worktrees", lambda root, skip_paths=(): [issue])

    report = mod.build_publication_audit(tmp_path)

    assert report["status"] == "WARN"
    assert "dirty_protected_worktrees" in report["warnings"]
    assert report["recommended_execution_surface"] == "clean_detached_origin_main_worktree"
