 ""Unit tests: SVP IT strategy targeting appendix (executive_summary PA)."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_pa import (
    format_strategy_executive_targeting_appendix,
    is_strategy_executive_target_title,
)


def test_is_strategy_title_brown_brown_svp() -> None:
    title = "SVP IT Strategy & Innovation"
    assert is_strategy_executive_target_title(title) is True
    appendix = format_strategy_executive_targeting_appendix(title)
    assert "technology strategy" in appendix.lower()
    assert "NOT PROOF" in appendix


def test_is_strategy_title_negative_engineering_manager() -> None:
    assert is_strategy_executive_target_title("Senior Engineering Manager") is False
    assert format_strategy_executive_targeting_appendix("Senior Engineering Manager") == ""
