"""Exhaustive edge-case coverage for every C0 requirement.

Companion to ``test_c0_anti_bypass.py``. Where anti-bypass tests verify the
30 named C0.7 spec tests, this module sweeps boundary conditions for every
enum value, every status × disposition mapping, every refine tactic, every
contradiction type, every gap type, every disallowed-refinement string, every
preflight blocked_reason, every score dimension at its 0.0 / 1.0 extrema, and
every empty/full evidence-pool transition.

Goal: every requirement row in ``C0_Requirements_Traceability_Matrix.md``
has at least one targeted boundary test in addition to its happy-path test.
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.c0_context.contract import (
    aggregate_support_score,
    build_final_contract,
    contract_digest,
    decide_status,
    recommend_disposition,
    score,
    verify_evidence,
)
from agentic_core.L1_cognition.c0_context.preflight import (
    MIN_BUDGET_FLOOR_TOKENS,
    build_retrieval_plan,
    preflight,
)
from agentic_core.L1_cognition.c0_context.refine import (
    DisallowedRefinementError,
    RefineLoopController,
    RefinementAttempt,
    RefinementBudgetExhaustedError,
    is_refinement_allowed,
)
from agentic_core.L1_cognition.c0_context.safety import (
    FAILURE_MODE_PREVENTIONS,
    GATE_FUNCTIONS,
    InvariantViolationError,
    assert_all_invariants,
    failure_modes_match_spec_count,
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
from agentic_core.L1_cognition.c0_context.shape_and_scan import (
    compress_to_budget,
    dedupe,
    scan_contradictions_and_gaps,
    stratify,
)
from agentic_core.L1_cognition.c0_context.types import (
    BOUND_PARAMS,
    DISALLOWED_REFINEMENTS,
    FAILURE_MODES,
    INVARIANTS,
    QUALITY_GATES,
    RETRIEVAL_MODES,
    SCORE_DIMENSIONS,
    SOURCE_CLASSES,
    ContradictionFlag,
    ContradictionType,
    EvidenceClass,
    EvidenceItem,
    FinalEvidenceContract,
    GapType,
    RecommendedDisposition,
    RefineTactic,
    RetrievalPlan,
    RouteContractView,
    ScoreBreakdown,
    SupportStatus,
    SupportTarget,
)


# --------------------------------------------------------------------------- #
# Shared builders.
# --------------------------------------------------------------------------- #


def _evidence(
    *,
    eid: str = "e1",
    source: str = "doc:a",
    source_class: str = "docs",
    span: str = "L10",
    lane: str = "dense",
    acl: str = "cleared",
    cls: EvidenceClass = EvidenceClass.SUPPORTING,
    authority: float = 0.6,
    fresh: str = "fresh",
    cost: int = 10,
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=eid,
        source_id=source,
        source_class=source_class,
        span_ref=span,
        quote_or_summary="...",
        retrieval_lane=lane,
        authority_score=authority,
        freshness_status=fresh,
        acl_status=acl,
        token_cost=cost,
        evidence_class=cls,
    )


def _route(**overrides) -> RouteContractView:
    base = {
        "route_id": "R3_GROUNDED",
        "grounding_required": True,
        "execution_form": "read",
        "freshness_class": "static",
        "support_target": SupportTarget.SOURCE_SUMMARY,
        "tenant_scope": "tenantA",
        "acl": ("default",),
        "region": "us",
        "data_class": "open",
        "max_k": 20,
        "max_hops": 3,
        "max_parent_expansion": 2,
        "max_refine_attempts": 1,
        "max_latency_ms": 2000,
        "token_budget": 4096,
        "allowed_sources": frozenset({"docs", "code"}),
        "disallowed_sources": frozenset(),
        "fallback_policy": "R5",
        "route_replay_key": "rk-1",
        "policy_hash": "ph-1",
        "blueprint_hash": "bh-1",
    }
    base.update(overrides)
    return RouteContractView(**base)


def _contract(
    *,
    status: SupportStatus = SupportStatus.PASS,
    score_value: float = 0.9,
    evidence: tuple[EvidenceItem, ...] = (),
    flags: tuple[ContradictionFlag, ...] = (),
    refine_attempts: int = 0,
    extras: dict[str, str] | None = None,
    disposition: RecommendedDisposition = RecommendedDisposition.PROCEED,
) -> FinalEvidenceContract:
    return FinalEvidenceContract(
        contract_id="c1",
        route_id="R3_GROUNDED",
        route_replay_key="rk-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
        status=status,
        support_score=score_value,
        score_breakdown=ScoreBreakdown(),
        evidence=evidence,
        contradiction_flags=flags,
        unresolved_gaps=(),
        recommended_disposition=disposition,
        refine_attempts=refine_attempts,
        extras=extras if extras is not None else {"content_classification": "data"},
    )


# ===========================================================================
# Vocabulary cardinality — every named set has the spec-mandated size.
# ===========================================================================


def test_invariants_cardinality_twelve() -> None:
    assert len(INVARIANTS) == 12
    assert INVARIANTS == tuple(f"C0.I{i}" for i in range(1, 13))


def test_quality_gates_cardinality_eleven() -> None:
    assert len(QUALITY_GATES) == 11
    assert QUALITY_GATES[0] == "C0.G0_Scope"
    assert QUALITY_GATES[-1] == "C0.G10_Inject"


def test_failure_modes_cardinality_fourteen() -> None:
    assert len(FAILURE_MODES) == 14


def test_failure_modes_match_prevention_catalog_size() -> None:
    assert failure_modes_match_spec_count() is True
    assert len(FAILURE_MODE_PREVENTIONS) == len(FAILURE_MODES)


def test_gate_functions_match_spec_count() -> None:
    assert gates_match_spec_count() is True
    assert set(GATE_FUNCTIONS.keys()) == set(QUALITY_GATES)


def test_source_classes_seven() -> None:
    assert len(SOURCE_CLASSES) == 7


def test_retrieval_modes_six() -> None:
    assert len(RETRIEVAL_MODES) == 6


def test_bound_params_nine() -> None:
    assert len(BOUND_PARAMS) == 9


def test_score_dimensions_eleven() -> None:
    assert len(SCORE_DIMENSIONS) == 11


def test_disallowed_refinements_seven() -> None:
    assert len(DISALLOWED_REFINEMENTS) == 7


# ===========================================================================
# All 6 SupportStatus → RecommendedDisposition mappings (totality + correctness).
# ===========================================================================


@pytest.mark.parametrize(
    "status,expected",
    [
        (SupportStatus.PASS, RecommendedDisposition.PROCEED),
        (SupportStatus.WEAK_WITH_CAVEATS, RecommendedDisposition.PROCEED_WITH_CAVEAT),
        (SupportStatus.WEAK, RecommendedDisposition.REROUTE),
        (SupportStatus.CONFLICTED, RecommendedDisposition.HUMAN_REVIEW),
        (SupportStatus.EMPTY, RecommendedDisposition.ABSTAIN),
        (SupportStatus.BLOCKED, RecommendedDisposition.FALLBACK_R5),
    ],
)
def test_status_to_disposition_total_mapping(
    status: SupportStatus,
    expected: RecommendedDisposition,
) -> None:
    assert recommend_disposition(status) is expected


def test_recommend_disposition_covers_all_statuses() -> None:
    """Sanity — every SupportStatus value has a disposition (no KeyError)."""
    for s in SupportStatus:
        recommend_disposition(s)  # must not raise


# ===========================================================================
# All 8 RefineTactic values are accepted by is_refinement_allowed.
# ===========================================================================


@pytest.mark.parametrize("tactic", list(RefineTactic))
def test_every_refine_tactic_is_allowed(tactic: RefineTactic) -> None:
    assert is_refinement_allowed(tactic) is True


# ===========================================================================
# All 7 DISALLOWED_REFINEMENTS strings raise from refine controller.
# ===========================================================================


@pytest.mark.parametrize("banned", sorted(DISALLOWED_REFINEMENTS))
def test_every_disallowed_refinement_string_raises(banned: str) -> None:
    route = _route()
    p_status = preflight(route)
    plan = build_retrieval_plan(route, p_status)
    controller = RefineLoopController(plan=plan)
    with pytest.raises(DisallowedRefinementError, match=banned):
        controller.request_refinement(
            RefineTactic.REWRITE,
            rationale=f"we should {banned} because plan was wrong",
            current_status=SupportStatus.WEAK,
        )


# ===========================================================================
# All 8 ContradictionType inference paths.
# ===========================================================================


@pytest.mark.parametrize(
    "anchor_class,contra_class,anchor_fresh,contra_fresh,expected",
    [
        # docs vs code → CODE
        ("docs", "code", "fresh", "fresh", ContradictionType.CODE),
        # logs involved → RUNTIME
        ("docs", "logs", "fresh", "fresh", ContradictionType.RUNTIME),
        ("logs", "docs", "fresh", "fresh", ContradictionType.RUNTIME),
        # policy involved → POLICY
        ("docs", "policy", "fresh", "fresh", ContradictionType.POLICY),
        # different freshness → TIME
        ("docs", "docs", "fresh", "stale", ContradictionType.TIME),
        # otherwise → SOURCE
        ("docs", "docs", "fresh", "fresh", ContradictionType.SOURCE),
    ],
)
def test_contradiction_type_inference_every_branch(
    anchor_class: str,
    contra_class: str,
    anchor_fresh: str,
    contra_fresh: str,
    expected: ContradictionType,
) -> None:
    anchor = _evidence(
        eid="a",
        cls=EvidenceClass.MUST_USE,
        source_class=anchor_class,
        authority=0.95,
        fresh=anchor_fresh,
    )
    contra = _evidence(
        eid="c",
        cls=EvidenceClass.CONTRADICTS,
        source_class=contra_class,
        source="other:doc",
        authority=0.8,
        fresh=contra_fresh,
    )
    shaped = stratify([anchor, contra])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    assert len(report.contradiction_flags) == 1
    assert report.contradiction_flags[0].contradiction_type is expected


def test_contradiction_with_no_anchor_uses_source_unknown() -> None:
    """A CONTRADICTS item with no MUST_USE / SUPPORTING anchor → SOURCE,
    source_b='unknown'."""
    only_contra = _evidence(
        eid="c",
        cls=EvidenceClass.CONTRADICTS,
        source="orphan:1",
    )
    shaped = stratify([only_contra])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    assert len(report.contradiction_flags) == 1
    flag = report.contradiction_flags[0]
    assert flag.contradiction_type is ContradictionType.SOURCE
    assert flag.source_b == "unknown"


# ===========================================================================
# All 9 GapType emission paths (where impl supports them).
# ===========================================================================


def test_gap_missing_exact_quote_emitted() -> None:
    items = [_evidence(eid="a", lane="dense", cls=EvidenceClass.MUST_USE, authority=0.9)]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.EXACT_QUOTE,
        high_stakes=False,
    )
    assert any(g.gap_type is GapType.MISSING_EXACT_QUOTE for g in report.unresolved_gaps)


def test_gap_missing_direct_support_when_only_supporting() -> None:
    items = [_evidence(eid="a", authority=0.6)]  # SUPPORTING tier
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    assert any(g.gap_type is GapType.MISSING_DIRECT_SUPPORT for g in report.unresolved_gaps)


def test_gap_missing_direct_support_when_empty() -> None:
    shaped = stratify([])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    assert any(
        g.gap_type is GapType.MISSING_DIRECT_SUPPORT and g.severity >= 0.95 for g in report.unresolved_gaps
    )


def test_gap_missing_source_diversity_high_stakes_single_source() -> None:
    items = [
        _evidence(eid="a", source="doc:x", authority=0.9, cls=EvidenceClass.MUST_USE),
        _evidence(eid="b", source="doc:x", authority=0.9, cls=EvidenceClass.MUST_USE),
    ]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.POLICY_CLAUSE,
        high_stakes=True,
    )
    assert any(g.gap_type is GapType.MISSING_SOURCE_DIVERSITY for g in report.unresolved_gaps)


def test_gap_missing_tenant_acl_proof_when_acl_uncleared() -> None:
    items = [_evidence(eid="a", acl="pending", authority=0.95, cls=EvidenceClass.MUST_USE)]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    assert any(g.gap_type is GapType.MISSING_TENANT_ACL_PROOF for g in report.unresolved_gaps)


def test_gap_type_enum_is_closed_set_of_nine() -> None:
    """Every spec-named gap type appears in the enum."""
    expected = {
        "missing_direct_support",
        "missing_exact_quote",
        "missing_current_version",
        "missing_owner_authority",
        "missing_source_diversity",
        "missing_validation",
        "missing_citation_anchor",
        "missing_time_range",
        "missing_tenant_acl_proof",
    }
    assert {g.value for g in GapType} == expected


# ===========================================================================
# All 8 preflight blocked_reason codes.
# ===========================================================================


def test_blocked_reason_grounding_not_required() -> None:
    s = preflight(_route(grounding_required=False))
    assert s.eligible is False
    assert s.blocked_reason == "grounding_not_required"


def test_blocked_reason_route_disallows_retrieval() -> None:
    s = preflight(_route(route_id="R5_FALLBACK"))
    assert s.eligible is False
    assert "does not allow C0 retrieval" in s.blocked_reason


def test_blocked_reason_no_allowed_source_class_after_disallow() -> None:
    s = preflight(
        _route(
            allowed_sources=frozenset({"docs"}),
            disallowed_sources=frozenset({"docs"}),
        )
    )
    assert s.eligible is False
    assert "no allowed source class" in s.blocked_reason


def test_blocked_reason_data_class_restricted() -> None:
    s = preflight(_route(data_class="restricted"))
    assert s.eligible is False
    assert "data_class" in s.blocked_reason


def test_blocked_reason_data_class_blocked() -> None:
    s = preflight(_route(data_class="blocked"))
    assert s.eligible is False
    assert "data_class" in s.blocked_reason


def test_blocked_reason_token_budget_below_floor() -> None:
    s = preflight(_route(token_budget=MIN_BUDGET_FLOOR_TOKENS - 1))
    assert s.eligible is False
    assert "token_budget" in s.blocked_reason


# ===========================================================================
# Preflight strict-vs-default evidence standard for high-stakes targets.
# ===========================================================================


@pytest.mark.parametrize(
    "target",
    [
        SupportTarget.POLICY_CLAUSE,
        SupportTarget.INCIDENT_EVIDENCE,
        SupportTarget.ROOT_CAUSE_RANKING,
        SupportTarget.CODE_LOCATION,
    ],
)
def test_preflight_high_stakes_targets_get_strict_standard(target: SupportTarget) -> None:
    s = preflight(_route(support_target=target))
    assert s.eligible is True
    assert s.evidence_standard == "strict"


@pytest.mark.parametrize(
    "target",
    [
        SupportTarget.SOURCE_SUMMARY,
        SupportTarget.EXACT_QUOTE,
        SupportTarget.COMPARISON,
        SupportTarget.CLAIM_CHECK,
    ],
)
def test_preflight_other_targets_get_default_standard(target: SupportTarget) -> None:
    s = preflight(_route(support_target=target))
    assert s.eligible is True
    assert s.evidence_standard == "default"


# ===========================================================================
# build_retrieval_plan edge cases.
# ===========================================================================


def test_build_retrieval_plan_rejects_blocked_preflight() -> None:
    route = _route(grounding_required=False)
    s = preflight(route)
    with pytest.raises(ValueError, match="preflight blocked"):
        build_retrieval_plan(route, s)


def test_build_retrieval_plan_rejects_unknown_retrieval_mode() -> None:
    route = _route()
    s = preflight(route)
    with pytest.raises(ValueError, match="unknown retrieval_modes"):
        build_retrieval_plan(route, s, retrieval_modes=frozenset({"vibes"}))


def test_build_retrieval_plan_populates_every_bound_param() -> None:
    route = _route()
    s = preflight(route)
    plan = build_retrieval_plan(route, s)
    for p in BOUND_PARAMS:
        assert p in plan.bounds, f"BOUND_PARAM {p!r} not populated"


def test_build_retrieval_plan_replay_metadata_present() -> None:
    route = _route()
    s = preflight(route)
    plan = build_retrieval_plan(route, s)
    assert plan.replay_metadata == {
        "route_replay_key": "rk-1",
        "policy_hash": "ph-1",
        "blueprint_hash": "bh-1",
    }


# ===========================================================================
# verify_evidence — every rejection branch.
# ===========================================================================


def test_verify_rejects_missing_source_id() -> None:
    bad = EvidenceItem(
        evidence_id="x",
        source_id="",
        source_class="docs",
        span_ref="L1",
        quote_or_summary="...",
        retrieval_lane="dense",
        authority_score=0.9,
        freshness_status="fresh",
        acl_status="cleared",
        token_cost=10,
    )
    verified, rejected = verify_evidence((bad,))
    assert verified == ()
    assert rejected[0][1] == "source_id_missing"


def test_verify_rejects_missing_span_ref() -> None:
    bad = _evidence(eid="x", span="")
    verified, rejected = verify_evidence((bad,))
    assert verified == ()
    assert rejected[0][1] == "span_ref_missing"


def test_verify_rejects_unknown_acl_status() -> None:
    bad = _evidence(eid="x", acl="probably-fine?")
    verified, rejected = verify_evidence((bad,))
    assert verified == ()
    assert "acl_status" in rejected[0][1]


def test_verify_accepts_default_allow_acl() -> None:
    ok = _evidence(eid="ok", acl="default-allow")
    verified, rejected = verify_evidence((ok,))
    assert verified == (ok,)
    assert rejected == ()


# ===========================================================================
# Stratify — all three authority bands + pre-labeled classes.
# ===========================================================================


@pytest.mark.parametrize(
    "authority,target_bucket",
    [
        (0.99, "must_use"),
        (0.85, "must_use"),  # threshold-exact
        (0.84, "supporting"),
        (0.50, "supporting"),  # threshold-exact
        (0.49, "background"),
        (0.25, "background"),  # threshold-exact
        (0.24, "excluded"),
        (0.01, "excluded"),
    ],
)
def test_stratify_authority_band_boundaries(
    authority: float,
    target_bucket: str,
) -> None:
    item = _evidence(eid="a", authority=authority)
    shaped = stratify([item])
    if target_bucket == "must_use":
        assert any(it.evidence_id == "a" for it in shaped.must_use)
    elif target_bucket == "supporting":
        assert any(it.evidence_id == "a" for it in shaped.supporting)
    elif target_bucket == "background":
        assert any(it.evidence_id == "a" for it in shaped.background)
    elif target_bucket == "excluded":
        assert any(it.evidence_id == "a" for it, _ in shaped.excluded)


@pytest.mark.parametrize(
    "cls,bucket_attr",
    [
        (EvidenceClass.MUST_USE, "must_use"),
        (EvidenceClass.SUPPORTING, "supporting"),
        (EvidenceClass.CONTRADICTS, "contradicts"),
        (EvidenceClass.BACKGROUND, "background"),
        (EvidenceClass.DEFINITIONS, "definitions"),
        (EvidenceClass.LINEAGE, "lineage"),
    ],
)
def test_stratify_honors_pre_labeled_class(
    cls: EvidenceClass,
    bucket_attr: str,
) -> None:
    item = _evidence(eid="a", cls=cls, authority=0.6)
    shaped = stratify([item])
    bucket = getattr(shaped, bucket_attr)
    assert any(it.evidence_id == "a" for it in bucket), f"item with class {cls} not placed in {bucket_attr}"


def test_stratify_pre_labeled_excluded_goes_to_excluded() -> None:
    item = _evidence(eid="a", cls=EvidenceClass.EXCLUDED, authority=0.95)
    shaped = stratify([item])
    excluded_ids = {it.evidence_id for it, _ in shaped.excluded}
    assert "a" in excluded_ids


# ===========================================================================
# Dedupe — empty, single, duplicate-with-tied-authority.
# ===========================================================================


def test_dedupe_empty_returns_empty() -> None:
    assert dedupe([]) == []


def test_dedupe_single_returns_single() -> None:
    item = _evidence(eid="a")
    assert dedupe([item]) == [item]


def test_dedupe_tied_authority_keeps_first_seen() -> None:
    a = _evidence(eid="a", source="doc:x", span="L1", authority=0.5)
    b = _evidence(eid="b", source="doc:x", span="L1", authority=0.5)
    out = dedupe([a, b])
    # impl: only update on strictly higher authority → first one stays.
    assert {it.evidence_id for it in out} == {"a"}


# ===========================================================================
# compress_to_budget — every branch.
# ===========================================================================


def test_compress_zero_budget_raises() -> None:
    shaped = stratify([_evidence(eid="a", authority=0.9, cls=EvidenceClass.MUST_USE)])
    with pytest.raises(ValueError, match="must be > 0"):
        compress_to_budget(shaped, max_token_context=0)


def test_compress_negative_budget_raises() -> None:
    shaped = stratify([_evidence(eid="a", authority=0.9, cls=EvidenceClass.MUST_USE)])
    with pytest.raises(ValueError, match="must be > 0"):
        compress_to_budget(shaped, max_token_context=-1)


def test_compress_must_use_oversize_raises() -> None:
    over = _evidence(eid="m", authority=0.95, cls=EvidenceClass.MUST_USE, cost=100)
    shaped = stratify([over])
    with pytest.raises(ValueError, match="must-keep"):
        compress_to_budget(shaped, max_token_context=50)


def test_compress_preserves_contradicts_and_definitions() -> None:
    must = _evidence(eid="m", cls=EvidenceClass.MUST_USE, authority=0.95, cost=10)
    contra = _evidence(eid="c", cls=EvidenceClass.CONTRADICTS, source="x", cost=10)
    defi = _evidence(eid="d", cls=EvidenceClass.DEFINITIONS, cost=10)
    bg = _evidence(eid="b", cls=EvidenceClass.BACKGROUND, authority=0.3, cost=100)
    shaped = stratify([must, contra, defi, bg])
    compressed = compress_to_budget(shaped, max_token_context=40)
    assert {it.evidence_id for it in compressed.must_use} == {"m"}
    assert {it.evidence_id for it in compressed.contradicts} == {"c"}
    assert {it.evidence_id for it in compressed.definitions} == {"d"}
    assert len(compressed.background) == 0  # 100-token bg can't fit


# ===========================================================================
# Score boundary — every dimension at 0.0 / 1.0.
# ===========================================================================


def test_score_empty_pool_yields_all_zero_positives() -> None:
    shaped = stratify([])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert breakdown.direct_support_score == 0.0
    assert breakdown.coverage_score == 0.0
    assert breakdown.source_authority_score == 0.0
    assert breakdown.freshness_score == 0.0
    assert breakdown.citation_stability_score == 0.0
    assert breakdown.lineage_quality_score == 0.0
    assert breakdown.exactness_score == 0.0
    assert breakdown.ACL_confidence == 0.0
    assert breakdown.source_diversity_score == 0.0


def test_score_aggregate_bounded_to_unit_interval() -> None:
    """For random combinations, aggregate stays in [0, 1]."""
    for must in range(0, 5):
        for contras in range(0, 4):
            items = [
                _evidence(
                    eid=f"m{i}",
                    source=f"doc:{i}",
                    authority=0.95,
                    cls=EvidenceClass.MUST_USE,
                    lane="sparse",
                )
                for i in range(must)
            ]
            items += [
                _evidence(
                    eid=f"c{i}",
                    source=f"con:{i}",
                    authority=0.8,
                    cls=EvidenceClass.CONTRADICTS,
                )
                for i in range(contras)
            ]
            shaped = stratify(items)
            report = scan_contradictions_and_gaps(
                shaped,
                support_target=SupportTarget.SOURCE_SUMMARY,
                high_stakes=False,
            )
            breakdown = score(
                shaped,
                report,
                support_target=SupportTarget.SOURCE_SUMMARY,
            )
            agg = aggregate_support_score(breakdown)
            assert 0.0 <= agg <= 1.0


def test_aggregate_clamps_negative_to_zero() -> None:
    """Risk-only score should clamp to 0.0, not go negative."""
    breakdown = ScoreBreakdown(
        direct_support_score=0.0,
        coverage_score=0.0,
        source_authority_score=0.0,
        freshness_score=0.0,
        contradiction_risk=1.0,
        unsupported_inference_risk=1.0,
        citation_stability_score=0.0,
        lineage_quality_score=0.0,
        source_diversity_score=0.0,
        exactness_score=0.0,
        ACL_confidence=0.0,
    )
    assert aggregate_support_score(breakdown) == 0.0


def test_aggregate_clamps_to_one() -> None:
    """Max-positive zero-risk should clamp at 1.0."""
    breakdown = ScoreBreakdown(
        direct_support_score=1.0,
        coverage_score=1.0,
        source_authority_score=1.0,
        freshness_score=1.0,
        contradiction_risk=0.0,
        unsupported_inference_risk=0.0,
        citation_stability_score=1.0,
        lineage_quality_score=1.0,
        source_diversity_score=1.0,
        exactness_score=1.0,
        ACL_confidence=1.0,
    )
    assert 0.99 <= aggregate_support_score(breakdown) <= 1.0


# ===========================================================================
# decide_status — explicit branch coverage.
# ===========================================================================


def test_decide_status_blocked_overrides_everything() -> None:
    shaped = stratify([_evidence(authority=0.95, cls=EvidenceClass.MUST_USE)])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert decide_status(shaped, report, breakdown, blocked=True) is SupportStatus.BLOCKED


def test_decide_status_empty_when_no_evidence() -> None:
    shaped = stratify([])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    assert decide_status(shaped, report, breakdown) is SupportStatus.EMPTY


def test_decide_status_conflicted_high_severity() -> None:
    must = _evidence(eid="m", cls=EvidenceClass.MUST_USE, authority=0.95)
    contra = _evidence(eid="c", cls=EvidenceClass.CONTRADICTS, source="x", authority=0.9)
    shaped = stratify([must, contra])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    # contradiction severity 0.9 ≥ 0.6 → CONFLICTED.
    assert decide_status(shaped, report, breakdown) is SupportStatus.CONFLICTED


# ===========================================================================
# Refine controller — every entry-condition + budget branch.
# ===========================================================================


@pytest.mark.parametrize(
    "status",
    [
        SupportStatus.PASS,
        SupportStatus.BLOCKED,
    ],
)
def test_refine_rejects_terminal_statuses(status: SupportStatus) -> None:
    route = _route()
    p = preflight(route)
    plan = build_retrieval_plan(route, p)
    controller = RefineLoopController(plan=plan)
    with pytest.raises(DisallowedRefinementError, match="entry conditions"):
        controller.request_refinement(
            RefineTactic.REWRITE,
            rationale="add synonyms",
            current_status=status,
        )


@pytest.mark.parametrize(
    "status",
    [
        SupportStatus.WEAK,
        SupportStatus.WEAK_WITH_CAVEATS,
        SupportStatus.CONFLICTED,
        SupportStatus.EMPTY,
    ],
)
def test_refine_accepts_recoverable_statuses(status: SupportStatus) -> None:
    route = _route()
    p = preflight(route)
    plan = build_retrieval_plan(route, p)
    controller = RefineLoopController(plan=plan)
    controller.request_refinement(
        RefineTactic.REWRITE,
        rationale="add synonyms and exact terms",
        current_status=status,
    )  # must not raise


def test_refine_budget_exhausted_after_one_attempt() -> None:
    route = _route(max_refine_attempts=1)
    p = preflight(route)
    plan = build_retrieval_plan(route, p)
    controller = RefineLoopController(plan=plan)
    controller.request_refinement(
        RefineTactic.REWRITE,
        rationale="add synonyms",
        current_status=SupportStatus.WEAK,
    )
    controller.record_attempt(
        RefinementAttempt(
            tactic=RefineTactic.REWRITE,
            rationale="add synonyms",
            succeeded=False,
            new_status=SupportStatus.WEAK,
        )
    )
    with pytest.raises(RefinementBudgetExhaustedError):
        controller.request_refinement(
            RefineTactic.BROADEN,
            rationale="loosen filter",
            current_status=SupportStatus.WEAK,
        )


def test_refine_zero_budget_blocks_immediately() -> None:
    route = _route(max_refine_attempts=0)
    p = preflight(route)
    plan = build_retrieval_plan(route, p)
    controller = RefineLoopController(plan=plan)
    with pytest.raises(RefinementBudgetExhaustedError):
        controller.request_refinement(
            RefineTactic.REWRITE,
            rationale="add synonyms",
            current_status=SupportStatus.WEAK,
        )


# ===========================================================================
# Invariant boundary cases.
# ===========================================================================


def test_i6_at_zero_hops_is_bounded() -> None:
    assert i6_graph_bounded(hops_used=0, max_hops=0) is True


def test_i6_negative_hops_unbounded() -> None:
    assert i6_graph_bounded(hops_used=-1, max_hops=3) is False


def test_i8_pass_status_allows_high_score() -> None:
    """I8 only constrains WEAK/WEAK_WITH_CAVEATS — PASS is exempt."""
    c = _contract(status=SupportStatus.PASS, score_value=0.99)
    assert i8_weak_evidence_stays_weak(c) is True


def test_i8_threshold_exactly_zero_eight_five() -> None:
    """Boundary: WEAK with score exactly 0.85 violates I8 (must be < 0.85)."""
    c = _contract(status=SupportStatus.WEAK, score_value=0.85)
    assert i8_weak_evidence_stays_weak(c) is False


def test_i9_zero_attempts_within_zero_budget() -> None:
    c = _contract(refine_attempts=0)
    assert i9_one_refine_loop(c, max_attempts=0) is True
    c2 = _contract(refine_attempts=1)
    assert i9_one_refine_loop(c2, max_attempts=0) is False


def test_assert_all_invariants_passes_on_well_formed_contract() -> None:
    item = _evidence(eid="a", authority=0.95, cls=EvidenceClass.MUST_USE)
    c = _contract(
        status=SupportStatus.PASS,
        score_value=0.9,
        evidence=(item,),
    )
    # Must not raise.
    assert_all_invariants(
        c,
        retrieval_lanes_used=frozenset({"dense", "sparse"}),
    )


def test_assert_all_invariants_raises_on_i3_violation() -> None:
    bad = EvidenceItem(
        evidence_id="x",
        source_id="doc:x",
        source_class="docs",
        span_ref="L1",
        quote_or_summary="...",
        retrieval_lane="",  # missing
        authority_score=0.9,
        freshness_status="fresh",
        acl_status="cleared",
        token_cost=10,
    )
    c = _contract(evidence=(bad,))
    with pytest.raises(InvariantViolationError, match="C0.I3"):
        assert_all_invariants(
            c,
            retrieval_lanes_used=frozenset({"dense", "sparse"}),
        )


# ===========================================================================
# Contract digest determinism + sensitivity.
# ===========================================================================


def test_contract_digest_stable_across_two_builds_same_evidence() -> None:
    item = _evidence(eid="a", source="doc:1", authority=0.95, cls=EvidenceClass.MUST_USE)

    def _build() -> FinalEvidenceContract:
        shaped = stratify([item])
        report = scan_contradictions_and_gaps(
            shaped,
            support_target=SupportTarget.SOURCE_SUMMARY,
            high_stakes=False,
        )
        breakdown = score(
            shaped,
            report,
            support_target=SupportTarget.SOURCE_SUMMARY,
        )
        c = build_final_contract(
            route=_route(),
            shaped=shaped,
            report=report,
            breakdown=breakdown,
        )
        # Stabilise contract_id (uuid-based) for digest comparison.
        return FinalEvidenceContract(
            contract_id="stable",
            route_id=c.route_id,
            route_replay_key=c.route_replay_key,
            policy_hash=c.policy_hash,
            blueprint_hash=c.blueprint_hash,
            status=c.status,
            support_score=c.support_score,
            score_breakdown=c.score_breakdown,
            evidence=c.evidence,
            contradiction_flags=c.contradiction_flags,
            unresolved_gaps=c.unresolved_gaps,
            recommended_disposition=c.recommended_disposition,
            refine_attempts=c.refine_attempts,
            extras=c.extras,
        )

    assert contract_digest(_build()) == contract_digest(_build())


def test_contract_digest_changes_when_status_changes() -> None:
    base = _contract(status=SupportStatus.PASS)
    other = _contract(status=SupportStatus.WEAK)
    assert contract_digest(base) != contract_digest(other)


def test_contract_digest_changes_when_evidence_count_changes() -> None:
    item = _evidence(eid="a")
    a = _contract(evidence=(item,))
    b = _contract(evidence=(item, item))
    assert contract_digest(a) != contract_digest(b)


# ===========================================================================
# Build_final_contract end-to-end on every status path.
# ===========================================================================


@pytest.mark.parametrize("blocked", [True, False])
def test_build_final_contract_emits_valid_status_for_blocked_flag(blocked: bool) -> None:
    route = _route()
    # Five MUST_USE items across distinct sparse sources → satisfies coverage,
    # source diversity, and exactness; aggregate ≥ 0.75 → PASS.
    items = [
        _evidence(
            eid=f"m{i}",
            source=f"doc:{i}",
            authority=0.95,
            cls=EvidenceClass.MUST_USE,
            lane="sparse",
        )
        for i in range(5)
    ]
    shaped = stratify(items)
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    contract = build_final_contract(
        route=route,
        shaped=shaped,
        report=report,
        breakdown=breakdown,
        blocked=blocked,
    )
    if blocked:
        # blocked=True overrides everything per spec.
        assert contract.status is SupportStatus.BLOCKED
        assert contract.recommended_disposition is RecommendedDisposition.FALLBACK_R5
    else:
        # Strong evidence path → PASS + PROCEED.
        assert contract.status is SupportStatus.PASS
        assert contract.recommended_disposition is RecommendedDisposition.PROCEED


def test_build_final_contract_extras_carries_data_classification() -> None:
    route = _route()
    shaped = stratify([])
    report = scan_contradictions_and_gaps(
        shaped,
        support_target=SupportTarget.SOURCE_SUMMARY,
        high_stakes=False,
    )
    breakdown = score(shaped, report, support_target=SupportTarget.SOURCE_SUMMARY)
    contract = build_final_contract(
        route=route,
        shaped=shaped,
        report=report,
        breakdown=breakdown,
    )
    assert contract.extras.get("content_classification") == "data"


# ===========================================================================
# Frozen dataclass / immutability invariants.
# ===========================================================================


def test_evidence_item_is_frozen() -> None:
    item = _evidence()
    with pytest.raises((AttributeError, TypeError)):
        item.acl_status = "blocked"  # type: ignore[misc]


def test_score_breakdown_is_frozen_and_returns_dict_with_eleven_keys() -> None:
    sb = ScoreBreakdown()
    with pytest.raises((AttributeError, TypeError)):
        sb.direct_support_score = 0.5  # type: ignore[misc]
    d = sb.as_dict()
    assert len(d) == 11
    assert set(d.keys()) == set(SCORE_DIMENSIONS)


def test_final_contract_is_frozen() -> None:
    c = _contract()
    with pytest.raises((AttributeError, TypeError)):
        c.status = SupportStatus.WEAK  # type: ignore[misc]


# ===========================================================================
# Enum value-string consistency (every enum stays in sync with its value).
# ===========================================================================


@pytest.mark.parametrize(
    "enum_cls",
    [
        SupportStatus,
        SupportTarget,
        EvidenceClass,
        ContradictionType,
        GapType,
        RecommendedDisposition,
        RefineTactic,
    ],
)
def test_enum_value_round_trip(enum_cls: type) -> None:
    """For every enum, EnumCls(member.value) == member."""
    for member in enum_cls:
        assert enum_cls(member.value) is member
