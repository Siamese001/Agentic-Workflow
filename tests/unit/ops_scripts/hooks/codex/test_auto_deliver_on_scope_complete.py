"""Tests for the auto-deliver Stop hook (.codex/hooks/auto_deliver_on_scope_complete.py).

Covers the pure decision logic: marker detection (line-anchored, last-wins, ignores prose),
last-assistant transcript extraction, worktree resolution, idempotency state, deliver argv
construction, and mode mapping. The actual push is NOT exercised (no remote in unit tests).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[5]
_HOOK = _REPO / ".codex" / "hooks" / "auto_deliver_on_scope_complete.py"


def _load():
    spec = importlib.util.spec_from_file_location("auto_deliver", _HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hook = _load()


# --- marker detection ----------------------------------------------------------------------


def test_marker_branch_and_tests() -> None:
    text = "All done.\nSCOPE_COMPLETE: branch=feat/x tests=tests/unit/tools/git\n"
    assert hook.find_scope_complete(text) == ("feat/x", "tests/unit/tools/git")


def test_marker_branch_only() -> None:
    assert hook.find_scope_complete("SCOPE_COMPLETE: branch=chat/abc") == ("chat/abc", None)


def test_marker_ignores_backticked_prose() -> None:
    # The SessionStart instruction shows it back-ticked & inline — must NOT trigger.
    text = "emit `SCOPE_COMPLETE: branch=feat/x` when done"
    assert hook.find_scope_complete(text) is None


def test_marker_last_wins() -> None:
    text = "SCOPE_COMPLETE: branch=feat/a\nmore\nSCOPE_COMPLETE: branch=feat/b\n"
    assert hook.find_scope_complete(text) == ("feat/b", None)


def test_marker_absent() -> None:
    assert hook.find_scope_complete("nothing here") is None
    assert hook.find_scope_complete("") is None


# --- transcript extraction -----------------------------------------------------------------


def test_last_assistant_text_picks_final_assistant(tmp_path: Path) -> None:
    t = tmp_path / "t.jsonl"
    lines = [
        {"type": "user", "message": {"role": "user", "content": "hi"}},
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "first"}]}},
        {"type": "user", "message": {"role": "user", "content": "more"}},
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "SCOPE_COMPLETE: branch=feat/x"}]}},
    ]
    t.write_text("\n".join(json.dumps(x) for x in lines), encoding="utf-8")
    text = hook.last_assistant_text(str(t))
    assert "SCOPE_COMPLETE: branch=feat/x" in text
    assert "first" not in text  # only the LAST assistant message


def test_last_assistant_text_role_only_shape(tmp_path: Path) -> None:
    t = tmp_path / "t.jsonl"
    t.write_text(json.dumps({"role": "assistant", "content": "done here"}), encoding="utf-8")
    assert hook.last_assistant_text(str(t)) == "done here"


def test_last_assistant_text_missing_file() -> None:
    assert hook.last_assistant_text(None) == ""
    assert hook.last_assistant_text("/no/such/file.jsonl") == ""


# --- worktree resolution -------------------------------------------------------------------


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=30, check=True
    ).stdout.strip()


def test_resolve_worktree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@t.t")
    _git(root, "config", "user.name", "t")
    (root / "f.txt").write_text("x", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "init")
    wt = tmp_path / "wt-foo"
    _git(root, "worktree", "add", "-q", str(wt), "-b", "feat/foo")

    monkeypatch.setattr(hook, "REPO_ROOT", root)
    resolved = hook.resolve_worktree("feat/foo")
    assert resolved is not None and resolved.resolve() == wt.resolve()
    assert hook.resolve_worktree("feat/missing") is None


# --- idempotency state ---------------------------------------------------------------------


def test_delivered_state_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hook, "STATE_PATH", tmp_path / "state.json")
    assert hook.already_delivered("feat/x", "sha1") is False
    hook.record_delivered("feat/x", "sha1")
    assert hook.already_delivered("feat/x", "sha1") is True
    # A new tip on the same branch is NOT considered delivered.
    assert hook.already_delivered("feat/x", "sha2") is False


# --- argv + mode ---------------------------------------------------------------------------


def test_build_deliver_argv_with_tests() -> None:
    argv = hook.build_deliver_argv(Path("/wt"), "tests/unit/tools/git", "push", "main", False)
    assert argv[argv.index("--worktree") + 1] == str(Path("/wt"))
    assert argv[argv.index("--mode") + 1] == "push"
    assert argv[argv.index("--trunk") + 1] == "main"
    assert "--test" in argv
    assert "--dry-run" not in argv


def test_build_deliver_argv_skip_tests_and_dry() -> None:
    argv = hook.build_deliver_argv(Path("/wt"), "skip", "pr", "main", True)
    assert "--test" not in argv
    assert argv[argv.index("--mode") + 1] == "pr"
    assert "--dry-run" in argv


def test_resolve_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKTREE_AUTODELIVER", "1")
    assert hook._resolve_mode() == ("pr", False)
    monkeypatch.setenv("WORKTREE_AUTODELIVER", "pr")
    assert hook._resolve_mode() == ("pr", False)
    monkeypatch.setenv("WORKTREE_AUTODELIVER", "dry")
    assert hook._resolve_mode() == ("pr", True)
    monkeypatch.setenv("WORKTREE_AUTODELIVER", "push")
    assert hook._resolve_mode() == ("push", False)
    monkeypatch.delenv("WORKTREE_AUTODELIVER", raising=False)
    assert hook._resolve_mode() == (None, False)


def test_main_disabled_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_AUTODELIVER", raising=False)
    assert hook.main() == 0
