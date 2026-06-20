"""Hermetic tests for the merged-chat-worktree reaper (.claude/hooks/prune_merged_chat_worktrees.py).

Builds a real temp git repo + chat worktrees and verifies the safety envelope: only ephemeral
chat/* worktrees under the chat root that are merged into trunk AND clean AND not the current
worktree get reaped; unmerged, dirty, non-chat, and current worktrees are never touched.
"""
from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
import time
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


# --- item #4: .keep-worktree opt-out marker -------------------------------------------------


def test_keep_marker_protects_merged_clean_worktree(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-keep")
    (wt / ".keep-worktree").write_text("", encoding="utf-8")
    report = _reap(repo)
    assert report["reaped"] == []
    assert wt.exists()
    assert any(s["reason"] == "keep_marker" for s in report["skipped"])


# --- item #4: opt-in non-chat reap prefixes -------------------------------------------------


def _add_worktree_at(repo: Path, path: Path, branch: str) -> Path:
    _git(repo, "worktree", "add", "-q", str(path), "-b", branch)
    return path


def test_default_prefixes_ignore_sibling_feat_worktree(repo: Path) -> None:
    # A merged+clean feat/* SIBLING (not under the chat root) is never reaped by default.
    wt = _add_worktree_at(repo, repo.parent / "feat-sib", "feat/sib")
    report = _reap(repo)  # default reap_branch_prefixes=("chat/",)
    assert report["reaped"] == []
    assert wt.exists()
    # Outside the chat root + non-matching prefix → silently ignored (not even skipped).
    assert not any(Path(s["path"]) == wt.resolve() for s in report["skipped"])


def test_optin_feat_prefix_reaps_merged_sibling(repo: Path) -> None:
    wt = _add_worktree_at(repo, repo.parent / "feat-sib2", "feat/sib2")  # merged + clean
    report = _reap(repo, reap_branch_prefixes=("chat/", "feat/"))
    assert [r["branch"] for r in report["reaped"]] == ["feat/sib2"]
    assert not wt.exists()


def test_optin_feat_prefix_keeps_unmerged_sibling(repo: Path) -> None:
    wt = repo.parent / "feat-sib3"
    _git(repo, "worktree", "add", "-q", str(wt), "-b", "feat/sib3")
    (wt / "x.txt").write_text("x", encoding="utf-8")
    _git(wt, "add", "-A")
    _git(wt, "commit", "-qm", "unmerged feat work")
    report = _reap(repo, reap_branch_prefixes=("chat/", "feat/"))
    assert report["reaped"] == []
    assert wt.exists()
    assert any(s["reason"] == "not_merged_into_trunk" for s in report["skipped"])


# --- item #1: env-reader default grace window raised 0 -> 30 min ----------------------------


def test_min_age_seconds_defaults_to_30min(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_CLEANUP_MIN_AGE_MINUTES", raising=False)
    assert reaper._min_age_seconds() == 30 * 60


def test_min_age_seconds_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKTREE_CLEANUP_MIN_AGE_MINUTES", "5")
    assert reaper._min_age_seconds() == 5 * 60
    monkeypatch.setenv("WORKTREE_CLEANUP_MIN_AGE_MINUTES", "0")
    assert reaper._min_age_seconds() == 0


def test_reap_prefixes_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_REAP_BRANCH_PREFIXES", raising=False)
    assert reaper._reap_prefixes() == ("chat/", "feat/")  # module default (worktree-deliver-reap)
    monkeypatch.setenv("WORKTREE_REAP_BRANCH_PREFIXES", "chat/, feat/ ,codex/")
    assert reaper._reap_prefixes() == ("chat/", "feat/", "codex/")


# --- item #1: grace window honors worktree creation mtime (not just HEAD commit time) ------


def test_worktree_age_fresh_is_small(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-fresh")
    age = reaper._worktree_age_seconds(wt, time.time())
    assert age is not None and 0 <= age < 600


def test_worktree_age_uses_creation_mtime_when_head_is_old(repo: Path) -> None:
    # A worktree whose HEAD points at an OLD commit but was JUST created must read as recent
    # (its creation mtime wins) — this is the empty-but-just-created reap-race fix.
    wt = _add_chat_worktree(repo, "20260608-oldhead")
    old = "2000-01-01T00:00:00 +0000"
    subprocess.run(
        ["git", "commit", "--allow-empty", "-qm", "old", "--date", old],
        cwd=str(wt),
        env={**os.environ, "GIT_COMMITTER_DATE": old},
        check=True,
        timeout=30,
    )
    # HEAD committer date is ~25 years old …
    head_ct = subprocess.run(
        ["git", "show", "-s", "--format=%ct", "HEAD"],
        cwd=str(wt), capture_output=True, text=True, timeout=30, check=True,
    ).stdout.strip()
    assert time.time() - float(head_ct) > 600  # HEAD really is old
    # … but the worktree was just created, so the recency signal is small.
    age = reaper._worktree_age_seconds(wt, time.time())
    assert age is not None and age < 600


def test_grace_window_protects_fresh_worktree_with_old_head(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-protect")
    old = "2000-01-01T00:00:00 +0000"
    subprocess.run(
        ["git", "commit", "--allow-empty", "-qm", "old", "--date", old],
        cwd=str(wt),
        env={**os.environ, "GIT_COMMITTER_DATE": old},
        check=True,
        timeout=30,
    )
    # Make it an ancestor of trunk so only the grace window can keep it.
    _git(repo, "merge", "--ff-only", "chat/20260608-protect")
    report = _reap(repo, min_age_seconds=3600)
    assert report["reaped"] == []
    assert any(s["reason"] == "within_grace_window" for s in report["skipped"])


# --- ancestry containment: patch/no-unique equivalence is not cleanup proof ---------------------


def test_ancestor_helper_requires_reachability(repo: Path) -> None:
    _add_chat_worktree(repo, "20260608-noop")
    assert reaper._is_ancestor("chat/20260608-noop", "main", repo_root=repo)
    _add_chat_worktree(repo, "20260608-work", diverge=True)
    assert not reaper._is_ancestor("chat/20260608-work", "main", repo_root=repo)
    assert not reaper._is_ancestor("chat/20260608-work", "origin/does-not-exist", repo_root=repo)


def test_stale_local_main_noop_worktree_is_kept_until_ancestor_merged(repo: Path) -> None:
    # Reproduce the confusing pileup: local ``main`` diverged from the configured origin trunk.
    # The chat worktree sits at local main's tip, but it is NOT an ancestor of the origin trunk.
    # Even if its patch content is equivalent/no-unique relative to local main, cleanup must keep
    # it until an explicit merge records the branch tip on the configured trunk.
    _git(repo, "checkout", "-q", "-b", "otrunk")
    (repo / "real.txt").write_text("real work on origin", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "47 real commits on origin")
    _git(repo, "checkout", "-q", "main")
    (repo / "stale.txt").write_text("stale plan commit on local main", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "stale local-main commit")
    wt = _add_chat_worktree(repo, "20260608-stale")

    kept = reaper.reap_merged_chat_worktrees(
        repo_root=repo, trunk_ref="otrunk", do_fetch=False
    )
    assert kept["reaped"] == []
    assert any(s["reason"] == "not_merged_into_trunk" for s in kept["skipped"])
    assert wt.exists()

    _git(repo, "checkout", "-q", "otrunk")
    _git(repo, "merge", "-s", "ours", "--no-ff", "--no-edit", "chat/20260608-stale")

    got = reaper.reap_merged_chat_worktrees(repo_root=repo, trunk_ref="otrunk", do_fetch=False)
    assert [r["branch"] for r in got["reaped"]] == ["chat/20260608-stale"]
    assert not wt.exists()


# --- branch-prune: delete merged local branches that have no worktree ---------------------------


def _prune(repo: Path, **kw):
    kw.setdefault("trunk_ref", "main")
    return reaper.prune_merged_branches(repo_root=repo, do_fetch=False, **kw)


def _merged_branch_no_worktree(repo: Path, name: str) -> None:
    """Create a chat/* branch at main's tip (delivered) with NO worktree."""
    _git(repo, "branch", name, "main")


def test_prune_deletes_merged_branch_without_worktree(repo: Path) -> None:
    _merged_branch_no_worktree(repo, "chat/20260608-orphan")
    report = _prune(repo)
    assert [d["branch"] for d in report["deleted"]] == ["chat/20260608-orphan"]
    assert _git(repo, "branch", "--list", "chat/20260608-orphan") == ""


def test_prune_keeps_branch_with_unique_commits(repo: Path) -> None:
    _git(repo, "branch", "chat/20260608-unmerged", "main")
    # Give it a unique commit via a throwaway worktree, then remove the worktree (branch stays).
    wt = repo.parent / ".tmpwt"
    _git(repo, "worktree", "add", "-q", str(wt), "chat/20260608-unmerged")
    (wt / "u.txt").write_text("u", encoding="utf-8")
    _git(wt, "add", "-A")
    _git(wt, "commit", "-qm", "unique work")
    _git(repo, "worktree", "remove", "--force", str(wt))
    report = _prune(repo)
    assert report["deleted"] == []
    assert any(s["reason"] == "not_merged_into_trunk" for s in report["skipped"])
    assert _git(repo, "branch", "--list", "chat/20260608-unmerged") != ""


def test_prune_skips_branch_that_has_a_worktree(repo: Path) -> None:
    wt = _add_chat_worktree(repo, "20260608-haswt")  # merged + clean, but HAS a worktree
    report = _prune(repo, branch_prefixes=("chat/",))
    assert report["deleted"] == []
    assert any(s["reason"] == "has_worktree" for s in report["skipped"])
    assert wt.exists()  # worktree reaper owns it, branch-prune left it alone


def test_prune_skips_current_branch(repo: Path) -> None:
    _git(repo, "checkout", "-q", "-b", "chat/20260608-current")
    report = _prune(repo)
    assert report["deleted"] == []
    assert any(s["reason"] == "current_branch" for s in report["skipped"])


def test_prune_skips_protected_and_non_prefix_branches(repo: Path) -> None:
    _git(repo, "branch", "random-branch", "main")  # non-prefix
    report = _prune(repo)
    assert report["deleted"] == []
    assert any(
        s["branch"] == "random-branch" and s["reason"] == "not_reap_prefix"
        for s in report["skipped"]
    )
    # main itself is protected + non-prefix → skipped, never deleted.
    assert _git(repo, "branch", "--list", "main") != ""


def test_prune_dry_run_deletes_nothing(repo: Path) -> None:
    _merged_branch_no_worktree(repo, "chat/20260608-dry")
    report = _prune(repo, dry_run=True)
    assert [d["branch"] for d in report["deleted"]] == ["chat/20260608-dry"]
    assert all(d.get("dry_run") for d in report["deleted"])
    assert _git(repo, "branch", "--list", "chat/20260608-dry") != ""  # still there


def test_prune_feat_prefix_default(repo: Path) -> None:
    _git(repo, "branch", "feat/delivered-thing", "main")
    report = _prune(repo)  # default prefixes include feat/
    assert "feat/delivered-thing" in [d["branch"] for d in report["deleted"]]


def test_worktree_branches_helper() -> None:
    sample = (
        "worktree /a\nHEAD abc\nbranch refs/heads/main\n\n"
        "worktree /b\nHEAD def\nbranch refs/heads/chat/x\n\n"
        "worktree /c\nHEAD ghi\ndetached\n\n"
    )
    assert reaper._worktree_branches(sample) == {"main", "chat/x"}


# --- CLI safety defaults -------------------------------------------------------------------


def test_session_start_invocation_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fail_if_called(**kwargs):
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(reaper, "reap_merged_chat_worktrees", fail_if_called)
    monkeypatch.setattr(sys, "stdin", io.StringIO("{}"))
    monkeypatch.setattr(sys, "argv", ["prune_merged_chat_worktrees.py"])

    assert reaper.main(None) == 0
    assert called is False


def test_cli_defaults_to_dry_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    seen: dict[str, bool] = {}

    monkeypatch.setattr(reaper, "_primary_worktree", lambda start: tmp_path)
    monkeypatch.setattr(reaper, "_cwd_toplevel", lambda start: tmp_path)

    def fake_reap(**kwargs):
        seen["dry_run"] = kwargs["dry_run"]
        return {"reaped": [], "skipped": [], "dry_run": kwargs["dry_run"], "status": "ok"}

    monkeypatch.setattr(reaper, "reap_merged_chat_worktrees", fake_reap)
    monkeypatch.setattr(reaper, "prune_merged_branches", lambda **kwargs: {"deleted": []})

    assert reaper.main(["--no-branches"]) == 0
    assert seen["dry_run"] is True


def test_cli_delete_merged_is_explicit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    seen: dict[str, bool] = {}

    monkeypatch.setattr(reaper, "_primary_worktree", lambda start: tmp_path)
    monkeypatch.setattr(reaper, "_cwd_toplevel", lambda start: tmp_path)

    def fake_reap(**kwargs):
        seen["dry_run"] = kwargs["dry_run"]
        return {"reaped": [], "skipped": [], "dry_run": kwargs["dry_run"], "status": "ok"}

    monkeypatch.setattr(reaper, "reap_merged_chat_worktrees", fake_reap)
    monkeypatch.setattr(reaper, "prune_merged_branches", lambda **kwargs: {"deleted": []})

    assert reaper.main(["--delete-merged", "--no-branches"]) == 0
    assert seen["dry_run"] is False
