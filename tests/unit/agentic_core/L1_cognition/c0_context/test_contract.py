"""Tests for C0.5 verify + score + status decision + final contract."""

from __future__ import annotations

from agentic_core.L1_cognition.c0_context.contract import (
    aggregate_support_score,
    build_final_contract,
    contract_digest,
    decide_status,
    recommend_disposition,
    score,
    verify_evidence,
)
from agentic_core.L1_cognition.c0_context.shape_and_scan import (
    ConflictGapReport,
    scan_contradictions_and_gaps,
    stratify,
)
from agentic_core.L1_cognition.c0_context.types import (
    SCORE_DIMENSIONS,
    ContradictionFlag,
    ContradictionType,
    EvidenceClass,
    EvidenceItem,
    RecommendedDisposition,
    RouteContractView,
    SupportStatus,
    SupportTarget,
    UnresolvedGap,
)


def _ev(eid: str, **kw) -> EvidenceItem:
    base: dict = dict(
        evidence_id=eid,
        source_id="doc:a",
        source_class="docs",
        span_ref="L10",
        quote_or_summary="...",
        retrieval_lane="hybrid",
        authority_score=0.9,
        freshness_status="fresh",
        acl_status="cleared",
        token_cost=10,
        evidence_class=EvidenceClass.SUPPORTING,
    )
    base.update(kw)
    return EvidenceItem(**base)


def _route() -> RouteContractView:
    return RouteContractView(
        route_id="R3_GROUNDED",
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class="current",
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope="t",
        acl=("read",),
        region="us",
        data_class="standard",
        max_k=10,
        max_hops=2,
        max_parent_expansion=2,
        max_refine_attempts=1,
        max_latency_ms=2000,
        token_budget=4000,
        allowed_sources=frozenset({"docs"}),
        disallowed_sources=frozenset(),
        fallback_policy="caveat",
        route_replay_key="rk",
        policy_hash="ph",
        blueprint_hash="bh",
    )


# ---------- VERIFY ----------


def test_verify_rejects_missing_source() -> None:
    items = (_ev("a", source_id=""),)
    verified, rejected = verify_evidence(items)
    assert verified == ()
    assert len(rejected) == 1
    assert rejected[0][1] == "source_id_missing"


def test_verify_rejects_missing_span() -> None:
    items = (_ev("a", span_ref=""),)
    _, rejected = verify_evidence(items)
    assert rejected[0][1] == "span_ref_missing"


def test_verify_rejects_uncleared_acl() -> None:
    items = (_ev("a", acl_status="pending"),)
    _, rejected = verify_evidence(items)
    assert "acl_status" in rejected[0][1]


def test_verify_passes_clean_item() -> None:
    items = (_ev("a"),)
    verified, rejected = verify_evidence(items)
    assert len(verified) == 1
    assert rejected == ()


# ---------- SCORE ----------


def test_score_returns_all_eleven_dimensions() -> None:
    shaped = stratify([_ev("a", authority_score=0.9), _ev("b", authority_score=0.6)])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    d = breakdown.as_dict()
    assert set(d.keys()) == set(SCORE_DIMENSIONS)
    for v in d.values():
        assert 0.0 <= v <= 1.0


def test_score_zero_evidence_zero_dimensions() -> None:
    shaped = stratify([])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert breakdown.source_authority_score == 0.0
    assert breakdown.coverage_score == 0.0


