"""Stage 02.3 — Contextual Refinement Reasoning Loop.

Doctrine: ``docs/reference/02_L1_Reasoning/02.3_Contextual_Refinement_Reasoning_Loop_detailed.md``.

This module implements a deterministic, bounded refinement loop over the
visible inputs from stages 02.1 + 02.2. It is **planning-only**:

* No retrieval adapter calls.
* No route selector calls.
* No tool / model invocation for the user task.
* No durable writes.
* No private chain-of-thought is stored — only audit-safe summaries.

The loop runs at most :attr:`PlanningReasoningInput.max_refinement_passes`
passes. Each pass focuses on a different concern:

  1. Constraints + deliverable preservation.
  2. Support / action / risk markers.
  3. Lowest-viable-agency simplification.

When a stop signal fires (clarify / abstain / policy review needed) the
loop terminates early. The stop signals are derived from the
:class:`FirstSafetyAuthorityReading` and the ambiguity register.
"""

from __future__ import annotations

from typing import Sequence

from agentic_core.L1_cognition.planning.contracts import (
    FirstSafetyAuthorityReading,
    InternalPlanState,
    L1ContractViolation,
    PassStatus,
    PlanningLoopBudgetReceipt,
    PlanningReasoningInput,
    PlanningReasoningPacket,
    PlanningReasoningTraceSummary,
    PlanningRefinementPass,
    ReasoningQualitySignals,
)
from agentic_core.L1_cognition.planning.digests import stable_digest
from agentic_core.L1_cognition.planning.otel import SpanSink, emit_stage_spans

__all__ = ["run_l1_reasoning_loop"]


# ---------------------------------------------------------------------------
# Loop helpers
# ---------------------------------------------------------------------------


def _initial_state(input_: PlanningReasoningInput) -> InternalPlanState:
    intent = input_.intent_frame
    constraints = tuple(c.get("statement", "") for c in intent.constraints)
    safety = input_.first_safety_authority_reading

    support_summary = (
        "grounding_required"
        if any(t in intent.work_class for t in ("retrieve", "explain", "compare", "factual", "summarize"))
        and not intent.action_requirement == "none"
        else "support_optional"
    )

    action_risk_summary = (
        "high_impact"
        if safety.external_side_effect_request or intent.high_risk
        else (
            "durable_write"
            if safety.durable_write_request
            else ("reversible" if safety.reversible_action_request else "read_only")
        )
    )

    artifact_summary = (
        intent.artifact_requirement
        if intent.artifact_requirement and intent.artifact_requirement != "inline"
        else "inline_answer"
    )

    # Preliminary work units — derived heuristically from work class.
    prelim_units: tuple[str, ...] = (intent.work_class,)
    if action_risk_summary in ("high_impact", "durable_write"):
        prelim_units = prelim_units + ("propose_action", "validate_output")
    elif intent.work_class in ("plan", "decide"):
        prelim_units = prelim_units + ("validate_output",)

    state = InternalPlanState(
        internal_plan_state_id=f"ips::{input_.request_id}::0",
        normalized_goal_summary=intent.normalized_goal[:240],
        deliverable_summary=intent.user_visible_deliverable,
        constraint_bindings=constraints,
        source_expectation_summary=", ".join(input_.request_detail_inventory.source_names),
        support_need_summary=support_summary,
        action_risk_summary=action_risk_summary,
        artifact_need_summary=artifact_summary,
        preliminary_work_units=prelim_units,
        dependency_candidates=tuple(),
        route_discriminator_candidates=("R3" if support_summary == "grounding_required" else "R5",),
        uncertainty_markers=tuple(input_.ambiguity_register.get("unresolved", [])),
        unsafe_or_unsupported_markers=(
            ("authority_override_attempt",) if safety.authority_override_attempt else ()
        )
        + (("prompt_injection_signal",) if safety.prompt_injection_like_text_present else ())
        + (("direct_refusal_may_be_needed",) if safety.direct_refusal_may_be_needed else ()),
        simplification_candidates=(
            ("answer_directly_possible",) if safety.safe_direct_response_possible else ()
        ),
        stop_state_candidates=(),
    )
    return _attach_state_digest(state)


