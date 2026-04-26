"""Tests for c0_retrieval.verdicts — every enum + invariants table."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.verdicts import (
    CORE_INVARIANTS,
    EXACTNESS_REQUIRED,
    BlockedReason,
    C0Gate,
    ContradictionType,
    EvidenceClass,
    FailureMode,
    FreshnessClass,
    GapType,
    GraphRelation,
    RecommendedDisposition,
    RefineTactic,
    RetrievalLane,
    RetrievalMode,
    SourceClass,
    SupportStatus,
    SupportTarget,
)


class TestEnumCardinality:
    """Each enum should have the exact number of members the spec calls for."""

    def test_freshness_class_4_values(self):
        assert len(list(FreshnessClass)) == 4

    def test_support_target_8_values(self):
        # Spec lines 204-212.
        assert len(list(SupportTarget)) == 8

    def test_source_class_7_values(self):
        # Spec lines 214-221.
        assert len(list(SourceClass)) == 7

    def test_retrieval_mode_6_values(self):
        # Spec lines 223-229.
        assert len(list(RetrievalMode)) == 6

    def test_retrieval_lane_7_values(self):
        # Spec line 316.
        assert len(list(RetrievalLane)) == 7

    def test_graph_relation_14_values(self):
        # Spec lines 405-419.
        assert len(list(GraphRelation)) == 14

    def test_evidence_class_7_values(self):
        # Spec lines 499-506.
        assert len(list(EvidenceClass)) == 7

    def test_contradiction_type_8_values(self):
        # Spec lines 539-547.
        assert len(list(ContradictionType)) == 8

    def test_gap_type_9_values(self):
        # Spec lines 549-558.
        assert len(list(GapType)) == 9

    def test_support_status_6_values(self):
        # Spec lines 602-608.
        assert len(list(SupportStatus)) == 6

    def test_refine_tactic_8_values(self):
        # Spec lines 656-664.
        assert len(list(RefineTactic)) == 8

    def test_recommended_disposition_6_values(self):
        # Spec lines 1115-1121.
        assert len(list(RecommendedDisposition)) == 6

    def test_c0_gate_11_values(self):
        # Spec lines 909-923 (G0..G10).
        assert len(list(C0Gate)) == 11

    def test_failure_mode_14_values(self):
        # Spec lines 929-946.
        assert len(list(FailureMode)) == 14


class TestInvariantsTable:
    def test_12_core_invariants(self):
        assert len(CORE_INVARIANTS) == 12
        ids = [code for code, _ in CORE_INVARIANTS]
        assert ids == [f"C0.I{i}" for i in range(1, 13)]

    def test_each_invariant_has_text(self):
        for _code, text in CORE_INVARIANTS:
            assert text and isinstance(text, str)
            assert len(text) > 10


class TestExactnessRequired:
    def test_5_exactness_targets(self):
        # EXACT_QUOTE, POLICY_CLAUSE, CODE_LOCATION, INCIDENT_EVIDENCE, CLAIM_CHECK
        assert len(EXACTNESS_REQUIRED) == 5

    def test_summary_not_required(self):
        assert SupportTarget.SOURCE_SUMMARY not in EXACTNESS_REQUIRED

    @pytest.mark.parametrize(
        "target",
        [
            SupportTarget.EXACT_QUOTE,
            SupportTarget.POLICY_CLAUSE,
            SupportTarget.CODE_LOCATION,
            SupportTarget.INCIDENT_EVIDENCE,
            SupportTarget.CLAIM_CHECK,
        ],
    )
    def test_exact_targets_membership(self, target):
        assert target in EXACTNESS_REQUIRED


class TestStringValues:
    """All enums are str-typed for stable serialization."""

    def test_support_status_str(self):
        assert SupportStatus.PASS.value == "PASS"
        assert SupportStatus.WEAK_WITH_CAVEATS.value == "WEAK_WITH_CAVEATS"

    def test_recommended_disposition_str(self):
        assert RecommendedDisposition.PROCEED.value == "proceed"
        assert RecommendedDisposition.FALLBACK_R5.value == "fallback_R5"

    def test_blocked_reason_str(self):
        assert BlockedReason.GROUNDING_NOT_REQUIRED.value == "grounding_not_required"
        assert BlockedReason.INSTRUCTION_PAYLOAD.value == "instruction_payload"

    def test_c0_gate_prefix(self):
        for g in C0Gate:
            assert g.value.startswith("C0.G")

    def test_failure_mode_snake_case(self):
        for m in FailureMode:
            assert " " not in m.value
            assert m.value == m.value.lower()
