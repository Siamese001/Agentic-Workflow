"""Tests for the clarify + replan primitives (ADR-043, W3/P3.2 + P3.3).

Covers:
- plan_clarify returns clarify when ambiguity_score >= threshold
- plan_clarify returns proceed when below threshold
- Out-of-range inputs raise ValueError
- ClarifyDecision serializes to a round-trippable dict
- ReplanRequest validates required fields + non-empty strings + non-neg ints
- MAX_REPLAN_DEPTH enforced
- advance_replan_depth increments + refuses to exceed cap
- clarify_planner shim re-exports the same primitive
"""

from __future__ import annotations

import json

import pytest

from agentic_core.runtime.contracts.abstain_contract import (
    ACTION_CONTINUE,
    ACTION_REQUEST_CLARIFICATION,
    DECISION_CLARIFY,
    DECISION_PROCEED,
    DEFAULT_AMBIGUITY_THRESHOLD,
    ClarifyDecision,
    plan_clarify,
)
from agentic_core.runtime.contracts.replan_contract import (
    MAX_REPLAN_DEPTH,
    REPLAN_BRANCH_ABSTAIN,
    REPLAN_BRANCH_ACCEPT,
    REPLAN_BRANCH_BEST_EFFORT,
    REPLAN_BRANCH_RETRY,
    ReplanContractViolation,
    ReplanRequest,
    advance_replan_depth,
    validate_replan_request,
)


# ---------------------------------------------------------------------------
# plan_clarify
# ---------------------------------------------------------------------------


class TestPlanClarify:
    def test_high_ambiguity_returns_clarify(self):
        d = plan_clarify(confidence=0.8, ambiguity_score=0.75)
        assert d["decision"] == DECISION_CLARIFY
        assert d["action"] == ACTION_REQUEST_CLARIFICATION

    def test_low_ambiguity_returns_proceed(self):
        d = plan_clarify(confidence=0.9, ambiguity_score=0.1)
        assert d["decision"] == DECISION_PROCEED
        assert d["action"] == ACTION_CONTINUE

    def test_ambiguity_at_threshold_triggers_clarify(self):
        d = plan_clarify(confidence=0.9, ambiguity_score=DEFAULT_AMBIGUITY_THRESHOLD)
        assert d["decision"] == DECISION_CLARIFY

    def test_custom_threshold(self):
        d = plan_clarify(confidence=0.9, ambiguity_score=0.4, threshold=0.3)
        assert d["decision"] == DECISION_CLARIFY

    def test_reason_hint_propagates(self):
        d = plan_clarify(
            confidence=0.9,
            ambiguity_score=0.9,
            reason_hint="two valid interpretations",
        )
        assert d["reason"] == "two valid interpretations"

    def test_decision_is_json_round_trippable(self):
        d = plan_clarify(confidence=0.8, ambiguity_score=0.75)
        assert json.loads(json.dumps(d)) == d

    def test_invalid_confidence_raises(self):
        with pytest.raises(ValueError, match="confidence"):
            plan_clarify(confidence=-0.1, ambiguity_score=0.5)

    def test_invalid_ambiguity_raises(self):
        with pytest.raises(ValueError, match="ambiguity_score"):
            plan_clarify(confidence=0.5, ambiguity_score=1.1)

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError, match="threshold"):
            plan_clarify(confidence=0.5, ambiguity_score=0.5, threshold=2.0)


class TestClarifyPlannerShim:
    def test_shim_reexports_same_symbols(self):
        from agentic_core.L1_cognition.reasoning import clarify_planner as shim
        from agentic_core.runtime.contracts import abstain_contract as ssot

        assert shim.plan_clarify is ssot.plan_clarify
        assert shim.ClarifyDecision is ssot.ClarifyDecision
        assert shim.ACTION_REQUEST_CLARIFICATION == ssot.ACTION_REQUEST_CLARIFICATION
        assert shim.DECISION_CLARIFY == ssot.DECISION_CLARIFY


