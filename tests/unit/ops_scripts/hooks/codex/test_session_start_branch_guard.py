"""Tests for the non-mutating SessionStart worktree advisor."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[5]
_HOOK = _REPO / ".codex" / "hooks" / "session_start_branch_guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("ssbg", _HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


guard = _load()


def test_default_named_worktree_path_and_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHAT_WORKTREE_ROOT", raising=False)
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)

    assert guard._branch_name("apps-rg") == "claude-apps-rg"
    assert guard._worktree_path("apps-rg") == (
        guard.REPO_ROOT.parent / "Agentic-Workflow-FRESH-worktrees" / "claude-apps-rg"
    )
    assert ".chat-worktrees" not in str(guard._worktree_path("apps-rg"))


def test_codex_owner_sets_branch_and_worktree_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.setenv("WORKTREE_IDE_OWNER", "codex")

    assert guard._branch_name("governance-hooks") == "codex-governance-hooks"
    assert guard._worktree_path("governance-hooks").name == "codex-governance-hooks"


def test_branch_prefix_override_cannot_change_default_claude_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)
    monkeypatch.setenv("WORKTREE_BRANCH_PREFIX", "codex")

    assert guard._branch_name("governance-hooks") == "claude-governance-hooks"


def test_branch_prefix_override_cannot_contradict_codex_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WORKTREE_IDE_OWNER", "codex")
    monkeypatch.setenv("WORKTREE_BRANCH_PREFIX", "claude")

    assert guard._branch_name("governance-hooks") == "codex-governance-hooks"


def test_worktree_summary_parses_registered_worktrees(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    primary = tmp_path / "Agentic-Workflow-FRESH"
    lane = tmp_path / "Agentic-Workflow-FRESH-worktrees" / "codex-apps-rg"
    porcelain = (
        f"worktree {primary}\nbranch refs/heads/main\n\n"
        f"worktree {lane}\nbranch refs/heads/codex-apps-rg\n"
    )

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        assert args == ("worktree", "list", "--porcelain")
        return 0, porcelain

    monkeypatch.setattr(guard, "_git", fake_git)

    summary = guard._worktree_summary()
    assert "main" in summary
    assert "codex-apps-rg" in summary
    assert str(lane) in summary


def test_guidance_uses_named_worktree_not_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)

    def fake_summary() -> str:
        return "Existing worktrees:\n  - claude-apps-rg C:/Git/Agentic-Workflow-FRESH-worktrees/claude-apps-rg"

    monkeypatch.setattr(guard, "_worktree_summary", fake_summary)

    msg = guard._guidance("main")

    assert "git worktree add" in msg
    assert "claude-apps-rg" in msg
    assert "codex-apps-rg" not in msg
    assert "do not use the other agent's prefix" in msg
    assert "chat/<timestamp>" in msg
    assert "auto-creates" in msg
    assert "per wave" in msg
    assert "apps-rg-hotspot-tests" in msg
    assert "apps-rg-wave4-tests" in msg


def test_main_on_feature_branch_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        calls.append(args)
        return 0, "claude-apps-rg"

    monkeypatch.setattr(guard, "_git", fake_git)
    monkeypatch.setattr(
        guard,
        "_worktree_root",
        lambda: Path(r"C:\Git\Agentic-Workflow-FRESH-worktrees\claude-apps-rg"),
    )
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
    assert "claude-apps-rg" in context
    assert not any(call[:2] == ("worktree", "add") for call in calls)


def test_main_on_noncanonical_branch_emits_warning_but_never_mutates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
        calls.append(args)
        if args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "claude/zen-mcnulty-654733"
        if args == ("rev-parse", "--show-toplevel"):
            return 0, r"C:\Git\Agentic-Workflow-FRESH-worktrees\zen-mcnulty-654733"
        if args == ("rev-parse", "--git-common-dir"):
            return 0, r"C:\Git\Agentic-Workflow-FRESH\.git"
        raise AssertionError(args)

    monkeypatch.setattr(guard, "_git", fake_git)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": "abc"})))
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)

    assert guard.main() == 0
    payload = json.loads(out.getvalue())
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert "worktree-naming-contract" in context
    assert "claude/zen-mcnulty-654733" in context
    assert "branch must not contain slash path separators" in context
    assert "branch must start with `claude-`" in context
    assert "worktree folder basename must exactly equal the local branch name" in context
    assert "PreToolUse edit guard will block" in context
    assert not any(call[:2] == ("worktree", "add") for call in calls)
