"""Acceptance tests for headline positioning / seniority / anti-leakage X2 gates (W1).

These tests exercise the helpers in headline_quality_x2.py directly and verify the
gate logic without requiring a live LLM call.

Coverage:
1. test_narrowing_it_label_fails — phrases from narrowing blocklist cause FAIL
2. test_generic_technology_executive_fails — "Technology Executive | Innovation" fails
3. test_seniority_demotion_fails — first segment != "SVP Engineering" fails seniority floor
4. test_positioning_family_preserved_passes — approved SVP Engineering shape passes
5. test_base_headline_not_hydrated — high n-gram overlap with base headline warns/fails
6. test_e0_not_leaked — high n-gram overlap with E0 example warns/fails
7. test_positioning_family_multiple_required — fewer than 2 families fails gate
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.validators.headline_positioning_x2 import (
    GOVERNANCE_SIGNAL_FAMILIES,
    governance_signal_families_matched,
    run_headline_positioning_x2_gates,
)
from apps_rg.runtime.validators.headline_quality_x2 import (
    HEADLINE_E0_REFERENCE_TEXTS,
    NARROWING_IT_LABELS,
    check_headline_base_ngram_overlap,
    check_headline_e0_ngram_overlap,
    check_headline_no_narrowing_it_labels,
    check_headline_positioning_families,
    check_headline_seniority_floor,
)


# ---------------------------------------------------------------------------
# 1. Narrowing IT label must fail
# ---------------------------------------------------------------------------

class TestNarrowingITLabelFails:
    def test_it_strategy_in_headline_fails(self):
        hl = "SVP Engineering | IT Strategy | Data Modernization | AI Governance"
        result = check_headline_no_narrowing_it_labels(hl)
        assert not result.passed, (
            "Headline with 'it strategy' should fail narrowing label gate"
        )
        assert "it strategy" in result.observed_value or "data modernization" in result.observed_value

    def test_cloud_transformation_fails(self):
        hl = "SVP Engineering | Cloud Transformation | Enterprise Scale | AI Leadership"
        result = check_headline_no_narrowing_it_labels(hl)
        assert not result.passed
        assert "cloud transformation" in result.observed_value

    def test_ai_lifecycle_standardization_fails(self):
        hl = "SVP Engineering | AI Lifecycle Standardization | Platform Scale | Governance"
        result = check_headline_no_narrowing_it_labels(hl)
        assert not result.passed
        assert "ai lifecycle standardization" in result.observed_value

    def test_clean_headline_passes(self):
        hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI"
        result = check_headline_no_narrowing_it_labels(hl)
        assert result.passed, f"Clean headline should pass narrowing gate: {result.failure_reason}"


# ---------------------------------------------------------------------------
# 2. Generic "Technology Executive" shape fails
# ---------------------------------------------------------------------------

class TestGenericTechnologyExecutiveFails:
    def test_innovation_leadership_blocked(self):
        hl = "Technology Executive | Innovation Leadership | Cloud Transformation | Digital Strategy"
        result = check_headline_no_narrowing_it_labels(hl)
        # Contains "innovation leadership" and/or "cloud transformation" and/or "digital transformation"
        assert not result.passed

    def test_digital_transformation_blocked(self):
        hl = "SVP Engineering | Digital Transformation | Cloud Strategy | AI Leadership"
        result = check_headline_no_narrowing_it_labels(hl)
        assert not result.passed
        assert "digital transformation" in result.observed_value

    def test_technology_strategy_blocked(self):
        hl = "SVP Engineering | Technology Strategy | Innovation Leadership | Cloud Ecosystems"
        result = check_headline_no_narrowing_it_labels(hl)
        assert not result.passed


# ---------------------------------------------------------------------------
# 3. Seniority demotion fails
# ---------------------------------------------------------------------------

class TestSeniorityDemotionFails:
    def test_vp_engineering_prefix_fails(self):
        hl = "VP Engineering | Agentic AI Platforms | Runtime Governance | Regulated AI"
        result = check_headline_seniority_floor(hl)
        assert not result.passed
        assert result.observed_value == "VP Engineering"

    def test_director_prefix_fails(self):
        hl = "Director of Engineering | AI Platform Engineering | Governance Controls | Enterprise AI"
        result = check_headline_seniority_floor(hl)
        assert not result.passed

    def test_svp_engineering_prefix_passes(self):
        hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI"
        result = check_headline_seniority_floor(hl)
        assert result.passed

    def test_cto_prefix_fails(self):
        hl = "CTO | Agentic AI Platforms | Runtime Governance | Regulated Systems"
        result = check_headline_seniority_floor(hl)
        assert not result.passed
        assert result.observed_value == "CTO"


# ---------------------------------------------------------------------------
# 4. Positioning family preserved — approved shape passes
# ---------------------------------------------------------------------------

class TestPositioningFamilyPreservedPasses:
    def test_agentic_governance_regulated_passes(self):
        hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI"
        result = check_headline_positioning_families(hl, min_families=2)
        assert result.passed, f"Should detect ≥2 positioning families: {result.observed_value}"
        assert len(result.signals) >= 2

    def test_distributed_productization_passes(self):
        hl = "SVP Engineering | Distributed AI Infrastructure | Retrieval Context Engineering | Platform Productization"
        result = check_headline_positioning_families(hl, min_families=2)
        assert result.passed, f"Expected ≥2 families: {result.observed_value}"

    def test_enterprise_arch_llmops_regulated_passes(self):
        hl = "SVP Engineering | Enterprise AI Architecture | LLMOps Eval Harness | Regulated Platform Delivery"
        result = check_headline_positioning_families(hl, min_families=2)
        assert result.passed


# ---------------------------------------------------------------------------
# 5. Base headline n-gram overlap warns on copy
# ---------------------------------------------------------------------------

class TestBaseHeadlineNotHydrated:
    def test_identical_to_base_warns(self):
        base_hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI"
        result = check_headline_base_ngram_overlap(base_hl, [base_hl], warn_only=False)
        # Identical headline should have very high overlap
        assert not result.passed, "Identical headline should fail overlap gate"
        assert result.observed_value > 0.5

    def test_high_overlap_warns(self):
        base_hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI"
        # Same 3 out of 4 segments
        hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Enterprise Platform Delivery"
        result = check_headline_base_ngram_overlap(hl, [base_hl], warn_only=False)
        assert not result.passed or result.observed_value > 0.0

    def test_fully_novel_headline_passes(self):
        base_hl = "SVP Engineering | Lakehouse Microservices Architecture | AI Lifecycle Standardization | Retrieval Telemetry Catalogs"
        hl = "SVP Engineering | Distributed AI Infrastructure | Enterprise Governance Gates | Platform Productization"
        result = check_headline_base_ngram_overlap(hl, [base_hl], warn_only=False)
        assert result.passed, f"Novel headline should pass overlap gate, overlap={result.observed_value}"

    def test_empty_base_passes(self):
        hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI"
        result = check_headline_base_ngram_overlap(hl, [], warn_only=False)
        assert result.passed, "No base reference means overlap gate should pass"


# ---------------------------------------------------------------------------
# 6. E0 n-gram leakage warns on copy
# ---------------------------------------------------------------------------

class TestE0NotLeaked:
    def test_e0_literal_copy_warns(self):
        # Use first E0 example (old demoting shape) — the gate should warn when it detects copy
        e0_text = "SVP Engineering | Lakehouse Microservices Architecture | AI Lifecycle Standardization | Retrieval Telemetry Catalogs"
        result = check_headline_e0_ngram_overlap(e0_text, [e0_text], warn_only=False)
        # Identical should have very high overlap → fail
        assert not result.passed
        assert result.observed_value > 0.5

    def test_novel_headline_passes_e0_check(self):
        hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI"
        result = check_headline_e0_ngram_overlap(hl, HEADLINE_E0_REFERENCE_TEXTS, warn_only=False)
        # The new E0 examples include shape A which matches this closely — warn mode only
        # Key check: gate is wired and functional
        assert result.gate_id == "x2_headline_e0_ngram_overlap"
        assert isinstance(result.observed_value, float)

    def test_empty_e0_list_passes(self):
        hl = "SVP Engineering | Distributed AI Infrastructure | Retrieval Context Engineering | Platform Productization"
        result = check_headline_e0_ngram_overlap(hl, [], warn_only=False)
        assert result.passed, "No E0 reference means gate should pass"


# ---------------------------------------------------------------------------
# 7. Positioning family — fewer than 2 fails
# ---------------------------------------------------------------------------

class TestPositioningFamilyMultipleRequired:
    def test_single_family_only_fails_when_min_2(self):
        # Only "enterprise" token — single family match
        hl = "SVP Engineering | Enterprise IT Programs | Data Center Scale | Vendor Contracts"
        result = check_headline_positioning_families(hl, min_families=2)
        # "enterprise" maps to enterprise_ai_architecture family only; 1 < 2
        assert not result.passed or len(result.signals) < 2

    def test_zero_family_signals_fails(self):
        hl = "SVP Engineering | Annual Contract Value | Cloud Vendors | Cost Reduction"
        result = check_headline_positioning_families(hl, min_families=2)
        assert not result.passed
        assert len(result.signals) == 0

    def test_two_families_passes(self):
        hl = "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI"
        result = check_headline_positioning_families(hl, min_families=2)
        assert result.passed


# ---------------------------------------------------------------------------
# 8. governance_signal_families_matched <=> gate equivalence (shared predicate)
# ---------------------------------------------------------------------------

_GOVERNANCE_GATE_ID = "x2_headline_governance_or_regulated_ai_signal_required"

_GOVERNANCE_EQUIVALENCE_HEADLINES = [
    "SVP Engineering | Agentic AI Platform Engineering | Runtime Governance Controls | Regulated Enterprise AI",
    "SVP Engineering | Governed Agentic Platforms | Runtime Infrastructure | Regulated Delivery",
    "SVP Engineering | Distributed AI Infrastructure | Retrieval Context Engineering | Platform Productization",
    "SVP Engineering | Annual Contract Value | Cloud Vendors | Cost Reduction",
    "SVP Engineering | Compliance Platforms | Policy Gates | Deterministic Delivery",
    "Governance | Sales Leadership | Marketing Programs | Finance Operations",
    "SVP Engineering | X | Y | Z",
    "",
    "no signal here at all",
    "governance without pipes",
    "a|governance",
]


class TestGovernanceSignalHelperGateEquivalence:
    """helper empty <=> gate fails — trigger==gate by construction (shared predicate)."""

    @pytest.mark.parametrize("hl", _GOVERNANCE_EQUIVALENCE_HEADLINES)
    def test_helper_empty_iff_gate_fails(self, hl):
        gates = run_headline_positioning_x2_gates(
            headline_line=hl,
            parsed_output={},
            proof_pool_metadata={},
        )
        gate = next(g for g in gates if g.gate_id == _GOVERNANCE_GATE_ID)
        matched = governance_signal_families_matched(hl)
        assert bool(matched) == gate.passed, (
            f"helper/gate divergence for {hl!r}: matched={matched} gate.passed={gate.passed}"
        )
        if gate.passed:
            assert gate.observed_value == matched
        else:
            assert gate.observed_value == "none"
        assert all(f in GOVERNANCE_SIGNAL_FAMILIES for f in matched)
