"""Stage 02.5 — Plan Validation & Self-Repair.

Doctrine: ``docs/reference/02_L1_Reasoning/02.5_Plan_Validation_Self_Repair_detailed.md``.

This module validates the :class:`DraftPlan` from stage 02.4 along nine
axes (listened-to-user, constraints preserved, deliverable fit, style
fit, safety, coherence, route-hint consistency, support-expectation
consistency, action-expectation consistency, lowest-viable-agency),
runs a bounded self-repair loop (max 2 passes), and emits the
:class:`ValidatedPlanPacket`.

Self-repair operates only on the v6 :class:`DraftPlan` — it does not
call the v4 :func:`agentic_core.L1_cognition.reasoning.plan_self_repair.repair_plan_with_loop`
(that wraps :class:`L1PlanContractV2`). The v6 layer keeps repair
deterministic, hash-stable, and limited to the doctrine's repair-rule
catalogue.
"""

from __future__ import annotations

from dataclasses import replace

from agentic_core.L1_cognition.planning.contracts import (
    ClarifyAbstainFallbackMarker,
    DraftPlan,
    FinalPlanReadinessReceipt,
    L1ContractViolation,
    L1SelfRepairLedger,
    LowestViableAgencyReceipt,
    PlanConsistencyAudit,
    PlanValidationInput,
    PlanValidationReport,
    ProposedRouteHint,
    RepairAction,
    RouteHintSet,
    SupportExpectation,
    ValidatedPlanPacket,
    ValidationStatus,
)
from agentic_core.L1_cognition.planning.digests import stable_digest
from agentic_core.L1_cognition.planning.otel import SpanSink, emit_stage_spans

__all__ = ["validate_and_repair_l1_plan"]


# ---------------------------------------------------------------------------
# Validation primitives
# ---------------------------------------------------------------------------


