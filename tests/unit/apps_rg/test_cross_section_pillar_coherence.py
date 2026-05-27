"""Tests for W3 — F6: cross-section pillar coherence X2 gate."""

from __future__ import annotations

from apps_rg.runtime.aggregation.cross_section_x2 import (
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_WARN,
    check_cross_section_pillar_coherence,
)


def _section(section_id: str, pillar_ids: list[str]) -> dict:
    return {
        "section_id": section_id,
        "graph_targeting": {"pillar_hint_ids": pillar_ids},
    }


# ---------------------------------------------------------------------------
# UNKNOWN — fewer than 2 primary sections with pillar data
# ---------------------------------------------------------------------------


def test_coherence_unknown_when_no_sections():
    result = check_cross_section_pillar_coherence([])
    assert result.verdict == VERDICT_UNKNOWN
    assert result.gate_id == "x2_cross_section_pillar_coherence"


def test_coherence_unknown_when_only_one_primary_section():
    sections = [_section("executive_summary", ["AI_PLATFORM", "GOVERNANCE_RISK"])]
    result = check_cross_section_pillar_coherence(sections)
    assert result.verdict == VERDICT_UNKNOWN


def test_coherence_unknown_when_no_pillar_data_on_sections():
    sections = [
        _section("executive_summary", []),
        _section("competencies", []),
    ]
    result = check_cross_section_pillar_coherence(sections)
    assert result.verdict == VERDICT_UNKNOWN


def test_coherence_unknown_for_non_primary_sections_only():
    sections = [
        _section("certifications", ["AI_PLATFORM"]),
        _section("education", ["AI_PLATFORM"]),
    ]
    result = check_cross_section_pillar_coherence(sections)
    assert result.verdict == VERDICT_UNKNOWN


# ---------------------------------------------------------------------------
# PASS — high Jaccard similarity across primary sections
# ---------------------------------------------------------------------------


def test_coherence_pass_identical_pillar_sets():
    pillars = ["AI_PLATFORM", "GOVERNANCE_RISK", "CLOUD_INFRASTRUCTURE"]
    sections = [
        _section("executive_summary", pillars),
        _section("competencies", pillars),
        _section("unify_bullets", pillars),
    ]
    result = check_cross_section_pillar_coherence(sections)
    assert result.verdict == VERDICT_PASS
    assert result.observed == 1.0


def test_coherence_pass_at_threshold():
    # 2 shared out of (2+2-2)=2 union → Jaccard = 1.0; test with partial overlap ≥ 0.4
    sections = [
        _section("executive_summary", ["AI_PLATFORM", "GOVERNANCE_RISK", "CLOUD_INFRASTRUCTURE"]),
        _section("competencies", ["AI_PLATFORM", "GOVERNANCE_RISK"]),
    ]
    result = check_cross_section_pillar_coherence(sections)
    # intersection={AI_PLATFORM, GOVERNANCE_RISK} / union={AI_PLATFORM, GOVERNANCE_RISK, CLOUD} = 2/3 ≈ 0.667
    assert result.verdict == VERDICT_PASS
    assert result.observed is not None and result.observed >= 0.4


# ---------------------------------------------------------------------------
# WARN — low Jaccard similarity
# ---------------------------------------------------------------------------


def test_coherence_warn_completely_disjoint_pillars():
    sections = [
        _section("executive_summary", ["AI_PLATFORM", "CLOUD_INFRASTRUCTURE"]),
        _section("competencies", ["INSURANCE_DOMAIN", "FINANCE_DOMAIN"]),
    ]
    result = check_cross_section_pillar_coherence(sections)
    assert result.verdict == VERDICT_WARN
    assert result.observed == 0.0


def test_coherence_warn_below_threshold():
    # 1 shared out of 5 union → Jaccard = 0.2 < 0.4
    sections = [
        _section("executive_summary", ["A", "B", "C"]),
        _section("competencies", ["C", "D", "E", "F"]),
    ]
    result = check_cross_section_pillar_coherence(sections)
    assert result.verdict == VERDICT_WARN
    assert result.observed < 0.4
    assert "x2_cross_section_pillar_coherence" == result.gate_id


# ---------------------------------------------------------------------------
# Gate result structure
# ---------------------------------------------------------------------------


def test_coherence_gate_result_has_required_fields():
    sections = [
        _section("executive_summary", ["AI_PLATFORM"]),
        _section("competencies", ["GOVERNANCE_RISK"]),
    ]
    result = check_cross_section_pillar_coherence(sections)
    d = result.to_dict()
    assert d["gate_id"] == "x2_cross_section_pillar_coherence"
    assert "verdict" in d
    assert "threshold" in d
    assert "decisive_reason" in d
    assert "pass" in d


def test_coherence_gate_never_hard_fails():
    """Gate must never raise — even with unexpected section shapes."""
    broken_sections = [
        {"section_id": "executive_summary"},
        {"section_id": "competencies", "l2_output_snapshot": None},
        {"section_id": None},
        {},
    ]
    result = check_cross_section_pillar_coherence(broken_sections)  # must not raise
    assert result.verdict in (VERDICT_PASS, VERDICT_WARN, VERDICT_UNKNOWN)
