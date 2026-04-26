"""End-to-end L1 v6 pipeline: stages 02.1 → 02.6.

Doctrine: parent ``02_L1_Reasoning_Plan_Generation_detailed.md`` § CANONICAL L1 FLOW.

The pipeline orchestrator chains the six stage entrypoints, threading
the v6 packet contracts through each step. It is deterministic given a
fixed :class:`ParsedRequestInput` and a fixed :class:`PlanningPriorReader`.

L1 invariants preserved end-to-end: no retrieval (no C0 calls), no route
authority (only advisory hints), no execution (no tool/model invocation
for the user task), no durable writes.
"""

from __future__ import annotations

from agentic_core.L1_cognition.planning.contracts import (
    DraftPlanInput,
    L1PlanContractInput,
    L1PlanHandoffPacket,
    PlanValidationInput,
    PlanningPriorReadInput,
    PlanningReasoningInput,
    QuerySpec,
    TaskSpec,
)
from agentic_core.L1_cognition.planning.contracts import (
    ParsedRequestInput,
)
from agentic_core.L1_cognition.planning.intent_frame import parse_intent_frame
from agentic_core.L1_cognition.planning.planning_priors import (
    PlanningPriorReader,
    StaticPlanningPriorReader,
    build_plan_bundle,
)
from agentic_core.L1_cognition.planning.reasoning_loop import run_l1_reasoning_loop
from agentic_core.L1_cognition.planning.draft_plan import write_draft_plan
from agentic_core.L1_cognition.planning.plan_validation import (
    validate_and_repair_l1_plan,
)
from agentic_core.L1_cognition.planning.plan_contract_handoff import (
    emit_l1_plan_contract,
)
from agentic_core.L1_cognition.planning.otel import SpanSink

__all__ = ["run_l1_planning"]


def _build_query_spec(parsed_packet, draft_plan) -> QuerySpec | None:
    """Derive the v6 :class:`QuerySpec` from the parsed inventory + draft."""
    support = draft_plan.support_expectation
    if not support.grounding_required:
        return None
    inv = parsed_packet.request_detail_inventory
    intent = parsed_packet.intent_frame
    return QuerySpec(
        normalized_request=intent.normalized_goal,
        entities=tuple(inv.entities),
        aliases=tuple(inv.exact_terms),
        terms=tuple(inv.exact_terms),
        files_or_sources=tuple(inv.files) + tuple(inv.urls),
        connectors=tuple(inv.connectors),
        uploaded_file_expectations=tuple(inv.uploaded_objects),
        dates_or_versions=tuple(inv.dates) + tuple(inv.versions),
        freshness_class=intent.freshness_class,
        source_expectations=tuple(support.source_expectations),
        support_need=support.support_target,
        currentness_mandatory=intent.freshness_class in ("current", "live"),
        citation_or_exact_span_may_be_required=(
            inv.citation_needed or inv.direct_quote_needed
        ),
    )


def _build_task_spec(parsed_packet, draft_plan) -> TaskSpec:
    """Derive the v6 :class:`TaskSpec` from the draft plan + intent."""
    intent = parsed_packet.intent_frame
    return TaskSpec(
        work_units=tuple(u.description for u in draft_plan.work_unit_set.units),
        output_target=intent.user_visible_deliverable,
        output_format=intent.artifact_requirement,
        structure_requirements=tuple(),
        style_constraints=tuple(
            c.get("statement", "")
            for c in intent.constraints
            if c.get("severity") == "should"
        ),
        acceptance_criteria=tuple(
            ac
            for u in draft_plan.work_unit_set.units
            for ac in u.acceptance_criteria
        ),
        stop_condition=intent.success_condition,
        expected_length_or_depth="",
        artifact_packaging_requirement=intent.artifact_requirement,
        partial_completion_allowed=True,
    )


def _build_assumptions_and_gaps(parsed_packet, validated_packet) -> dict:
    intent = parsed_packet.intent_frame
    marker = validated_packet.clarify_abstain_fallback_marker
    declared = list(intent.ambiguity.get("assumed", []))
    unresolved = list(intent.ambiguity.get("unresolved", []))
    return {
        "declared_assumptions": declared,
        "unresolved_gaps": unresolved,
        "clarify_required": marker.clarify_recommended,
        "clarify_question": marker.clarify_question,
        "abstain_or_fallback_marker": (
            "abstain"
            if marker.abstain_recommended
            else "fallback"
            if marker.fallback_recommended
            else "clarify"
            if marker.clarify_recommended
            else "policy_review"
            if marker.policy_review_recommended
            else "none"
        ),
    }


def _build_validation_summary(validated_packet) -> dict:
    report = validated_packet.plan_validation_report
    return {
        "listened_to_user": report.listened_to_user_status.value
        != "fail",
        "constraints_preserved": report.constraints_preserved_status.value
        != "fail",
        "deliverable_fit": report.deliverable_fit_status.value != "fail",
        "style_format_fit": report.style_format_fit_status.value != "fail",
        "safety_checked": report.safety_checked_status.value != "fail",
        "coherent_plan": report.coherent_plan_status.value != "fail",
        "route_hint_consistency": report.route_hint_consistency_status.value
        != "fail",
        "support_expectation_consistency": report.support_expectation_status.value
        != "fail",
        "action_expectation_consistency": report.action_expectation_status.value
        != "fail",
        "lowest_viable_agency_applied": report.lowest_viable_agency_status.value
        != "fail",
        "no_retrieval_performed": True,
        "no_execution_performed": True,
        "no_write_performed": True,
        "validation_failures": list(report.validation_failures),
        "validation_warnings": list(report.validation_warnings),
    }