def _validate(draft: DraftPlan, input_: PlanValidationInput) -> tuple[
    PlanValidationReport, PlanConsistencyAudit
]:
    intent = input_.intent_frame
    safety = input_.first_safety_authority_reading
    failures: list[str] = []
    warnings: list[str] = []

    # 1. Listened to user — primary work unit must reference the goal.
    primary = draft.work_unit_set.units[0]
    listened_status = ValidationStatus.PASS
    if intent.normalized_goal and intent.normalized_goal[:50] not in primary.description:
        warnings.append("primary work_unit description does not echo intent.goal")
        listened_status = ValidationStatus.WARN

    # 2. Constraints preserved.
    constraints_status = ValidationStatus.PASS
    if intent.constraints and not primary.constraints:
        warnings.append("draft primary unit dropped intent constraints")
        constraints_status = ValidationStatus.WARN

    # 3. Deliverable fit.
    deliverable_status = ValidationStatus.PASS
    if intent.user_visible_deliverable == "action" and draft.action_expectation.action_required is False:
        failures.append("intent requested an action but action_required=False")
        deliverable_status = ValidationStatus.FAIL
    if intent.user_visible_deliverable == "artifact" and not any(
        u.requires_artifact_output_hint for u in draft.work_unit_set.units
    ):
        failures.append("intent requested an artifact but no artifact unit present")
        deliverable_status = ValidationStatus.FAIL

    # 4. Style/format fit.
    style_status = ValidationStatus.PASS

    # 5. Safety — unsafe markers, refusal, injection.
    safety_status = ValidationStatus.PASS
    if safety.direct_refusal_may_be_needed and draft.route_hint_set.proposed_route_hint != ProposedRouteHint.R5_FALLBACK:
        failures.append(
            "direct refusal may be needed but route_hint != R5_FALLBACK"
        )
        safety_status = ValidationStatus.FAIL
    if safety.authority_override_attempt:
        warnings.append("authority_override_attempt detected — keep route advisory")
        safety_status = max(safety_status, ValidationStatus.WARN, key=_status_rank)

    # 6. Coherence — DAG sanity.
    coherent_status = ValidationStatus.PASS
    seen_ids = {u.work_unit_id for u in draft.work_unit_set.units}
    for u in draft.work_unit_set.units:
        for dep in u.dependency_refs:
            if dep not in seen_ids:
                failures.append(f"work_unit {u.work_unit_id!r} references unknown dep {dep!r}")
                coherent_status = ValidationStatus.FAIL

    # 7. Route hint consistency.
    route_hint_status = _validate_route_hint(draft.route_hint_set, draft.support_expectation, failures, warnings)

    # 8. Support expectation consistency.
    support_status = ValidationStatus.PASS
    if (
        draft.support_expectation.support_target != "none"
        and not draft.support_expectation.grounding_required
    ):
        failures.append(
            "support_target requested but grounding_required=False"
        )
        support_status = ValidationStatus.FAIL

    # 9. Action expectation consistency.
    action_status = ValidationStatus.PASS
    if (
        draft.action_expectation.irreversible_action_marker
        and not draft.action_expectation.hitl_hint
    ):
        warnings.append(
            "irreversible action proposed without hitl_hint=True"
        )
        action_status = ValidationStatus.WARN

    # 10. Lowest viable agency.
    lva_status = ValidationStatus.PASS
    if (
        safety.safe_direct_response_possible
        and draft.route_hint_set.proposed_route_hint
        in (ProposedRouteHint.R3R4_MANAGED_WORKFLOW,)
    ):
        warnings.append(
            "managed workflow proposed but direct response is safe — consider simplification"
        )
        lva_status = ValidationStatus.WARN

    # Consistency audit (PHASE 1.3).
    audit = PlanConsistencyAudit(
        cache_hint_freshness_consistent=not (
            draft.route_hint_set.proposed_route_hint
            in (ProposedRouteHint.R1A_EXACT_CACHE, ProposedRouteHint.R1B_SEMANTIC_CACHE)
            and draft.support_expectation.freshness_class in ("current", "live")
        ),
        grounded_read_marks_c0=not draft.support_expectation.grounding_required
        or draft.route_hint_set.proposed_route_hint
        in (
            ProposedRouteHint.R3_GROUNDED_READ,
            ProposedRouteHint.R3R4_MANAGED_WORKFLOW,
        ),
        single_action_bounded=(
            draft.route_hint_set.proposed_route_hint != ProposedRouteHint.R4_SINGLE_ACTION
            or len(draft.work_unit_set.units) <= 3
        ),
        managed_workflow_justified=(
            draft.route_hint_set.proposed_route_hint != ProposedRouteHint.R3R4_MANAGED_WORKFLOW
            or len(draft.work_unit_set.units) >= 2
            or bool(draft.dependency_sketch.l3_may_be_needed_reason)
        ),
        fallback_reason_present=(
            draft.route_hint_set.proposed_route_hint != ProposedRouteHint.R5_FALLBACK
            or bool(draft.route_hint_set.reason_codes)
        ),
        durable_mutation_marks_uwg=(
            draft.action_expectation.side_effect_class not in ("write_proposal", "high_impact", "durable_write")
            or draft.action_expectation.uwg_hint
            or draft.route_hint_set.uwg_hint
        ),
        high_risk_marks_hitl=(
            not safety.high_impact_domain_hint
            or draft.action_expectation.hitl_hint
            or draft.route_hint_set.hitl_hint
        ),
        confidence_matches_evidence=(
            draft.route_hint_set.confidence < 0.9
            or not draft.support_expectation.grounding_required
            or draft.support_expectation.support_target != "none"
        ),
        full_overwrite_preserves_structure=True,
        findings=tuple(failures + warnings),
    )

    report_payload = {
        "failures": failures,
        "warnings": warnings,
        "audit": audit.to_dict(),
    }
    report_digest = stable_digest(report_payload, prefix="l1.02.5.report")

    report = PlanValidationReport(
        report_id=f"pvr::{input_.request_id}",
        listened_to_user_status=listened_status,
        constraints_preserved_status=constraints_status,
        deliverable_fit_status=deliverable_status,
        style_format_fit_status=style_status,
        safety_checked_status=safety_status,
        coherent_plan_status=coherent_status,
        route_hint_consistency_status=route_hint_status,
        support_expectation_status=support_status,
        action_expectation_status=action_status,
        lowest_viable_agency_status=lva_status,
        validation_failures=tuple(failures),
        validation_warnings=tuple(warnings),
        report_digest=report_digest,
    )
    return report, audit


