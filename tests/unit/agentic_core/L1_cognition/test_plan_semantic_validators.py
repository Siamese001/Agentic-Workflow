"""Tests for V1-V5 semantic validators (doc § THE THINKING DESK)."""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L1_cognition.enforcement.plan_semantic_validators import (
    GateOutcome,
    can_it_be_simpler,
    did_we_listen,
    does_it_make_sense,
    is_it_safe,
    should_we_abstain_or_clarify,
    validate_plan_semantically,
)
from agentic_core.L1_cognition.reasoning.intent_parser import parse_intent
from agentic_core.L1_cognition.reasoning.plan_bundle_loader import load_plan_bundle
from agentic_core.L1_cognition.types.intent_frame_types import (
    AmbiguityRegister,
    AmbiguityResolutionStrategy,
    IntentFrame,
    OutputTargetKind,
    WorkClass,
)
from agentic_core.L1_cognition.types.plan_contract_types import (
    Assumption,
    AssumptionGrade,
    ClarifyOrAbstainMarker,
    EscalationHint,
    ExpectedGroundTruth,
    L1PlanContractV2,
    LowestViableAgency,
    PlanTaskStep,
    PlannerTelemetry,
    ProposedRoute,
    QuerySpec,
    ReasoningMode,
    Reversibility,
    RiskBand,
    RouteRisk,
    SupportTarget,
)


def _eg(predicate: str = "rows > 0") -> ExpectedGroundTruth:
    return ExpectedGroundTruth(
        signal_kind="tool_result",
        shape_hint="dict",
        success_predicate=predicate,
    )


def _step(sid: str = "s1") -> PlanTaskStep:
    return PlanTaskStep(step_id=sid, description="do thing", expected_ground_truth=_eg())


def _risk(rev: Reversibility = Reversibility.READ) -> RouteRisk:
    return RouteRisk(
        cost_band=RiskBand.LOW,
        latency_band=RiskBand.LOW,
        safety_band=RiskBand.LOW,
        reversibility=rev,
    )


def _telemetry() -> PlannerTelemetry:
    return PlannerTelemetry(
        refinements_used=0,
        wall_clock_ms=10,
        token_usage=100,
        critic_iterations=0,
    )


def _plan(**overrides: Any) -> L1PlanContractV2:
    defaults: dict[str, Any] = dict(
        plan_id="p1",
        request_id="req-1",
        policy_hash="sha256:p",
        proposed_route=ProposedRoute.R1A,
        reasoning_mode=ReasoningMode.DIRECT,
        query_spec=None,
        task_spec=(_step(),),
        route_risk=_risk(),
        confidence_score=0.9,
        grounding_required=False,
        declared_assumptions=(),
        unresolved_gaps=(),
        published_rationale="planner answered: summarize the quarterly results",
        planner_telemetry=_telemetry(),
        support_target=SupportTarget.NONE,
        lowest_viable_agency=LowestViableAgency.ANSWER_DIRECTLY,
        escalation_hint=EscalationHint.NONE,
        clarify_or_abstain_marker=ClarifyOrAbstainMarker.NONE,
    )
    defaults.update(overrides)
    return L1PlanContractV2(**defaults)


def _intent(**overrides: Any) -> IntentFrame:
    defaults: dict[str, Any] = dict(
        request_id="req-1",
        goal="summarize the quarterly results",
        success_condition="user receives summary",
        constraints=(),
        details=(),
        output_target_kind=OutputTargetKind.ANSWER,
        work_class=WorkClass.SUMMARIZE,
    )
    defaults.update(overrides)
    return IntentFrame(**defaults)


# ---------------------------------------------------------------------------
# V1
# ---------------------------------------------------------------------------


class TestV1DidWeListen:
    def test_pass_basic(self):
        r = did_we_listen(_plan(), _intent())
        assert r.outcome == GateOutcome.PASS

    def test_fail_request_id_mismatch(self):
        r = did_we_listen(_plan(request_id="other"), _intent())
        assert r.outcome == GateOutcome.FAIL
        assert any("request_id" in f for f in r.findings)

    def test_fail_goal_not_in_rationale(self):
        r = did_we_listen(
            _plan(published_rationale="completely unrelated story"),
            _intent(),
        )
        assert r.outcome == GateOutcome.FAIL

    def test_fail_clarification_intent_with_non_clarify_route(self):
        r = did_we_listen(
            _plan(),
            _intent(output_target_kind=OutputTargetKind.CLARIFICATION),
        )
        assert r.outcome == GateOutcome.FAIL

    def test_fail_action_intent_with_read_reversibility(self):
        r = did_we_listen(
            _plan(),
            _intent(output_target_kind=OutputTargetKind.ACTION),
        )
        assert r.outcome == GateOutcome.FAIL


# ---------------------------------------------------------------------------
# V2
# ---------------------------------------------------------------------------


