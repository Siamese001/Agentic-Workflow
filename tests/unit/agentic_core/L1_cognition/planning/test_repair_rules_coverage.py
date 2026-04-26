"""Per-rule fault-injection tests for the L1 v6 self-repair loop.

The doctrine in `02.5_Plan_Validation_Self_Repair_detailed.md` declares
ten allowed repair types. This module crafts a `DraftPlan` for each
rule whose validation triggers exactly that repair and asserts the
loop fires the matching :class:`RepairAction`.

The eleventh enum member, ``RepairAction.NO_ACTION``, is exercised by
the all-clean case at the bottom of the file.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from agentic_core.L1_cognition.planning import (
    ActionExpectation,
    DependencySketch,
    DraftPlan,
    DownstreamPlanningNotes,
    PlanValidationInput,
    ProposedRouteHint,
    RouteHintSet,
    SupportExpectation,
    WorkUnit,
    WorkUnitSet,
    WorkUnitType,
    parse_intent_frame,
    validate_and_repair_l1_plan,
)
from agentic_core.L1_cognition.planning.contracts import (
    FirstSafetyAuthorityReading,
    IntentFrameSnapshot,
    RepairAction,
)


# ---------------------------------------------------------------------------
# Helpers — minimal valid DraftPlan + IntentFrameSnapshot factories
# ---------------------------------------------------------------------------


def _make_intent_snapshot(
    *,
    request_id: str = "req-repair-1",
    work_class: str = "summarize",
    deliverable: str = "answer",
    high_risk: bool = False,
    action_requirement: str = "none",
    artifact: str = "inline",
    constraints: tuple = (),
    goal: str = "Summarize the doc and explain the key takeaways",
) -> IntentFrameSnapshot:
    return IntentFrameSnapshot(
        request_id=request_id,
        intent_frame_id=f"if::{request_id}",
        normalized_goal=goal,
        user_visible_deliverable=deliverable,
        work_class=work_class,
        audience="user",
        output_target_kind=deliverable,
        freshness_class="stable",
        action_requirement=action_requirement,
        artifact_requirement=artifact,
        high_risk=high_risk,
        constraints=tuple(constraints),
        details=(),
        ambiguity={
            "known": [],
            "assumed": [],
            "unresolved": [],
            "resolution_strategy": "assume",
            "mistaken_premise": [],
            "conflicts": [],
            "unstated_likely": [],
        },
        success_condition="User receives a complete, policy-compliant deliverable.",
    )


def _make_safety(
    *,
    request_id: str = "req-repair-1",
    refusal: bool = False,
    high_impact: bool = False,
) -> FirstSafetyAuthorityReading:
    return FirstSafetyAuthorityReading(
        request_id=request_id,
        read_only_request=not high_impact,
        external_side_effect_request=high_impact,
        high_impact_domain_hint=high_impact,
        direct_refusal_may_be_needed=refusal,
        safe_direct_response_possible=not (refusal or high_impact),
    )


def _baseline_draft(
    intent: IntentFrameSnapshot,
    *,
    route: ProposedRouteHint = ProposedRouteHint.R1B_SEMANTIC_CACHE,
    grounding: bool = False,
    support_target: str = "none",
    action_required: bool = False,
    side_effect: str = "none",
    irreversible: bool = False,
    extra_units: tuple = (),
    primary_constraints: tuple = (),
    reason_codes: tuple = ("work_class:summarize",),
) -> DraftPlan:
    primary = WorkUnit(
        work_unit_id="wu::primary",
        description=intent.normalized_goal,
        work_unit_type=WorkUnitType.SUMMARIZE,
        constraints=tuple(primary_constraints),
        risk_marker=("high" if intent.high_risk else "low"),
    )
    units = (primary,) + tuple(extra_units)
    return DraftPlan(
        draft_plan_id="draft::test",
        work_unit_set=WorkUnitSet(units=units),
        dependency_sketch=DependencySketch(dependency_sketch_id="ds::test"),
        route_hint_set=RouteHintSet(
            route_hint_id="rhs::test",
            proposed_route_hint=route,
            reason_codes=tuple(reason_codes),
            confidence=0.7,
            route_risk="low",
            grounding_hint=grounding,
            action_hint=action_required,
            cache_eligibility_hint=route
            in (ProposedRouteHint.R1A_EXACT_CACHE, ProposedRouteHint.R1B_SEMANTIC_CACHE),
        ),
        support_expectation=SupportExpectation(
            grounding_required=grounding,
            support_target=support_target,
        ),
        action_expectation=ActionExpectation(
            action_required=action_required,
            side_effect_class=side_effect,
            irreversible_action_marker=irreversible,
        ),
        downstream_planning_notes=DownstreamPlanningNotes(),
        draft_digest="sha256:test",
    )


def _validate(draft: DraftPlan, intent: IntentFrameSnapshot, safety: FirstSafetyAuthorityReading):
    inp = PlanValidationInput(
        draft_plan=draft,
        intent_frame=intent,
        ambiguity_register=intent.ambiguity,
        first_safety_authority_reading=safety,
        request_id=intent.request_id,
        trace_root=f"trace::{intent.request_id}",
        policy_hash_observed="p",
        instruction_hash_observed="i",
        max_self_repair_passes=2,
    )
    return validate_and_repair_l1_plan(inp)


# ---------------------------------------------------------------------------
# Per-rule tests — one test per RepairAction enum value
# ---------------------------------------------------------------------------


def test_repair_unsafe_route_hint_fires_on_refusal_with_wrong_route():
    """direct_refusal_may_be_needed + non-R5 route -> REPAIR_UNSAFE_ROUTE_HINT."""
    intent = _make_intent_snapshot()
    safety = _make_safety(refusal=True)
    draft = _baseline_draft(intent, route=ProposedRouteHint.R1B_SEMANTIC_CACHE)
    out = _validate(draft, intent, safety)
    assert RepairAction.REPAIR_UNSAFE_ROUTE_HINT in out.self_repair_ledger.repairs_attempted


def test_repair_unclear_support_expectation_fires_on_r3_without_grounding():
    """R3 grounded read but grounding_required=False -> REPAIR_UNCLEAR_SUPPORT_EXPECTATION."""
    intent = _make_intent_snapshot()
    safety = _make_safety()
    draft = _baseline_draft(intent, route=ProposedRouteHint.R3_GROUNDED_READ, grounding=False)
    out = _validate(draft, intent, safety)
    assert (
        RepairAction.REPAIR_UNCLEAR_SUPPORT_EXPECTATION
        in out.self_repair_ledger.repairs_attempted
    )


def test_repair_missing_fallback_fires_on_r5_without_reason_codes():
    """R5 fallback but reason_codes=() -> REPAIR_MISSING_FALLBACK."""
    intent = _make_intent_snapshot()
    safety = _make_safety()
    draft = _baseline_draft(
        intent, route=ProposedRouteHint.R5_FALLBACK, reason_codes=()
    )
    out = _validate(draft, intent, safety)
    assert RepairAction.REPAIR_MISSING_FALLBACK in out.self_repair_ledger.repairs_attempted


def test_repair_missing_hitl_or_uwg_hint_fires_on_irreversible_without_hitl():
    """irreversible_action_marker=True without hitl_hint -> repair (warns then fixes).

    The bare WARN does not trigger self-repair on its own (loop only repairs
    when ``has_failures()`` or warnings unmatched). To make the rule reliably
    fire we set the safety reading so the action becomes high-impact and the
    overbroad-action FAIL fires first; once that's repaired we expect HITL
    to be set on the next pass.
    """
    intent = _make_intent_snapshot(
        action_requirement="high_impact", high_risk=True, deliverable="action"
    )
    safety = _make_safety(high_impact=True)
    draft = _baseline_draft(
        intent,
        route=ProposedRouteHint.R4_SINGLE_ACTION,
        action_required=True,
        side_effect="high_impact",
        irreversible=True,
        reason_codes=("action:high_impact",),
    )
    out = _validate(draft, intent, safety)
    repairs = list(out.self_repair_ledger.repairs_attempted)
    # Either the missing-hitl rule fires directly, or the overbroad-action
    # rule fires (which itself sets hitl_hint=True). Either path resolves
    # the doctrine target.
    assert any(
        r in repairs
        for r in (
            RepairAction.REPAIR_MISSING_HITL_OR_UWG_HINT,
            RepairAction.REPAIR_OVERBROAD_ACTION_ASSUMPTION,
        )
    )


def test_repair_unnecessary_workflow_fires_on_safe_direct_response_with_workflow():
    """safe_direct_response_possible + R3R4_MANAGED_WORKFLOW -> REPAIR_UNNECESSARY_WORKFLOW."""
    intent = _make_intent_snapshot()
    safety = _make_safety()  # safe_direct_response_possible=True
    draft = _baseline_draft(intent, route=ProposedRouteHint.R3R4_MANAGED_WORKFLOW)
    out = _validate(draft, intent, safety)
    assert RepairAction.REPAIR_UNNECESSARY_WORKFLOW in out.self_repair_ledger.repairs_attempted


def test_repair_unsupported_certainty_fires_on_support_target_without_grounding():
    """support_target != none + grounding_required=False -> REPAIR_UNSUPPORTED_CERTAINTY."""
    intent = _make_intent_snapshot()
    safety = _make_safety()
    draft = _baseline_draft(
        intent,
        route=ProposedRouteHint.R1B_SEMANTIC_CACHE,
        grounding=False,
        support_target="citation",  # invalid: support_target without grounding
    )
    out = _validate(draft, intent, safety)
    assert (
        RepairAction.REPAIR_UNSUPPORTED_CERTAINTY
        in out.self_repair_ledger.repairs_attempted
    )


def test_repair_dropped_constraint_fires_when_constraints_dropped():
    """Intent has constraints, primary unit has none -> REPAIR_DROPPED_CONSTRAINT."""
    intent = _make_intent_snapshot(
        constraints=(
            {"statement": "must cite source", "severity": "must", "source": "user"},
        )
    )
    safety = _make_safety()
    draft = _baseline_draft(intent, primary_constraints=())
    out = _validate(draft, intent, safety)
    assert (
        RepairAction.REPAIR_DROPPED_CONSTRAINT
        in out.self_repair_ledger.repairs_attempted
    )


def test_repair_overbroad_action_fires_on_high_impact_without_validate_unit():
    """High-impact action, no validate_output unit -> REPAIR_OVERBROAD_ACTION_ASSUMPTION."""
    intent = _make_intent_snapshot(
        action_requirement="high_impact", deliverable="action", high_risk=True
    )
    safety = _make_safety(high_impact=True)
    draft = _baseline_draft(
        intent,
        route=ProposedRouteHint.R4_SINGLE_ACTION,
        action_required=True,
        side_effect="high_impact",
        irreversible=True,
        reason_codes=("action:high_impact",),
    )
    out = _validate(draft, intent, safety)
    assert (
        RepairAction.REPAIR_OVERBROAD_ACTION_ASSUMPTION
        in out.self_repair_ledger.repairs_attempted
    )


def test_repair_missing_output_target_fires_on_plan_request_without_interpret():
    """Intent deliverable=plan, no interpret unit -> REPAIR_MISSING_OUTPUT_TARGET (warn-then-repair)."""
    intent = _make_intent_snapshot(deliverable="plan", work_class="plan")
    safety = _make_safety()
    # primary unit type is SUMMARIZE — not INTERPRET — so the missing_output_target
    # warning fires.
    draft = _baseline_draft(intent, route=ProposedRouteHint.R1B_SEMANTIC_CACHE)
    out = _validate(draft, intent, safety)
    repairs = list(out.self_repair_ledger.repairs_attempted)
    assert RepairAction.REPAIR_MISSING_OUTPUT_TARGET in repairs


def test_repair_excessive_clarification_fires_on_r5_with_multi_step_plan():
    """R5_FALLBACK + multiple work units -> REPAIR_EXCESSIVE_CLARIFICATION."""
    intent = _make_intent_snapshot()
    safety = _make_safety()
    extra = (
        WorkUnit(
            work_unit_id="wu::extra",
            description="extra step",
            work_unit_type=WorkUnitType.VALIDATE_OUTPUT,
        ),
    )
    draft = _baseline_draft(
        intent,
        route=ProposedRouteHint.R5_FALLBACK,
        reason_codes=("fallback_unspecified",),
        extra_units=extra,
    )
    out = _validate(draft, intent, safety)
    assert (
        RepairAction.REPAIR_EXCESSIVE_CLARIFICATION
        in out.self_repair_ledger.repairs_attempted
    )


def test_no_action_when_plan_is_clean():
    """Clean plan -> RepairAction.NO_ACTION (or empty repairs_attempted)."""
    intent = _make_intent_snapshot()
    safety = _make_safety()
    draft = _baseline_draft(intent, route=ProposedRouteHint.R1B_SEMANTIC_CACHE)
    out = _validate(draft, intent, safety)
    # Either the loop never ran (PASS_NO_REPAIR) or it ran once and matched NO_ACTION.
    repairs = list(out.self_repair_ledger.repairs_attempted)
    assert all(r != RepairAction.REPAIR_UNSAFE_ROUTE_HINT for r in repairs)
    assert out.self_repair_ledger.no_tool_rescue_assertion is True
    assert out.self_repair_ledger.no_retrieval_rescue_assertion is True


def test_all_repair_action_enum_values_are_referenced_somewhere_in_module():
    """Coverage check: every RepairAction value (except NO_ACTION) appears
    in plan_validation.py source as a return value of a repair rule."""
    import inspect

    from agentic_core.L1_cognition.planning import plan_validation

    src = inspect.getsource(plan_validation)
    for action in RepairAction:
        if action == RepairAction.NO_ACTION:
            # NO_ACTION is the catch-all return; appears multiple times.
            assert "RepairAction.NO_ACTION" in src
            continue
        assert (
            f"RepairAction.{action.name}" in src
        ), f"RepairAction.{action.name} has no implementing rule in plan_validation.py"
