"""Tests for C0.6 spec-grade weak-support-refinement contracts.

Spec source: ``docs/reference/03_L0_Routing/C0 - Context Engine/
C0.6_Weak_Support_Refinement_detailed.md`` — TEST REQUIREMENTS section.

Each spec test requirement is implemented as a named test below.
"""

from __future__ import annotations

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
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    FreshnessClass,
    GapType,
    RefineTactic,
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
    bridge_tactic_to_strategy,
    build_no_more_refinement_report,
    build_otel_attributes,
    compute_ledger_hash,
    compute_reentry_input_hash,
    diagnose_from_contract,
    is_eligible_for_refinement,
    run_gates,
    seal_ledger,
)


# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------
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
        replay_metadata=ReplayMetadata(
            route_replay_key="rk-1",
            policy_hash="ph-1",
            blueprint_hash="bh-1",
        ),
    )
    return seal_final_contract(contract)


def _make_input(
    *,
    contract: FinalEvidenceContract | None = None,
    plan: RetrievalPlan | None = None,
    refine_attempts_used: int = 0,
    max_refine_attempts: int = 1,
    budget_remaining: float = 1000.0,
    allowed_source_classes: tuple[SourceClass, ...] = (SourceClass.DOCS,),
    disallowed_sources: tuple[str, ...] = ("rumor-shelf",),
) -> WeakSupportRefinementInput:
    return WeakSupportRefinementInput(
        final_evidence_contract=contract or _make_contract(),
        retrieval_plan=plan or _make_plan(max_refine_attempts=max_refine_attempts),
        original_query_spec="example query",
        route_id="R3_GROUNDED",
        route_replay_key="rk-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
        max_refine_attempts=max_refine_attempts,
        refine_attempts_used=refine_attempts_used,
        budget_remaining=budget_remaining,
        allowed_sources=("doc-shelf",),
        disallowed_sources=disallowed_sources,
        allowed_source_classes=allowed_source_classes,
        freshness_class="current",
        weak_support_policy="caveat",
    )


# ---------------------------------------------------------------------------
# 1. test C0.6 refuses PASS contracts.
# ---------------------------------------------------------------------------
class TestRefuseNonEligibleStatuses:
    def test_pass_contract_rejected_at_input_construction(self):
        contract = _make_contract(status=SupportStatus.PASS, gaps=())
        with pytest.raises(ValueError, match="C0.6 refuses status='PASS'"):
            _make_input(contract=contract)

    def test_eligibility_helper_rejects_pass(self):
        contract = _make_contract(status=SupportStatus.PASS, gaps=())
        assert not is_eligible_for_refinement(
            contract,
            refine_attempts_used=0,
            max_refine_attempts=2,
            budget_remaining=1000,
        )

    def test_weak_with_caveats_eligible(self):
        contract = _make_contract(status=SupportStatus.WEAK_WITH_CAVEATS)
        assert is_eligible_for_refinement(
            contract,
            refine_attempts_used=0,
            max_refine_attempts=2,
            budget_remaining=1000,
        )

    def test_blocked_eligible_for_diagnosis(self):
        # BLOCKED contracts can be diagnosed; the gates will then halt them.
        # Construct directly because _make_contract() doesn't pass blocked_reason.
        contract = FinalEvidenceContract(
            contract_id="c2",
            route_id="R3_GROUNDED",
            route_replay_key="rk-1",
            policy_hash="ph-1",
            blueprint_hash="bh-1",
            status=SupportStatus.BLOCKED,
            blocked_reason="acl_blocked",
            replay_metadata=ReplayMetadata(
                route_replay_key="rk-1", policy_hash="ph-1", blueprint_hash="bh-1"
            ),
        )
        assert is_eligible_for_refinement(
            contract,
            refine_attempts_used=0,
            max_refine_attempts=2,
            budget_remaining=1000,
        )