def test_score_contradiction_risk_increases_with_count() -> None:
    shaped_one = stratify([
        _ev("m", authority_score=0.9, evidence_class=EvidenceClass.MUST_USE),
        _ev("c1", authority_score=0.8, evidence_class=EvidenceClass.CONTRADICTS),
    ])
    shaped_three = stratify([
        _ev("m", authority_score=0.9, evidence_class=EvidenceClass.MUST_USE),
        _ev("c1", authority_score=0.8, evidence_class=EvidenceClass.CONTRADICTS),
        _ev("c2", authority_score=0.8, evidence_class=EvidenceClass.CONTRADICTS),
        _ev("c3", authority_score=0.8, evidence_class=EvidenceClass.CONTRADICTS),
    ])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    s1 = score(shaped_one, report, support_target=SupportTarget.SOURCE_SUMMARY)
    s3 = score(shaped_three, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert s3.contradiction_risk > s1.contradiction_risk


def test_aggregate_score_clamped_to_unit() -> None:
    shaped = stratify([_ev(f"e{i}", authority_score=1.0) for i in range(10)])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert 0.0 <= aggregate_support_score(breakdown) <= 1.0


# ---------- DECIDE STATUS ----------


def test_status_blocked_when_blocked_flag() -> None:
    shaped = stratify([_ev("a", authority_score=0.9)])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert decide_status(shaped, report, breakdown, blocked=True) == SupportStatus.BLOCKED


def test_status_empty_when_no_evidence() -> None:
    shaped = stratify([])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert decide_status(shaped, report, breakdown) == SupportStatus.EMPTY


def test_status_conflicted_when_credible_conflict() -> None:
    shaped = stratify([_ev("a", authority_score=0.9)])
    report = ConflictGapReport(
        contradiction_flags=(ContradictionFlag(ContradictionType.SOURCE, "x", "y", 0.8, "..."),),
        unresolved_gaps=(),
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert decide_status(shaped, report, breakdown) == SupportStatus.CONFLICTED


def test_status_pass_when_strong_evidence() -> None:
    shaped = stratify([
        _ev(f"e{i}", authority_score=0.95, evidence_class=EvidenceClass.MUST_USE)
        for i in range(3)
    ])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert decide_status(shaped, report, breakdown) == SupportStatus.PASS


# ---------- RECOMMEND DISPOSITION ----------


def test_recommend_disposition_covers_all_six_statuses() -> None:
    mapping = {s: recommend_disposition(s) for s in SupportStatus}
    assert mapping[SupportStatus.PASS] == RecommendedDisposition.PROCEED
    assert mapping[SupportStatus.WEAK_WITH_CAVEATS] == RecommendedDisposition.PROCEED_WITH_CAVEAT
    assert mapping[SupportStatus.WEAK] == RecommendedDisposition.REROUTE
    assert mapping[SupportStatus.CONFLICTED] == RecommendedDisposition.HUMAN_REVIEW
    assert mapping[SupportStatus.EMPTY] == RecommendedDisposition.ABSTAIN
    assert mapping[SupportStatus.BLOCKED] == RecommendedDisposition.FALLBACK_R5


# ---------- BUILD FINAL CONTRACT ----------


def test_build_final_contract_carries_route_metadata() -> None:
    shaped = stratify([_ev("a", authority_score=0.9)])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    contract = build_final_contract(
        route=_route(), shaped=shaped, report=report, breakdown=breakdown,
    )
    assert contract.route_id == "R3_GROUNDED"
    assert contract.route_replay_key == "rk"
    assert contract.policy_hash == "ph"
    assert contract.blueprint_hash == "bh"
    assert contract.extras["content_classification"] == "data"


def test_build_final_contract_concatenates_classes() -> None:
    items = [
        _ev("m", authority_score=0.95, evidence_class=EvidenceClass.MUST_USE),
        _ev("s", authority_score=0.6, evidence_class=EvidenceClass.SUPPORTING),
        _ev("c", authority_score=0.8, evidence_class=EvidenceClass.CONTRADICTS),
        _ev("d", authority_score=0.5, evidence_class=EvidenceClass.DEFINITIONS),
    ]
    shaped = stratify(items)
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    contract = build_final_contract(
        route=_route(), shaped=shaped, report=report, breakdown=breakdown,
    )
    ids = {x.evidence_id for x in contract.evidence}
    assert {"m", "s", "c", "d"} <= ids


def test_contract_digest_stable() -> None:
    shaped = stratify([_ev("a", authority_score=0.9)])
    report = ConflictGapReport(contradiction_flags=(), unresolved_gaps=())
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    c1 = build_final_contract(
        route=_route(), shaped=shaped, report=report, breakdown=breakdown,
    )
    # Same contract-id, same digest
    d1 = contract_digest(c1)
    d2 = contract_digest(c1)
    assert d1 == d2
    assert len(d1) == 32  # 32-hex chars