_STATUS_RANK = {
    ValidationStatus.NOT_RUN: 0,
    ValidationStatus.PASS: 1,
    ValidationStatus.WARN: 2,
    ValidationStatus.FAIL: 3,
}


def _status_rank(s: ValidationStatus) -> int:
    return _STATUS_RANK[s]


def _validate_route_hint(
    route: RouteHintSet, support: SupportExpectation, failures: list[str], warnings: list[str]
) -> ValidationStatus:
    proposed = route.proposed_route_hint
    if proposed == ProposedRouteHint.R3_GROUNDED_READ and not support.grounding_required:
        failures.append("R3 grounded read proposed but grounding_required=False")
        return ValidationStatus.FAIL
    if proposed == ProposedRouteHint.R5_FALLBACK and not route.reason_codes:
        failures.append("R5 fallback proposed without reason_codes")
        return ValidationStatus.FAIL
    if proposed == ProposedRouteHint.R3R4_MANAGED_WORKFLOW and route.single_step_or_workflow == "single_step":
        warnings.append("managed_workflow route but single_step_or_workflow=single_step")
        return ValidationStatus.WARN
    return ValidationStatus.PASS


# ---------------------------------------------------------------------------
# Self-repair
# ---------------------------------------------------------------------------


def _repair_once(
    draft: DraftPlan, report: PlanValidationReport
) -> tuple[DraftPlan, RepairAction]:
    findings = list(report.validation_failures) + list(report.validation_warnings)
    if not findings:
        return draft, RepairAction.NO_ACTION

    # 1. Unsafe route hint — direct refusal not honoured.
    if any("direct refusal may be needed" in f for f in findings):
        repaired_route = replace(
            draft.route_hint_set,
            proposed_route_hint=ProposedRouteHint.R5_FALLBACK,
            reason_codes=draft.route_hint_set.reason_codes + ("direct_refusal_advised",),
        )
        return (
            replace(draft, route_hint_set=repaired_route),
            RepairAction.REPAIR_UNSAFE_ROUTE_HINT,
        )

    # 2. R3 grounded read but grounding_required=False — flip support_target.
    if any("R3 grounded read proposed but grounding_required=False" in f for f in findings):
        repaired_support = replace(draft.support_expectation, grounding_required=True)
        return (
            replace(draft, support_expectation=repaired_support),
            RepairAction.REPAIR_UNCLEAR_SUPPORT_EXPECTATION,
        )

    # 3. Missing fallback reason — annotate.
    if any("R5 fallback proposed without reason_codes" in f for f in findings):
        new_codes = draft.route_hint_set.reason_codes + ("fallback_unspecified",)
        repaired_route = replace(draft.route_hint_set, reason_codes=new_codes)
        return (
            replace(draft, route_hint_set=repaired_route),
            RepairAction.REPAIR_MISSING_FALLBACK,
        )

    # 4. Action without HITL — set hitl_hint=True.
    if any("irreversible action proposed without hitl_hint" in f for f in findings):
        repaired_action = replace(draft.action_expectation, hitl_hint=True)
        repaired_route = replace(draft.route_hint_set, hitl_hint=True)
        return (
            replace(
                draft,
                action_expectation=repaired_action,
                route_hint_set=repaired_route,
            ),
            RepairAction.REPAIR_MISSING_HITL_OR_UWG_HINT,
        )

    # 5. Unnecessary workflow — collapse to single step.
    if any("managed workflow proposed but direct response is safe" in f for f in findings):
        repaired_route = replace(
            draft.route_hint_set,
            proposed_route_hint=ProposedRouteHint.R1B_SEMANTIC_CACHE,
            single_step_or_workflow="single_step",
        )
        return (
            replace(draft, route_hint_set=repaired_route),
            RepairAction.REPAIR_UNNECESSARY_WORKFLOW,
        )

    # 6. Support target requested without grounding — mark unsupported certainty.
    if any("support_target requested but grounding_required=False" in f for f in findings):
        repaired_support = replace(draft.support_expectation, support_target="none")
        return (
            replace(draft, support_expectation=repaired_support),
            RepairAction.REPAIR_UNSUPPORTED_CERTAINTY,
        )

    return draft, RepairAction.NO_ACTION


