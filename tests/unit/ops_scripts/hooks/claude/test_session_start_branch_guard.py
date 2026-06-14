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
