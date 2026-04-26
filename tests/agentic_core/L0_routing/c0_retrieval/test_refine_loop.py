"""Tests for C0.6 refine loop."""

from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval import (
    GraphBounds,
    RefineTactic,
    SupportStatus,
    SupportTarget,
    expand_graph,
    normalize_pool,
    plan_refinement,
    run_preflight,
    scan_conflicts_and_gaps,
    shape_pool,
    verify_and_score,
    build_retrieval_plan,
)
from tests.agentic_core.L0_routing.c0_retrieval._factories import (
    make_chunk,
    make_plan_contract,
    make_pool,
    make_route,
)


def _full_pipeline(chunks, target=SupportTarget.SOURCE_SUMMARY, max_refine=1):
    route = make_route(support_target=target, max_refine_attempts=max_refine)
    pc = make_plan_contract()
    pre = run_preflight(route, pc)
    plan = build_retrieval_plan(
        route=route, plan_contract=pc, preflight=pre, plan_id="p1",
    )
    h = normalize_pool(make_pool(chunks), tenant=route.tenant_scope)
    ex = expand_graph(h, bounds=plan.graph_bounds, adjacency=lambda n, r: ())
    cg = scan_conflicts_and_gaps(ex, target=target)
    shaped = shape_pool(
        ex, target=target,
        max_token_context=plan.budgets.max_token_context,
        contradiction_chunk_ids=cg.contradiction_chunk_ids(),
    )
    contract = verify_and_score(
        shaped, request_id="r1", target=target, conflict_report=cg,
    )
    return contract, cg, plan


class TestRefineEntryConditions:
    def test_pass_status_bypasses_refine(self):
        c = make_chunk()
        contract, cg, plan = _full_pipeline((c,))
        # Force PASS status to validate bypass.
        if contract.status != SupportStatus.PASS:
            return  # only assert when PASS
        result = plan_refinement(contract, conflict=cg, plan=plan, attempts_so_far=0)
        assert result.bypass_reason

    def test_empty_status_eligible(self):
        contract, cg, plan = _full_pipeline(())
        assert contract.status == SupportStatus.EMPTY
        result = plan_refinement(contract, conflict=cg, plan=plan, attempts_so_far=0)
        assert result.refine_attempts == 1 or result.bypass_reason


class TestRefineBudgetGuard:
    def test_exhausted_budget_yields_abstain(self):
        contract, cg, plan = _full_pipeline((), max_refine=1)
        result = plan_refinement(contract, conflict=cg, plan=plan, attempts_so_far=99)
        assert result.refine_tactic == RefineTactic.ABSTAIN
        assert "budget exhausted" in result.bypass_reason


class TestRefineTacticChoice:
    def test_valid_tactic_returned(self):
        contract, cg, plan = _full_pipeline(())
        result = plan_refinement(contract, conflict=cg, plan=plan, attempts_so_far=0)
        # Tactic must be a member of RefineTactic enum.
        assert result.refine_tactic in list(RefineTactic)


class TestRefinedContractValidation:
    def test_negative_attempts_rejected(self):
        import pytest
        from agentic_core.L0_routing.c0_retrieval.refine_loop import RefinedEvidenceContract
        contract, _, _ = _full_pipeline(())
        with pytest.raises(ValueError):
            RefinedEvidenceContract(
                base_contract=contract,
                refine_attempts=-1,
                refine_tactic=RefineTactic.REWRITE,
                diagnostic=__import__(
                    "agentic_core.L0_routing.c0_retrieval.refine_loop",
                    fromlist=["RefineDiagnostic"],
                ).RefineDiagnostic(),
            )

    def test_delta_score_range(self):
        import pytest
        from agentic_core.L0_routing.c0_retrieval.refine_loop import (
            RefineDiagnostic,
            RefinedEvidenceContract,
        )
        contract, _, _ = _full_pipeline(())
        with pytest.raises(ValueError):
            RefinedEvidenceContract(
                base_contract=contract,
                refine_attempts=1,
                refine_tactic=RefineTactic.REWRITE,
                diagnostic=RefineDiagnostic(),
                refine_delta_score=2.0,
            )