def _attach_state_digest(state: InternalPlanState) -> InternalPlanState:
    """Compute and attach the deterministic state_digest."""
    payload = state.to_dict()
    payload["state_digest"] = ""
    digest = stable_digest(payload, prefix="l1.02.3.state")
    return InternalPlanState(
        internal_plan_state_id=state.internal_plan_state_id,
        normalized_goal_summary=state.normalized_goal_summary,
        deliverable_summary=state.deliverable_summary,
        constraint_bindings=state.constraint_bindings,
        source_expectation_summary=state.source_expectation_summary,
        support_need_summary=state.support_need_summary,
        action_risk_summary=state.action_risk_summary,
        artifact_need_summary=state.artifact_need_summary,
        preliminary_work_units=state.preliminary_work_units,
        dependency_candidates=state.dependency_candidates,
        route_discriminator_candidates=state.route_discriminator_candidates,
        uncertainty_markers=state.uncertainty_markers,
        unsafe_or_unsupported_markers=state.unsafe_or_unsupported_markers,
        simplification_candidates=state.simplification_candidates,
        stop_state_candidates=state.stop_state_candidates,
        state_digest=digest,
    )


def _refine_for_constraints(
    state: InternalPlanState, input_: PlanningReasoningInput, pass_index: int
) -> tuple[InternalPlanState, PlanningRefinementPass]:
    constraints = state.constraint_bindings
    deliverable_summary = state.deliverable_summary or "inline_answer"

    new_state = InternalPlanState(
        internal_plan_state_id=f"{state.internal_plan_state_id}::pass{pass_index}",
        normalized_goal_summary=state.normalized_goal_summary,
        deliverable_summary=deliverable_summary,
        constraint_bindings=constraints,
        source_expectation_summary=state.source_expectation_summary,
        support_need_summary=state.support_need_summary,
        action_risk_summary=state.action_risk_summary,
        artifact_need_summary=state.artifact_need_summary,
        preliminary_work_units=state.preliminary_work_units,
        dependency_candidates=state.dependency_candidates,
        route_discriminator_candidates=state.route_discriminator_candidates,
        uncertainty_markers=state.uncertainty_markers,
        unsafe_or_unsupported_markers=state.unsafe_or_unsupported_markers,
        simplification_candidates=state.simplification_candidates,
        stop_state_candidates=state.stop_state_candidates,
    )
    new_state = _attach_state_digest(new_state)
    pass_record = PlanningRefinementPass(
        pass_id=f"pass::{pass_index}::constraints",
        pass_index=pass_index,
        input_state_digest=state.state_digest,
        refinement_focus="constraints_and_deliverable",
        constraints_preserved=constraints,
        ambiguities_resolved_by_assumption=(),
        ambiguities_left_open=tuple(input_.ambiguity_register.get("unresolved", [])),
        risks_promoted_to_marker=(),
        support_needs_promoted=(),
        action_needs_promoted=(),
        simplifications_applied=(),
        overreach_removed=(),
        output_state_digest=new_state.state_digest,
        pass_status=PassStatus.PASS_IMPROVED if constraints else PassStatus.PASS_NO_CHANGE,
    )
    return new_state, pass_record


def _refine_for_safety(
    state: InternalPlanState,
    input_: PlanningReasoningInput,
    pass_index: int,
    safety: FirstSafetyAuthorityReading,
) -> tuple[InternalPlanState, PlanningRefinementPass]:
    risks_promoted: list[str] = []
    if safety.authority_override_attempt:
        risks_promoted.append("authority_override_attempt")
    if safety.prompt_injection_like_text_present:
        risks_promoted.append("prompt_injection")
    if safety.direct_refusal_may_be_needed:
        risks_promoted.append("direct_refusal_may_be_needed")
    if safety.external_side_effect_request:
        risks_promoted.append("external_side_effect")

    support_needs: list[str] = []
    if state.support_need_summary == "grounding_required":
        support_needs.append("grounding_required")

    action_needs: list[str] = []
    if state.action_risk_summary in ("high_impact", "durable_write", "reversible"):
        action_needs.append(state.action_risk_summary)

    new_state = InternalPlanState(
        internal_plan_state_id=f"{state.internal_plan_state_id}::pass{pass_index}",
        normalized_goal_summary=state.normalized_goal_summary,
        deliverable_summary=state.deliverable_summary,
        constraint_bindings=state.constraint_bindings,
        source_expectation_summary=state.source_expectation_summary,
        support_need_summary=state.support_need_summary,
        action_risk_summary=state.action_risk_summary,
        artifact_need_summary=state.artifact_need_summary,
        preliminary_work_units=state.preliminary_work_units,
        dependency_candidates=state.dependency_candidates,
        route_discriminator_candidates=state.route_discriminator_candidates,
        uncertainty_markers=state.uncertainty_markers,
        unsafe_or_unsupported_markers=state.unsafe_or_unsupported_markers
        + tuple(r for r in risks_promoted if r not in state.unsafe_or_unsupported_markers),
        simplification_candidates=state.simplification_candidates,
        stop_state_candidates=state.stop_state_candidates
        + (
            ("policy_review_needed",)
            if safety.direct_refusal_may_be_needed
            and "policy_review_needed" not in state.stop_state_candidates
            else ()
        ),
    )
    new_state = _attach_state_digest(new_state)

    status = PassStatus.PASS_IMPROVED
    if safety.direct_refusal_may_be_needed:
        status = PassStatus.PASS_STOP_POLICY_REVIEW_NEEDED
    elif input_.ambiguity_register.get("unresolved"):
        status = PassStatus.PASS_STOP_CLARIFY_RECOMMENDED if not risks_promoted else PassStatus.PASS_IMPROVED

    pass_record = PlanningRefinementPass(
        pass_id=f"pass::{pass_index}::safety",
        pass_index=pass_index,
        input_state_digest=state.state_digest,
        refinement_focus="support_action_risk_markers",
        constraints_preserved=state.constraint_bindings,
        ambiguities_resolved_by_assumption=(),
        ambiguities_left_open=tuple(input_.ambiguity_register.get("unresolved", [])),
        risks_promoted_to_marker=tuple(risks_promoted),
        support_needs_promoted=tuple(support_needs),
        action_needs_promoted=tuple(action_needs),
        simplifications_applied=(),
        overreach_removed=(),
        output_state_digest=new_state.state_digest,
        pass_status=status,
    )
    return new_state, pass_record


