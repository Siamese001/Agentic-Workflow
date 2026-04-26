"""Tests for C0.6 refinement loop with allowed/disallowed enforcement."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.c0_context.refine import (
    DisallowedRefinementError,
    RefineLoopController,
    RefinementAttempt,
    RefinementBudgetExhaustedError,
    is_refinement_allowed,
)
from agentic_core.L1_cognition.c0_context.types import (
    DISALLOWED_REFINEMENTS,
    RefineTactic,
    RetrievalPlan,
    SupportStatus,
    SupportTarget,
)


def _plan(*, max_refine: int = 1) -> RetrievalPlan:
    return RetrievalPlan(
        source_classes=frozenset({"docs"}),
        allowed_sources=frozenset({"docs"}),
        disallowed_sources=frozenset(),
        retrieval_modes=frozenset({"dense", "sparse"}),
        support_target=SupportTarget.SOURCE_SUMMARY,
        freshness_rule="current",
        evidence_standard="default",
        bounds={
            "max_k": 10, "max_parent_expansion": 2, "max_child_expansion": 2,
            "max_graph_hops": 2, "max_refine_attempts": max_refine,
            "max_token_context": 4000, "max_source_classes": 1,
            "max_latency_ms": 2000, "max_cost_tier": 1,
        },
        cache_policy="READ_THROUGH",
        weak_support_policy="caveat",
        replay_metadata={},
    )


def test_request_refinement_allowed_when_weak() -> None:
    ctrl = RefineLoopController(plan=_plan())
    # Should not raise
    ctrl.request_refinement(
        RefineTactic.REWRITE,
        rationale="rewrite query terms",
        current_status=SupportStatus.WEAK,
    )


def test_request_refinement_disallowed_when_pass() -> None:
    ctrl = RefineLoopController(plan=_plan())
    with pytest.raises(DisallowedRefinementError, match="entry conditions"):
        ctrl.request_refinement(
            RefineTactic.REWRITE,
            rationale="rewrite query terms",
            current_status=SupportStatus.PASS,
        )


def test_request_refinement_blocks_disallowed_rationale() -> None:
    ctrl = RefineLoopController(plan=_plan())
    with pytest.raises(DisallowedRefinementError, match="disallowed behavior"):
        ctrl.request_refinement(
            RefineTactic.BROADEN,
            rationale="we should change_user_task to recover",
            current_status=SupportStatus.WEAK,
        )


def test_request_refinement_blocks_acl_expansion() -> None:
    ctrl = RefineLoopController(plan=_plan())
    with pytest.raises(DisallowedRefinementError):
        ctrl.request_refinement(
            RefineTactic.BROADEN,
            rationale="expand_tenant_acl_region to capture more sources",
            current_status=SupportStatus.WEAK,
        )


def test_each_disallowed_behavior_blocked() -> None:
    """Every behavior in DISALLOWED_REFINEMENTS must be detected."""
    ctrl = RefineLoopController(plan=_plan())
    for banned in DISALLOWED_REFINEMENTS:
        with pytest.raises(DisallowedRefinementError):
            ctrl.request_refinement(
                RefineTactic.REWRITE,
                rationale=f"plan to {banned} for better results",
                current_status=SupportStatus.WEAK,
            )


def test_budget_exhausted_after_max_attempts() -> None:
    ctrl = RefineLoopController(plan=_plan(max_refine=1))
    ctrl.request_refinement(
        RefineTactic.REWRITE, rationale="rewrite query", current_status=SupportStatus.WEAK,
    )
    ctrl.record_attempt(RefinementAttempt(
        tactic=RefineTactic.REWRITE, rationale="r", succeeded=True,
        new_status=SupportStatus.PASS,
    ))
    assert ctrl.attempts_made == 1
    assert ctrl.can_refine is False
    with pytest.raises(RefinementBudgetExhaustedError):
        ctrl.request_refinement(
            RefineTactic.REWRITE, rationale="another rewrite",
            current_status=SupportStatus.WEAK,
        )


def test_zero_budget_blocks_all() -> None:
    ctrl = RefineLoopController(plan=_plan(max_refine=0))
    with pytest.raises(RefinementBudgetExhaustedError):
        ctrl.request_refinement(
            RefineTactic.REWRITE, rationale="r",
            current_status=SupportStatus.WEAK,
        )


def test_history_records_all_attempts() -> None:
    ctrl = RefineLoopController(plan=_plan(max_refine=2))
    a1 = RefinementAttempt(RefineTactic.REWRITE, "r", False, SupportStatus.WEAK)
    a2 = RefinementAttempt(RefineTactic.HYBRIDIZE, "h", True, SupportStatus.PASS)
    ctrl.record_attempt(a1)
    ctrl.record_attempt(a2)
    assert ctrl.attempts_made == 2
    assert ctrl.history == [a1, a2]


def test_is_refinement_allowed_for_every_tactic() -> None:
    for t in RefineTactic:
        assert is_refinement_allowed(t) is True


def test_refinement_allowed_for_conflicted_and_empty() -> None:
    ctrl = RefineLoopController(plan=_plan())
    ctrl.request_refinement(
        RefineTactic.HYBRIDIZE, rationale="add sparse lane", current_status=SupportStatus.CONFLICTED,
    )
    ctrl2 = RefineLoopController(plan=_plan())
    ctrl2.request_refinement(
        RefineTactic.BROADEN, rationale="broader synonyms", current_status=SupportStatus.EMPTY,
    )
