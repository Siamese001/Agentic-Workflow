"""Tests for session_start_branch_guard helpers (cut-from-trunk + local-trunk sync).

Covers the env-gated decision paths of items #B/#D without touching the network.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[5]
_HOOK = _REPO / ".claude" / "hooks" / "session_start_branch_guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("ssbg", _HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


guard = _load()


def test_default_worktree_path_is_registered_sibling_style(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = tmp_path / "Agentic-Workflow-FRESH"
    monkeypatch.setattr(guard, "REPO_ROOT", repo)
    monkeypatch.delenv("CHAT_WORKTREE_ROOT", raising=False)
    monkeypatch.delenv("WORKTREE_DIR_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)

    slug = guard._worktree_slug("20260615-120000", "abcdef12")

    assert guard._branch_name(slug) == "feat/chat-20260615-120000-abcdef12"
    assert guard._worktree_path(slug) == tmp_path / "Agentic-Workflow-FRESH-chat-20260615-120000-abcdef12"


def test_worktree_branch_prefix_override_normalizes_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKTREE_BRANCH_PREFIX", "codex")

    assert guard._branch_name("chat-demo") == "codex/chat-demo"


def test_is_registered_worktree_normalizes_porcelain_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = tmp_path / "Agentic-Workflow-FRESH-chat-demo"

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        assert args == ("worktree", "list", "--porcelain")
        return 0, f"worktree {target}\nHEAD abc\nbranch refs/heads/feat/chat-demo\n"

    monkeypatch.setattr(guard, "_git", fake_git)

    assert guard._is_registered_worktree(target)
    assert not guard._is_registered_worktree(tmp_path / "Agentic-Workflow-FRESH-chat-other")


def test_add_registered_removes_unregistered_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = tmp_path / "Agentic-Workflow-FRESH"
    repo.mkdir()
    target = tmp_path / "Agentic-Workflow-FRESH-chat-demo"
    monkeypatch.setattr(guard, "REPO_ROOT", repo)
    monkeypatch.delenv("WORKTREE_DIR_PREFIX", raising=False)

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        if args[:2] == ("worktree", "add"):
            target.mkdir()
            return 0, "added"
        if args == ("worktree", "list", "--porcelain"):
            return 0, f"worktree {repo}\nHEAD abc\nbranch refs/heads/main\n"
        raise AssertionError(args)

    monkeypatch.setattr(guard, "_git", fake_git)

    rc, message = guard._add_registered(target, "feat/chat-demo", "origin/main")

    assert rc == 1
    assert "not registered" in message
    assert not target.exists()


def test_trunk_branch_default_and_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_AUTODELIVER_TRUNK", raising=False)
    assert guard._trunk_branch() == "main"
    monkeypatch.setenv("WORKTREE_AUTODELIVER_TRUNK", "develop")
    assert guard._trunk_branch() == "develop"


def test_cut_base_disabled_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKTREE_CUT_FROM_TRUNK", "0")
    # Disabled path returns "" WITHOUT any fetch/git call.
    assert guard._cut_base() == ""


def test_sync_local_trunk_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKTREE_SYNC_LOCAL_TRUNK", "0")
    assert guard._sync_local_trunk("main") == ""


def test_sync_local_trunk_skips_non_trunk_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_SYNC_LOCAL_TRUNK", raising=False)
    monkeypatch.delenv("WORKTREE_AUTODELIVER_TRUNK", raising=False)
    # On a feature branch (not the trunk) the primary is never ff'd.
    assert guard._sync_local_trunk("feat/x") == ""


def test_default_worktree_path_is_registered_sibling_style(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHAT_WORKTREE_ROOT", raising=False)
    monkeypatch.delenv("WORKTREE_DIR_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)

    slug = "chat-20260615-abcdef12"

    assert guard._branch_name(slug) == f"feat/{slug}"
    assert guard._worktree_path(slug) == guard.REPO_ROOT.parent / f"{guard.REPO_ROOT.name}-{slug}"
    assert ".chat-worktrees" not in str(guard._worktree_path(slug))


def test_worktree_branch_prefix_override_normalizes_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKTREE_BRANCH_PREFIX", "codex")

    assert guard._branch_name("chat-1") == "codex/chat-1"


def test_is_registered_worktree_normalizes_porcelain_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = tmp_path / "Agentic-Workflow-FRESH-chat-1"
    porcelain = f"worktree {target.as_posix()}\nHEAD abc123\nbranch refs/heads/feat/chat-1\n"

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        assert args == ("worktree", "list", "--porcelain")
        return 0, porcelain

    monkeypatch.setattr(guard, "_git", fake_git)

    assert guard._is_registered_worktree(target)


def test_add_registered_removes_unregistered_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("CHAT_WORKTREE_ROOT", str(tmp_path))
    monkeypatch.setenv("WORKTREE_DIR_PREFIX", "Agentic-Workflow-FRESH")
    target = guard._worktree_path("chat-unregistered")
    target.mkdir()

    calls: list[tuple[str, ...]] = []

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        calls.append(args)
        if args[:2] == ("worktree", "add"):
            return 0, "created"
        if args == ("worktree", "list", "--porcelain"):
            return 0, ""
        return 1, ""

    monkeypatch.setattr(guard, "_git", fake_git)

    rc, out = guard._add_registered(target, "feat/chat-unregistered", "origin/main")

    assert rc == 1
    assert "not registered" in out
    assert not target.exists()
    assert calls[0][:2] == ("worktree", "add")