def run_l1_planning(
    parsed_input: ParsedRequestInput,
    *,
    prior_reader: PlanningPriorReader | None = None,
    span_sink: SpanSink | None = None,
    max_refinement_passes: int = 3,
    max_self_repair_passes: int = 2,
    reasoning_budget: int = 8192,
    planning_prior_budget: int = 4096,
) -> L1PlanHandoffPacket:
    """End-to-end L1 v6 planning.

    Args:
        parsed_input: U0 → L1 input wrapper.
        prior_reader: A :class:`PlanningPriorReader`. When ``None``, a
            :class:`StaticPlanningPriorReader` with a small default
            reference set is used so the pipeline runs end-to-end in
            tests and isolated environments.
        span_sink: Optional sink for OTEL span events emitted by every
            stage.
        max_refinement_passes: Cap for the 02.3 refinement loop.
        max_self_repair_passes: Cap for the 02.5 self-repair loop.
        reasoning_budget: Synthetic reasoning-budget limit for 02.3.
        planning_prior_budget: Token budget for 02.2's prior reads.

    Returns:
        :class:`L1PlanHandoffPacket` ready for L0.
    """
    # --- Stage 02.1 ---
    parsed_packet = parse_intent_frame(parsed_input, span_sink=span_sink)

    # --- Stage 02.2 ---
    if prior_reader is None:
        prior_reader = StaticPlanningPriorReader(
            references_by_class={
                "task_schemas": ("schema:answer", "schema:plan"),
                "route_heuristics": (
                    "if grounded -> R3",
                    "if cache -> R1B",
                    "if action -> R4",
                ),
                "output_contracts": ("contract:json", "contract:markdown"),
                "validation_rubrics": ("rubric:listened_to_user", "rubric:safety"),
                "compliance_bounds": ("policy:no_pii", "policy:no_external_egress"),
                "escalation_thresholds": ("hitl:high_impact", "hitl:irreversible"),
                "safe_decomposition_patterns": (
                    "decomp:read+answer",
                    "decomp:propose+validate",
                ),
                "fallback_templates": ("fallback:abstain", "fallback:clarify"),
            },
            snapshot_manifest={"snapshot": "default-l1-static-v6"},
        )
    prior_input = PlanningPriorReadInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        caller_scope_baseline=parsed_input.caller_scope_baseline,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        planning_prior_budget=planning_prior_budget,
        replay_key_seed=parsed_input.request_id,
    )
    bundle_packet = build_plan_bundle(prior_input, prior_reader, span_sink=span_sink)

    # --- Stage 02.3 ---
    reasoning_input = PlanningReasoningInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        request_detail_inventory=parsed_packet.request_detail_inventory,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        plan_bundle=bundle_packet.plan_bundle,
        rule_aware_planning_frame=bundle_packet.rule_aware_planning_frame,
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        max_refinement_passes=max_refinement_passes,
        reasoning_budget=reasoning_budget,
        replay_key_seed=parsed_input.request_id,
    )
    reasoning_packet = run_l1_reasoning_loop(reasoning_input, span_sink=span_sink)

    # --- Stage 02.4 ---
    draft_input = DraftPlanInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        request_detail_inventory=parsed_packet.request_detail_inventory,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        plan_bundle=bundle_packet.plan_bundle,
        rule_aware_planning_frame=bundle_packet.rule_aware_planning_frame,
        internal_plan_state=reasoning_packet.internal_plan_state,
        reasoning_trace_summary=reasoning_packet.planning_reasoning_trace_summary,
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        replay_key_seed=parsed_input.request_id,
    )
    draft_packet = write_draft_plan(draft_input, span_sink=span_sink)

    # --- Stage 02.5 ---
    validation_input = PlanValidationInput(
        draft_plan=draft_packet.draft_plan,
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        max_self_repair_passes=max_self_repair_passes,
        replay_key_seed=parsed_input.request_id,
    )
    validated_packet = validate_and_repair_l1_plan(validation_input, span_sink=span_sink)

    final_draft = validated_packet.final_draft_plan
    query_spec = _build_query_spec(parsed_packet, final_draft)
    task_spec = _build_task_spec(parsed_packet, final_draft)
    assumptions = _build_assumptions_and_gaps(parsed_packet, validated_packet)
    validation_summary = _build_validation_summary(validated_packet)

    contract_input = L1PlanContractInput(
        validated_plan_packet=validated_packet,
        intent_frame=parsed_packet.intent_frame,
        query_spec=query_spec,
        task_spec=task_spec,
        route_hint_set=final_draft.route_hint_set,
        support_expectation=final_draft.support_expectation,
        action_expectation=final_draft.action_expectation,
        assumptions_and_gaps=assumptions,
        validation_summary=validation_summary,
        downstream_notes=final_draft.downstream_planning_notes,
        request_id=parsed_input.request_id,
        session_id=parsed_input.session_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        source_envelope_id=parsed_input.source_envelope_id,
        replay_key_seed=parsed_input.request_id,
    )

    # --- Stage 02.6 ---
    return emit_l1_plan_contract(contract_input, span_sink=span_sink)