# ---------------------------------------------------------------------------
# 2. test attempts exhausted stops with NoMoreRefinementReport.
# ---------------------------------------------------------------------------
class TestAttemptsExhausted:
    def test_attempts_exhausted_gate_fails(self):
        inp = _make_input(refine_attempts_used=2, max_refine_attempts=2)
        diagnosis = diagnose_from_contract(
            inp.final_evidence_contract, diagnosis_id="d-1"
        )
        results = run_gates(inp, diagnosis)
        attempt_gate = next(r for r in results if r.gate is C06Gate.REFINEMENT_ATTEMPT_LIMIT)
        assert not attempt_gate.passed
        assert "used=2" in attempt_gate.reason

    def test_no_more_refinement_report_built_correctly(self):
        inp = _make_input(refine_attempts_used=2, max_refine_attempts=2)
        report = build_no_more_refinement_report(
            inp, reason="attempts_exhausted"
        )
        assert isinstance(report, NoMoreRefinementReport)
        assert report.attempts_used == 2
        assert report.max_refine_attempts == 2
        assert report.unresolved_gap_report  # gap report is forwarded


# ---------------------------------------------------------------------------
# 3. test budget exhausted stops.
# ---------------------------------------------------------------------------
class TestBudgetExhausted:
    def test_zero_budget_fails_gate(self):
        inp = _make_input(budget_remaining=0.0)
        diagnosis = diagnose_from_contract(
            inp.final_evidence_contract, diagnosis_id="d-1"
        )
        results = run_gates(inp, diagnosis)
        budget_gate = next(r for r in results if r.gate is C06Gate.BUDGET_REMAINING)
        assert not budget_gate.passed

    def test_eligibility_helper_rejects_zero_budget(self):
        contract = _make_contract()
        assert not is_eligible_for_refinement(
            contract,
            refine_attempts_used=0,
            max_refine_attempts=2,
            budget_remaining=0,
        )

    def test_negative_budget_rejected_at_construction(self):
        with pytest.raises(ValueError, match="budget_remaining must be >= 0"):
            _make_input(budget_remaining=-1.0)


# ---------------------------------------------------------------------------
# 4. test disallowed source is not introduced during broaden.
# ---------------------------------------------------------------------------
class TestDisallowedSourceNotIntroduced:
    def test_broaden_to_disallowed_source_blocked(self):
        inp = _make_input(disallowed_sources=("rumor-shelf",))
        broaden = ScopeBroadenPlan(
            broaden_plan_id="bp-1",
            broaden_dimension=BroadenDimension.SOURCE_CLASS,
            old_value="docs",
            new_value="rumor-shelf",
            bound_source="RouteContract.allowed_source_classes",
        )
        diagnosis = diagnose_from_contract(
            inp.final_evidence_contract, diagnosis_id="d-1"
        )
        results = run_gates(inp, diagnosis, broaden=broaden)
        scope_gate = next(
            r for r in results if r.gate is C06Gate.SOURCE_SCOPE_NO_EXPAND
        )
        assert not scope_gate.passed

    def test_broaden_to_unlisted_source_class_blocked(self):
        inp = _make_input(allowed_source_classes=(SourceClass.DOCS,))
        broaden = ScopeBroadenPlan(
            broaden_plan_id="bp-1",
            broaden_dimension=BroadenDimension.SOURCE_CLASS,
            old_value="docs",
            new_value="logs",  # not in allowed_source_classes
            bound_source="RouteContract.allowed_source_classes",
        )
        diagnosis = diagnose_from_contract(
            inp.final_evidence_contract, diagnosis_id="d-1"
        )
        results = run_gates(inp, diagnosis, broaden=broaden)
        scope_gate = next(
            r for r in results if r.gate is C06Gate.SOURCE_SCOPE_NO_EXPAND
        )
        assert not scope_gate.passed

    def test_broaden_within_scope_passes_gate(self):
        inp = _make_input(
            allowed_source_classes=(SourceClass.DOCS, SourceClass.CODE)
        )
        broaden = ScopeBroadenPlan(
            broaden_plan_id="bp-1",
            broaden_dimension=BroadenDimension.SOURCE_CLASS,
            old_value="docs",
            new_value="code",
            bound_source="RouteContract.allowed_source_classes",
        )
        diagnosis = diagnose_from_contract(
            inp.final_evidence_contract, diagnosis_id="d-1"
        )
        results = run_gates(inp, diagnosis, broaden=broaden)
        scope_gate = next(
            r for r in results if r.gate is C06Gate.SOURCE_SCOPE_NO_EXPAND
        )
        assert scope_gate.passed


