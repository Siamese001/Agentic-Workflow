"""Tests for C0 invariants, quality gates, and failure-mode catalog."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.c0_context.safety import (
    FAILURE_MODE_PREVENTIONS,
    GATE_FUNCTIONS,
    InvariantViolationError,
    assert_all_invariants,
    failure_modes_match_spec_count,
    gate_g0_scope,
    gate_g1_acl,
    gate_g2_fresh,
    gate_g3_exact,
    gate_g4_dense,
    gate_g5_graph,
    gate_g6_cite,
    gate_g7_conflict,
    gate_g8_cover,
    gate_g9_budget,
    gate_g10_inject,
    gates_match_spec_count,
    i1_retrieval_only,
    i2_retrieved_data_not_instruction,
    i3_lineage_preserved,
    i4_dense_alone_not_enough_for_high_stakes,
    i5_exact_claims_need_sparse_or_metadata,
    i6_graph_bounded,
    i7_contradictions_surfaced,
    i8_weak_evidence_stays_weak,
    i9_one_refine_loop,
    i10_no_self_authorize_route,
    i11_output_is_contract_not_answer,
    i12_only_verified_to_prompt_assembly,
)
from agentic_core.L1_cognition.c0_context.types import (
    ContradictionFlag,
    ContradictionType,
    EvidenceClass,
    EvidenceItem,
    FinalEvidenceContract,
    RecommendedDisposition,
    ScoreBreakdown,
    SupportStatus,
)


def _evidence(
    *,
    eid: str = "e1",
    source: str = "doc:a",
    span: str = "L10",
    lane: str = "dense",
    acl: str = "cleared",
    cls: EvidenceClass = EvidenceClass.MUST_USE,
    authority: float = 0.9,
    fresh: str = "fresh",
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=eid,
        source_id=source,
        source_class="docs",
        span_ref=span,
        quote_or_summary="...",
        retrieval_lane=lane,
        authority_score=authority,
        freshness_status=fresh,
        acl_status=acl,
        token_cost=10,
        evidence_class=cls,
    )


def _contract(
    *,
    status: SupportStatus = SupportStatus.PASS,
    score: float = 0.9,
    evidence: tuple[EvidenceItem, ...] = (),
    flags: tuple[ContradictionFlag, ...] = (),
    refine: int = 0,
    extras: dict[str, str] | None = None,
) -> FinalEvidenceContract:
    return FinalEvidenceContract(
        contract_id="c1",
        route_id="R3_GROUNDED",
        route_replay_key="rk",
        policy_hash="ph",
        blueprint_hash="bh",
        status=status,
        support_score=score,
        score_breakdown=ScoreBreakdown(),
        evidence=evidence,
        contradiction_flags=flags,
        unresolved_gaps=(),
        recommended_disposition=RecommendedDisposition.PROCEED,
        refine_attempts=refine,
        extras=extras or {"content_classification": "data"},
    )


# ---------- INVARIANTS I1..I12 ----------


def test_i1_blocked_when_final_answer_extras() -> None:
    assert i1_retrieval_only(_contract(extras={"content_classification": "data"})) is True
    assert i1_retrieval_only(
        _contract(extras={"content_classification": "data", "final_answer": "no"})
    ) is False


def test_i2_data_classification() -> None:
    assert i2_retrieved_data_not_instruction({"content_classification": "data"}) is True
    assert i2_retrieved_data_not_instruction({"content_classification": "instruction"}) is False
    assert i2_retrieved_data_not_instruction({}) is True  # default = data


def test_i3_lineage_required_fields() -> None:
    assert i3_lineage_preserved(_evidence()) is True
    assert i3_lineage_preserved(_evidence(source="")) is False
    assert i3_lineage_preserved(_evidence(acl="")) is False
    assert i3_lineage_preserved(_evidence(lane="")) is False


def test_i4_dense_only_blocks_high_stakes() -> None:
    assert i4_dense_alone_not_enough_for_high_stakes(
        high_stakes=True, retrieval_lanes_used=frozenset({"dense"}),
    ) is False
    assert i4_dense_alone_not_enough_for_high_stakes(
        high_stakes=True, retrieval_lanes_used=frozenset({"dense", "sparse"}),
    ) is True
    assert i4_dense_alone_not_enough_for_high_stakes(
        high_stakes=False, retrieval_lanes_used=frozenset({"dense"}),
    ) is True


def test_i5_exact_claim_needs_sparse_or_metadata() -> None:
    assert i5_exact_claims_need_sparse_or_metadata(
        has_exact_claim=True, retrieval_lanes_used=frozenset({"dense"}),
    ) is False
    assert i5_exact_claims_need_sparse_or_metadata(
        has_exact_claim=True, retrieval_lanes_used=frozenset({"sparse"}),
    ) is True
    assert i5_exact_claims_need_sparse_or_metadata(
        has_exact_claim=False, retrieval_lanes_used=frozenset({"dense"}),
    ) is True


def test_i6_graph_bounded() -> None:
    assert i6_graph_bounded(hops_used=2, max_hops=3) is True
    assert i6_graph_bounded(hops_used=4, max_hops=3) is False
    assert i6_graph_bounded(hops_used=-1, max_hops=3) is False


def test_i7_conflicted_must_have_flags() -> None:
    flag = ContradictionFlag(ContradictionType.SOURCE, "a", "b", 0.7, "x")
    assert i7_contradictions_surfaced(_contract(status=SupportStatus.CONFLICTED, flags=(flag,))) is True
    assert i7_contradictions_surfaced(_contract(status=SupportStatus.CONFLICTED, flags=())) is False
    assert i7_contradictions_surfaced(_contract(status=SupportStatus.PASS, flags=())) is True


def test_i8_weak_score_capped() -> None:
    assert i8_weak_evidence_stays_weak(_contract(status=SupportStatus.WEAK, score=0.5)) is True
    assert i8_weak_evidence_stays_weak(_contract(status=SupportStatus.WEAK, score=0.9)) is False


def test_i9_refine_budget() -> None:
    assert i9_one_refine_loop(_contract(refine=1), max_attempts=1) is True
    assert i9_one_refine_loop(_contract(refine=2), max_attempts=1) is False


def test_i10_no_self_authorize() -> None:
    assert i10_no_self_authorize_route(_contract()) is True
    assert i10_no_self_authorize_route(
        _contract(extras={"content_classification": "data", "self_authorized_route_change": "yes"}),
    ) is False


def test_i11_no_final_answer_text() -> None:
    assert i11_output_is_contract_not_answer(_contract()) is True
    assert i11_output_is_contract_not_answer(
        _contract(extras={"content_classification": "data", "final_answer_text": "..."}),
    ) is False


def test_i12_evidence_acl_required() -> None:
    assert i12_only_verified_to_prompt_assembly(_contract(evidence=(_evidence(),))) is True
    assert i12_only_verified_to_prompt_assembly(
        _contract(evidence=(_evidence(acl=""),)),
    ) is False


def test_assert_all_invariants_passes() -> None:
    contract = _contract(evidence=(_evidence(),))
    assert_all_invariants(contract)  # no raise


def test_assert_all_invariants_raises_on_violation() -> None:
    bad = _contract(status=SupportStatus.WEAK, score=0.95, evidence=(_evidence(),))
    with pytest.raises(InvariantViolationError):
        assert_all_invariants(bad)


# ---------- QUALITY GATES G0..G10 ----------


def test_g0_scope() -> None:
    assert gate_g0_scope(route_allows_retrieval=True).passed is True
    assert gate_g0_scope(route_allows_retrieval=False).passed is False


def test_g1_acl() -> None:
    assert gate_g1_acl(all_sources_acl_cleared=True).passed is True
    assert gate_g1_acl(all_sources_acl_cleared=False).passed is False


def test_g2_fresh() -> None:
    assert gate_g2_fresh(freshness_satisfied=True).passed is True
    assert gate_g2_fresh(freshness_satisfied=False).passed is False


def test_g3_exact_no_claim_passes() -> None:
    assert gate_g3_exact(has_exact_claim=False, sparse_or_metadata_present=False).passed is True
    assert gate_g3_exact(has_exact_claim=True, sparse_or_metadata_present=True).passed is True
    assert gate_g3_exact(has_exact_claim=True, sparse_or_metadata_present=False).passed is False


def test_g4_dense_threshold() -> None:
    assert gate_g4_dense(dense_relevance_score=0.5).passed is True
    assert gate_g4_dense(dense_relevance_score=0.1).passed is False


def test_g5_graph_bounded() -> None:
    assert gate_g5_graph(hops_used=2, max_hops=3).passed is True
    assert gate_g5_graph(hops_used=4, max_hops=3).passed is False


def test_g6_cite() -> None:
    assert gate_g6_cite(all_anchors_resolve=True).passed is True
    assert gate_g6_cite(all_anchors_resolve=False).passed is False


def test_g7_conflict() -> None:
    assert gate_g7_conflict(contradictions_surfaced=True).passed is True


def test_g8_coverage() -> None:
    assert gate_g8_cover(coverage_score=0.6).passed is True
    assert gate_g8_cover(coverage_score=0.2).passed is False


def test_g9_budget() -> None:
    assert gate_g9_budget(must_use_fits_budget=True).passed is True
    assert gate_g9_budget(must_use_fits_budget=False).passed is False


def test_g10_inject() -> None:
    assert gate_g10_inject(retrieved_text_classified_data=True).passed is True
    assert gate_g10_inject(retrieved_text_classified_data=False).passed is False


def test_gates_match_spec_count() -> None:
    assert gates_match_spec_count() is True
    assert len(GATE_FUNCTIONS) == 11


def test_failure_modes_match_spec_count() -> None:
    assert failure_modes_match_spec_count() is True
    assert len(FAILURE_MODE_PREVENTIONS) == 14
