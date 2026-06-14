"""Unit tests for agentic_core.L1_cognition.reasoning.plan_bundle_loader.

Wave 6.1 (P2 untested-module coverage) — pure-function aggregator. Covers
``load_plan_bundle`` (iterables → frozen PlanBundle) and
``derive_rule_aware_frame`` (IntentFrame + PlanBundle → RuleAwarePlanningFrame
projection: route/template → proposable, ground/evidence/cite → grounded,
hitl/escalation/high_risk → escalated).
"""

from __future__ import annotations

from agentic_core.L1_cognition.reasoning.plan_bundle_loader import (
    derive_rule_aware_frame,
    load_plan_bundle,
)
from agentic_core.L1_cognition.types.intent_frame_types import IntentFrame, OutputTargetKind
from agentic_core.L1_cognition.types.plan_bundle_types import PlanBundle, RuleAwarePlanningFrame
from agentic_core.runtime.contracts.routing_features import WorkClass


def _intent(high_risk: bool = False) -> IntentFrame:
    return IntentFrame(
        request_id="req-1",
        goal="g",
        success_condition="s",
        constraints=(),
        details=(),
        output_target_kind=OutputTargetKind.ANSWER,
        work_class=list(WorkClass)[0],
        high_risk=high_risk,
    )


class TestLoadPlanBundle:
    def test_defaults_produce_empty_bundle(self) -> None:
        b = load_plan_bundle()
        assert isinstance(b, PlanBundle)
        assert b.schemas == ()
        assert b.max_steps == 10
        assert b.max_wallclock_ms == 60_000

    def test_iterables_coerced_to_tuples(self) -> None:
        b = load_plan_bundle(schemas=["a", "b"], policy_bounds=("p",))
        assert b.schemas == ("a", "b")
        assert b.policy_bounds == ("p",)

    def test_generator_input_consumed(self) -> None:
        b = load_plan_bundle(exemplars=(x for x in ["e1", "e2"]))
        assert b.exemplars == ("e1", "e2")

    def test_custom_limits(self) -> None:
        b = load_plan_bundle(max_steps=3, max_wallclock_ms=500)
        assert b.max_steps == 3
        assert b.max_wallclock_ms == 500

    def test_result_is_hash_stable(self) -> None:
        assert load_plan_bundle(schemas=["a"]).bundle_hash == load_plan_bundle(
            schemas=["a"]
        ).bundle_hash


class TestDeriveRuleAwareFrame:
    def test_returns_frame(self) -> None:
        frame = derive_rule_aware_frame(_intent(), PlanBundle())
        assert isinstance(frame, RuleAwarePlanningFrame)

    def test_proposable_is_routes_plus_templates(self) -> None:
        b = PlanBundle(route_heuristics=("r1",), approved_templates=("t1",))
        frame = derive_rule_aware_frame(_intent(), b)
        assert frame.can_be_proposed == ("r1", "t1")

    def test_grounded_filters_on_keywords(self) -> None:
        b = PlanBundle(
            policy_bounds=("must ground claims", "unrelated bound"),
            validation_rubric=("cite the source", "evidence required", "tone check"),
        )
        frame = derive_rule_aware_frame(_intent(), b)
        assert frame.must_be_grounded == (
            "must ground claims",
            "cite the source",
            "evidence required",
        )

    def test_grounded_empty_when_no_keywords(self) -> None:
        b = PlanBundle(policy_bounds=("be polite",), validation_rubric=("check tone",))
        assert derive_rule_aware_frame(_intent(), b).must_be_grounded == ()

    def test_escalated_includes_hitl_and_thresholds(self) -> None:
        b = PlanBundle(hitl_triggers=("h1",), escalation_thresholds=("e1",))
        frame = derive_rule_aware_frame(_intent(high_risk=False), b)
        assert frame.must_be_escalated == ("h1", "e1")

    def test_high_risk_appends_escalation_marker(self) -> None:
        frame = derive_rule_aware_frame(_intent(high_risk=True), PlanBundle())
        assert frame.must_be_escalated == ("intent_frame.high_risk=True",)

    def test_low_risk_omits_marker(self) -> None:
        frame = derive_rule_aware_frame(_intent(high_risk=False), PlanBundle())
        assert "intent_frame.high_risk=True" not in frame.must_be_escalated