def _lva_receipt(
    draft: DraftPlan, input_: PlanValidationInput
) -> LowestViableAgencyReceipt:
    safety = input_.first_safety_authority_reading
    proposed = draft.route_hint_set.proposed_route_hint
    direct_possible = safety.safe_direct_response_possible

    if proposed == ProposedRouteHint.R5_FALLBACK:
        recommendation = "fallback"
    elif direct_possible and proposed in (
        ProposedRouteHint.R1A_EXACT_CACHE,
        ProposedRouteHint.R1B_SEMANTIC_CACHE,
    ):
        recommendation = "answer_directly"
    elif proposed == ProposedRouteHint.R3_GROUNDED_READ:
        recommendation = "grounded_read"
    elif proposed == ProposedRouteHint.R4_SINGLE_ACTION:
        recommendation = "single_action"
    elif proposed == ProposedRouteHint.R3R4_MANAGED_WORKFLOW:
        recommendation = "workflow"
    else:
        recommendation = "answer_directly"

    return LowestViableAgencyReceipt(
        receipt_id=f"lva::{input_.request_id}",
        original_complexity_class=(
            "workflow"
            if len(draft.work_unit_set.units) > 2
            else "single_step"
        ),
        reduced_complexity_class=draft.route_hint_set.single_step_or_workflow,
        direct_answer_possible=direct_possible,
        grounded_read_needed=draft.support_expectation.grounding_required,
        single_action_sufficient=(
            draft.action_expectation.action_required
            and not draft.action_expectation.irreversible_action_marker
            and len(draft.work_unit_set.units) <= 3
        ),
        managed_workflow_justified=(
            proposed == ProposedRouteHint.R3R4_MANAGED_WORKFLOW
            and len(draft.work_unit_set.units) >= 2
        ),
        workflow_removed_reason=(
            "direct_response_safe" if direct_possible else ""
        ),
        tool_use_removed_reason="" if draft.action_expectation.action_required else "no_action_required",
        clarification_removed_reason="",
        final_agency_recommendation=recommendation,
    )


