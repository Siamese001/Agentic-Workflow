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
    monkeypatch.delenv("WORKTREE_DIR_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)

    text = guard._remediation_example("governance")

    assert "-b claude/governance" in text
    assert "Agentic-Workflow-FRESH-claude-governance" in text


def test_remediation_can_render_codex_owned_worktree(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKTREE_BRANCH_PREFIX", raising=False)
    monkeypatch.delenv("WORKTREE_DIR_PREFIX", raising=False)
    monkeypatch.setenv("WORKTREE_IDE_OWNER", "codex")

    text = guard._remediation_example("governance")

    assert "-b codex/governance" in text
    assert "Agentic-Workflow-FRESH-codex-governance" in text