# ---------------------------------------------------------------------------
# 5. test query rewrite does not change original intent.
# ---------------------------------------------------------------------------
class TestQueryRewriteIntentBound:
    def test_unbounded_rewrite_rejected(self):
        with pytest.raises(ValueError, match="bounded_by_original_intent"):
            QueryRewritePlan(
                rewrite_plan_id="rp-1",
                original_query_terms=("a", "b"),
                added_terms=("c",),
                bounded_by_original_intent=False,
            )

    def test_bounded_rewrite_constructs(self):
        plan = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("a", "b"),
            added_terms=("c", "d"),
            bounded_by_original_intent=True,
        )
        assert plan.added_terms == ("c", "d")
        assert plan.bounded_by_original_intent


# ---------------------------------------------------------------------------
# 6. test decomposition stays evidence-only and does not authorize L3.
# ---------------------------------------------------------------------------
class TestDecompositionNoExecutionAuthority:
    def test_reason_codes_with_execute_blocked(self):
        decomp = DecompositionPlan(
            decomposition_plan_id="dp-1",
            sub_queries=(
                SubQuerySpec(sub_query_id="sq1", text="what is X"),
                SubQuerySpec(sub_query_id="sq2", text="what is Y"),
            ),
            reason_codes=("authorize_l3_step",),
        )
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, decomposition=decomp)
        l3_gate = next(
            r for r in results if r.gate is C06Gate.NO_L3_SELF_AUTHORIZATION
        )
        assert not l3_gate.passed

    def test_reason_codes_with_invoke_tool_blocked(self):
        decomp = DecompositionPlan(
            decomposition_plan_id="dp-1",
            sub_queries=(SubQuerySpec(sub_query_id="sq1", text="what is X"),),
            reason_codes=("invoke_tool_search",),
        )
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, decomposition=decomp)
        l3_gate = next(
            r for r in results if r.gate is C06Gate.NO_L3_SELF_AUTHORIZATION
        )
        assert not l3_gate.passed

    def test_decomposition_with_only_evidence_reason_codes_passes(self):
        decomp = DecompositionPlan(
            decomposition_plan_id="dp-1",
            sub_queries=(
                SubQuerySpec(sub_query_id="sq1", text="what is X"),
                SubQuerySpec(sub_query_id="sq2", text="what is Y"),
            ),
            reason_codes=("compound_target", "evidence_decomposition"),
            workflow_reroute_candidate_hint=True,  # hint is allowed
        )
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, decomposition=decomp)
        l3_gate = next(
            r for r in results if r.gate is C06Gate.NO_L3_SELF_AUTHORIZATION
        )
        assert l3_gate.passed

    def test_empty_subqueries_rejected(self):
        with pytest.raises(ValueError, match="at least one sub-query"):
            DecompositionPlan(
                decomposition_plan_id="dp-1",
                sub_queries=(),
            )

    def test_subqueries_exceeding_max_rejected(self):
        with pytest.raises(ValueError, match="exceeds max_subqueries"):
            DecompositionPlan(
                decomposition_plan_id="dp-1",
                sub_queries=tuple(
                    SubQuerySpec(sub_query_id=f"sq{i}", text=f"q{i}") for i in range(5)
                ),
                max_subqueries=4,
            )


