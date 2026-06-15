"""Tests for the non-mutating SessionStart worktree advisor."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
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


def test_default_named_worktree_path_and_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHAT_WORKTREE_ROOT", raising=False)
    monkeypatch.delenv("WORKTREE_DIR_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)

    assert guard._branch_name("apps-rg") == "claude/apps-rg"
    assert guard._worktree_path("apps-rg") == guard.REPO_ROOT.parent / "Agentic-Workflow-FRESH-claude-apps-rg"
    assert ".chat-worktrees" not in str(guard._worktree_path("apps-rg"))


def test_codex_owner_sets_branch_and_worktree_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_DIR_PREFIX", raising=False)
    monkeypatch.setenv("WORKTREE_IDE_OWNER", "codex")

    assert guard._branch_name("governance") == "codex/governance"
    assert guard._worktree_path("governance").name == "Agentic-Workflow-FRESH-codex-governance"


def test_worktree_branch_prefix_override_normalizes_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)
    monkeypatch.setenv("WORKTREE_BRANCH_PREFIX", "codex")

    assert guard._branch_name("governance") == "codex/governance"


def test_worktree_summary_parses_registered_worktrees(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    primary = tmp_path / "Agentic-Workflow-FRESH"
    lane = tmp_path / "Agentic-Workflow-FRESH-apps-rg"
    porcelain = (
        f"worktree {primary}\nbranch refs/heads/main\n\n"
        f"worktree {lane}\nbranch refs/heads/work/apps-rg\n"
    )

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        assert args == ("worktree", "list", "--porcelain")
        return 0, porcelain

    monkeypatch.setattr(guard, "_git", fake_git)

    summary = guard._worktree_summary()
    assert "main" in summary
    assert "work/apps-rg" in summary
    assert str(lane) in summary


def test_guidance_uses_named_worktree_not_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)

    def fake_summary() -> str:
        return "Existing worktrees:\n  - claude/apps-rg C:/Git/Agentic-Workflow-FRESH-claude-apps-rg"

    monkeypatch.setattr(guard, "_worktree_summary", fake_summary)

    msg = guard._guidance("main")

    assert "git worktree add" in msg
    assert "claude/apps-rg" in msg
    assert "Agentic-Workflow-FRESH-claude-apps-rg" in msg
    assert "Agentic-Workflow-FRESH-codex-apps-rg" in msg
    assert "chat/<timestamp>" in msg
    assert "auto-creates" in msg


def test_main_on_feature_branch_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        calls.append(args)
        return 0, "work/apps-rg"

    monkeypatch.setattr(guard, "_git", fake_git)
    monkeypatch.setattr(sys, "stdin", io.StringIO("{}"))

    assert guard.main() == 0
    assert calls == [("rev-parse", "--abbrev-ref", "HEAD")]


def test_main_on_protected_branch_emits_context_but_never_creates_worktree(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        calls.append(args)
        if args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "main"
        if args == ("rev-parse", "--git-common-dir"):
            return 0, r"C:\Git\Agentic-Workflow-FRESH\.git"
        if args == ("worktree", "list", "--porcelain"):
            return 0, "worktree C:/repo\nbranch refs/heads/main\n"
        raise AssertionError(args)

    monkeypatch.setattr(guard, "_git", fake_git)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": "abc"})))
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)

    assert guard.main() == 0
    payload = json.loads(out.getvalue())
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert "git worktree add" in context
    assert "claude/apps-rg" in context
    assert not any(call[:2] == ("worktree", "add") for call in calls)
