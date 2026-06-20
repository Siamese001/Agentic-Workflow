"""Contract tests for the apps_rg app-level agent guidance."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
APPS_RG_ROOT = REPO_ROOT / "apps_rg"


def test_apps_rg_agent_contract_is_codex_owned() -> None:
    agents = APPS_RG_ROOT / "AGENTS.md"
    claude = APPS_RG_ROOT / "AGENTS.md"

    assert agents.is_file(), "apps_rg/AGENTS.md must exist"
    assert not claude.exists(), "apps_rg/AGENTS.md should be removed"

    agents_text = agents.read_text(encoding="utf-8")

    assert "AGENTS.md" not in agents_text
    assert "AGENTIC_SPINE.md" in agents_text
    assert "LEAN_CORE.md" in agents_text