def _refine_for_simplification(
    state: InternalPlanState,
    input_: PlanningReasoningInput,
    pass_index: int,
) -> tuple[InternalPlanState, PlanningRefinementPass]:
    simplifications: list[str] = []
    overreach_removed: list[str] = []
    safety = input_.first_safety_authority_reading
    if safety.safe_direct_response_possible:
        simplifications.append("answer_directly_possible")
        if "validate_output" in state.preliminary_work_units:
            overreach_removed.append("validate_output")

    # Only keep validate_output for high-impact / durable-write actions.
    new_units = tuple(u for u in state.preliminary_work_units if u not in overreach_removed)

    new_state = InternalPlanState(
        internal_plan_state_id=f"{state.internal_plan_state_id}::pass{pass_index}",
        normalized_goal_summary=state.normalized_goal_summary,
        deliverable_summary=state.deliverable_summary,
        constraint_bindings=state.constraint_bindings,
        source_expectation_summary=state.source_expectation_summary,
        support_need_summary=state.support_need_summary,
        action_risk_summary=state.action_risk_summary,
        artifact_need_summary=state.artifact_need_summary,
        preliminary_work_units=new_units or state.preliminary_work_units,
        dependency_candidates=state.dependency_candidates,
        route_discriminator_candidates=state.route_discriminator_candidates,
        uncertainty_markers=state.uncertainty_markers,
        unsafe_or_unsupported_markers=state.unsafe_or_unsupported_markers,
        simplification_candidates=state.simplification_candidates
        + tuple(s for s in simplifications if s not in state.simplification_candidates),
        stop_state_candidates=state.stop_state_candidates,
    )
    new_state = _attach_state_digest(new_state)

    pass_record = PlanningRefinementPass(
        pass_id=f"pass::{pass_index}::simplification",
        pass_index=pass_index,
        input_state_digest=state.state_digest,
        refinement_focus="lowest_viable_agency",
        constraints_preserved=state.constraint_bindings,
        ambiguities_resolved_by_assumption=(),
        ambiguities_left_open=(),
        risks_promoted_to_marker=(),
        support_needs_promoted=(),
        action_needs_promoted=(),
        simplifications_applied=tuple(simplifications),
        overreach_removed=tuple(overreach_removed),
        output_state_digest=new_state.state_digest,
        pass_status=PassStatus.PASS_IMPROVED if simplifications else PassStatus.PASS_NO_CHANGE,
    )
    return new_state, pass_record


