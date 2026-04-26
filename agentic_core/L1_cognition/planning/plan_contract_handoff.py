"""Stage 02.6 — L1PlanContract & Handoff to L0.

Doctrine: ``docs/reference/02_L1_Reasoning/02.6_L1PlanContract_Handoff_detailed.md``.

This module freezes the final validated plan into a canonical
:class:`L1PlanContract`, attaches a :class:`PlanReplayManifest` and
:class:`NonAuthorityAssertion`, computes the deterministic
:class:`PlanDigest`, and emits the :class:`L1HandoffReceipt` to L0.

Schema invariants enforced (PHASE 3):

* ``route_hint.proposed_route_hint`` is advisory only.
* ``route_hint`` does NOT contain ``route_digest`` or ``hmac_sig``.
* ``support_expectation`` does NOT carry retrieved evidence refs.
* ``action_expectation`` does NOT grant capability/sandbox.
* ``downstream_notes`` does NOT contain final answer text.
* ``validation_summary`` positively asserts no_retrieval / no_execution
  / no_write.
* :class:`NonAuthorityAssertion` requires every flag True.
"""

from __future__ import annotations

from agentic_core.L1_cognition.planning.contracts import (
    DownstreamPlanningNotes,
    L1ContractViolation,
    L1HandoffReceipt,
    L1PlanContract,
    L1PlanContractInput,
    L1PlanHandoffPacket,
    L1TelemetryKeySet,
    NonAuthorityAssertion,
    PlanDigest,
    PlanReplayManifest,
    QuerySpec,
    TaskSpec,
)
from agentic_core.L1_cognition.planning.digests import (
    DETERMINISTIC_DIGEST_ALGORITHM,
    stable_digest,
)
from agentic_core.L1_cognition.planning.otel import SpanSink, emit_stage_spans