# ---------------------------------------------------------------------------
# 7. test unresolved contradiction remains surfaced.
# ---------------------------------------------------------------------------
class TestContradictionPreserved:
    def test_contradiction_diagnosed_as_primary_gap(self):
        contract = _make_contract(
            status=SupportStatus.CONFLICTED,
            gaps=(),
            contradictions=(
                ContradictionFlagOut(
                    type="version", source_a="docA", source_b="docB"
                ),
            ),
        )
        diagnosis = diagnose_from_contract(contract, diagnosis_id="d-1")
        assert diagnosis.primary_gap_type is PrimaryGapType.CONTRADICTION_UNRESOLVED
        assert diagnosis.contradiction_refs

    def test_contradiction_recovery_strategy_is_decompose(self):
        contract = _make_contract(
            status=SupportStatus.CONFLICTED,
            gaps=(),
            contradictions=(
                ContradictionFlagOut(
                    type="version", source_a="docA", source_b="docB"
                ),
            ),
        )
        diagnosis = diagnose_from_contract(contract, diagnosis_id="d-1")
        assert diagnosis.recovery_strategy is RefinementStrategy.DECOMPOSE_EVIDENCE_NEED


# ---------------------------------------------------------------------------
# 8. test re-entry input hash deterministic.
# ---------------------------------------------------------------------------
class TestReentryHashDeterministic:
    def test_same_inputs_same_hash(self):
        rewrite = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("a", "b"),
            added_terms=("c",),
            bounded_by_original_intent=True,
        )
        h1 = compute_reentry_input_hash(
            target=ReentryTarget.C0_1, rewrite=rewrite, prior_contract_hash="prior-1"
        )
        h2 = compute_reentry_input_hash(
            target=ReentryTarget.C0_1, rewrite=rewrite, prior_contract_hash="prior-1"
        )
        assert h1 == h2
        assert len(h1) == 32  # blake2b 16-byte digest hex-encoded

    def test_different_strategy_different_hash(self):
        rewrite = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("a",),
            bounded_by_original_intent=True,
        )
        broaden = ScopeBroadenPlan(
            broaden_plan_id="bp-1",
            broaden_dimension=BroadenDimension.TOP_K,
            old_value="5",
            new_value="10",
            bound_source="RouteContract.max_k",
        )
        h_rewrite = compute_reentry_input_hash(
            target=ReentryTarget.C0_1, rewrite=rewrite
        )
        h_broaden = compute_reentry_input_hash(
            target=ReentryTarget.C0_1, broaden=broaden
        )
        assert h_rewrite != h_broaden

    def test_different_target_different_hash(self):
        rewrite = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("a",),
            bounded_by_original_intent=True,
        )
        h1 = compute_reentry_input_hash(target=ReentryTarget.C0_1, rewrite=rewrite)
        h2 = compute_reentry_input_hash(target=ReentryTarget.C0_4, rewrite=rewrite)
        assert h1 != h2

    def test_reentry_hash_gate_requires_nonempty_hash(self):
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, reentry_input_hash="")
        # When empty hash supplied, gate is not run; sanity check it's absent.
        assert not any(r.gate is C06Gate.REENTRY_HASH for r in results)
        # When non-empty hash supplied, gate is run and passes.
        results = run_gates(
            _make_input(), diagnosis, reentry_input_hash="abc123"
        )
        gate = next(r for r in results if r.gate is C06Gate.REENTRY_HASH)
        assert gate.passed


# ---------------------------------------------------------------------------
# 9. test no runtime disposition vocabulary appears in outputs.
# ---------------------------------------------------------------------------
class TestNoRuntimeDispositionLeak:
    def test_forbidden_token_in_recommendation_hint_blocked(self):
        with pytest.raises(ValueError, match="runtime-disposition vocabulary"):
            NoMoreRefinementReport(
                reason="exhausted",
                attempts_used=2,
                max_refine_attempts=2,
                budget_remaining=0,
                non_authoritative_recommendation_hint="please ESCALATE_HITL now",
            )

    def test_clean_recommendation_hint_allowed(self):
        report = NoMoreRefinementReport(
            reason="exhausted",
            attempts_used=2,
            max_refine_attempts=2,
            budget_remaining=0,
            non_authoritative_recommendation_hint="consider broader source class",
        )
        assert report.reason == "exhausted"

    def test_forbidden_token_in_rewrite_rationale_caught_by_gate(self):
        rewrite = QueryRewritePlan(
            rewrite_plan_id="rp-1",
            original_query_terms=("a",),
            rationale="DENY this evidence and use cached version",
            bounded_by_original_intent=True,
        )
        diagnosis = diagnose_from_contract(_make_contract(), diagnosis_id="d-1")
        results = run_gates(_make_input(), diagnosis, rewrite=rewrite)
        gate = next(
            r for r in results if r.gate is C06Gate.NO_RUNTIME_DISPOSITION
        )
        assert not gate.passed


