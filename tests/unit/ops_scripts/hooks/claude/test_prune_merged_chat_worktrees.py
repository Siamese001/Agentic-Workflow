"""Hermetic tests for the merged-chat-worktree reaper (.claude/hooks/prune_merged_chat_worktrees.py).

Builds a real temp git repo + chat worktrees and verifies the safety envelope: only ephemeral
chat/* worktrees under the chat root that are merged into trunk AND clean AND not the current
worktree get reaped; unmerged, dirty, non-chat, and current worktrees are never touched.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[5]
_HOOK = _REPO / ".claude" / "hooks" / "prune_merged_chat_worktrees.py"


def _load():
    spec = importlib.util.spec_from_file_location("prune_merged_chat_worktrees", _HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


reaper = _load()


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=30, check=True
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A git repo on `main` with one commit; chat worktrees go under tmp/.chat-worktrees/."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@t.t")
    _git(root, "config", "user.name", "t")
    (root / "f.txt").write_text("x", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "init")
    return root


def _add_chat_worktree(repo: Path, name: str, *, diverge: bool = False, dirty: bool = False) -> Path:
    wt = repo.parent / ".chat-worktrees" / name
    _git(repo, "worktree", "add", "-q", str(wt), "-b", f"chat/{name}")
    if diverge:
        (wt / "extra.txt").write_text("e", encoding="utf-8")
        _git(wt, "add", "-A")
        _git(wt, "commit", "-qm", "unmerged work")
    if dirty:
        (wt / "dirty.txt").write_text("d", encoding="utf-8")
    return wt


def _reap(repo: Path, **kw):
    return reaper.reap_merged_chat_worktrees(
        repo_root=repo, trunk_ref="main", do_fetch=False, **kw
    )


def test_merged_clean_chat_worktree_is_reaped(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-aaaa")  # no divergence → ancestor of main
    assert wt.exists()
    report = _reap(repo)
    assert [r["branch"] for r in report["reaped"]] == ["chat/20260608-aaaa"]
    assert not wt.exists()  # worktree dir removed
    branches = _git(repo, "branch", "--list", "chat/20260608-aaaa")
    assert branches == ""  # branch deleted


def test_unmerged_worktree_is_kept(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-bbbb", diverge=True)
    report = _reap(repo)
    assert report["reaped"] == []
    assert wt.exists()
    assert any(s["reason"] == "not_merged_into_trunk" for s in report["skipped"])


def test_dirty_worktree_is_kept(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-cccc", dirty=True)
    report = _reap(repo)
    assert report["reaped"] == []
    assert wt.exists()
    assert any(s["reason"] == "uncommitted_changes" for s in report["skipped"])


def test_current_worktree_is_never_reaped(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-dddd")
    report = _reap(repo, current_worktree=wt)
    assert report["reaped"] == []
    assert wt.exists()
    assert any(s["reason"] == "current_worktree" for s in report["skipped"])


def test_non_chat_branch_under_root_is_kept(repo: Path) -> None:
    wt = repo.parent / ".chat-worktrees" / "feat-thing"
    _git(repo, "worktree", "add", "-q", str(wt), "-b", "feat/thing")
    report = _reap(repo)
    assert report["reaped"] == []
    assert wt.exists()
    assert any(s["reason"] == "not_chat_branch" for s in report["skipped"])


def test_worktree_outside_chat_root_is_ignored(repo: Path) -> None:
    # A chat/* worktree NOT under the chat root must never be considered (e.g. a manual worktree).
    other = repo.parent / "manual-elsewhere"
    _git(repo, "worktree", "add", "-q", str(other), "-b", "chat/manual")
    report = _reap(repo)
    assert report["reaped"] == []
    assert other.exists()
    # It is silently ignored (not under chat root) — not even in skipped.
    assert not any(Path(s["path"]) == other.resolve() for s in report["skipped"])


def test_dry_run_reports_without_deleting(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-eeee")
    report = _reap(repo, dry_run=True)
    assert [r["branch"] for r in report["reaped"]] == ["chat/20260608-eeee"]
    assert all(r.get("dry_run") for r in report["reaped"])
    assert wt.exists()  # nothing deleted in dry-run


def test_grace_window_protects_recent_worktree(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-ffff")  # HEAD just committed → very recent
    report = _reap(repo, min_age_seconds=3600)
    assert report["reaped"] == []
    assert wt.exists()
    assert any(s["reason"] == "within_grace_window" for s in report["skipped"])


def test_porcelain_parser() -> None:
    sample = (
        "worktree /a\nHEAD abc\nbranch refs/heads/main\n\n"
        "worktree /b\nHEAD def\nbranch refs/heads/chat/x\n\n"
    )
    parsed = reaper._parse_worktrees(sample)
    assert parsed == [
        {"path": "/a", "head": "abc", "branch": "main"},
        {"path": "/b", "head": "def", "branch": "chat/x"},
    ]
