"""Tests for C0 closed vocabularies — every named constant in the spec."""

from __future__ import annotations

from agentic_core.L1_cognition.c0_context.types import (
    BOUND_PARAMS,
    DISALLOWED_REFINEMENTS,
    FAILURE_MODES,
    INVARIANTS,
    QUALITY_GATES,
    RETRIEVAL_MODES,
    SCORE_DIMENSIONS,
    SOURCE_CLASSES,
    ContradictionType,
    EvidenceClass,
    GapType,
    RecommendedDisposition,
    RefineTactic,
    SupportStatus,
    SupportTarget,
)


def test_support_status_six_values() -> None:
    expected = {"PASS", "WEAK", "WEAK_WITH_CAVEATS", "CONFLICTED", "EMPTY", "BLOCKED"}
    assert {s.value for s in SupportStatus} == expected


def test_support_target_eight_values() -> None:
    expected = {
        "EXACT_QUOTE",
        "SOURCE_SUMMARY",
        "POLICY_CLAUSE",
        "CODE_LOCATION",
        "INCIDENT_EVIDENCE",
        "ROOT_CAUSE_RANKING",
        "COMPARISON",
        "CLAIM_CHECK",
    }
    assert {t.value for t in SupportTarget} == expected


def test_source_classes_seven() -> None:
    assert SOURCE_CLASSES == frozenset(
        {"docs", "code", "logs", "tickets", "tables", "policy", "prior_artifacts"},
    )


def test_retrieval_modes_six() -> None:
    assert RETRIEVAL_MODES == frozenset(
        {"dense", "sparse", "metadata", "graph", "cache", "hybrid"},
    )


def test_bound_params_nine() -> None:
    assert len(BOUND_PARAMS) == 9
    assert BOUND_PARAMS[0] == "max_k"
    assert "max_graph_hops" in BOUND_PARAMS
    assert "max_refine_attempts" in BOUND_PARAMS


def test_evidence_class_seven_values() -> None:
    expected = {
        "MUST_USE",
        "SUPPORTING",
        "CONTRADICTS",
        "BACKGROUND",
        "DEFINITIONS",
        "LINEAGE",
        "EXCLUDED",
    }
    assert {c.value for c in EvidenceClass} == expected


def test_contradiction_type_eight_values() -> None:
    expected = {
        "version", "source", "scope", "time",
        "semantic", "code", "runtime", "policy",
    }
    assert {c.value for c in ContradictionType} == expected


def test_gap_type_nine_values() -> None:
    assert len({g.value for g in GapType}) == 9


def test_score_dimensions_eleven() -> None:
    assert len(SCORE_DIMENSIONS) == 11
    assert "direct_support_score" in SCORE_DIMENSIONS
    assert "ACL_confidence" in SCORE_DIMENSIONS


def test_recommended_disposition_six_values() -> None:
    expected = {
        "proceed", "proceed_with_caveat", "abstain",
        "fallback_R5", "reroute", "human_review",
    }
    assert {d.value for d in RecommendedDisposition} == expected


def test_refine_tactic_eight_values() -> None:
    expected = {
        "REWRITE", "BROADEN", "NARROW", "DECOMPOSE",
        "GRAPH_HOP", "HYBRIDIZE", "FRESHEN", "ABSTAIN",
    }
    assert {t.value for t in RefineTactic} == expected


def test_disallowed_refinements_seven_behaviors() -> None:
    assert len(DISALLOWED_REFINEMENTS) == 7
    assert "change_user_task" in DISALLOWED_REFINEMENTS
    assert "expand_tenant_acl_region" in DISALLOWED_REFINEMENTS


def test_quality_gates_eleven() -> None:
    assert len(QUALITY_GATES) == 11
    assert QUALITY_GATES[0] == "C0.G0_Scope"
    assert QUALITY_GATES[-1] == "C0.G10_Inject"


def test_invariants_twelve() -> None:
    assert len(INVARIANTS) == 12
    assert INVARIANTS == tuple(f"C0.I{i}" for i in range(1, 13))


def test_failure_modes_fourteen() -> None:
    assert len(FAILURE_MODES) == 14
    assert "dense_only_hallucination" in FAILURE_MODES
    assert "runtime_vs_design_mismatch" in FAILURE_MODES
