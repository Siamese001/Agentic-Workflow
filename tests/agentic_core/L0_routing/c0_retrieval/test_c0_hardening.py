"""Edge-case hardening for C0.1-C0.6 spec-grade typed contracts.

Companion to ``test_spec_contracts.py`` and ``test_weak_support_refinement.py``.
This file exhaustively exercises every validation path, every forbidden-
vocabulary token, every numeric boundary, every authority-boundary token,
frozen-dataclass immutability, and determinism stress (order-invariance,
unicode round-trip stability) — the surface a happy-path test sweep can miss.

Layout:
    A. WeakSupportRefinementInput validation paths
    B. WeakSupportDiagnosis validation paths
    C. Plan ID-required (Rewrite / Broaden / Decomposition)
    D. RefinementAttemptLedger validation
    E. FORBIDDEN_OUTPUT_TOKENS — parametrized over every token
    F. _L3_AUTHORIZATION_TOKENS — parametrized over every substring
    G. Frozen-dataclass immutability — parametrized over every dataclass
    H. RetrievalModePlan numeric boundaries
    I. RawHit / RetrievalLaneResult validation
    J. SupportScoreBreakdownV2 per-field range
    K. Hash determinism / order-invariance / distinctness
    L. build_otel_attributes type checks (OTEL-compatible)
    M. is_eligible_for_refinement edge cases
    N. diagnose_from_contract heuristic edges
    O. ExclusionReason enum coverage
    P. SourceClassDecision INCLUDE / REQUIRED / OPTIONAL paths
    Q. CitationSupportMap recall + non-EXACT_QUOTE paths
    R. ReentryTarget hash distinctness across all 3 values
    S. Token-level matching (no false-positive on substring)
    T. SupportTargetProfile boundary cases
    U. EvidenceFingerprint extra-field coverage
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.c0_retrieval.evidence_contract import ScoreBreakdown
from agentic_core.L0_routing.c0_retrieval.final_contract import (
    ContradictionFlagOut,
    FinalEvidenceContract,
    ReplayMetadata,
    UnresolvedGapOut,
    seal_final_contract,
)
from agentic_core.L0_routing.c0_retrieval.plan import (
    Budgets,
    CachePolicy,
    DenseQuerySpec,
    GraphBounds,
    MetadataFilters,
    RetrievalPlan,
)
from agentic_core.L0_routing.c0_retrieval.preflight import EvidenceStandard
from agentic_core.L0_routing.c0_retrieval.spec_contracts import (
    CitationPrecision,
    CitationSupportMap,
    EvidenceFingerprint,
    EvidenceGapReportV2,
    ExcludedEvidenceItem,
    ExclusionReason,
    RawHit,
    RetrievalLaneResult,
    RetrievalModePlan,
    SourceClassDecision,
    SourceDecision,
    SupportScoreBreakdownV2,
    SupportTargetProfile,
    UnsupportedInferencePolicy,
    compute_pool_manifest_hash,
    compute_profile_hash,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    FreshnessClass,
    GapType,
    GraphRelation,
    RetrievalLane,
    RetrievalMode,
    SourceClass,
    SupportStatus,
    SupportTarget,
)
from agentic_core.L0_routing.c0_retrieval.weak_support_refinement import (
    AttemptStatus,
    BroadenDimension,
    C06Gate,
    DecompositionPlan,
    FORBIDDEN_OUTPUT_TOKENS,
    NoMoreRefinementReport,
    PrimaryGapType,
    QueryRewritePlan,
    ReentryTarget,
    RefinementAttemptLedger,
    RefinementStrategy,
    ScopeBroadenPlan,
    SubQuerySpec,
    WeakSupportDiagnosis,
    WeakSupportRefinementInput,
    build_otel_attributes,
    compute_ledger_hash,
    compute_reentry_input_hash,
    diagnose_from_contract,
    is_eligible_for_refinement,
    run_gates,
)


# ===========================================================================
# Fixtures
# ===========================================================================
def _make_plan(*, max_refine_attempts: int = 1) -> RetrievalPlan:
    return RetrievalPlan(
        plan_id="plan-test",
        route_replay_key="rk-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
        support_target=SupportTarget.SOURCE_SUMMARY,
        evidence_standard=EvidenceStandard.STANDARD,
        freshness_class=FreshnessClass.CURRENT,
        source_classes=(SourceClass.DOCS,),
        allowed_sources=(SourceClass.DOCS,),
        disallowed_sources=(),
        retrieval_modes=(RetrievalMode.HYBRID,),
        dense_query_spec=DenseQuerySpec(query_text="example query", top_k=5),
        sparse_query_spec=None,
        metadata_filters=MetadataFilters(tenant_id="tenantA"),
        cache_policy=CachePolicy(allow_cache=False),
        graph_bounds=GraphBounds(max_hops=1),
        budgets=Budgets(max_refine_attempts=max_refine_attempts),
    )


def _make_contract(
    *,
    status: SupportStatus = SupportStatus.WEAK_WITH_CAVEATS,
    gaps: tuple[UnresolvedGapOut, ...] = (
        UnresolvedGapOut(
            gap_type=GapType.MISSING_DIRECT_SUPPORT,
            severity="medium",
            impact_on_answer="cannot quote without direct span",
        ),
    ),
    contradictions: tuple[ContradictionFlagOut, ...] = (),
    blocked_reason: str = "",
) -> FinalEvidenceContract:
    contract = FinalEvidenceContract(
        contract_id="contract-test",
        route_id="R3_GROUNDED",
        route_replay_key="rk-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
        status=status,
        support_score=0.4,
        score_breakdown=ScoreBreakdown(),
        unresolved_gaps=gaps,
        contradiction_flags=contradictions,
        blocked_reason=blocked_reason,
        replay_metadata=ReplayMetadata(
            route_replay_key="rk-1",
            policy_hash="ph-1",
            blueprint_hash="bh-1",
        ),
    )
    return seal_final_contract(contract)


def _make_input(**overrides) -> WeakSupportRefinementInput:
    base: dict = dict(
        final_evidence_contract=_make_contract(),
        retrieval_plan=_make_plan(),
        original_query_spec="example query",
        route_id="R3_GROUNDED",
        route_replay_key="rk-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
        max_refine_attempts=1,
        refine_attempts_used=0,
        budget_remaining=1000.0,
        allowed_sources=("doc-shelf",),
        disallowed_sources=("rumor-shelf",),
        allowed_source_classes=(SourceClass.DOCS,),
        freshness_class="current",
        weak_support_policy="caveat",
    )
    base.update(overrides)
    return WeakSupportRefinementInput(**base)


def _make_ledger(**kw) -> RefinementAttemptLedger:
    """Helper for RefinementAttemptLedger with all required positional args."""
    defaults = dict(
        refinement_attempt_id="ra-1",
        request_id="req-1",
        run_id="run-1",
        trace_id="tr-1",
        route_id="R3_GROUNDED",
        prior_contract_hash="ph1",
        diagnosis_ref="d-1",
        selected_strategy=RefinementStrategy.QUERY_REWRITE,
        attempt_number=0,
        max_refine_attempts=2,
        attempt_status=AttemptStatus.ELIGIBLE,
        budget_before=1000.0,
        budget_after_reserved=900.0,
    )
    defaults.update(kw)
    return RefinementAttemptLedger(**defaults)


# ===========================================================================
# A. WeakSupportRefinementInput — every validation path
# ===========================================================================
class TestInputAllValidationPaths:
    def test_negative_refine_attempts_used_rejected(self):
        with pytest.raises(ValueError, match="refine_attempts_used must be >= 0"):
            _make_input(refine_attempts_used=-1)

    def test_negative_budget_remaining_rejected(self):
        with pytest.raises(ValueError, match="budget_remaining must be >= 0"):
            _make_input(budget_remaining=-0.01)

    def test_zero_budget_accepted_at_construction(self):
        # Boundary: exactly zero is valid at construction; budget gate handles it.
        inp = _make_input(budget_remaining=0.0)
        assert inp.budget_remaining == 0.0

    def test_empty_route_replay_key_rejected(self):
        with pytest.raises(ValueError, match="route_replay_key required"):
            _make_input(route_replay_key="")

    def test_empty_policy_hash_rejected(self):
        with pytest.raises(ValueError, match="policy_hash required"):
            _make_input(policy_hash="")

    def test_empty_blueprint_hash_rejected(self):
        with pytest.raises(ValueError, match="blueprint_hash required"):
            _make_input(blueprint_hash="")

    @pytest.mark.parametrize(
        "status",
        [SupportStatus.WEAK, SupportStatus.WEAK_WITH_CAVEATS, SupportStatus.CONFLICTED, SupportStatus.EMPTY],
    )
    def test_eligible_statuses_accepted(self, status):
        contract = _make_contract(
            status=status,
            gaps=(
                UnresolvedGapOut(
                    gap_type=GapType.MISSING_DIRECT_SUPPORT,
                    severity="low",
                ),
            )
            if status != SupportStatus.CONFLICTED
            else (),
            contradictions=(ContradictionFlagOut(type="version", source_a="a", source_b="b"),)
            if status == SupportStatus.CONFLICTED
            else (),
        )
        inp = _make_input(final_evidence_contract=contract)
        assert inp.final_evidence_contract.status is status

    def test_blocked_status_with_reason_accepted(self):
        # BLOCKED requires a reason at the contract level (final_contract invariant).
        contract = _make_contract(
            status=SupportStatus.BLOCKED,
            gaps=(),
            blocked_reason="ACL forbids",
        )
        inp = _make_input(final_evidence_contract=contract)
        assert inp.final_evidence_contract.status is SupportStatus.BLOCKED

    def test_pass_status_rejected_explicitly(self):
        contract = _make_contract(status=SupportStatus.PASS, gaps=())
        with pytest.raises(ValueError, match="C0.6 refuses status='PASS'"):
            _make_input(final_evidence_contract=contract)


# ===========================================================================
# B. WeakSupportDiagnosis validation paths
# ===========================================================================
class TestDiagnosisValidation:
    def test_empty_diagnosis_id_rejected(self):
        with pytest.raises(ValueError, match="diagnosis_id required"):
            WeakSupportDiagnosis(
                diagnosis_id="",
                evidence_status=SupportStatus.WEAK_WITH_CAVEATS,
                primary_gap_type=PrimaryGapType.SPARSE_MISSING,
                recovery_strategy=RefinementStrategy.QUERY_REWRITE,
                likely_recoverable=True,
            )

    def test_non_recoverable_without_reason_rejected(self):
        with pytest.raises(ValueError, match="non_recoverable_reason"):
            WeakSupportDiagnosis(
                diagnosis_id="d-1",
                evidence_status=SupportStatus.BLOCKED,
                primary_gap_type=PrimaryGapType.ACL_BLOCKED,
                recovery_strategy=RefinementStrategy.STOP_WITH_GAP_REPORT,
                likely_recoverable=False,
                non_recoverable_reason="",
            )

    def test_non_recoverable_with_reason_accepted(self):
        d = WeakSupportDiagnosis(
            diagnosis_id="d-1",
            evidence_status=SupportStatus.BLOCKED,
            primary_gap_type=PrimaryGapType.ACL_BLOCKED,
            recovery_strategy=RefinementStrategy.STOP_WITH_GAP_REPORT,
            likely_recoverable=False,
            non_recoverable_reason="ACL forbids this scope",
        )
        assert d.non_recoverable_reason


# ===========================================================================
# C. Plan ID-required (Rewrite / Broaden / Decomposition)
# ===========================================================================
class TestPlanIdRequired:
    def test_query_rewrite_empty_id_rejected(self):
        with pytest.raises(ValueError, match="rewrite_plan_id required"):
            QueryRewritePlan(
                rewrite_plan_id="",
                original_query_terms=("x",),
                bounded_by_original_intent=True,
            )

    def test_query_rewrite_unbounded_intent_rejected(self):
        with pytest.raises(ValueError, match="bounded_by_original_intent"):
            QueryRewritePlan(
                rewrite_plan_id="rp-1",
                original_query_terms=("x",),
                bounded_by_original_intent=False,
            )

    def test_scope_broaden_empty_id_rejected(self):
        with pytest.raises(ValueError, match="broaden_plan_id required"):
            ScopeBroadenPlan(
                broaden_plan_id="",
                broaden_dimension=BroadenDimension.TOP_K,
                old_value="5",
                new_value="10",
                bound_source="RouteContract.max_k",
            )

    def test_scope_broaden_empty_bound_source_rejected(self):
        with pytest.raises(ValueError, match="bound_source required"):
            ScopeBroadenPlan(
                broaden_plan_id="bp-1",
                broaden_dimension=BroadenDimension.TOP_K,
                old_value="5",
                new_value="10",
                bound_source="",
            )

    def test_decomposition_empty_id_rejected(self):
        with pytest.raises(ValueError, match="decomposition_plan_id required"):
            DecompositionPlan(
                decomposition_plan_id="",
                sub_queries=(SubQuerySpec(sub_query_id="sq-1", text="q"),),
            )

    def test_decomposition_at_exactly_max_subqueries_accepted(self):
        # Boundary: equal to max_subqueries is valid; only > rejects.
        decomp = DecompositionPlan(
            decomposition_plan_id="dp-1",
            sub_queries=tuple(SubQuerySpec(sub_query_id=f"sq{i}", text=f"q{i}") for i in range(4)),
            max_subqueries=4,
        )
        assert len(decomp.sub_queries) == 4


# ===========================================================================
# D. RefinementAttemptLedger validation
# ===========================================================================
class TestLedgerValidation:
    def test_empty_attempt_id_rejected(self):
        with pytest.raises(ValueError, match="refinement_attempt_id required"):
            _make_ledger(refinement_attempt_id="")

    def test_negative_attempt_number_rejected(self):
        with pytest.raises(ValueError, match="attempt_number must be >= 0"):
            _make_ledger(attempt_number=-1)

    def test_attempt_zero_with_eligible_accepted(self):
        ledger = _make_ledger(attempt_number=0, attempt_status=AttemptStatus.ELIGIBLE)
        assert ledger.attempt_number == 0

    def test_below_max_with_executed_status_accepted(self):
        ledger = _make_ledger(
            attempt_number=1,
            max_refine_attempts=2,
            attempt_status=AttemptStatus.EXECUTED,
        )
        assert ledger.attempt_status is AttemptStatus.EXECUTED

    def test_at_max_with_blocked_status_accepted(self):
        ledger = _make_ledger(
            attempt_number=2,
            max_refine_attempts=2,
            attempt_status=AttemptStatus.BLOCKED,
        )
        assert ledger.attempt_status is AttemptStatus.BLOCKED

    def test_at_max_with_exhausted_status_accepted(self):
        ledger = _make_ledger(
            attempt_number=2,
            max_refine_attempts=2,
            attempt_status=AttemptStatus.EXHAUSTED,
        )
        assert ledger.attempt_status is AttemptStatus.EXHAUSTED

    def test_above_max_with_eligible_status_rejected(self):
        with pytest.raises(ValueError, match="requires status=EXHAUSTED or BLOCKED"):
            _make_ledger(
                attempt_number=3,
                max_refine_attempts=2,
                attempt_status=AttemptStatus.ELIGIBLE,
            )

    def test_above_max_with_executed_status_rejected(self):
        with pytest.raises(ValueError, match="requires status=EXHAUSTED or BLOCKED"):
            _make_ledger(
                attempt_number=3,
                max_refine_attempts=2,
                attempt_status=AttemptStatus.EXECUTED,
            )

    def test_budget_equal_before_after_accepted(self):
        # Boundary: budget_after == budget_before is valid (no reservation).
        ledger = _make_ledger(budget_before=1000.0, budget_after_reserved=1000.0)
        assert ledger.budget_after_reserved == 1000.0


# ===========================================================================
# E. FORBIDDEN_OUTPUT_TOKENS — every token blocks NoMoreRefinementReport
# ===========================================================================
class TestEveryForbiddenTokenBlocks:
    @pytest.mark.parametrize("token", sorted(FORBIDDEN_OUTPUT_TOKENS))
    def test_token_in_recommendation_hint_blocked(self, token):
        with pytest.raises(ValueError, match="runtime-disposition vocabulary"):
            NoMoreRefinementReport(
                reason="attempts_exhausted",
                attempts_used=2,
                max_refine_attempts=2,
                budget_remaining=0.0,
                non_authoritative_recommendation_hint=f"recommend {token} downstream",
            )

    def test_clean_recommendation_hint_accepted(self):
        report = NoMoreRefinementReport(
            reason="attempts_exhausted",
            attempts_used=2,
            max_refine_attempts=2,
            budget_remaining=0.0,
            non_authoritative_recommendation_hint="advisory: see gap report",
        )
        assert "advisory" in report.non_authoritative_recommendation_hint

    def test_forbidden_set_size_at_least_19(self):
        # Spec FORBIDDEN OUTPUTS lists at least 19 items; assert no shrinkage.
        assert len(FORBIDDEN_OUTPUT_TOKENS) >= 19

    @pytest.mark.parametrize(
        "token",
        [
            "ALLOW",
            "DENY",
            "REROUTE",
            "RETRY",
            "HEAL",
            "ESCALATE_HITL",
            "QUARANTINE",
            "MARK_DEGRADED",
            "BLOCK_COMMIT",
        ],
    )
    def test_canonical_runtime_disposition_tokens_present(self, token):
        # Smoke check: the canonical runtime-disposition vocabulary must
        # remain in the forbidden set even if more get added later.
        assert token in FORBIDDEN_OUTPUT_TOKENS


# ===========================================================================
# F. _L3_AUTHORIZATION_TOKENS — every substring blocks decomposition
# ===========================================================================
class TestEveryL3AuthorizationTokenBlocks:
    @pytest.mark.parametrize(
        "forbidden_substring",
        ["execute", "invoke_tool", "authorize_l3", "approve_"],
    )
    def test_each_substring_blocks_l3_gate(self, forbidden_substring):
        decomp = DecompositionPlan(
            decomposition_plan_id="dp-1",
            sub_queries=(SubQuerySpec(sub_query_id="sq-1", text="q"),),
            reason_codes=(f"need to {forbidden_substring} the workflow",),
        )
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, decomposition=decomp)
        l3_gate = next(r for r in results if r.gate is C06Gate.NO_L3_SELF_AUTHORIZATION)
        assert not l3_gate.passed
        assert forbidden_substring in (l3_gate.reason or "")

    @pytest.mark.parametrize(
        "clean_code",
        [
            "need_more_evidence",
            "missing_clause_anchor",
            "policy_section_unmapped",
            "evidence_gap_only",
        ],
    )
    def test_clean_reason_codes_pass(self, clean_code):
        decomp = DecompositionPlan(
            decomposition_plan_id="dp-1",
            sub_queries=(SubQuerySpec(sub_query_id="sq-1", text="q"),),
            reason_codes=(clean_code,),
        )
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, decomposition=decomp)
        l3_gate = next(r for r in results if r.gate is C06Gate.NO_L3_SELF_AUTHORIZATION)
        assert l3_gate.passed


# ===========================================================================
# G. Frozen-dataclass immutability — every C0.6 dataclass + new C0.1-C0.5
# ===========================================================================
class TestFrozenDataclassesImmutable:
    """Spec invariant: all PHASE 1 contracts are immutable (frozen=True)."""

    def test_query_rewrite_plan_frozen(self):
        plan = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("x",),
            bounded_by_original_intent=True,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            plan.rewrite_plan_id = "rp-2"  # type: ignore[misc]

    def test_scope_broaden_plan_frozen(self):
        plan = ScopeBroadenPlan(
            broaden_plan_id="bp-1",
            broaden_dimension=BroadenDimension.TOP_K,
            old_value="5",
            new_value="10",
            bound_source="RouteContract.max_k",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            plan.new_value = "100"  # type: ignore[misc]

    def test_decomposition_plan_frozen(self):
        plan = DecompositionPlan(
            decomposition_plan_id="dp-1",
            sub_queries=(SubQuerySpec(sub_query_id="sq-1", text="q"),),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            plan.decomposition_plan_id = "dp-2"  # type: ignore[misc]

    def test_subquery_spec_frozen(self):
        sq = SubQuerySpec(sub_query_id="sq-1", text="q")
        with pytest.raises(dataclasses.FrozenInstanceError):
            sq.text = "modified"  # type: ignore[misc]

    def test_no_more_refinement_report_frozen(self):
        report = NoMoreRefinementReport(
            reason="r",
            attempts_used=0,
            max_refine_attempts=1,
            budget_remaining=0.0,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.reason = "different"  # type: ignore[misc]

    def test_diagnosis_frozen(self):
        d = WeakSupportDiagnosis(
            diagnosis_id="d-1",
            evidence_status=SupportStatus.WEAK_WITH_CAVEATS,
            primary_gap_type=PrimaryGapType.SPARSE_MISSING,
            recovery_strategy=RefinementStrategy.QUERY_REWRITE,
            likely_recoverable=True,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.diagnosis_id = "d-2"  # type: ignore[misc]

    def test_refinement_attempt_ledger_frozen(self):
        ledger = _make_ledger()
        with pytest.raises(dataclasses.FrozenInstanceError):
            ledger.attempt_number = 99  # type: ignore[misc]

    def test_support_target_profile_frozen(self):
        p = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.support_target_id = "t-2"  # type: ignore[misc]

    def test_source_class_decision_frozen(self):
        d = SourceClassDecision(source_class=SourceClass.DOCS, decision=SourceDecision.INCLUDE)
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.decision = SourceDecision.EXCLUDE  # type: ignore[misc]

    def test_retrieval_mode_plan_frozen(self):
        m = RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True)
        with pytest.raises(dataclasses.FrozenInstanceError):
            m.lane_id = "L2"  # type: ignore[misc]

    def test_raw_hit_frozen(self):
        h = RawHit(raw_hit_id="r-1", source_id="s-1", source_type=SourceClass.DOCS)
        with pytest.raises(dataclasses.FrozenInstanceError):
            h.source_id = "s-2"  # type: ignore[misc]

    def test_retrieval_lane_result_frozen(self):
        r = RetrievalLaneResult(
            lane_id="L1",
            lane_type=RetrievalLane.DENSE,
            query_ref="q-1",
            adapter_id="a",
            adapter_version="v1",
            source_class=SourceClass.DOCS,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.lane_id = "L2"  # type: ignore[misc]

    def test_evidence_fingerprint_frozen(self):
        f = EvidenceFingerprint(source_id="s-1")
        with pytest.raises(dataclasses.FrozenInstanceError):
            f.source_id = "s-2"  # type: ignore[misc]

    def test_excluded_evidence_item_frozen(self):
        e = ExcludedEvidenceItem(
            excluded_evidence_id="e-1",
            original_evidence_ref="ref",
            exclusion_reason=ExclusionReason.STALE,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.excluded_evidence_id = "e-2"  # type: ignore[misc]

    def test_citation_support_map_frozen(self):
        c = CitationSupportMap(
            claim_target_id="ct-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
            required_support_level="direct",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            c.claim_target_id = "ct-2"  # type: ignore[misc]

    def test_support_score_breakdown_v2_frozen(self):
        s = SupportScoreBreakdownV2(support_score=0.5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            s.support_score = 0.9  # type: ignore[misc]

    def test_evidence_gap_report_v2_frozen(self):
        g = EvidenceGapReportV2()
        with pytest.raises(dataclasses.FrozenInstanceError):
            g.missing_exact_terms = ("x",)  # type: ignore[misc]


# ===========================================================================
# H. RetrievalModePlan numeric boundaries
# ===========================================================================
class TestRetrievalModePlanBoundaries:
    def test_score_floor_zero_accepted(self):
        m = RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, score_floor=0.0)
        assert m.score_floor == 0.0

    def test_score_floor_one_accepted(self):
        m = RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, score_floor=1.0)
        assert m.score_floor == 1.0

    def test_score_floor_above_one_rejected(self):
        with pytest.raises(ValueError, match="score_floor"):
            RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, score_floor=1.01)

    def test_score_floor_negative_rejected(self):
        with pytest.raises(ValueError, match="score_floor"):
            RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, score_floor=-0.01)

    def test_budget_slice_zero_accepted(self):
        m = RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, budget_slice=0.0)
        assert m.budget_slice == 0.0

    def test_budget_slice_one_accepted(self):
        m = RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, budget_slice=1.0)
        assert m.budget_slice == 1.0

    def test_budget_slice_out_of_range_rejected(self):
        with pytest.raises(ValueError, match="budget_slice"):
            RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, budget_slice=1.5)

    def test_timeout_zero_rejected(self):
        with pytest.raises(ValueError, match="timeout_ms"):
            RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, timeout_ms=0)

    def test_timeout_negative_rejected(self):
        with pytest.raises(ValueError, match="timeout_ms"):
            RetrievalModePlan(lane_id="L1", lane_type=RetrievalLane.DENSE, enabled=True, timeout_ms=-1)


# ===========================================================================
# I. RawHit / RetrievalLaneResult validation
# ===========================================================================
class TestRawHitValidation:
    def test_empty_raw_hit_id_rejected(self):
        with pytest.raises(ValueError, match="raw_hit_id required"):
            RawHit(raw_hit_id="", source_id="s-1", source_type=SourceClass.DOCS)

    def test_empty_source_id_rejected(self):
        with pytest.raises(ValueError, match="source_id required"):
            RawHit(raw_hit_id="r-1", source_id="", source_type=SourceClass.DOCS)

    def test_line_range_none_accepted(self):
        h = RawHit(raw_hit_id="r-1", source_id="s-1", source_type=SourceClass.DOCS, line_range=None)
        assert h.line_range is None

    def test_line_range_zero_zero_accepted(self):
        h = RawHit(raw_hit_id="r-1", source_id="s-1", source_type=SourceClass.DOCS, line_range=(0, 0))
        assert h.line_range == (0, 0)

    def test_line_range_lo_above_hi_rejected(self):
        with pytest.raises(ValueError, match="invalid line_range"):
            RawHit(raw_hit_id="r-1", source_id="s-1", source_type=SourceClass.DOCS, line_range=(10, 5))

    def test_line_range_negative_lo_rejected(self):
        with pytest.raises(ValueError, match="invalid line_range"):
            RawHit(raw_hit_id="r-1", source_id="s-1", source_type=SourceClass.DOCS, line_range=(-1, 5))


class TestLaneResultValidation:
    def _make(self, **kw) -> RetrievalLaneResult:
        defaults = dict(
            lane_id="L1",
            lane_type=RetrievalLane.DENSE,
            query_ref="q-1",
            adapter_id="a",
            adapter_version="v1",
            source_class=SourceClass.DOCS,
        )
        defaults.update(kw)
        return RetrievalLaneResult(**defaults)

    def test_empty_lane_id_rejected(self):
        with pytest.raises(ValueError, match="lane_id required"):
            self._make(lane_id="")

    def test_empty_adapter_id_rejected(self):
        with pytest.raises(ValueError, match="adapter_id required"):
            self._make(adapter_id="")

    def test_negative_budget_used_rejected(self):
        with pytest.raises(ValueError, match="budget_used"):
            self._make(budget_used=-1.0)

    def test_negative_latency_rejected(self):
        with pytest.raises(ValueError, match="latency_ms"):
            self._make(latency_ms=-1)

    def test_zero_latency_accepted(self):
        r = self._make(latency_ms=0)
        assert r.latency_ms == 0


# ===========================================================================
# J. SupportScoreBreakdownV2 per-field range checks (parametrized)
# ===========================================================================
_SCORE_FIELDS = [
    "support_score",
    "directness_score",
    "coverage_score",
    "citation_score",
    "freshness_score",
    "authority_score",
    "lineage_score",
    "exactness_score",
    "source_parity_score",
]


class TestSupportScoreBreakdownV2Ranges:
    @pytest.mark.parametrize("field", _SCORE_FIELDS)
    def test_each_bounded_field_above_one_rejected(self, field):
        with pytest.raises(ValueError, match=field):
            SupportScoreBreakdownV2(**{"support_score": 0.5, field: 1.01})  # type: ignore[arg-type]

    @pytest.mark.parametrize("field", _SCORE_FIELDS)
    def test_each_bounded_field_below_zero_rejected(self, field):
        with pytest.raises(ValueError, match=field):
            SupportScoreBreakdownV2(**{"support_score": 0.5, field: -0.01})  # type: ignore[arg-type]

    @pytest.mark.parametrize("field", _SCORE_FIELDS)
    def test_each_bounded_field_at_zero_accepted(self, field):
        s = SupportScoreBreakdownV2(**{"support_score": 0.5, field: 0.0})  # type: ignore[arg-type]
        assert getattr(s, field) == 0.0

    @pytest.mark.parametrize("field", _SCORE_FIELDS)
    def test_each_bounded_field_at_one_accepted(self, field):
        s = SupportScoreBreakdownV2(**{"support_score": 0.5, field: 1.0})  # type: ignore[arg-type]
        assert getattr(s, field) == 1.0

    @pytest.mark.parametrize("band", ["low", "medium", "high"])
    def test_all_valid_confidence_bands_accepted(self, band):
        s = SupportScoreBreakdownV2(support_score=0.5, confidence_band=band)
        assert s.confidence_band == band

    @pytest.mark.parametrize(
        "invalid",
        ["LOW", "Medium", "HIGH", "extreme", "", "very_high", " low"],
    )
    def test_each_invalid_confidence_band_rejected(self, invalid):
        with pytest.raises(ValueError, match="confidence_band"):
            SupportScoreBreakdownV2(support_score=0.5, confidence_band=invalid)


# ===========================================================================
# K. Hash determinism / order-invariance / distinctness
# ===========================================================================
class TestHashStress:
    def test_pool_manifest_hash_order_invariant_on_hits(self):
        # raw_hit_ids is sorted internally → order should not matter.
        h1 = compute_pool_manifest_hash(
            plan_hash="plan-1",
            raw_hit_ids=("r1", "r2", "r3"),
            lane_manifest_hashes=("L1", "L2"),
        )
        h2 = compute_pool_manifest_hash(
            plan_hash="plan-1",
            raw_hit_ids=("r3", "r2", "r1"),
            lane_manifest_hashes=("L1", "L2"),
        )
        assert h1 == h2

    def test_pool_manifest_hash_order_invariant_on_lanes(self):
        h1 = compute_pool_manifest_hash(
            plan_hash="plan-1",
            raw_hit_ids=("r1",),
            lane_manifest_hashes=("L1", "L2"),
        )
        h2 = compute_pool_manifest_hash(
            plan_hash="plan-1",
            raw_hit_ids=("r1",),
            lane_manifest_hashes=("L2", "L1"),
        )
        assert h1 == h2

    def test_pool_manifest_hash_changes_with_plan_hash(self):
        h1 = compute_pool_manifest_hash(
            plan_hash="plan-A",
            raw_hit_ids=("r1",),
            lane_manifest_hashes=("L1",),
        )
        h2 = compute_pool_manifest_hash(
            plan_hash="plan-B",
            raw_hit_ids=("r1",),
            lane_manifest_hashes=("L1",),
        )
        assert h1 != h2

    def test_pool_manifest_hash_changes_with_hits(self):
        h1 = compute_pool_manifest_hash(
            plan_hash="plan-1",
            raw_hit_ids=("r1",),
            lane_manifest_hashes=("L1",),
        )
        h2 = compute_pool_manifest_hash(
            plan_hash="plan-1",
            raw_hit_ids=("r2",),
            lane_manifest_hashes=("L1",),
        )
        assert h1 != h2

    def test_profile_hash_changes_with_target_type(self):
        p1 = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
        )
        p2 = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.COMPARISON,
        )
        assert compute_profile_hash(p1) != compute_profile_hash(p2)

    def test_profile_hash_changes_with_min_independent_sources(self):
        p1 = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
            min_independent_sources=1,
        )
        p2 = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
            min_independent_sources=3,
        )
        assert compute_profile_hash(p1) != compute_profile_hash(p2)

    def test_lane_result_hash_independent_of_latency(self):
        # Spec: lane_manifest_hash deterministic over adapter + query +
        # raw_hits; latency is observation-only.
        common = dict(
            lane_id="L1",
            lane_type=RetrievalLane.DENSE,
            query_ref="q-1",
            adapter_id="a",
            adapter_version="v1",
            source_class=SourceClass.DOCS,
            raw_hits=(RawHit(raw_hit_id="r1", source_id="s1", source_type=SourceClass.DOCS),),
        )
        r1 = RetrievalLaneResult(**common, latency_ms=10)
        r2 = RetrievalLaneResult(**common, latency_ms=200)
        assert r1.compute_manifest_hash() == r2.compute_manifest_hash()

    def test_lane_result_hash_changes_with_adapter_version(self):
        common = dict(
            lane_id="L1",
            lane_type=RetrievalLane.DENSE,
            query_ref="q-1",
            adapter_id="a",
            source_class=SourceClass.DOCS,
        )
        r1 = RetrievalLaneResult(**common, adapter_version="v1")
        r2 = RetrievalLaneResult(**common, adapter_version="v2")
        assert r1.compute_manifest_hash() != r2.compute_manifest_hash()

    def test_reentry_hash_distinct_for_all_three_targets(self):
        rewrite = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("x",),
            bounded_by_original_intent=True,
        )
        h1 = compute_reentry_input_hash(target=ReentryTarget.C0_1, rewrite=rewrite)
        h2 = compute_reentry_input_hash(target=ReentryTarget.C0_4, rewrite=rewrite)
        h3 = compute_reentry_input_hash(target=ReentryTarget.C0_5, rewrite=rewrite)
        assert len({h1, h2, h3}) == 3

    def test_reentry_hash_unicode_stable(self):
        # Non-ASCII content must hash deterministically across calls.
        rewrite = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("café", "résumé", "naïve"),
            bounded_by_original_intent=True,
        )
        h1 = compute_reentry_input_hash(target=ReentryTarget.C0_1, rewrite=rewrite)
        h2 = compute_reentry_input_hash(target=ReentryTarget.C0_1, rewrite=rewrite)
        assert h1 == h2
        assert len(h1) > 0

    def test_ledger_hash_changes_with_attempt_number(self):
        l1 = _make_ledger(attempt_number=0)
        l2 = _make_ledger(attempt_number=1)
        assert compute_ledger_hash(l1) != compute_ledger_hash(l2)

    def test_ledger_hash_changes_with_status(self):
        l1 = _make_ledger(attempt_status=AttemptStatus.ELIGIBLE)
        l2 = _make_ledger(attempt_status=AttemptStatus.EXECUTED)
        assert compute_ledger_hash(l1) != compute_ledger_hash(l2)


# ===========================================================================
# L. build_otel_attributes type checks (OTEL spec compatibility)
# ===========================================================================
class TestOtelAttributeTypes:
    def _attrs(self):
        inp = _make_input()
        diagnosis = diagnose_from_contract(inp.final_evidence_contract, diagnosis_id="d-1")
        return build_otel_attributes(
            inp,
            diagnosis,
            selected_strategy=RefinementStrategy.QUERY_REWRITE,
            attempt_number=0,
            budget_before=1000.0,
            budget_after_reserved=900.0,
            reentry_target=ReentryTarget.C0_1,
            reentry_input_hash="h1",
            ledger_hash="lh1",
        )

    def test_all_values_otel_compatible_types(self):
        # OTEL attribute values must be str | bool | int | float (or sequences).
        for key, value in self._attrs().items():
            assert isinstance(key, str), f"{key!r} not str"
            assert isinstance(value, (str, bool, int, float)), (
                f"{key}={value!r} type={type(value).__name__} not OTEL-compatible"
            )

    def test_attribute_keys_namespaced(self):
        attrs = self._attrs()
        # At minimum the c0.stage key is dotted; others may be snake_case.
        assert "c0.stage" in attrs
        assert attrs["c0.stage"] == "C0.6"

    def test_otel_attributes_deterministic(self):
        a1 = self._attrs()
        a2 = self._attrs()
        assert a1 == a2

    def test_required_keys_present_with_correct_types(self):
        attrs = self._attrs()
        required = {
            "c0.stage": str,
            "prior_contract_hash": str,
            "evidence_status": str,
            "primary_gap_type": str,
            "selected_strategy": str,
            "attempt_number": int,
            "max_refine_attempts": int,
            "budget_before": float,
            "budget_after_reserved": float,
            "reentry_target": str,
            "reentry_input_hash": str,
            "ledger_hash": str,
        }
        for key, expected_type in required.items():
            assert key in attrs, f"{key} missing"
            assert isinstance(attrs[key], expected_type), (
                f"{key} type={type(attrs[key]).__name__} expected {expected_type.__name__}"
            )

    def test_reentry_target_none_yields_empty_string(self):
        inp = _make_input()
        diagnosis = diagnose_from_contract(inp.final_evidence_contract, diagnosis_id="d-1")
        attrs = build_otel_attributes(
            inp,
            diagnosis,
            selected_strategy=RefinementStrategy.STOP_WITH_GAP_REPORT,
            attempt_number=0,
            budget_before=1000.0,
            budget_after_reserved=1000.0,
            reentry_target=None,
            reentry_input_hash="",
            ledger_hash="lh1",
        )
        assert attrs["reentry_target"] == ""


# ===========================================================================
# M. is_eligible_for_refinement edge cases
# ===========================================================================
class TestIsEligibleEdges:
    @pytest.mark.parametrize(
        "status",
        [SupportStatus.WEAK, SupportStatus.WEAK_WITH_CAVEATS, SupportStatus.CONFLICTED, SupportStatus.EMPTY],
    )
    def test_eligible_statuses_pass_helper(self, status):
        contract = _make_contract(
            status=status,
            gaps=(UnresolvedGapOut(gap_type=GapType.MISSING_DIRECT_SUPPORT, severity="low"),)
            if status != SupportStatus.CONFLICTED
            else (),
            contradictions=(ContradictionFlagOut(type="version", source_a="a", source_b="b"),)
            if status == SupportStatus.CONFLICTED
            else (),
        )
        assert is_eligible_for_refinement(
            contract,
            refine_attempts_used=0,
            max_refine_attempts=2,
            budget_remaining=1000.0,
        )

    def test_blocked_eligible_only_with_reason(self):
        contract = _make_contract(
            status=SupportStatus.BLOCKED,
            gaps=(),
            blocked_reason="ACL forbids",
        )
        assert is_eligible_for_refinement(
            contract,
            refine_attempts_used=0,
            max_refine_attempts=2,
            budget_remaining=1000.0,
        )

    def test_attempts_at_max_not_eligible(self):
        contract = _make_contract()
        assert not is_eligible_for_refinement(
            contract,
            refine_attempts_used=2,
            max_refine_attempts=2,
            budget_remaining=1000.0,
        )

    def test_zero_budget_not_eligible(self):
        contract = _make_contract()
        assert not is_eligible_for_refinement(
            contract,
            refine_attempts_used=0,
            max_refine_attempts=2,
            budget_remaining=0.0,
        )

    def test_one_below_max_eligible(self):
        contract = _make_contract()
        assert is_eligible_for_refinement(
            contract,
            refine_attempts_used=1,
            max_refine_attempts=2,
            budget_remaining=1.0,
        )

    def test_pass_status_never_eligible(self):
        contract = _make_contract(status=SupportStatus.PASS, gaps=())
        assert not is_eligible_for_refinement(
            contract,
            refine_attempts_used=0,
            max_refine_attempts=2,
            budget_remaining=1000.0,
        )


# ===========================================================================
# N. diagnose_from_contract heuristic coverage
# ===========================================================================
class TestDiagnoseHeuristics:
    def test_empty_diagnosis_id_rejected(self):
        with pytest.raises(ValueError, match="diagnosis_id required"):
            diagnose_from_contract(_make_contract(), diagnosis_id="")

    def test_empty_status_yields_some_gap_type(self):
        contract = _make_contract(status=SupportStatus.EMPTY, gaps=())
        d = diagnose_from_contract(contract, diagnosis_id="d-1")
        assert isinstance(d.primary_gap_type, PrimaryGapType)
        assert d.evidence_status is SupportStatus.EMPTY

    def test_blocked_status_marked_non_recoverable(self):
        contract = _make_contract(
            status=SupportStatus.BLOCKED,
            gaps=(),
            blocked_reason="ACL forbids",
        )
        d = diagnose_from_contract(contract, diagnosis_id="d-1")
        assert d.primary_gap_type in (
            PrimaryGapType.ACL_BLOCKED,
            PrimaryGapType.ROUTE_SCOPE_BLOCKED,
        )
        assert not d.likely_recoverable
        assert d.non_recoverable_reason

    def test_diagnosis_includes_contradiction_refs(self):
        contract = _make_contract(
            status=SupportStatus.CONFLICTED,
            gaps=(),
            contradictions=(
                ContradictionFlagOut(type="version", source_a="docA", source_b="docB"),
                ContradictionFlagOut(type="value", source_a="docA", source_b="docC"),
            ),
        )
        d = diagnose_from_contract(contract, diagnosis_id="d-1")
        assert len(d.contradiction_refs) == 2
        assert "docA|docB" in d.contradiction_refs
        assert "docA|docC" in d.contradiction_refs

    def test_diagnosis_deterministic_across_calls(self):
        c = _make_contract()
        d1 = diagnose_from_contract(c, diagnosis_id="d-x")
        d2 = diagnose_from_contract(c, diagnosis_id="d-x")
        assert d1 == d2


# ===========================================================================
# O. ExclusionReason enum coverage
# ===========================================================================
class TestExclusionReasonCoverage:
    @pytest.mark.parametrize("reason", list(ExclusionReason))
    def test_each_reason_constructs_excluded_item(self, reason):
        e = ExcludedEvidenceItem(
            excluded_evidence_id="e-1",
            original_evidence_ref="ref",
            exclusion_reason=reason,
        )
        assert e.exclusion_reason is reason

    def test_canonical_codes_present(self):
        codes = {r.value for r in ExclusionReason}
        for required in (
            "stale",
            "no_citation_anchor",
            "policy_violation",
            "acl_blocked",
            "duplicate",
            "instruction_like_payload",
        ):
            assert required in codes, f"{required!r} missing from ExclusionReason"


# ===========================================================================
# P. SourceClassDecision INCLUDE / REQUIRED / OPTIONAL paths
# ===========================================================================
class TestSourceClassDecisionPaths:
    @pytest.mark.parametrize(
        "decision",
        [SourceDecision.INCLUDE, SourceDecision.REQUIRED, SourceDecision.OPTIONAL],
    )
    def test_non_exclude_decisions_dont_require_reason(self, decision):
        d = SourceClassDecision(source_class=SourceClass.DOCS, decision=decision)
        assert d.decision is decision
        assert d.reason_codes == ()

    def test_exclude_with_empty_tuple_reason_rejected(self):
        with pytest.raises(ValueError, match="EXCLUDE requires reason_codes"):
            SourceClassDecision(
                source_class=SourceClass.DOCS,
                decision=SourceDecision.EXCLUDE,
                reason_codes=(),
            )

    def test_exclude_with_multiple_reasons_accepted(self):
        d = SourceClassDecision(
            source_class=SourceClass.DOCS,
            decision=SourceDecision.EXCLUDE,
            reason_codes=("stale_corpus", "low_authority"),
        )
        assert len(d.reason_codes) == 2


# ===========================================================================
# Q. CitationSupportMap recall + non-EXACT_QUOTE paths
# ===========================================================================
class TestCitationSupportMapPaths:
    def _make(self, **kw) -> CitationSupportMap:
        defaults = dict(
            claim_target_id="ct-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
            required_support_level="direct",
        )
        defaults.update(kw)
        return CitationSupportMap(**defaults)

    def test_recall_score_above_one_rejected(self):
        with pytest.raises(ValueError, match="citation_recall_score"):
            self._make(citation_recall_score=1.01)

    def test_recall_score_negative_rejected(self):
        with pytest.raises(ValueError, match="citation_recall_score"):
            self._make(citation_recall_score=-0.01)

    def test_recall_score_zero_accepted(self):
        c = self._make(citation_recall_score=0.0)
        assert c.citation_recall_score == 0.0

    def test_recall_score_one_accepted(self):
        c = self._make(citation_recall_score=1.0)
        assert c.citation_recall_score == 1.0

    def test_precision_score_above_one_rejected(self):
        with pytest.raises(ValueError, match="citation_precision_score"):
            self._make(citation_precision_score=1.01)

    def test_non_exact_quote_with_quote_eligibility_no_span_allowed(self):
        # SOURCE_SUMMARY with quote_eligibility=True and no span is OK
        # — only EXACT_QUOTE forces direct_span_refs.
        c = self._make(
            support_target_type=SupportTarget.SOURCE_SUMMARY,
            quote_eligibility=True,
            direct_span_refs=(),
        )
        assert c.quote_eligibility is True

    def test_exact_quote_with_quote_eligibility_false_allowed(self):
        c = self._make(
            support_target_type=SupportTarget.EXACT_QUOTE,
            quote_eligibility=False,
            direct_span_refs=(),
        )
        assert c.quote_eligibility is False

    def test_exact_quote_with_eligibility_and_span_accepted(self):
        c = self._make(
            support_target_type=SupportTarget.EXACT_QUOTE,
            quote_eligibility=True,
            direct_span_refs=("span-1",),
        )
        assert c.direct_span_refs == ("span-1",)


# ===========================================================================
# R. Token-level matching: no false positives on substring
# ===========================================================================
class TestTokenLevelMatchingNoFalsePositives:
    def test_allowed_substring_in_word_does_not_trip_gate(self):
        """`_gate_no_runtime_disposition` uses split() to avoid 'ALLOW' inside
        'ALLOWED' tripping the gate (token-level, not substring)."""
        rewrite = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("x",),
            rationale="find allowed citations and disallowed sources",
            bounded_by_original_intent=True,
        )
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, rewrite=rewrite)
        gate = next(r for r in results if r.gate is C06Gate.NO_RUNTIME_DISPOSITION)
        assert gate.passed

    def test_retry_substring_in_word_does_not_trip_gate(self):
        rewrite = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("x",),
            rationale="retrying the synonym lookup is bounded",
            bounded_by_original_intent=True,
        )
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, rewrite=rewrite)
        gate = next(r for r in results if r.gate is C06Gate.NO_RUNTIME_DISPOSITION)
        assert gate.passed


# ===========================================================================
# S. Spec invariant: route_id mismatch caught by route_scope gate
# ===========================================================================
class TestRouteScopeGate:
    def test_input_route_id_matching_contract_passes_gate(self):
        contract = _make_contract()  # contract route_id = "R3_GROUNDED"
        inp = _make_input(final_evidence_contract=contract, route_id="R3_GROUNDED")
        diagnosis = diagnose_from_contract(contract, diagnosis_id="d-1")
        results = run_gates(inp, diagnosis)
        scope = next(r for r in results if r.gate is C06Gate.ROUTE_SCOPE)
        assert scope.passed


# ===========================================================================
# T. SupportTargetProfile boundary cases
# ===========================================================================
class TestSupportTargetProfileBoundaries:
    def test_min_independent_sources_zero_rejected(self):
        with pytest.raises(ValueError, match="min_independent_sources"):
            SupportTargetProfile(
                support_target_id="t-1",
                support_target_type=SupportTarget.SOURCE_SUMMARY,
                min_independent_sources=0,
            )

    def test_min_independent_sources_one_accepted(self):
        p = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
            min_independent_sources=1,
        )
        assert p.min_independent_sources == 1

    def test_exact_quote_full_compliance_accepted(self):
        p = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.EXACT_QUOTE,
            direct_quote_required=True,
            requires_sparse_support=True,
            required_citation_precision=CitationPrecision.SPAN_EXACT,
        )
        assert p.support_target_type is SupportTarget.EXACT_QUOTE

    def test_policy_clause_with_section_precision_accepted(self):
        p = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.POLICY_CLAUSE,
            required_citation_precision=CitationPrecision.SECTION,
        )
        assert p.required_citation_precision is CitationPrecision.SECTION

    def test_policy_clause_with_span_exact_precision_accepted(self):
        p = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.POLICY_CLAUSE,
            required_citation_precision=CitationPrecision.SPAN_EXACT,
        )
        assert p.required_citation_precision is CitationPrecision.SPAN_EXACT

    def test_policy_clause_with_none_precision_rejected(self):
        with pytest.raises(ValueError, match="POLICY_CLAUSE"):
            SupportTargetProfile(
                support_target_id="t-1",
                support_target_type=SupportTarget.POLICY_CLAUSE,
                required_citation_precision=CitationPrecision.NONE,
            )

    @pytest.mark.parametrize(
        "policy",
        [
            UnsupportedInferencePolicy.CAVEAT,
            UnsupportedInferencePolicy.REJECT,
            UnsupportedInferencePolicy.ALLOW_WITH_FLAG,
        ],
    )
    def test_all_unsupported_inference_policies_accepted(self, policy):
        p = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
            unsupported_inference_policy=policy,
        )
        assert p.unsupported_inference_policy is policy


# ===========================================================================
# U. EvidenceFingerprint extra-field coverage
# ===========================================================================
class TestEvidenceFingerprintExtras:
    def test_fingerprint_key_changes_with_source_version(self):
        f1 = EvidenceFingerprint(source_id="s1", source_version="v1")
        f2 = EvidenceFingerprint(source_id="s1", source_version="v2")
        assert f1.fingerprint_key != f2.fingerprint_key

    def test_fingerprint_key_changes_with_content_hash(self):
        f1 = EvidenceFingerprint(source_id="s1", content_hash="abc")
        f2 = EvidenceFingerprint(source_id="s1", content_hash="def")
        assert f1.fingerprint_key != f2.fingerprint_key

    def test_fingerprint_key_changes_with_line_range(self):
        f1 = EvidenceFingerprint(source_id="s1", line_range=(1, 10))
        f2 = EvidenceFingerprint(source_id="s1", line_range=(1, 20))
        assert f1.fingerprint_key != f2.fingerprint_key

    def test_graph_relation_refs_default_empty(self):
        f = EvidenceFingerprint(source_id="s1")
        assert f.graph_relation_refs == ()

    def test_all_graph_relation_types_storable(self):
        all_relations = tuple(GraphRelation)
        f = EvidenceFingerprint(source_id="s1", graph_relation_refs=all_relations)
        assert len(f.graph_relation_refs) == len(all_relations)

    def test_retrieval_lane_set_default_empty(self):
        f = EvidenceFingerprint(source_id="s1")
        assert f.retrieval_lane_set == ()

    def test_fingerprint_key_independent_of_lane_set(self):
        f1 = EvidenceFingerprint(
            source_id="s1",
            span_ref="span",
            retrieval_lane_set=(RetrievalLane.DENSE,),
        )
        f2 = EvidenceFingerprint(
            source_id="s1",
            span_ref="span",
            retrieval_lane_set=(RetrievalLane.SPARSE,),
        )
        # The fingerprint_key MUST be lane-independent (spec C0.4 dedupe rule).
        assert f1.fingerprint_key == f2.fingerprint_key