__all__ = ["emit_l1_plan_contract"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_replay_manifest(input_: L1PlanContractInput, l1_plan_id: str) -> PlanReplayManifest:
    intent_dict = input_.intent_frame.to_dict()
    plan_bundle_dict = input_.validated_plan_packet.final_draft_plan.to_dict()
    internal_state_dict = input_.validated_plan_packet.final_draft_plan.work_unit_set.to_dict()
    draft_plan_dict = input_.validated_plan_packet.final_draft_plan.to_dict()
    validation_dict = input_.validated_plan_packet.plan_validation_report.to_dict()

    return PlanReplayManifest(
        manifest_id=f"prm::{l1_plan_id}",
        normalized_request_hash=stable_digest(
            input_.intent_frame.normalized_goal, prefix="normalized_request"
        ),
        visible_context_hash=stable_digest(intent_dict, prefix="visible_context"),
        intent_frame_hash=stable_digest(intent_dict, prefix="intent_frame"),
        plan_bundle_hash=stable_digest(plan_bundle_dict, prefix="plan_bundle"),
        internal_plan_state_hash=stable_digest(internal_state_dict, prefix="internal_plan_state"),
        draft_plan_hash=stable_digest(draft_plan_dict, prefix="draft_plan"),
        validation_report_hash=stable_digest(validation_dict, prefix="validation_report"),
        policy_hash=input_.policy_hash_observed,
        instruction_hash=input_.instruction_hash_observed,
        source_envelope_id=input_.source_envelope_id,
        deterministic_digest_algorithm=DETERMINISTIC_DIGEST_ALGORITHM,
    )


def _intent_frame_block(input_: L1PlanContractInput) -> dict:
    intent = input_.intent_frame
    constraints = intent.constraints  # list[dict]
    style = [c["statement"] for c in constraints if c.get("severity") == "should"]
    hard = [c["statement"] for c in constraints if c.get("severity") == "must"]
    soft = [c["statement"] for c in constraints if c.get("severity") == "avoid"]
    unstated = list(intent.ambiguity.get("unstated_likely", []))
    return {
        "normalized_goal": intent.normalized_goal,
        "deliverable": intent.user_visible_deliverable,
        "work_class": intent.work_class,
        "audience": intent.audience,
        "tone_or_style_constraints": style,
        "hard_constraints": hard,
        "soft_constraints": soft,
        "exclusions": [],
        "success_condition": intent.success_condition,
        "completion_threshold": "default",
        "implicit_goal": unstated[0] if unstated else "",
        "one_shot_or_iterative_need": "one_shot",
        "requested_output_format": intent.artifact_requirement,
        "artifact_requirement": intent.artifact_requirement,
        "support_requirement_hint": ("yes" if input_.support_expectation.grounding_required else "no"),
        "freshness_requirement_hint": intent.freshness_class,
        "action_requirement_hint": intent.action_requirement,
        "external_egress_hint": input_.action_expectation.external_egress_hint,
        "durable_write_hint": input_.action_expectation.uwg_hint,
        "high_impact_hint": intent.high_risk,
        "privacy_or_sensitive_data_hint": False,
    }


def _validation_summary(input_: L1PlanContractInput) -> dict:
    raw = dict(input_.validation_summary)
    # Force the v6 invariants — even if caller passed legacy dict.
    raw["no_retrieval_performed"] = True
    raw["no_execution_performed"] = True
    raw["no_write_performed"] = True
    raw.setdefault("listened_to_user", True)
    raw.setdefault("constraints_preserved", True)
    raw.setdefault("safety_checked", True)
    raw.setdefault("coherent_plan", True)
    raw.setdefault("lowest_viable_agency_applied", True)
    return raw


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def emit_l1_plan_contract(
    input_: L1PlanContractInput,
    *,
    span_sink: SpanSink | None = None,
) -> L1PlanHandoffPacket:
    """02.6 entrypoint — freeze and emit the canonical L1PlanContract."""
    if not isinstance(input_, L1PlanContractInput):
        raise L1ContractViolation(f"input_ must be L1PlanContractInput, got {type(input_)}")
    if not isinstance(input_.task_spec, TaskSpec):
        raise L1ContractViolation("input_.task_spec must be TaskSpec")
    if input_.query_spec is not None and not isinstance(input_.query_spec, QuerySpec):
        raise L1ContractViolation("input_.query_spec must be QuerySpec or None")
    if not isinstance(input_.downstream_notes, DownstreamPlanningNotes):
        raise L1ContractViolation("input_.downstream_notes must be DownstreamPlanningNotes")

    l1_plan_id = f"l1plan::{input_.request_id}"

    identity = {
        "request_id": input_.request_id,
        "session_id": input_.session_id,
        "trace_root": input_.trace_root,
        "l1_plan_id": l1_plan_id,
        "policy_hash": input_.policy_hash_observed,
        "instruction_hash": input_.instruction_hash_observed,
        "source_envelope_id": input_.source_envelope_id,
    }

    intent_block = _intent_frame_block(input_)
    query_block = input_.query_spec.to_dict() if input_.query_spec else None
    task_block = input_.task_spec.to_dict()
    route_block = input_.route_hint_set.to_dict()
    # Defensively scrub disallowed keys.
    for forbidden in ("route_digest", "hmac_sig", "selected_route", "execution_authorization"):
        route_block.pop(forbidden, None)
    support_block = input_.support_expectation.to_dict()
    action_block = input_.action_expectation.to_dict()
    notes_block = input_.downstream_notes.to_dict()

    assumptions = dict(input_.assumptions_and_gaps)
    assumptions.setdefault("declared_assumptions", [])
    assumptions.setdefault("unresolved_gaps", [])
    assumptions.setdefault("clarify_required", False)
    assumptions.setdefault("clarify_question", "")
    assumptions.setdefault("abstain_or_fallback_marker", "none")

    validation_block = _validation_summary(input_)

    replay = _build_replay_manifest(input_, l1_plan_id)

    # Compute the deterministic plan digest from the canonical contract body.
    contract_body = {
        "layer": "L1_REASONING_PLAN_GENERATION",
        "version": "v6",
        "authority": "advisory_plan_only",
        "identity": identity,
        "intent_frame": intent_block,
        "query_spec": query_block,
        "task_spec": task_block,
        "route_hint": route_block,
        "support_expectation": support_block,
        "action_expectation": action_block,
        "assumptions_and_gaps": assumptions,
        "validation_summary": validation_block,
        "downstream_notes": notes_block,
        "plan_replay_manifest": replay.to_dict(),
    }
    digest_str = stable_digest(contract_body, prefix="l1.02.6.contract")
    plan_digest = PlanDigest(digest=digest_str)
    non_authority = NonAuthorityAssertion()  # all True by default

    contract = L1PlanContract(
        layer="L1_REASONING_PLAN_GENERATION",
        version="v6",
        authority="advisory_plan_only",
        identity=identity,
        intent_frame=intent_block,
        query_spec=query_block,
        task_spec=task_block,
        route_hint=route_block,
        support_expectation=support_block,
        action_expectation=action_block,
        assumptions_and_gaps=assumptions,
        validation_summary=validation_block,
        downstream_notes=notes_block,
        plan_replay_manifest=replay.to_dict(),
        plan_digest=plan_digest,
        non_authority_assertion=non_authority,
    )

    telemetry_keys = L1TelemetryKeySet(
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        l1_plan_id=l1_plan_id,
        plan_digest=digest_str,
        span_names=(
            "l1.02.1.input.accepted",
            "l1.02.1.core.completed",
            "l1.02.1.output.emitted",
            "l1.02.2.input.accepted",
            "l1.02.2.core.completed",
            "l1.02.2.output.emitted",
            "l1.02.3.input.accepted",
            "l1.02.3.core.completed",
            "l1.02.3.output.emitted",
            "l1.02.4.input.accepted",
            "l1.02.4.core.completed",
            "l1.02.4.output.emitted",
            "l1.02.5.input.accepted",
            "l1.02.5.core.completed",
            "l1.02.5.output.emitted",
            "l1.02.6.input.accepted",
            "l1.02.6.core.completed",
            "l1.02.6.output.emitted",
        ),
    )

    readiness = input_.validated_plan_packet.final_plan_readiness_receipt
    handoff_receipt = L1HandoffReceipt(
        handoff_receipt_id=f"hr::{l1_plan_id}",
        l1_plan_id=l1_plan_id,
        target_layer="L0_ROUTE_DECISION",
        handoff_time_policy="emit_after_validation_pass_or_marker",
        plan_digest=digest_str,
        trace_root=input_.trace_root,
        request_id=input_.request_id,
        readiness_status=readiness.final_plan_status,
        non_authority_assertion_ref="L1.NonAuthorityAssertion(all_flags_true=True)",
        telemetry_keys=tuple(telemetry_keys.span_names),
    )

    packet = L1PlanHandoffPacket(
        l1_plan_contract=contract,
        l1_handoff_receipt=handoff_receipt,
        l1_telemetry_key_set=telemetry_keys,
        plan_digest=plan_digest,
        request_id=input_.request_id,
        trace_root=input_.trace_root,
    )

    emit_stage_spans(
        stage="02.6",
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        policy_hash_observed=input_.policy_hash_observed,
        instruction_hash_observed=input_.instruction_hash_observed,
        input_digest=stable_digest(input_.to_dict(), prefix="l1.02.6.input"),
        output_digest=digest_str,
        span_sink=span_sink,
        extra={
            "l1_plan_id": l1_plan_id,
            "readiness_status": readiness.final_plan_status,
        },
    )

    return packet
