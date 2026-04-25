"""Edge cases + cross-module integration tests for the L1 v4 doctrine
implementation (IntentFrame + PlanBundle + L1PlanContractV2 v4 fields +
V1-V5 semantic validators).

Covers:
- ConstraintBinding.severity validation (closed-set enum)
- IntentFrame immutability + hash/equality semantics
- AmbiguityRegister with mixed populated/empty lists
- parse_intent edge cases (empty, unicode, very long, mixed-case)
- PlanBundle hash determinism + collision detection
- derive_rule_aware_frame with empty bundle / empty intent
- L1PlanContractV2.from_v1 with v4 fields supplied/defaulted
- V1-V5 interaction matrix (CLARIFY+marker, ABSTAIN+steps, etc.)
- End-to-end golden path: parse_intent → load_plan_bundle → contract → validate_plan_semantically
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from agentic_core.L1_cognition.enforcement.plan_semantic_validators import (
    GateOutcome,
    validate_plan_semantically,
)
from agentic_core.L1_cognition.reasoning.intent_parser import parse_intent
from agentic_core.L1_cognition.reasoning.plan_bundle_loader import (
    derive_rule_aware_frame,
    load_plan_bundle,
)
from agentic_core.L1_cognition.types.intent_frame_types import (
    AmbiguityRegister,
    AmbiguityResolutionStrategy,
    ConstraintBinding,
    ConstraintSeverity,
    IntentFrame,
    IntentFrameViolation,
    OutputTargetKind,
    WorkClass,
)
from agentic_core.L1_cognition.types.plan_bundle_types import (
    PlanBundle,
    PlanBundleViolation,
)
from agentic_core.L1_cognition.types.plan_contract_types import (
    Assumption,
    AssumptionGrade,
    ClarifyOrAbstainMarker,
    EscalationHint,
    ExpectedGroundTruth,
    L1PlanContract,
    L1PlanContractV2,
    LowestViableAgency,
    PlanContractViolation,
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


# ---------------------------------------------------------------------------
# ConstraintBinding hardening
# ---------------------------------------------------------------------------


class TestConstraintBindingHardening:
    def test_valid_severities_accepted(self):
        for sev in ("must", "should", "avoid"):
            ConstraintBinding(statement="x", severity=sev)

    def test_constraint_severity_enum_values_match(self):
        assert {s.value for s in ConstraintSeverity} == {"must", "should", "avoid"}

    def test_invalid_severity_rejected(self):
        with pytest.raises(IntentFrameViolation, match="severity"):
            ConstraintBinding(statement="x", severity="nope")

    def test_empty_severity_rejected(self):
        with pytest.raises(IntentFrameViolation, match="severity"):
            ConstraintBinding(statement="x", severity="")

    def test_uppercase_severity_rejected(self):
        # Case-sensitive — doctrine specifies lowercase tokens.
        with pytest.raises(IntentFrameViolation, match="severity"):
            ConstraintBinding(statement="x", severity="MUST")

    def test_empty_statement_rejected(self):
        with pytest.raises(IntentFrameViolation, match="statement"):
            ConstraintBinding(statement="   ", severity="must")

    def test_invalid_source_rejected(self):
        with pytest.raises(IntentFrameViolation, match="source"):
            ConstraintBinding(statement="x", severity="must", source="external")

    def test_all_valid_sources_accepted(self):
        for src in ("user", "policy", "schema", "prior"):
            ConstraintBinding(statement="x", severity="must", source=src)

    def test_constraint_binding_is_frozen(self):
        c = ConstraintBinding(statement="x", severity="must")
        with pytest.raises(FrozenInstanceError):
            c.statement = "y"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# IntentFrame immutability + equality
# ---------------------------------------------------------------------------


class TestIntentFrameImmutabilityAndEquality:
    def _frame(self, **overrides: Any) -> IntentFrame:
        defaults: dict[str, Any] = dict(
            request_id="r1",
            goal="g",
            success_condition="s",
            constraints=(),
            details=(),
            output_target_kind=OutputTargetKind.ANSWER,
            work_class=WorkClass.SUMMARIZE,
        )
        defaults.update(overrides)
        return IntentFrame(**defaults)

    def test_intent_frame_is_frozen(self):
        f = self._frame()
        with pytest.raises(FrozenInstanceError):
            f.goal = "different"  # type: ignore[misc]

    def test_two_identical_frames_compare_equal(self):
        assert self._frame() == self._frame()

    def test_different_goal_breaks_equality(self):
        assert self._frame(goal="a") != self._frame(goal="b")

    def test_constraints_field_is_tuple_after_build(self):
        f = self._frame(constraints=(ConstraintBinding(statement="x", severity="must"),))
        assert isinstance(f.constraints, tuple)


# ---------------------------------------------------------------------------
# AmbiguityRegister edge cases
# ---------------------------------------------------------------------------


class TestAmbiguityRegisterEdgeCases:
    def test_only_unresolved_set(self):
        ar = AmbiguityRegister(
            unresolved=("a",),
            resolution_strategy=AmbiguityResolutionStrategy.CLARIFY,
        )
        assert ar.has_unresolved()

    def test_all_three_lists_populated(self):
        ar = AmbiguityRegister(
            known=("k1", "k2"),
            assumed=("a1",),
            unresolved=("u1",),
            resolution_strategy=AmbiguityResolutionStrategy.GROUND,
        )
        d = ar.to_dict()
        assert d["known"] == ["k1", "k2"]
        assert d["assumed"] == ["a1"]
        assert d["unresolved"] == ["u1"]
        assert d["resolution_strategy"] == "ground"

    def test_all_resolution_strategies_accepted(self):
        for strat in AmbiguityResolutionStrategy:
            ar = AmbiguityRegister(resolution_strategy=strat)
            assert ar.resolution_strategy == strat


# ---------------------------------------------------------------------------
# parse_intent edge cases
# ---------------------------------------------------------------------------


class TestParseIntentEdgeCases:
    def test_empty_string_produces_default_goal(self):
        f = parse_intent("", request_id="r1")
        f.validate()
        # The fallback goal is non-empty — IntentFrame requires it.
        assert f.goal.strip()
        assert f.success_condition.strip()

    def test_whitespace_only_produces_default_goal(self):
        f = parse_intent("   \t\n   ", request_id="r1")
        f.validate()

    def test_unicode_request_handled(self):
        f = parse_intent("Résumé los datos del trimestre 📊", request_id="r1")
        f.validate()
        assert "Résumé" in f.goal or f.goal == "Respond to the user request"

    def test_very_long_request_handled(self):
        long = "summarize " + "data " * 1000
        f = parse_intent(long, request_id="r1")
        f.validate()
        assert len(f.goal) >= 100

    def test_must_constraint_dedup(self):
        # Same sentence with same severity should appear at most once.
        f = parse_intent(
            "The answer must cite a source. The answer must cite a source.",
            request_id="r1",
        )
        must_count = sum(1 for c in f.constraints if c.severity == "must")
        assert must_count == 1

    def test_non_str_request_text_raises(self):
        with pytest.raises(TypeError):
            parse_intent(None, request_id="r1")  # type: ignore[arg-type]

    def test_multiple_severity_keywords_classified(self):
        f = parse_intent(
            "The output must be JSON. The output should be terse. Avoid emojis.",
            request_id="r1",
        )
        severities = {c.severity for c in f.constraints}
        assert "must" in severities
        assert "should" in severities
        assert "avoid" in severities

    def test_high_risk_token_at_word_boundary(self):
        # `delete` keyword anywhere triggers high_risk inference.
        f = parse_intent("Please delete temp files", request_id="r1")
        assert f.high_risk is True

    def test_caller_high_risk_false_overrides_inference(self):
        f = parse_intent(
            "Please delete temp files",
            request_id="r1",
            high_risk=False,
        )
        assert f.high_risk is False

    def test_known_assumed_passthrough(self):
        f = parse_intent(
            "anything",
            request_id="r1",
            known=("user is logged in",),
            assumed=("default locale en-US",),
        )
        assert "user is logged in" in f.ambiguity.known
        assert "default locale en-US" in f.ambiguity.assumed


# ---------------------------------------------------------------------------
# PlanBundle hash determinism + collisions
# ---------------------------------------------------------------------------


class TestPlanBundleHashEdgeCases:
    def test_field_order_irrelevant_to_hash(self):
        # Different field assignment orders should yield identical hash.
        a = PlanBundle(schemas=("s1",), policy_bounds=("p1",))
        b = PlanBundle(policy_bounds=("p1",), schemas=("s1",))
        assert a.bundle_hash == b.bundle_hash

    def test_string_position_matters(self):
        # ("a", "b") != ("b", "a") in a tuple — order is content for hashing.
        a = PlanBundle(schemas=("a", "b"))
        b = PlanBundle(schemas=("b", "a"))
        assert a.bundle_hash != b.bundle_hash

    def test_max_steps_change_changes_hash(self):
        a = PlanBundle(max_steps=5)
        b = PlanBundle(max_steps=10)
        assert a.bundle_hash != b.bundle_hash

    def test_zero_wallclock_rejected(self):
        with pytest.raises(PlanBundleViolation, match="max_wallclock_ms"):
            PlanBundle(max_wallclock_ms=0)

    def test_negative_max_steps_rejected(self):
        with pytest.raises(PlanBundleViolation, match="max_steps"):
            PlanBundle(max_steps=-1)


class TestDeriveRuleAwareFrameEdgeCases:
    def test_empty_bundle_with_low_risk_intent_yields_empty_frame(self):
        intent = parse_intent("hello", request_id="r1")
        frame = derive_rule_aware_frame(intent, load_plan_bundle())
        assert frame.can_be_proposed == ()
        assert frame.must_be_grounded == ()
        assert frame.must_be_escalated == ()

    def test_grounding_keywords_case_insensitive(self):
        intent = parse_intent("anything", request_id="r1")
        bundle = load_plan_bundle(
            policy_bounds=("MUST GROUND ANSWERS", "must Cite"),
        )
        frame = derive_rule_aware_frame(intent, bundle)
        assert "MUST GROUND ANSWERS" in frame.must_be_grounded
        assert "must Cite" in frame.must_be_grounded

    def test_high_risk_intent_appended_after_explicit_triggers(self):
        intent = parse_intent("delete production", request_id="r1")
        bundle = load_plan_bundle(hitl_triggers=("requires uwg",))
        frame = derive_rule_aware_frame(intent, bundle)
        # both should be present; intent flag appended at end.
        assert "requires uwg" in frame.must_be_escalated
        assert any("high_risk" in p for p in frame.must_be_escalated)


# ---------------------------------------------------------------------------
# from_v1 v4-field handling
# ---------------------------------------------------------------------------


def _v1() -> L1PlanContract:
    return L1PlanContract(
        plan_id="p",
        request_id="r",
        policy_hash="h",
        reasoning_mode=ReasoningMode.DIRECT,
        grounding_required=False,
        confidence_score=0.9,
        steps=({"step": "x"},),
    )


def _eg() -> ExpectedGroundTruth:
    return ExpectedGroundTruth(signal_kind="x", shape_hint="y", success_predicate="ok")


def _step() -> PlanTaskStep:
    return PlanTaskStep(step_id="s1", description="d", expected_ground_truth=_eg())


def _risk() -> RouteRisk:
    return RouteRisk(
        cost_band=RiskBand.LOW,
        latency_band=RiskBand.LOW,
        safety_band=RiskBand.LOW,
        reversibility=Reversibility.READ,
    )


class TestFromV1WithV4Fields:
    def test_default_v4_fields_when_not_supplied(self):
        v2 = L1PlanContractV2.from_v1(
            _v1(),
            proposed_route=ProposedRoute.R1A,
            route_risk=_risk(),
            task_spec=(_step(),),
        )
        v2.validate()
        assert v2.support_target == SupportTarget.NONE
        assert v2.lowest_viable_agency == LowestViableAgency.ANSWER_DIRECTLY
        assert v2.escalation_hint == EscalationHint.NONE
        assert v2.clarify_or_abstain_marker == ClarifyOrAbstainMarker.NONE

    def test_explicit_v4_fields_propagate(self):
        v2 = L1PlanContractV2.from_v1(
            _v1(),
            proposed_route=ProposedRoute.R1A,
            route_risk=_risk(),
            task_spec=(_step(),),
            lowest_viable_agency=LowestViableAgency.GROUNDED_READ,
            escalation_hint=EscalationHint.HIGH_IMPACT,
        )
        v2.validate()
        assert v2.lowest_viable_agency == LowestViableAgency.GROUNDED_READ
        assert v2.escalation_hint == EscalationHint.HIGH_IMPACT

    def test_clarify_route_auto_sets_marker_when_missing(self):
        # Caller upgrades v1 → v2 with CLARIFY route but does not pass marker.
        v2 = L1PlanContractV2.from_v1(
            _v1(),
            proposed_route=ProposedRoute.CLARIFY,
            route_risk=_risk(),
            task_spec=(_step(),),
        )
        v2.validate()
        assert v2.clarify_or_abstain_marker == ClarifyOrAbstainMarker.CLARIFY

    def test_clarify_route_respects_explicit_marker(self):
        # If caller explicitly passes ABSTAIN with CLARIFY, the explicit
        # value wins (the auto-fix only triggers on NONE).
        v2 = L1PlanContractV2.from_v1(
            _v1(),
            proposed_route=ProposedRoute.CLARIFY,
            route_risk=_risk(),
            task_spec=(_step(),),
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.FALLBACK,
        )
        v2.validate()
        assert v2.clarify_or_abstain_marker == ClarifyOrAbstainMarker.FALLBACK


# ---------------------------------------------------------------------------
# V1-V5 interaction matrix
# ---------------------------------------------------------------------------


def _telemetry() -> PlannerTelemetry:
    return PlannerTelemetry(refinements_used=0, wall_clock_ms=1, token_usage=1, critic_iterations=0)


def _plan(**overrides: Any) -> L1PlanContractV2:
    defaults: dict[str, Any] = dict(
        plan_id="p",
        request_id="req-1",
        policy_hash="h",
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


class TestSemanticGateInteractions:
    def test_clarify_plan_with_clarify_marker_fully_validates(self):
        plan = _plan(
            proposed_route=ProposedRoute.CLARIFY,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.CLARIFY,
        )
        intent = _intent(
            output_target_kind=OutputTargetKind.CLARIFICATION,
            ambiguity=AmbiguityRegister(
                unresolved=("which X?",),
                resolution_strategy=AmbiguityResolutionStrategy.CLARIFY,
            ),
        )
        out = validate_plan_semantically(plan, intent, load_plan_bundle())
        # V4 may WARN (CLARIFICATION → FALLBACK is the only allowed agency)
        # because plan declares ANSWER_DIRECTLY; that's the expected hint.
        assert out.overall in (GateOutcome.PASS, GateOutcome.WARN)
        assert not out.has_failures()

    def test_abstain_plan_one_step_validates(self):
        plan = _plan(
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.ABSTAIN,
            lowest_viable_agency=LowestViableAgency.FALLBACK,
        )
        # Override V4 expected-set: FALLBACK is allowed only for CLARIFICATION
        # output target — for ANSWER it WARNs but doesn't FAIL.
        intent = _intent()
        out = validate_plan_semantically(plan, intent, load_plan_bundle())
        assert not out.has_failures()

    def test_insufficient_support_with_marker_passes_v5(self):
        plan = _plan(
            escalation_hint=EscalationHint.INSUFFICIENT_SUPPORT,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.FALLBACK,
        )
        out = validate_plan_semantically(plan, _intent(), load_plan_bundle())
        # V2 will WARN due to escalation_hint, but no FAIL.
        assert not out.has_failures()
        assert out.has_warnings()

    def test_write_with_escalation_passes(self):
        plan = _plan(
            route_risk=RouteRisk(
                cost_band=RiskBand.MED,
                latency_band=RiskBand.MED,
                safety_band=RiskBand.HIGH,
                reversibility=Reversibility.WRITE,
            ),
            escalation_hint=EscalationHint.IRREVERSIBLE,
        )
        out = validate_plan_semantically(plan, _intent(), load_plan_bundle())
        # V2 WARN from escalation, but not FAIL — write+escalation_hint OK.
        assert not out.has_failures()

    def test_write_without_escalation_or_hitl_fails_v2(self):
        plan = _plan(
            route_risk=RouteRisk(
                cost_band=RiskBand.MED,
                latency_band=RiskBand.MED,
                safety_band=RiskBand.HIGH,
                reversibility=Reversibility.WRITE,
            ),
        )
        out = validate_plan_semantically(plan, _intent(), load_plan_bundle())
        assert out.overall == GateOutcome.FAIL

    def test_aggregator_gate_count_is_five(self):
        out = validate_plan_semantically(_plan(), _intent(), load_plan_bundle())
        assert len(out.gates) == 5
        assert {g.gate_id for g in out.gates} == {"V1", "V2", "V3", "V4", "V5"}


# ---------------------------------------------------------------------------
# End-to-end golden integration
# ---------------------------------------------------------------------------


class TestEndToEndGolden:
    def test_full_pipeline_simple_summarize(self):
        # Stage 1: PARSE INTENT
        intent = parse_intent(
            "Summarize the Q2 financial results",
            request_id="e2e-1",
            success_condition="user receives 1-page summary",
        )
        intent.validate()
        assert intent.work_class in (WorkClass.SUMMARIZE, WorkClass.FACTUAL)

        # Stage 2: LOAD PLAN BUNDLE
        bundle = load_plan_bundle(
            schemas=("answer.v1",),
            route_heuristics=("R1A: cached", "R3: grounded"),
            output_contracts=("max 1 page",),
            validation_rubric=("must be factually grounded",),
            approved_templates=("simple-summary",),
            hitl_triggers=("requires uwg",),
        )
        rule_frame = derive_rule_aware_frame(intent, bundle)
        assert rule_frame.can_be_proposed  # at least one heuristic propagated
        assert rule_frame.must_be_grounded  # rubric was grounding-keyworded

        # Stage 3: BUILD PLAN
        plan = L1PlanContractV2(
            plan_id="e2e-plan-1",
            request_id="e2e-1",
            policy_hash="sha256:p",
            proposed_route=ProposedRoute.R3,
            reasoning_mode=ReasoningMode.DECOMPOSED,
            query_spec=QuerySpec(query_text="Q2 financials", freshness_window_s=86400, max_results=5),
            task_spec=(
                PlanTaskStep(
                    step_id="retrieve",
                    description="grounded retrieve of Q2 data",
                    expected_ground_truth=ExpectedGroundTruth(
                        signal_kind="document_set",
                        shape_hint="list[dict]",
                        success_predicate="non-empty result",
                    ),
                ),
            ),
            route_risk=RouteRisk(
                cost_band=RiskBand.LOW,
                latency_band=RiskBand.LOW,
                safety_band=RiskBand.LOW,
                reversibility=Reversibility.READ,
            ),
            confidence_score=0.92,
            grounding_required=True,
            declared_assumptions=(
                Assumption(statement="Q2 data is up-to-date", grade=AssumptionGrade.DERIVED),
            ),
            unresolved_gaps=(),
            published_rationale=("planner selected R3 to satisfy: summarize the q2 financial results"),
            planner_telemetry=_telemetry(),
            support_target=SupportTarget.CITATION,
            lowest_viable_agency=LowestViableAgency.GROUNDED_READ,
            escalation_hint=EscalationHint.NONE,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.NONE,
        )
        # Structural validation
        plan.validate()

        # Stage 4: SEMANTIC VALIDATION (V1-V5)
        out = validate_plan_semantically(plan, intent, bundle)
        assert out.overall == GateOutcome.PASS, out.to_dict()
        assert not out.has_failures()
        assert not out.has_warnings()

    def test_full_pipeline_clarify_path(self):
        intent = parse_intent(
            "Do the thing",
            request_id="e2e-2",
            unresolved=("which thing? deploy or test?",),
        )
        intent.validate()
        assert intent.ambiguity.has_unresolved()

        bundle = load_plan_bundle()
        plan = L1PlanContractV2(
            plan_id="e2e-plan-2",
            request_id="e2e-2",
            policy_hash="sha256:p",
            proposed_route=ProposedRoute.CLARIFY,
            reasoning_mode=ReasoningMode.DIRECT,
            query_spec=None,
            task_spec=(
                PlanTaskStep(
                    step_id="ask",
                    description="ask user to disambiguate 'do the thing'",
                    expected_ground_truth=ExpectedGroundTruth(
                        signal_kind="user_response",
                        shape_hint="str",
                        success_predicate="user picks a concrete action",
                    ),
                ),
            ),
            route_risk=_risk(),
            confidence_score=0.5,
            grounding_required=False,
            declared_assumptions=(),
            unresolved_gaps=("which thing?",),
            published_rationale=("ambiguity: do the thing — clarification needed before route"),
            planner_telemetry=_telemetry(),
            support_target=SupportTarget.NONE,
            lowest_viable_agency=LowestViableAgency.FALLBACK,
            escalation_hint=EscalationHint.NONE,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.CLARIFY,
        )
        plan.validate()

        out = validate_plan_semantically(plan, intent, bundle)
        # V1 PASSES: planner is allowed to escalate to CLARIFY even when the
        # parser did not classify the request as CLARIFICATION (only the
        # converse — intent CLARIFICATION + plan non-CLARIFY — is a V1 fail).
        v1_result = next(g for g in out.gates if g.gate_id == "V1")
        assert v1_result.outcome == GateOutcome.PASS
        # V5 PASSES — marker correctly set, route aligned.
        v5_result = next(g for g in out.gates if g.gate_id == "V5")
        assert v5_result.outcome == GateOutcome.PASS
        # V4 WARNS — output_target_kind=ANSWER allows only
        # {ANSWER_DIRECTLY, GROUNDED_READ}; FALLBACK is outside that set.
        v4_result = next(g for g in out.gates if g.gate_id == "V4")
        assert v4_result.outcome == GateOutcome.WARN
        # Overall WARN (not FAIL) — the plan is safe but suboptimal.
        assert out.overall == GateOutcome.WARN
        assert not out.has_failures()

    def test_full_pipeline_action_path(self):
        intent = parse_intent(
            "Execute the migration script for production",
            request_id="e2e-3",
        )
        # Parser should infer ACTION + high_risk.
        assert intent.output_target_kind == OutputTargetKind.ACTION
        assert intent.high_risk is True

        bundle = load_plan_bundle(
            hitl_triggers=("write requires uwg",),
            disallowed_actions=("DROP DATABASE",),
        )
        plan = L1PlanContractV2(
            plan_id="e2e-plan-3",
            request_id="e2e-3",
            policy_hash="sha256:p",
            proposed_route=ProposedRoute.R4,
            reasoning_mode=ReasoningMode.DIRECT,
            query_spec=None,
            task_spec=(
                PlanTaskStep(
                    step_id="run",
                    description="execute the migration script for production",
                    expected_ground_truth=ExpectedGroundTruth(
                        signal_kind="exit_code",
                        shape_hint="int",
                        success_predicate="exit_code == 0",
                    ),
                ),
            ),
            route_risk=RouteRisk(
                cost_band=RiskBand.MED,
                latency_band=RiskBand.MED,
                safety_band=RiskBand.HIGH,
                reversibility=Reversibility.WRITE,
            ),
            confidence_score=0.85,
            grounding_required=False,
            declared_assumptions=(),
            unresolved_gaps=(),
            published_rationale=("planner selected R4 to: execute the migration script for production"),
            planner_telemetry=_telemetry(),
            support_target=SupportTarget.NONE,
            lowest_viable_agency=LowestViableAgency.SINGLE_ACTION,
            escalation_hint=EscalationHint.IRREVERSIBLE,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.NONE,
        )
        plan.validate()

        out = validate_plan_semantically(plan, intent, bundle)
        # V2 should WARN (escalation_hint set), V1 PASS (action↔WRITE),
        # V4 PASS (action allows SINGLE_ACTION). Overall should not FAIL.
        assert not out.has_failures()
        assert out.has_warnings()