def _clarify_marker(
    draft: DraftPlan,
    report: PlanValidationReport,
    input_: PlanValidationInput,
    repair_used: bool,
) -> ClarifyAbstainFallbackMarker:
    safety = input_.first_safety_authority_reading
    unresolved = list(input_.ambiguity_register.get("unresolved", []))
    clarify = bool(unresolved) and not repair_used and not safety.direct_refusal_may_be_needed
    abstain = safety.direct_refusal_may_be_needed
    fallback = (
        draft.route_hint_set.proposed_route_hint == ProposedRouteHint.R5_FALLBACK
        and not abstain
    )
    policy_review = safety.authority_override_attempt or safety.prompt_injection_like_text_present

    return ClarifyAbstainFallbackMarker(
        marker_id=f"cafm::{input_.request_id}",
        clarify_recommended=clarify,
        clarify_question=(
            unresolved[0]
            if clarify and unresolved
            else ""
        ),
        abstain_recommended=abstain,
        fallback_recommended=fallback,
        policy_review_recommended=policy_review,
        reason_codes=tuple(report.validation_failures),
        critical_gap_refs=tuple(unresolved),
        unsafe_completion_refs=tuple(report.validation_failures),
    )


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def validate_and_repair_l1_plan(
    input_: PlanValidationInput,
    *,
    span_sink: SpanSink | None = None,
) -> ValidatedPlanPacket:
    """02.5 entrypoint — validate, audit, repair, finalise."""
    if not isinstance(input_, PlanValidationInput):
        raise L1ContractViolation(
            f"input_ must be PlanValidationInput, got {type(input_)}"
        )

    draft = input_.draft_plan
    repairs_attempted: list[RepairAction] = []
    repairs_accepted: list[RepairAction] = []
    repairs_rejected: list[RepairAction] = []
    passes_used = 0
    stop_reason = "stable"

    report, audit = _validate(draft, input_)

    while passes_used < input_.max_self_repair_passes and not report.is_pass():
        passes_used += 1
        new_draft, action = _repair_once(draft, report)
        repairs_attempted.append(action)
        if action == RepairAction.NO_ACTION:
            stop_reason = "no_repair_rule_matched"
            break
        new_report, new_audit = _validate(new_draft, replace(input_, draft_plan=new_draft))
        if _status_rank(new_report.coherent_plan_status) <= _status_rank(report.coherent_plan_status):
            draft = new_draft
            report = new_report
            audit = new_audit
            repairs_accepted.append(action)
        else:
            repairs_rejected.append(action)
            stop_reason = f"repair_rejected:{action.value}"
            break

    if passes_used >= input_.max_self_repair_passes and not report.is_pass():
        stop_reason = "max_passes_reached"

    ledger = L1SelfRepairLedger(
        ledger_id=f"l1srl::{input_.request_id}",
        max_passes=input_.max_self_repair_passes,
        passes_used=passes_used,
        repairs_attempted=tuple(repairs_attempted),
        repairs_accepted=tuple(repairs_accepted),
        repairs_rejected=tuple(repairs_rejected),
        unresolved_failures=tuple(report.validation_failures),
        stop_reason=stop_reason,
    )

    lva = _lva_receipt(draft, input_)
    marker = _clarify_marker(draft, report, input_, repair_used=bool(repairs_accepted))

    ready = (
        report.is_pass()
        and not marker.abstain_recommended
        and not marker.policy_review_recommended
    )
    final_status = (
        "ready"
        if ready
        else (
            "abstain_recommended"
            if marker.abstain_recommended
            else (
                "fallback_recommended"
                if marker.fallback_recommended
                else (
                    "clarify_recommended"
                    if marker.clarify_recommended
                    else "policy_review_recommended"
                    if marker.policy_review_recommended
                    else "validation_failed"
                )
            )
        )
    )

    readiness = FinalPlanReadinessReceipt(
        receipt_id=f"fpr::{input_.request_id}",
        plan_ready_for_handoff=ready,
        final_plan_status=final_status,
        validation_pass=report.is_pass(),
        self_repair_used=bool(repairs_accepted),
        clarify_or_abstain_recommended=marker.is_active(),
    )

    output_payload = {
        "final_draft_plan": draft.to_dict(),
        "report": report.to_dict(),
        "audit": audit.to_dict(),
        "lva": lva.to_dict(),
        "ledger": ledger.to_dict(),
        "marker": marker.to_dict(),
        "readiness": readiness.to_dict(),
    }
    output_digest = stable_digest(output_payload, prefix="l1.02.5.output")

    packet = ValidatedPlanPacket(
        final_draft_plan=draft,
        plan_validation_report=report,
        plan_consistency_audit=audit,
        lowest_viable_agency_receipt=lva,
        self_repair_ledger=ledger,
        clarify_abstain_fallback_marker=marker,
        final_plan_readiness_receipt=readiness,
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        output_digest=output_digest,
    )

    emit_stage_spans(
        stage="02.5",
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        policy_hash_observed=input_.policy_hash_observed,
        instruction_hash_observed=input_.instruction_hash_observed,
        input_digest=stable_digest(input_.to_dict(), prefix="l1.02.5.input"),
        output_digest=output_digest,
        span_sink=span_sink,
        extra={
            "ready_for_handoff": ready,
            "passes_used": passes_used,
            "final_status": final_status,
        },
    )

    return packet
