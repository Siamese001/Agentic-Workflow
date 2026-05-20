"""Contract tests for live-Qwen X2 repair helpers (no gate weakening)."""
from __future__ import annotations

from apps_rg.runtime.sections.competencies_lane_api import _fix_fact_id_typos
from apps_rg.runtime.sections.headline_lane import (
    deterministic_headline_word_count_expand,
    headline_word_count,
)
from apps_rg.runtime.validators.fact_id_typo_repair import repair_fact_id_against_allowlist


def test_repair_fact_governance_typo_against_allowlist() -> None:
    allowed = {"fact_governance_003", "fact_engineering_platform_005"}
    assert repair_fact_id_against_allowlist("fact_g_overnance_003", allowed) == "fact_governance_003"


def test_headline_word_count_expand_adds_one_word() -> None:
    hl = "SVP Engineering | Governed Agentic Platforms | Production Reliability | Enterprise Scale"
    assert headline_word_count(hl) == 9
    fixed = deterministic_headline_word_count_expand(hl)
    assert 10 <= headline_word_count(fixed) <= 13
    assert fixed.startswith("SVP Engineering | ")


def test_competencies_fix_fact_id_typos_delegates_to_allowlist() -> None:
    allowed = {"fact_governance_003"}
    assert _fix_fact_id_typos("fact_g_overnance_003", allowed) == "fact_governance_003"
