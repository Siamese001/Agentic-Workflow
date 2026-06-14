"""Wave 4.2 — unit tests for headline_quality_x2.

Covers the deterministic headline positioning-rigor gates: positioning-family
preservation, the SVP Engineering seniority floor, the narrowing IT-label
blocklist, and the WARN-mode E0/base-resume n-gram overlap gates.
"""

from __future__ import annotations

from apps_rg.runtime.validators.headline_quality_x2 import (
    BASE_NGRAM_THRESHOLD,
    E0_NGRAM_THRESHOLD,
    HeadlineQualityResult,
    NARROWING_IT_LABELS,
    POSITIONING_FAMILIES,
    check_headline_base_ngram_overlap,
    check_headline_e0_ngram_overlap,
    check_headline_no_narrowing_it_labels,
    check_headline_positioning_families,
    check_headline_seniority_floor,
)

_STRONG = (
    "SVP Engineering | Agentic AI Platforms | Runtime Governance | "
    "Distributed AI Infrastructure"
)


class TestPositioningFamilies:
    def test_strong_headline_passes(self) -> None:
        res = check_headline_positioning_families(_STRONG)
        assert isinstance(res, HeadlineQualityResult)
        assert res.passed is True
        assert len(res.signals) >= 2

    def test_weak_headline_fails(self) -> None:
        res = check_headline_positioning_families("SVP Engineering | Cooking | Hiking | Travel")
        assert res.passed is False
        assert res.failure_reason is not None

    def test_min_families_threshold_enforced(self) -> None:
        # one family signal, require 2 -> fail
        res = check_headline_positioning_families(
            "SVP Engineering | Runtime Governance | Cooking | Hiking",
            min_families=2,
        )
        assert res.passed is False

    def test_gate_id(self) -> None:
        res = check_headline_positioning_families(_STRONG)
        assert res.gate_id == "x2_headline_positioning_family_preserved"

    def test_token_level_signal_matches(self) -> None:
        # "enterprise" token signal should match enterprise_ai_architecture family
        res = check_headline_positioning_families(
            "SVP Engineering | Enterprise systems | Agentic platform | Governance gates"
        )
        assert res.passed is True


class TestSeniorityFloor:
    def test_svp_engineering_prefix_passes(self) -> None:
        res = check_headline_seniority_floor(_STRONG)
        assert res.passed is True
        assert res.signals == ["svp_engineering_present"]

    def test_other_prefix_fails(self) -> None:
        res = check_headline_seniority_floor("Senior Engineer | A | B | C")
        assert res.passed is False
        assert res.failure_reason is not None

    def test_no_pipe_single_segment(self) -> None:
        assert check_headline_seniority_floor("SVP Engineering").passed is True
        assert check_headline_seniority_floor("Director").passed is False

    def test_gate_id(self) -> None:
        assert (
            check_headline_seniority_floor(_STRONG).gate_id
            == "x2_headline_seniority_floor"
        )


class TestNarrowingItLabels:
    def test_clean_headline_passes(self) -> None:
        res = check_headline_no_narrowing_it_labels(_STRONG)
        assert res.passed is True
        assert res.observed_value == "none"

    def test_narrowing_label_fails(self) -> None:
        res = check_headline_no_narrowing_it_labels(
            "SVP Engineering | IT Strategy | Digital Transformation | Foo"
        )
        assert res.passed is False
        assert "it strategy" in res.observed_value
        assert "digital transformation" in res.observed_value

    def test_case_insensitive(self) -> None:
        res = check_headline_no_narrowing_it_labels("Foo | DATA MODERNIZATION | Bar")
        assert res.passed is False

    def test_blocklist_is_frozenset(self) -> None:
        assert isinstance(NARROWING_IT_LABELS, frozenset)
        assert "it strategy" in NARROWING_IT_LABELS


class TestNgramOverlapGates:
    def test_e0_warn_mode_passes_despite_overlap(self) -> None:
        # heavy overlap but warn_only -> passed True, failure_reason populated
        ref = "SVP Engineering | Lakehouse Microservices Architecture | AI Lifecycle Standardization | X"
        res = check_headline_e0_ngram_overlap(ref, [ref], warn_only=True)
        assert res.passed is True
        assert res.signals == ["warn_mode"]

    def test_e0_hard_mode_blocks_overlap(self) -> None:
        ref = "SVP Engineering | Lakehouse Microservices Architecture | AI Lifecycle Standardization | X"
        res = check_headline_e0_ngram_overlap(ref, [ref], warn_only=False)
        assert res.passed is False
        assert res.failure_reason is not None

    def test_e0_empty_references_passes(self) -> None:
        res = check_headline_e0_ngram_overlap("anything", [], warn_only=False)
        assert res.passed is True
        assert res.observed_value == 0.0

    def test_base_empty_references_passes(self) -> None:
        res = check_headline_base_ngram_overlap("anything", [], warn_only=False)
        assert res.passed is True

    def test_base_hard_mode_blocks_overlap(self) -> None:
        ref = "alpha beta gamma delta epsilon zeta eta theta"
        res = check_headline_base_ngram_overlap(ref, [ref], warn_only=False)
        assert res.passed is False

    def test_thresholds_in_range(self) -> None:
        assert 0.0 < E0_NGRAM_THRESHOLD < 1.0
        assert 0.0 < BASE_NGRAM_THRESHOLD < 1.0


class TestPositioningFamiliesConstant:
    def test_families_are_frozensets(self) -> None:
        assert all(isinstance(v, frozenset) for v in POSITIONING_FAMILIES.values())
        assert "runtime_governance" in POSITIONING_FAMILIES
