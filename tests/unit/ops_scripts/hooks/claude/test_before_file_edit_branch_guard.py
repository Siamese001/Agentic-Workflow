"""Tests for the named-worktree edit guard remediation text."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[5]
_HOOK = _REPO / ".claude" / "hooks" / "before_file_edit_branch_guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("branch_guard_under_test", _HOOK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["branch_guard_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


guard = _load()


def test_remediation_defaults_to_claude_owned_worktree(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)

    text = guard._remediation_example("governance-hooks")

    assert "-b claude-governance-hooks" in text
    assert "Agentic-Workflow-FRESH-worktrees" in text
    assert "claude-governance-hooks" in text


def test_remediation_can_render_codex_owned_worktree(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.setenv("WORKTREE_IDE_OWNER", "codex")

    text = guard._remediation_example("governance-hooks")

    assert "-b codex-governance-hooks" in text
    assert "Agentic-Workflow-FRESH-worktrees" in text
    assert "codex-governance-hooks" in text


def test_worktree_branch_prefix_override_normalizes_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)
    monkeypatch.setenv("WORKTREE_BRANCH_PREFIX", "codex/")

    assert guard._branch_name("governance-hooks") == "codex-governance-hooks"


def test_contract_accepts_matching_high_signal_agent_branch(tmp_path: Path) -> None:
    wt = tmp_path / "claude-apps-rg-anthropic-streaming-transport"
    wt.mkdir()

    assert guard._contract_violations("claude-apps-rg-anthropic-streaming-transport", wt) == []


def test_contract_accepts_codex_branch_when_owner_is_codex(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("WORKTREE_IDE_OWNER", "codex")
    wt = tmp_path / "codex-worktree-naming-contract"
    wt.mkdir()

    assert guard._contract_violations("codex-worktree-naming-contract", wt) == []


def test_contract_rejects_codex_branch_in_default_claude_mode(tmp_path: Path) -> None:
    wt = tmp_path / "codex-worktree-naming-contract"
    wt.mkdir()

    violations = guard._contract_violations("codex-worktree-naming-contract", wt)

    assert "branch must start with `claude-` for this agent" in violations


def test_contract_rejects_slash_namespace(tmp_path: Path) -> None:
    wt = tmp_path / "apps-rg"
    wt.mkdir()

    violations = guard._contract_violations("claude/apps-rg", wt)

    assert "branch must not contain slash path separators" in violations
    assert "branch must start with `claude-` for this agent" in violations


def test_contract_rejects_generated_low_signal_name(tmp_path: Path) -> None:
    wt = tmp_path / "claude-pedantic-archimedes-7c4f6c"
    wt.mkdir()

    violations = guard._contract_violations("claude-pedantic-archimedes-7c4f6c", wt)

    assert "branch topic must be high-signal, not a generated or generic name" in violations


def test_contract_rejects_folder_branch_mismatch(tmp_path: Path) -> None:
    wt = tmp_path / "different-folder"
    wt.mkdir()

    violations = guard._contract_violations("codex-worktree-naming-contract", wt)

    assert "worktree folder basename must exactly equal the local branch name" in violations
