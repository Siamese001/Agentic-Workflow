"""Stage 02.4 — Draft Plan & Advisory Route Hints.

Doctrine: ``docs/reference/02_L1_Reasoning/02.4_Draft_Plan_and_Route_Hints_detailed.md``.

This module turns the :class:`InternalPlanState` from stage 02.3 into a
frozen :class:`DraftPlan`: a :class:`WorkUnitSet`, a
:class:`DependencySketch`, a :class:`RouteHintSet` (advisory only), a
:class:`SupportExpectation`, an :class:`ActionExpectation`, and a
:class:`DownstreamPlanningNotes` block.

Route hint consistency rules (PHASE 3) are enforced when assigning the
proposed route. The route hint set carries
``route_authority_assertion="advisory_only"`` — the contracts module
rejects any other value.
"""

from __future__ import annotations

from agentic_core.L1_cognition.planning.contracts import (
    ActionExpectation,
    DependencySketch,
    DownstreamPlanningNotes,
    DraftPlan,
    DraftPlanInput,
    DraftPlanPacket,
    L1ContractViolation,
    ProposedRouteHint,
    RouteHintSet,
    SupportExpectation,
    WorkUnit,
    WorkUnitSet,
    WorkUnitType,
)
from agentic_core.L1_cognition.planning.digests import stable_digest
from agentic_core.L1_cognition.planning.otel import SpanSink, emit_stage_spans

__all__ = ["write_draft_plan"]


# ---------------------------------------------------------------------------
# Heuristics
# ---------------------------------------------------------------------------


_WORK_CLASS_TO_UNIT_TYPE: dict[str, WorkUnitType] = {
    "summarize": WorkUnitType.SUMMARIZE,
    "compare": WorkUnitType.COMPARE,
    "explain": WorkUnitType.INTERPRET,
    "analyze": WorkUnitType.INTERPRET,
    "plan": WorkUnitType.INTERPRET,
    "act": WorkUnitType.PROPOSE_ACTION,
    "create": WorkUnitType.CREATE_ARTIFACT,
    "edit": WorkUnitType.EDIT_ARTIFACT,
    "retrieve": WorkUnitType.RETRIEVE_NEEDED,
    "decide": WorkUnitType.INTERPRET,
    "escalate": WorkUnitType.ESCALATE_CANDIDATE,
    "factual": WorkUnitType.INTERPRET,
    "creative": WorkUnitType.CREATE_ARTIFACT,
    "code": WorkUnitType.CREATE_ARTIFACT,
    "mathematical": WorkUnitType.INTERPRET,
    "unknown": WorkUnitType.INTERPRET,
}


def _build_work_unit_set(input_: DraftPlanInput) -> WorkUnitSet:
    intent = input_.intent_frame
    state = input_.internal_plan_state
    safety = input_.first_safety_authority_reading

    primary_type = _WORK_CLASS_TO_UNIT_TYPE.get(
        intent.work_class, WorkUnitType.INTERPRET
    )

    primary = WorkUnit(
        work_unit_id="wu::primary",
        description=state.normalized_goal_summary or intent.normalized_goal,
        work_unit_type=primary_type,
        constraints=state.constraint_bindings,
        support_need=state.support_need_summary,
        action_need=state.action_risk_summary,
        risk_marker=("high" if intent.high_risk else "low"),
        can_be_single_step=safety.safe_direct_response_possible,
        requires_external_action_hint=safety.external_side_effect_request,
        requires_grounding_hint=state.support_need_summary == "grounding_required",
        requires_artifact_output_hint=intent.artifact_requirement != "inline",
        acceptance_criteria=(intent.success_condition,) if intent.success_condition else (),
        stop_condition=intent.success_condition,
    )

    units: list[WorkUnit] = [primary]

    if state.support_need_summary == "grounding_required":
        units.append(
            WorkUnit(
                work_unit_id="wu::grounded_read",
                description="C0 retrieval expected for support spans",
                work_unit_type=WorkUnitType.RETRIEVE_NEEDED,
                support_need="evidence_bundle",
                action_need="none",
                risk_marker="low",
                requires_grounding_hint=True,
                dependency_refs=("wu::primary",),
            )
        )

    if state.action_risk_summary in ("high_impact", "durable_write"):
        units.append(
            WorkUnit(
                work_unit_id="wu::propose_action",
                description="Action proposal awaiting capability and HITL approval",
                work_unit_type=WorkUnitType.PROPOSE_ACTION,
                support_need="none",
                action_need=state.action_risk_summary,
                risk_marker="high",
                requires_external_action_hint=True,
                dependency_refs=("wu::primary",),
            )
        )

    if intent.artifact_requirement == "inline":
        # No artifact step required.
        pass
    else:
        units.append(
            WorkUnit(
                work_unit_id="wu::artifact",
                description=f"Artifact rendering: {intent.artifact_requirement}",
                work_unit_type=WorkUnitType.CREATE_ARTIFACT,
                support_need="none",
                action_need="none",
                risk_marker="low",
                requires_artifact_output_hint=True,
                dependency_refs=("wu::primary",),
            )
        )

    if (
        safety.external_side_effect_request
        or intent.high_risk
        or state.action_risk_summary in ("high_impact", "durable_write")
    ):
        units.append(
            WorkUnit(
                work_unit_id="wu::validate",
                description="Final validation step before egress / commit",
                work_unit_type=WorkUnitType.VALIDATE_OUTPUT,
                support_need="none",
                action_need="none",
                risk_marker="low",
                dependency_refs=tuple(u.work_unit_id for u in units),
            )
        )

    return WorkUnitSet(units=tuple(units))