def _quality_signals(
    state: InternalPlanState, passes: Sequence[PlanningRefinementPass]
) -> ReasoningQualitySignals:
    constraints_score = 1.0 if state.constraint_bindings else 0.7
    deliverable_score = 1.0 if state.deliverable_summary else 0.5
    safety_score = 1.0 if not state.unsafe_or_unsupported_markers else 0.6
    simplification_score = 1.0 if any(p.refinement_focus == "lowest_viable_agency" for p in passes) else 0.7
    avg = (constraints_score + deliverable_score + safety_score + simplification_score) / 4.0
    band = "high" if avg >= 0.85 else ("medium" if avg >= 0.6 else "low")
    return ReasoningQualitySignals(
        constraints_preserved_score=constraints_score,
        deliverable_clarity_score=deliverable_score,
        safety_alignment_score=safety_score,
        simplification_score=simplification_score,
        overall_quality_band=band,
    )


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def run_l1_reasoning_loop(
    input_: PlanningReasoningInput,
    *,
    span_sink: SpanSink | None = None,
) -> PlanningReasoningPacket:
    """02.3 entrypoint — bounded planning-only refinement loop.

    Returns:
        :class:`PlanningReasoningPacket`.
    """
    if not isinstance(input_, PlanningReasoningInput):
        raise L1ContractViolation(f"input_ must be PlanningReasoningInput, got {type(input_)}")

    initial_state = _initial_state(input_)
    initial_digest = initial_state.state_digest
    visible_inputs_hash = stable_digest(input_.to_dict(), prefix="l1.02.3.visible")
    plan_bundle_hash = input_.plan_bundle.bundle_hash

    passes: list[PlanningRefinementPass] = []
    state = initial_state

    safety = input_.first_safety_authority_reading
    early_stop_reason = ""

    if input_.max_refinement_passes >= 1:
        state, p1 = _refine_for_constraints(state, input_, pass_index=1)
        passes.append(p1)
        if p1.pass_status in (
            PassStatus.PASS_STOP_CLARIFY_RECOMMENDED,
            PassStatus.PASS_STOP_ABSTAIN_RECOMMENDED,
            PassStatus.PASS_STOP_POLICY_REVIEW_NEEDED,
        ):
            early_stop_reason = p1.pass_status.value

    if not early_stop_reason and input_.max_refinement_passes >= 2:
        state, p2 = _refine_for_safety(state, input_, pass_index=2, safety=safety)
        passes.append(p2)
        if p2.pass_status in (
            PassStatus.PASS_STOP_CLARIFY_RECOMMENDED,
            PassStatus.PASS_STOP_ABSTAIN_RECOMMENDED,
            PassStatus.PASS_STOP_POLICY_REVIEW_NEEDED,
        ):
            early_stop_reason = p2.pass_status.value

    if not early_stop_reason and input_.max_refinement_passes >= 3:
        state, p3 = _refine_for_simplification(state, input_, pass_index=3)
        passes.append(p3)

    final_state = state
    passes_used = len(passes)
    stopped_reason = early_stop_reason or "max_passes_reached_or_stable"

    # Reasoning budget bookkeeping — strictly bounded, no real model token use.
    used_budget_per_pass = 64  # synthetic, deterministic.
    used_budget = passes_used * used_budget_per_pass
    remaining = max(input_.reasoning_budget - used_budget, 0)

    budget_receipt = PlanningLoopBudgetReceipt(
        max_refinement_passes=input_.max_refinement_passes,
        passes_used=passes_used,
        reasoning_budget_initial=input_.reasoning_budget,
        reasoning_budget_remaining=remaining,
        stopped_reason=stopped_reason,
        loop_not_spinning_assertion=True,
        no_tool_calls_assertion=True,
        no_retrieval_assertion=True,
        no_route_commit_assertion=True,
    )

    quality = _quality_signals(final_state, passes)

    summary = PlanningReasoningTraceSummary(
        summary_id=f"prts::{input_.request_id}",
        visible_inputs_hash=visible_inputs_hash,
        plan_bundle_hash=plan_bundle_hash,
        initial_state_digest=initial_digest,
        final_state_digest=final_state.state_digest,
        pass_receipts=tuple(passes),
        quality_signals=quality,
    )

    output_payload = {
        "internal_plan_state": final_state.to_dict(),
        "planning_loop_budget_receipt": budget_receipt.to_dict(),
        "planning_reasoning_trace_summary": summary.to_dict(),
    }
    output_digest = stable_digest(output_payload, prefix="l1.02.3.output")

    packet = PlanningReasoningPacket(
        internal_plan_state=final_state,
        planning_loop_budget_receipt=budget_receipt,
        planning_reasoning_trace_summary=summary,
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        output_digest=output_digest,
    )

    emit_stage_spans(
        stage="02.3",
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        policy_hash_observed=input_.policy_hash_observed,
        instruction_hash_observed=input_.instruction_hash_observed,
        input_digest=stable_digest(input_.to_dict(), prefix="l1.02.3.input"),
        output_digest=output_digest,
        span_sink=span_sink,
        extra={
            "passes_used": passes_used,
            "stopped_reason": stopped_reason,
            "quality_band": quality.overall_quality_band,
        },
    )

    return packet
