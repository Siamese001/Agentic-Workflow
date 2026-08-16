"""Tests for scripts/governance/codex_main_closeout.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import codex_main_closeout as mod  # noqa: E402


def test_closeout_check_passes_for_clean_single_main(monkeypatch, tmp_path: Path) -> None:
    staging_root = tmp_path.with_name(f"{tmp_path.name}-worktrees")
    staging_root.mkdir()

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        if command == ("branch", "--format=%(refname:short)"):
            return 0, "main", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)

    report = mod.build_closeout_report(tmp_path)

    assert report["status"] == "PASS"
    assert report["issues"] == []
    assert staging_root.exists()


def test_release_closeout_blocks_critical_hook_failopen(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        mod,
        "_critical_hook_failopen_issues",
        lambda _root: [mod.CloseoutIssue("critical_hook_failopen", "beforeSubmitPrompt: 1")],
    )
    monkeypatch.setattr(mod, "_publication_closeout_issues", lambda _root, base_ref: [])
    monkeypatch.setattr(mod, "_workspace_topology_issues", lambda _root, expected_path, base_ref: [])
    monkeypatch.setattr(mod, "_extra_local_branch_issues", lambda _root: [])

    report = mod.build_closeout_report(tmp_path, require_governance_health=True)

    assert report["publication_closeout"]["status"] == "FAIL"
    assert report["governance_health"]["status"] == "FAIL"
    assert {"code": "critical_hook_failopen", "detail": "beforeSubmitPrompt: 1"} in report["issues"]


def test_closeout_check_fails_on_extra_local_branch(monkeypatch, tmp_path: Path) -> None:
    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        if command == ("branch", "--format=%(refname:short)"):
            return 0, "main\ncodex/merged", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)

    report = mod.build_closeout_report(tmp_path)

    assert report["status"] == "FAIL"
    assert {"code": "extra_local_branches", "detail": "codex/merged"} in report["issues"]


def test_closeout_check_passes_when_worktree_staging_root_remains(monkeypatch, tmp_path: Path) -> None:
    staging_root = tmp_path.with_name(f"{tmp_path.name}-worktrees")
    staging_root.mkdir()

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        if command == ("branch", "--format=%(refname:short)"):
            return 0, "main", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)

    report = mod.build_closeout_report(tmp_path)

    assert report["status"] == "PASS"
    assert report["issues"] == []
    assert staging_root.exists()


def test_publication_closeout_passes_while_workspace_topology_fails(
    monkeypatch,
    tmp_path: Path,
) -> None:
    other = tmp_path.parent / "codex-unrelated-work"

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return (
                0,
                f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n"
                f"worktree {other}\nHEAD def\nbranch refs/heads/codex/unrelated-work\n\n",
                "",
            )
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main\n M docs/local-notes.md\nM  docs/staged-note.md", ""
        if command == ("diff", "--quiet"):
            return 1, "", ""
        if command == ("diff", "--cached", "--quiet"):
            return 1, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "codex/unrelated-work", ""
        if command == ("branch", "--format=%(refname:short)"):
            return 0, "main\ncodex/unrelated-work", ""
        raise AssertionError((command, cwd))

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)

    report = mod.build_closeout_report(tmp_path)

    assert report["status"] == "FAIL"
    assert report["publication_closeout"]["status"] == "PASS"
    assert report["workspace_topology_closeout"]["status"] == "FAIL"
    assert {"code": "worktree_count", "detail": "expected=1 actual=2"} in report["workspace_topology_closeout"]["issues"]
    assert {"code": "extra_local_branches", "detail": "codex/unrelated-work"} in report["workspace_topology_closeout"]["issues"]
    assert {"code": "dirty_status", "detail": " M docs/local-notes.md\nM  docs/staged-note.md"} in report[
        "workspace_topology_closeout"
    ]["issues"]
    assert {"code": "unstaged_diff", "detail": "git diff --quiet reported changes"} in report[
        "workspace_topology_closeout"
    ]["issues"]
    assert {"code": "staged_diff", "detail": "git diff --cached --quiet reported changes"} in report[
        "workspace_topology_closeout"
    ]["issues"]
    assert {"code": "unmerged_branches", "detail": "codex/unrelated-work"} in report[
        "workspace_topology_closeout"
    ]["issues"]


def test_publication_closeout_blocks_unresolved_conflict_status(monkeypatch, tmp_path: Path) -> None:
    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main\nUU docs/conflicted.md", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 1, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        if command == ("branch", "--format=%(refname:short)"):
            return 0, "main", ""
        raise AssertionError((command, cwd))

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)

    report = mod.build_closeout_report(tmp_path)

    assert report["status"] == "FAIL"
    assert report["publication_closeout"]["status"] == "FAIL"
    assert {"code": "conflicted_status", "detail": "UU docs/conflicted.md"} in report["publication_closeout"][
        "issues"
    ]


def test_closeout_apply_preserves_empty_worktree_staging_root(monkeypatch, tmp_path: Path) -> None:
    staging_root = tmp_path.with_name(f"{tmp_path.name}-worktrees")
    staging_root.mkdir()

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        if command == ("branch", "--format=%(refname:short)"):
            return 0, "main", ""
        raise AssertionError(command)

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)
    monkeypatch.setattr(mod, "_active_process_refs", lambda path: [])

    report = mod.build_closeout_report(tmp_path, apply=True)

    assert report["status"] == "PASS"
    assert staging_root.exists()
    assert report["issues"] == []


def test_closeout_apply_removes_clean_ancestor_contained_worktree_and_branch(
    monkeypatch,
    tmp_path: Path,
) -> None:
    other = tmp_path.parent / "codex-old"
    state = {"extra_worktree": True, "extra_branch": True}

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            rows = [f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n"]
            if state["extra_worktree"]:
                rows.append(f"worktree {other}\nHEAD def\nbranch refs/heads/codex/old\n\n")
            return 0, "".join(rows), ""
        if command == ("status", "--short") and cwd == other:
            return 0, "", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command in {
            ("merge-base", "--is-ancestor", "codex/old", "origin/main"),
            ("merge-base", "--is-ancestor", "HEAD", "origin/main"),
        }:
            return 0, "", ""
        if command == ("worktree", "remove", str(other.resolve())):
            state["extra_worktree"] = False
            return 0, "", ""
        if command == ("branch", "--format=%(refname:short)"):
            branches = ["main"]
            if state["extra_branch"]:
                branches.append("codex/old")
            return 0, "\n".join(branches), ""
        if command == ("branch", "-d", "codex/old"):
            state["extra_branch"] = False
            return 0, "Deleted branch codex/old.", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        raise AssertionError((command, cwd))

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)

    report = mod.build_closeout_report(tmp_path, apply=True)

    assert report["status"] == "PASS"
    assert [action["action"] for action in report["actions"]] == [
        "remove_extra_worktree",
        "delete_merged_local_branch",
    ]
    assert state == {"extra_worktree": False, "extra_branch": False}


def test_closeout_apply_refuses_active_clean_worktree(
    monkeypatch,
    tmp_path: Path,
) -> None:
    other = tmp_path.parent / "codex-active-adg"

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return (
                0,
                f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n"
                f"worktree {other}\nHEAD def\nbranch refs/heads/codex/active-adg\n\n",
                "",
            )
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("branch", "--format=%(refname:short)"):
            return 0, "main\ncodex/active-adg", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "", ""
        raise AssertionError((command, cwd))

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)
    monkeypatch.setattr(
        mod,
        "_active_process_refs",
        lambda path: [f"python {other}\\tools\\adg\\run_full_adg_audit.py"] if path == other.resolve() else [],
    )

    report = mod.build_closeout_report(tmp_path, apply=True)
    issue_codes = {issue["code"] for issue in report["issues"]}

    assert report["status"] == "FAIL"
    assert "active_extra_worktree_process" in issue_codes
    assert "branch_checked_out" in issue_codes
    assert report["actions"] == []


def test_closeout_apply_refuses_dirty_worktree_and_unmerged_branch(
    monkeypatch,
    tmp_path: Path,
) -> None:
    other = tmp_path.parent / "codex-risky"

    def fake_git(*args: str, cwd: Path):
        command = tuple(args)
        if command == ("worktree", "list", "--porcelain"):
            return (
                0,
                f"worktree {tmp_path}\nHEAD abc\nbranch refs/heads/main\n\n"
                f"worktree {other}\nHEAD def\nbranch refs/heads/codex/risky\n\n",
                "",
            )
        if command == ("status", "--short") and cwd == other:
            return 0, " M docs/risky.md", ""
        if command == ("status", "--short", "--branch"):
            return 0, "## main...origin/main", ""
        if command in {("diff", "--quiet"), ("diff", "--cached", "--quiet")}:
            return 0, "", ""
        if command == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main", ""
        if command in {("rev-parse", "--verify", "HEAD"), ("rev-parse", "--verify", "origin/main")}:
            return 0, "abc", ""
        if command == ("merge-base", "--is-ancestor", "codex/risky", "origin/main"):
            return 1, "", ""
        if command == ("branch", "--format=%(refname:short)"):
            return 0, "main\ncodex/risky", ""
        if command == ("branch", "--no-merged", "origin/main", "--format=%(refname:short)"):
            return 0, "codex/risky", ""
        raise AssertionError((command, cwd))

    monkeypatch.setattr(mod.worktree_hygiene, "run_git", fake_git)
    monkeypatch.setattr(mod, "_active_process_refs", lambda path: [])

    report = mod.build_closeout_report(tmp_path, apply=True)
    issue_codes = {issue["code"] for issue in report["issues"]}

    assert report["status"] == "FAIL"
    assert "dirty_extra_worktree" in issue_codes
    assert "branch_checked_out" in issue_codes
    assert "unmerged_branches" in issue_codes
    assert report["actions"] == []