def _build_dependency_sketch(units: WorkUnitSet) -> DependencySketch:
    edges: list[tuple[str, str]] = []
    for u in units.units:
        for dep in u.dependency_refs:
            edges.append((dep, u.work_unit_id))
    parallel_safe: list[tuple[str, ...]] = []
    if len(units.units) > 1:
        roots = tuple(u.work_unit_id for u in units.units if not u.dependency_refs)
        if len(roots) > 1:
            parallel_safe.append(roots)
    return DependencySketch(
        dependency_sketch_id="ds::v6",
        sequential_edges=tuple(tuple(e) for e in edges),
        parallel_safe_groups=tuple(parallel_safe),
        join_points=(units.units[-1].work_unit_id,) if len(units.units) > 1 else (),
        prerequisite_checks=(),
        stopping_points=(units.units[-1].work_unit_id,),
        retry_or_repair_posture="advisory_only",
        l3_may_be_needed_reason=(
            "multi_step_with_join"
            if len(units.units) >= 3 and edges
            else ""
        ),
        l3_not_needed_reason=("single_step" if len(units.units) == 1 else ""),
    )


def _proposed_route(input_: DraftPlanInput) -> ProposedRouteHint:
    state = input_.internal_plan_state
    safety = input_.first_safety_authority_reading
    intent = input_.intent_frame

    if safety.direct_refusal_may_be_needed:
        return ProposedRouteHint.R5_FALLBACK
    if input_.ambiguity_register.get("unresolved"):
        # Ambiguity may still be addressable — but if no support is
        # required and the request is read-only, we can answer directly.
        if state.support_need_summary == "grounding_required":
            return ProposedRouteHint.R3_GROUNDED_READ
        return ProposedRouteHint.R5_FALLBACK
    if state.action_risk_summary in ("high_impact", "durable_write", "reversible"):
        if state.support_need_summary == "grounding_required":
            return ProposedRouteHint.R3R4_MANAGED_WORKFLOW
        return ProposedRouteHint.R4_SINGLE_ACTION
    if state.support_need_summary == "grounding_required":
        return ProposedRouteHint.R3_GROUNDED_READ
    if intent.freshness_class == "stable" and not intent.high_risk:
        return ProposedRouteHint.R1B_SEMANTIC_CACHE
    return ProposedRouteHint.R3_GROUNDED_READ