# ---------------------------------------------------------------------------
# ReplanRequest / validate_replan_request
# ---------------------------------------------------------------------------


def _valid_replan(**overrides) -> ReplanRequest:
    defaults: dict = dict(
        original_plan_id="plan-001",
        failed_assumption="cache is fresh",
        observed_evidence="cache was stale: ts=2026-01-01",
        residual_budget_ms=5_000,
        residual_refinements=1,
        replan_depth=0,
    )
    defaults.update(overrides)
    return ReplanRequest(**defaults)  # type: ignore[typeddict-item]


class TestReplanConstants:
    def test_max_replan_depth_is_three(self):
        assert MAX_REPLAN_DEPTH == 3

    def test_branch_constants(self):
        assert REPLAN_BRANCH_ACCEPT == "accept"
        assert REPLAN_BRANCH_RETRY == "retry"
        assert REPLAN_BRANCH_BEST_EFFORT == "best_effort"
        assert REPLAN_BRANCH_ABSTAIN == "abstain"


class TestReplanValidation:
    def test_valid_request_passes(self):
        validate_replan_request(_valid_replan())

    def test_missing_field_raises(self):
        req = _valid_replan()
        del req["observed_evidence"]  # type: ignore[misc]
        with pytest.raises(ReplanContractViolation, match="observed_evidence"):
            validate_replan_request(req)

    def test_empty_plan_id_raises(self):
        with pytest.raises(ReplanContractViolation, match="original_plan_id"):
            validate_replan_request(_valid_replan(original_plan_id=""))

    def test_whitespace_assumption_raises(self):
        with pytest.raises(ReplanContractViolation, match="failed_assumption"):
            validate_replan_request(_valid_replan(failed_assumption="   "))

    def test_negative_budget_raises(self):
        with pytest.raises(ReplanContractViolation, match="residual_budget_ms"):
            validate_replan_request(_valid_replan(residual_budget_ms=-1))

    def test_negative_refinements_raises(self):
        with pytest.raises(ReplanContractViolation, match="residual_refinements"):
            validate_replan_request(_valid_replan(residual_refinements=-1))

    def test_replan_depth_at_cap_raises(self):
        with pytest.raises(ReplanContractViolation, match="exceeds cap"):
            validate_replan_request(_valid_replan(replan_depth=MAX_REPLAN_DEPTH))

    def test_replan_depth_above_cap_raises(self):
        with pytest.raises(ReplanContractViolation, match="exceeds cap"):
            validate_replan_request(_valid_replan(replan_depth=MAX_REPLAN_DEPTH + 1))

    def test_request_is_json_round_trippable(self):
        req = _valid_replan()
        assert json.loads(json.dumps(req)) == req


class TestAdvanceReplanDepth:
    def test_advance_from_zero(self):
        req = _valid_replan(replan_depth=0)
        out = advance_replan_depth(req)
        assert out["replan_depth"] == 1
        # Original unchanged (TypedDict is a dict but we returned a new one).
        assert req["replan_depth"] == 0

    def test_advance_from_one_to_two(self):
        req = _valid_replan(replan_depth=1)
        out = advance_replan_depth(req)
        assert out["replan_depth"] == 2

    def test_advance_past_cap_raises(self):
        # From 2, advancing would reach 3 which is MAX_REPLAN_DEPTH → forbidden.
        req = _valid_replan(replan_depth=2)
        with pytest.raises(ReplanContractViolation, match="escalate"):
            advance_replan_depth(req)

    def test_advance_preserves_other_fields(self):
        req = _valid_replan(
            original_plan_id="plan-xyz",
            failed_assumption="a",
            observed_evidence="b",
            residual_budget_ms=1234,
            residual_refinements=2,
            replan_depth=0,
        )
        out = advance_replan_depth(req)
        assert out["original_plan_id"] == "plan-xyz"
        assert out["failed_assumption"] == "a"
        assert out["observed_evidence"] == "b"
        assert out["residual_budget_ms"] == 1234
        assert out["residual_refinements"] == 2