class TestV2IsItSafe:
    def test_pass_default(self):
        r = is_it_safe(_plan(), load_plan_bundle())
        assert r.outcome == GateOutcome.PASS

    def test_warn_when_escalation_hint_set(self):
        r = is_it_safe(
            _plan(escalation_hint=EscalationHint.HIGH_IMPACT),
            load_plan_bundle(),
        )
        assert r.outcome == GateOutcome.WARN

    def test_fail_disallowed_action_in_rationale(self):
        bundle = load_plan_bundle(disallowed_actions=("DROP TABLE",))
        r = is_it_safe(
            _plan(published_rationale="will DROP TABLE users for cleanup"),
            bundle,
        )
        assert r.outcome == GateOutcome.FAIL

    def test_fail_write_without_escalation_or_hitl(self):
        r = is_it_safe(
            _plan(route_risk=_risk(Reversibility.WRITE)),
            load_plan_bundle(),
        )
        assert r.outcome == GateOutcome.FAIL

    def test_pass_write_with_hitl_in_bundle(self):
        bundle = load_plan_bundle(hitl_triggers=("requires uwg",))
        r = is_it_safe(
            _plan(route_risk=_risk(Reversibility.WRITE)),
            bundle,
        )
        assert r.outcome == GateOutcome.PASS


# ---------------------------------------------------------------------------
# V3
# ---------------------------------------------------------------------------


class TestV3MakesSense:
    def test_pass_basic(self):
        r = does_it_make_sense(_plan())
        assert r.outcome == GateOutcome.PASS

    def test_fail_duplicate_step_ids(self):
        r = does_it_make_sense(_plan(task_spec=(_step("s1"), _step("s1"))))
        assert r.outcome == GateOutcome.FAIL
        assert any("duplicate" in f for f in r.findings)

    def test_fail_empty_success_predicate(self):
        bad_step = PlanTaskStep(
            step_id="s1",
            description="do",
            expected_ground_truth=ExpectedGroundTruth(
                signal_kind="x", shape_hint="y", success_predicate="   "
            ),
        )
        r = does_it_make_sense(_plan(task_spec=(bad_step,)))
        assert r.outcome == GateOutcome.FAIL


# ---------------------------------------------------------------------------
# V4
# ---------------------------------------------------------------------------


class TestV4CanItBeSimpler:
    def test_pass_for_aligned_plan(self):
        r = can_it_be_simpler(_plan(), _intent())
        assert r.outcome == GateOutcome.PASS

    def test_warn_when_workflow_for_single_step(self):
        r = can_it_be_simpler(
            _plan(lowest_viable_agency=LowestViableAgency.WORKFLOW),
            _intent(output_target_kind=OutputTargetKind.PLAN),
        )
        assert r.outcome == GateOutcome.WARN

    def test_warn_when_answer_directly_for_multi_step(self):
        r = can_it_be_simpler(
            _plan(task_spec=(_step("s1"), _step("s2"))),
            _intent(),
        )
        assert r.outcome == GateOutcome.WARN

    def test_warn_for_action_intent_with_answer_directly(self):
        r = can_it_be_simpler(
            _plan(),
            _intent(output_target_kind=OutputTargetKind.ACTION),
        )
        assert r.outcome == GateOutcome.WARN


# ---------------------------------------------------------------------------
# V5
# ---------------------------------------------------------------------------


class TestV5AbstainOrClarify:
    def test_pass_default(self):
        r = should_we_abstain_or_clarify(_plan(), _intent())
        assert r.outcome == GateOutcome.PASS

    def test_fail_unresolved_without_marker(self):
        intent = _intent(
            ambiguity=AmbiguityRegister(
                unresolved=("which X?",),
                resolution_strategy=AmbiguityResolutionStrategy.CLARIFY,
            )
        )
        r = should_we_abstain_or_clarify(_plan(), intent)
        assert r.outcome == GateOutcome.FAIL

    def test_fail_clarify_marker_with_non_clarify_route(self):
        r = should_we_abstain_or_clarify(
            _plan(clarify_or_abstain_marker=ClarifyOrAbstainMarker.CLARIFY),
            _intent(),
        )
        assert r.outcome == GateOutcome.FAIL

    def test_fail_abstain_marker_with_multi_step(self):
        r = should_we_abstain_or_clarify(
            _plan(
                task_spec=(_step("s1"), _step("s2")),
                clarify_or_abstain_marker=ClarifyOrAbstainMarker.ABSTAIN,
            ),
            _intent(),
        )
        assert r.outcome == GateOutcome.FAIL

    def test_fail_insufficient_support_without_marker(self):
        r = should_we_abstain_or_clarify(
            _plan(escalation_hint=EscalationHint.INSUFFICIENT_SUPPORT),
            _intent(),
        )
        assert r.outcome == GateOutcome.FAIL


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------


class TestAggregator:
    def test_overall_pass(self):
        out = validate_plan_semantically(_plan(), _intent(), load_plan_bundle())
        assert out.overall == GateOutcome.PASS
        assert len(out.gates) == 5

    def test_overall_fail_when_any_gate_fails(self):
        out = validate_plan_semantically(
            _plan(request_id="other"),
            _intent(),
            load_plan_bundle(),
        )
        assert out.overall == GateOutcome.FAIL
        assert out.has_failures()

    def test_overall_warn_when_only_warnings(self):
        out = validate_plan_semantically(
            _plan(escalation_hint=EscalationHint.HIGH_IMPACT),
            _intent(),
            load_plan_bundle(),
        )
        assert out.overall == GateOutcome.WARN
        assert out.has_warnings()

    def test_to_dict_shape(self):
        out = validate_plan_semantically(_plan(), _intent(), load_plan_bundle())
        d = out.to_dict()
        assert d["overall"] == "pass"
        assert len(d["gates"]) == 5
        assert {g["gate_id"] for g in d["gates"]} == {"V1", "V2", "V3", "V4", "V5"}