def _build_route_hint_set(
    input_: DraftPlanInput, work_unit_set: WorkUnitSet
) -> RouteHintSet:
    state = input_.internal_plan_state
    safety = input_.first_safety_authority_reading
    intent = input_.intent_frame

    proposed = _proposed_route(input_)
    confidence = 0.85 if not state.unsafe_or_unsupported_markers else 0.55
    risk = "high" if intent.high_risk else ("medium" if state.unsafe_or_unsupported_markers else "low")

    fallback_chain: dict[ProposedRouteHint, tuple[str, ...]] = {
        ProposedRouteHint.R1A_EXACT_CACHE: ("R1B_SEMANTIC_CACHE", "R3_GROUNDED_READ", "R5_FALLBACK"),
        ProposedRouteHint.R1B_SEMANTIC_CACHE: ("R3_GROUNDED_READ", "R5_FALLBACK"),
        ProposedRouteHint.R3_GROUNDED_READ: ("R5_FALLBACK",),
        ProposedRouteHint.R4_SINGLE_ACTION: ("R3R4_MANAGED_WORKFLOW", "R5_FALLBACK"),
        ProposedRouteHint.R3R4_MANAGED_WORKFLOW: ("R5_FALLBACK",),
        ProposedRouteHint.R5_FALLBACK: (),
    }

    reason_codes: list[str] = [f"work_class:{intent.work_class}"]
    if intent.freshness_class != "stable":
        reason_codes.append(f"freshness:{intent.freshness_class}")
    if state.action_risk_summary != "read_only":
        reason_codes.append(f"action:{state.action_risk_summary}")
    if state.support_need_summary == "grounding_required":
        reason_codes.append("grounding_required")
    if intent.high_risk:
        reason_codes.append("high_risk")
    if safety.requires_hitl_later if hasattr(safety, "requires_hitl_later") else safety.hitl_may_be_needed:
        reason_codes.append("hitl_marker")
    if safety.uwg_may_be_needed:
        reason_codes.append("uwg_marker")

    return RouteHintSet(
        route_hint_id=f"rhs::{input_.request_id}",
        proposed_route_hint=proposed,
        reason_codes=tuple(reason_codes),
        confidence=confidence,
        route_risk=risk,
        fallback_chain_hint=fallback_chain[proposed],
        single_step_or_workflow=(
            "managed_workflow"
            if proposed == ProposedRouteHint.R3R4_MANAGED_WORKFLOW
            or len(work_unit_set.units) > 2
            else "single_step"
        ),
        cache_eligibility_hint=proposed
        in (ProposedRouteHint.R1A_EXACT_CACHE, ProposedRouteHint.R1B_SEMANTIC_CACHE),
        grounding_hint=state.support_need_summary == "grounding_required",
        action_hint=state.action_risk_summary != "read_only",
        hitl_hint=bool(safety.hitl_may_be_needed),
        uwg_hint=bool(safety.uwg_may_be_needed),
        cost_latency_sensitivity="low",
    )


def _build_support_expectation(input_: DraftPlanInput) -> SupportExpectation:
    state = input_.internal_plan_state
    intent = input_.intent_frame
    inv = input_.request_detail_inventory

    grounding = state.support_need_summary == "grounding_required"
    if grounding and inv.citation_needed:
        target = "citation"
    elif grounding and inv.direct_quote_needed:
        target = "direct_span"
    elif grounding and inv.files:
        target = "code_location"
    elif grounding:
        target = "evidence_bundle"
    else:
        target = "none"

    return SupportExpectation(
        grounding_required=grounding,
        support_target=target,
        evidence_classes=("docs",) if grounding else (),
        freshness_class=intent.freshness_class,
        source_expectations=tuple(inv.source_names) or ("none",),
        citation_mode_hint="inline" if grounding and inv.citation_needed else "none",
        contradiction_policy=(
            "surface_conflict" if grounding else "abstain_if_unresolved"
        ),
        weak_support_policy="caveat" if grounding else "no_op",
        cite_or_abstain_posture="cite_or_abstain" if inv.citation_needed else "caveat",
        exact_span_needed=inv.direct_quote_needed,
        code_location_needed=bool(inv.files),
        policy_clause_needed=False,
        evidence_bundle_needed=grounding,
    )


def _build_action_expectation(input_: DraftPlanInput) -> ActionExpectation:
    state = input_.internal_plan_state
    safety = input_.first_safety_authority_reading
    intent = input_.intent_frame

    action_required = state.action_risk_summary not in ("read_only", "")
    side_effect = state.action_risk_summary if action_required else "none"
    irreversible = state.action_risk_summary == "high_impact"

    candidate_tool_class = (
        "filesystem"
        if intent.artifact_requirement == "file"
        else (
            "code"
            if intent.artifact_requirement == "code"
            else "doc"
            if intent.artifact_requirement in ("doc", "slide", "spreadsheet")
            else "none"
        )
    )

    return ActionExpectation(
        action_required=action_required,
        candidate_tool_class=candidate_tool_class,
        side_effect_class=side_effect,
        sandbox_need_hint=action_required,
        capability_token_need_hint=action_required,
        external_egress_hint=safety.external_side_effect_request,
        hitl_hint=bool(safety.hitl_may_be_needed),
        uwg_hint=bool(safety.uwg_may_be_needed),
        irreversible_action_marker=irreversible,
        proposed_mutation_only_marker=True,
    )


