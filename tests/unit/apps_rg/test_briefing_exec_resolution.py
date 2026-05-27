"""Unit tests for exec briefing sibling resolution (Brown RCA R0/R1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.briefing_exec_resolution import (
    discover_exec_briefing_sibling,
    resolve_manual_brief_path,
)


def test_discover_exec_sibling_for_brown_full_brief() -> None:
    root = Path(__file__).resolve().parents[3]
    full = root / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    if not full.is_file():
        pytest.skip("Brown briefing fixtures missing")
    sibling = discover_exec_briefing_sibling(full)
    assert sibling is not None
    assert sibling.name.endswith("_briefing_exec.md")


def test_resolve_manual_brief_auto_swap(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[3]
    full = root / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    if not full.is_file():
        pytest.skip("Brown briefing fixtures missing")
    monkeypatch.setenv("APPS_RG_AUTO_EXEC_BRIEF", "1")
    res = resolve_manual_brief_path(str(full))
    assert res.swapped is True
    assert res.resolved_path.name.endswith("_briefing_exec.md")


def test_resolve_manual_brief_unchanged_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[3]
    full = root / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    if not full.is_file():
        pytest.skip("Brown briefing fixtures missing")
    monkeypatch.delenv("APPS_RG_AUTO_EXEC_BRIEF", raising=False)
    res = resolve_manual_brief_path(str(full), auto_exec=False)
    assert res.swapped is False
    assert res.resolved_path == full.resolve()
