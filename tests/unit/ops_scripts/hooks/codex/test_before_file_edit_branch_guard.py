"""Tests for the named-worktree edit guard remediation text."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[5]
_HOOK = _REPO / ".codex" / "hooks" / "before_file_edit_branch_guard.py"


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


def test_branch_prefix_override_cannot_change_default_claude_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("WORKTREE_IDE_OWNER", raising=False)
    monkeypatch.setenv("WORKTREE_BRANCH_PREFIX", "codex/")

    assert guard._branch_name("governance-hooks") == "claude-governance-hooks"


def test_branch_prefix_override_cannot_contradict_codex_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WORKTREE_IDE_OWNER", "codex")
    monkeypatch.setenv("WORKTREE_BRANCH_PREFIX", "claude/")

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


# --- app-scope segment -----------------------------------------------------------------------


def test_app_token_extracts_hyphenated_segment_from_apps_package() -> None:
    assert guard._app_token_for_path("apps_rg/section_generation.py") == "apps-rg"
    assert guard._app_token_for_path("C:/Git/x/apps_lic/config/x.yaml") == "apps-lic"
    # Backslash (Windows) paths normalise too.
    assert guard._app_token_for_path("apps_rg\\__main__.py") == "apps-rg"
    # Numeric app package (apps01) has no underscore to normalise.
    assert guard._app_token_for_path("apps01/worker.py") == "apps01"


def test_app_token_empty_for_core_and_infra_paths() -> None:
    assert guard._app_token_for_path("agentic_core/L4_persistence/x.py") == ""
    assert guard._app_token_for_path(".codex/hooks/before_file_edit_branch_guard.py") == ""
    assert guard._app_token_for_path("tests/_apps_contract/test_rg_x.py") == ""
    assert guard._app_token_for_path("") == ""


def test_contract_accepts_app_branch_for_matching_app_edit(tmp_path: Path) -> None:
    wt = tmp_path / "claude-apps-rg-competencies-finish"
    wt.mkdir()

    violations = guard._contract_violations(
        "claude-apps-rg-competencies-finish", wt, app_token="apps-rg"
    )

    assert violations == []


def test_contract_accepts_durable_app_hotspot_branch_for_later_waves(tmp_path: Path) -> None:
    wt = tmp_path / "claude-apps-rg-hotspot-tests"
    wt.mkdir()

    violations = guard._contract_violations(
        "claude-apps-rg-hotspot-tests", wt, app_token="apps-rg"
    )

    assert violations == []


def test_contract_rejects_app_branch_named_for_single_wave(tmp_path: Path) -> None:
    wt = tmp_path / "claude-apps-rg-wave4-tests"
    wt.mkdir()

    violations = guard._contract_violations(
        "claude-apps-rg-wave4-tests", wt, app_token="apps-rg"
    )

    assert any("not a wave-specific slice" in v for v in violations)
    assert any("claude-apps-rg-hotspot-tests" in v for v in violations)


def test_contract_rejects_app_branch_with_only_generic_test_scope(tmp_path: Path) -> None:
    wt = tmp_path / "claude-apps-rg-tests"
    wt.mkdir()

    violations = guard._contract_violations("claude-apps-rg-tests", wt, app_token="apps-rg")

    assert any("not only generic test/change tokens" in v for v in violations)


def test_contract_requires_app_segment_when_editing_app_file(tmp_path: Path) -> None:
    # High-signal, agent-owned, folder matches — but no apps-rg segment while editing apps_rg.
    wt = tmp_path / "claude-token-budget-fix"
    wt.mkdir()

    violations = guard._contract_violations("claude-token-budget-fix", wt, app_token="apps-rg")

    assert any("app-scoped edit under `apps_rg/`" in v for v in violations)


def test_contract_rejects_wrong_app_segment(tmp_path: Path) -> None:
    # Branch names apps-lic but the edit lands in apps_rg.
    wt = tmp_path / "claude-apps-lic-model-ssot"
    wt.mkdir()

    violations = guard._contract_violations(
        "claude-apps-lic-model-ssot", wt, app_token="apps-rg"
    )

    assert any("app-scoped edit under `apps_rg/`" in v for v in violations)


def test_contract_requires_scope_after_app_segment(tmp_path: Path) -> None:
    # `claude-apps-rg` names the app but carries no scope after it.
    wt = tmp_path / "claude-apps-rg"
    wt.mkdir()

    violations = guard._contract_violations("claude-apps-rg", wt, app_token="apps-rg")

    assert any("app-scoped edit under `apps_rg/`" in v for v in violations)


def test_contract_no_app_segment_required_for_core_edit(tmp_path: Path) -> None:
    # Core/governance edit (app_token == "") on a plain high-signal branch — still valid.
    wt = tmp_path / "claude-governance-hooks"
    wt.mkdir()

    assert guard._contract_violations("claude-governance-hooks", wt, app_token="") == []


def test_app_segment_not_double_reported_for_protected_or_slash_branch(tmp_path: Path) -> None:
    # A slash/wrong-prefix branch already fails on those grounds; the app check must not pile on.
    wt = tmp_path / "apps-rg"
    wt.mkdir()

    violations = guard._contract_violations("claude/apps-rg", wt, app_token="apps-rg")

    assert not any("app-scoped edit" in v for v in violations)