def _build_downstream_notes(
    input_: DraftPlanInput,
    route_hint: RouteHintSet,
    support: SupportExpectation,
    action: ActionExpectation,
) -> DownstreamPlanningNotes:
    intent = input_.intent_frame
    return DownstreamPlanningNotes(
        for_l0=(
            f"proposed_route_hint={route_hint.proposed_route_hint.value}",
            f"confidence={route_hint.confidence}",
            f"route_risk={route_hint.route_risk}",
        ),
        for_c0=(
            (
                f"support_target={support.support_target}",
                f"freshness={support.freshness_class}",
                f"evidence_classes={','.join(support.evidence_classes) or 'none'}",
            )
            if support.grounding_required
            else ()
        ),
        for_prompt_assembly=(
            f"output_target={intent.user_visible_deliverable}",
            f"artifact={intent.artifact_requirement}",
            f"work_class={intent.work_class}",
        ),
        for_l2=(
            f"action_required={action.action_required}",
            f"side_effect_class={action.side_effect_class}",
        ),
        for_exit_control=(
            (("hitl_required",) if action.hitl_hint else ())
            + (("uwg_required",) if action.uwg_hint else ())
            + (
                ("recommend_refusal",)
                if input_.first_safety_authority_reading.direct_refusal_may_be_needed
                else ()
            )
        ),
        for_l6=(
            f"work_class={intent.work_class}",
            f"action_class={action.side_effect_class}",
            f"high_risk={intent.high_risk}",
        ),
    )


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def write_draft_plan(
    input_: DraftPlanInput,
    *,
    span_sink: SpanSink | None = None,
) -> DraftPlanPacket:
    """02.4 entrypoint — convert internal plan state into a DraftPlan."""
    if not isinstance(input_, DraftPlanInput):
        raise L1ContractViolation(
            f"input_ must be DraftPlanInput, got {type(input_)}"
        )

    work_unit_set = _build_work_unit_set(input_)
    dep_sketch = _build_dependency_sketch(work_unit_set)
    route_hint = _build_route_hint_set(input_, work_unit_set)
    support_exp = _build_support_expectation(input_)
    action_exp = _build_action_expectation(input_)
    notes = _build_downstream_notes(input_, route_hint, support_exp, action_exp)

    draft_payload = {
        "work_unit_set": work_unit_set.to_dict(),
        "dependency_sketch": dep_sketch.to_dict(),
        "route_hint_set": route_hint.to_dict(),
        "support_expectation": support_exp.to_dict(),
        "action_expectation": action_exp.to_dict(),
        "downstream_planning_notes": notes.to_dict(),
    }
    draft_digest = stable_digest(draft_payload, prefix="l1.02.4.draft")

    draft = DraftPlan(
        draft_plan_id=f"draft::{input_.request_id}",
        work_unit_set=work_unit_set,
        dependency_sketch=dep_sketch,
        route_hint_set=route_hint,
        support_expectation=support_exp,
        action_expectation=action_exp,
        downstream_planning_notes=notes,
        draft_digest=draft_digest,
    )

    output_digest = stable_digest({"draft_plan": draft.to_dict()}, prefix="l1.02.4.output")

    packet = DraftPlanPacket(
        draft_plan=draft,
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        output_digest=output_digest,
    )

    emit_stage_spans(
        stage="02.4",
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        policy_hash_observed=input_.policy_hash_observed,
        instruction_hash_observed=input_.instruction_hash_observed,
        input_digest=stable_digest(input_.to_dict(), prefix="l1.02.4.input"),
        output_digest=output_digest,
        span_sink=span_sink,
        extra={
            "proposed_route_hint": route_hint.proposed_route_hint.value,
            "work_units": len(work_unit_set.units),
        },
    )

    return packet