# ---------------------------------------------------------------------------
# Bonus: ledger hash + sealing.
# ---------------------------------------------------------------------------
class TestLedgerHashing:
    def _make_ledger(self, **overrides) -> RefinementAttemptLedger:
        kwargs: dict = {
            "refinement_attempt_id": "att-1",
            "request_id": "req-1",
            "run_id": "run-1",
            "trace_id": "trace-1",
            "route_id": "R3_GROUNDED",
            "prior_contract_hash": "prior-1",
            "diagnosis_ref": "d-1",
            "selected_strategy": RefinementStrategy.QUERY_REWRITE,
            "attempt_number": 1,
            "max_refine_attempts": 2,
            "attempt_status": AttemptStatus.EXECUTED,
            "budget_before": 1000.0,
            "budget_after_reserved": 900.0,
        }
        kwargs.update(overrides)
        return RefinementAttemptLedger(**kwargs)

    def test_seal_stamps_hash(self):
        ledger = self._make_ledger()
        sealed = seal_ledger(ledger)
        assert sealed.ledger_hash
        assert len(sealed.ledger_hash) == 32

    def test_seal_idempotent(self):
        ledger = self._make_ledger()
        sealed_once = seal_ledger(ledger)
        sealed_twice = seal_ledger(sealed_once)
        assert sealed_once.ledger_hash == sealed_twice.ledger_hash

    def test_hash_changes_with_strategy(self):
        l1 = self._make_ledger(selected_strategy=RefinementStrategy.QUERY_REWRITE)
        l2 = self._make_ledger(
            selected_strategy=RefinementStrategy.BROADEN_WITHIN_SCOPE
        )
        assert compute_ledger_hash(l1) != compute_ledger_hash(l2)

    def test_budget_after_cannot_exceed_before(self):
        with pytest.raises(ValueError, match="budget_after_reserved cannot exceed"):
            self._make_ledger(budget_before=100.0, budget_after_reserved=200.0)

    def test_attempt_number_at_max_requires_terminal_status(self):
        with pytest.raises(ValueError, match="EXHAUSTED or BLOCKED"):
            self._make_ledger(
                attempt_number=2,
                max_refine_attempts=2,
                attempt_status=AttemptStatus.EXECUTED,
            )

    def test_attempt_number_at_max_with_exhausted_ok(self):
        ledger = self._make_ledger(
            attempt_number=2,
            max_refine_attempts=2,
            attempt_status=AttemptStatus.EXHAUSTED,
        )
        assert ledger.attempt_status is AttemptStatus.EXHAUSTED


# ---------------------------------------------------------------------------
# Bonus: OTEL attributes, diagnosis bridging, ScopeBroadenPlan validation.
# ---------------------------------------------------------------------------
class TestOTELAttributes:
    def test_required_attributes_present(self):
        inp = _make_input()
        diagnosis = diagnose_from_contract(
            inp.final_evidence_contract, diagnosis_id="d-1"
        )
        attrs = build_otel_attributes(
            inp,
            diagnosis,
            selected_strategy=RefinementStrategy.QUERY_REWRITE,
            attempt_number=1,
            budget_before=1000.0,
            budget_after_reserved=900.0,
            reentry_target=ReentryTarget.C0_1,
            reentry_input_hash="abc123",
            ledger_hash="def456",
        )
        # Spec OTEL/REPLAY required attributes.
        for key in (
            "c0.stage",
            "prior_contract_hash",
            "evidence_status",
            "primary_gap_type",
            "selected_strategy",
            "attempt_number",
            "max_refine_attempts",
            "budget_before",
            "budget_after_reserved",
            "reentry_target",
            "reentry_input_hash",
            "ledger_hash",
        ):
            assert key in attrs, f"missing attr {key!r}"
        assert attrs["c0.stage"] == "C0.6"


class TestBridgeTacticToStrategy:
    def test_rewrite_tactic_maps_to_query_rewrite(self):
        assert (
            bridge_tactic_to_strategy(RefineTactic.REWRITE)
            is RefinementStrategy.QUERY_REWRITE
        )

    def test_decompose_tactic_maps_to_decompose(self):
        assert (
            bridge_tactic_to_strategy(RefineTactic.DECOMPOSE)
            is RefinementStrategy.DECOMPOSE_EVIDENCE_NEED
        )

    def test_abstain_tactic_maps_to_stop(self):
        assert (
            bridge_tactic_to_strategy(RefineTactic.ABSTAIN)
            is RefinementStrategy.STOP_WITH_GAP_REPORT
        )


class TestScopeBroadenPlanValidation:
    def test_missing_bound_source_rejected(self):
        with pytest.raises(ValueError, match="bound_source required"):
            ScopeBroadenPlan(
                broaden_plan_id="bp-1",
                broaden_dimension=BroadenDimension.TOP_K,
                old_value="5",
                new_value="10",
                bound_source="",
            )


class TestDiagnosisHeuristics:
    def test_acl_block_marked_non_recoverable(self):
        contract = _make_contract(
            status=SupportStatus.WEAK_WITH_CAVEATS,
            gaps=(
                UnresolvedGapOut(
                    gap_type=GapType.MISSING_TENANT_PROOF,
                    severity="high",
                    impact_on_answer="cannot serve",
                ),
            ),
        )
        diag = diagnose_from_contract(contract, diagnosis_id="d-1")
        assert diag.primary_gap_type is PrimaryGapType.ACL_BLOCKED
        assert not diag.likely_recoverable
        assert diag.non_recoverable_reason
        assert diag.recovery_strategy is RefinementStrategy.STOP_WITH_GAP_REPORT

    def test_missing_quote_marks_citation_anchor_missing(self):
        contract = _make_contract(
            status=SupportStatus.WEAK_WITH_CAVEATS,
            gaps=(
                UnresolvedGapOut(
                    gap_type=GapType.MISSING_EXACT_QUOTE,
                    severity="medium",
                ),
            ),
        )
        diag = diagnose_from_contract(contract, diagnosis_id="d-1")
        assert diag.primary_gap_type is PrimaryGapType.CITATION_ANCHOR_MISSING
        assert diag.likely_recoverable
        assert diag.recovery_strategy is RefinementStrategy.QUERY_REWRITE


class TestForbiddenVocabulary:
    def test_token_set_contains_runtime_dispositions(self):
        # Sanity check: the constitutional set covers the spec's list.
        for token in ("DENY", "REROUTE", "ESCALATE_HITL", "COMMIT_REQUEST"):
            assert token in FORBIDDEN_OUTPUT_TOKENS


class TestInputValidation:
    def test_missing_route_id_rejected(self):
        with pytest.raises(ValueError, match="route_id required"):
            WeakSupportRefinementInput(
                final_evidence_contract=_make_contract(),
                retrieval_plan=_make_plan(),
                original_query_spec="q",
                route_id="",
                route_replay_key="rk-1",
                policy_hash="ph-1",
                blueprint_hash="bh-1",
                max_refine_attempts=1,
                refine_attempts_used=0,
                budget_remaining=100.0,
            )

    def test_negative_max_attempts_rejected(self):
        with pytest.raises(ValueError, match="max_refine_attempts must be >= 0"):
            _make_input(max_refine_attempts=-1)


class TestNoMoreRefinementReportValidation:
    def test_negative_budget_rejected(self):
        with pytest.raises(ValueError, match="budget_remaining must be >= 0"):
            NoMoreRefinementReport(
                reason="x", attempts_used=0, max_refine_attempts=1, budget_remaining=-1
            )

    def test_empty_reason_rejected(self):
        with pytest.raises(ValueError, match="reason required"):
            NoMoreRefinementReport(
                reason="", attempts_used=0, max_refine_attempts=1, budget_remaining=0
            )
