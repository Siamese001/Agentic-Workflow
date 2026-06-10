"""W5 validation Exit binding for canonical apps_lic outreach."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Iterable, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_lic.engines.recipient_classification import derive_recipient_class_from_store
from apps_lic.engines.validation_exit import (
    EXIT_CLEAR_DRAFT,
    ExitProofBundle,
    X1DJudgeResult,
    run_validation_exit,
)
from apps_lic.engines.whole_message_generation import (
    WholeMessageCandidate,
    WholeMessageGenerationRequest,
    build_whole_message_generation_request,
)
from apps_lic.engines.x1d_judge_feedback_regeneration import (
    RepairRunner,
    X1DFeedbackRegenerationResult,
    run_x1d_judge_feedback_regeneration,
)
from apps_lic.runtime.bindings.c0_binding import (
    c0_readiness_store_from_validated_request,
)
from apps_lic.runtime.bindings.c03_binding import (
    C03_APPLICATION_STATUS_INPUT_KEY,
    C03_DESIRED_NEXT_STEP_INPUT_KEY,
    C03SenderProofResult,
)
from apps_lic.runtime.bindings.w4_candidate_batch_binding import W4CandidateBatchResult


APPS_LIC_W5_CERT_REF = "w5-apps-lic-validation-exit-wireup-4c9d2a"


@dataclass(frozen=True)
class W5ValidationExitResult:
    request_id: str
    run_id: str
    app_id: str
    trace_id: str
    status: str
    disposition: str
    request: WholeMessageGenerationRequest
    exit_proof_bundle: ExitProofBundle
    selected_candidate_id: str
    final_selected_candidate: Mapping[str, Any] | None = None
    x1d_regeneration: X1DFeedbackRegenerationResult | None = None
    l5_certification_ref: str = APPS_LIC_W5_CERT_REF

    @property
    def clear(self) -> bool:
        return self.disposition == EXIT_CLEAR_DRAFT and self.exit_proof_bundle.x2_result.passed

    def to_receipt_payload(self) -> dict[str, Any]:
        proof = self.exit_proof_bundle
        regeneration_packet = (
            self.x1d_regeneration.to_packet() if self.x1d_regeneration else {}
        )
        return {
            "schema_version": "apps_lic.w5_validation_exit_result.v1",
            "status": self.status,
            "disposition": self.disposition,
            "clear": self.clear,
            "selected_candidate_id": self.selected_candidate_id,
            "final_user_visible_draft_id": proof.final_user_visible_draft_id,
            "final_selected_candidate": dict(self.final_selected_candidate or {}),
            "exit_reason": proof.exit_reason,
            "review_required_reason": proof.review_required_reason,
            "proof_packet_id": proof.proof_packet_id,
            "prompt_contract_id": proof.prompt_contract_id,
            "no_send_receipt": proof.no_send_receipt,
            "no_durable_write_receipt": self.request.no_durable_write_receipt,
            "instruction_data_boundary_receipt": self.request.instruction_data_boundary_receipt,
            "generation_request": self.request.to_packet(),
            "exit_proof_bundle": proof.to_packet(),
            "x2_status": proof.x2_result.status,
            "x2_failed_gate_ids": list(proof.x2_result.failed_gate_ids),
            "x2_reason_codes": list(proof.x2_result.reason_codes),
            "x1d_status": proof.x1d_result.status,
            "x1d_required_depth": proof.x1d_result.required_depth,
            "x1d_required_judge_ids": [
                profile.judge_id for profile in proof.x1d_result.required_profiles
            ],
            "x1d_missing_judge_ids": list(proof.x1d_result.missing_judge_ids),
            "x1d_reason_codes": list(proof.x1d_result.reason_codes),
            "x1d_judge_result_count": len(proof.x1d_result.judge_results),
            "x1d_regeneration_attempted": bool(
                self.x1d_regeneration and self.x1d_regeneration.attempted
            ),
            "x1d_regeneration_iteration_count": (
                self.x1d_regeneration.iteration_count if self.x1d_regeneration else 0
            ),
            "x1d_regeneration_stop_reason": (
                self.x1d_regeneration.stop_reason if self.x1d_regeneration else ""
            ),
            "x1d_repair_effective": bool(
                regeneration_packet.get("x1d_repair_effective", False)
            ),
            "x1d_repair_resolved_issue_ids": list(
                regeneration_packet.get("x1d_repair_resolved_issue_ids", [])
            ),
            "x1d_repair_unresolved_issue_ids": list(
                regeneration_packet.get("x1d_repair_unresolved_issue_ids", [])
            ),
            "repair_candidate_sanitization_passed": bool(
                regeneration_packet.get("repair_candidate_sanitization_passed", False)
            ),
            "x1d_regeneration": regeneration_packet,
            "l5_certification_ref": self.l5_certification_ref,
        }


def _app_payload(validated_request: ValidatedRequest) -> Mapping[str, Any]:
    payload = validated_request.app_payload or {}
    return payload if isinstance(payload, Mapping) else {}


def _personalization_inputs(validated_request: ValidatedRequest) -> Mapping[str, Any]:
    inputs = (_app_payload(validated_request).get("personalization") or {}).get("inputs") or {}
    return inputs if isinstance(inputs, Mapping) else {}


def _candidate_packet_by_id(
    batch: WholeMessageCandidateBatch,
    candidate_id: str,
) -> dict[str, Any]:
    for candidate in batch.candidates:
        if candidate.candidate_id == candidate_id:
            return candidate.to_packet()
    return {}


def _final_selected_candidate_packet(
    batch: WholeMessageCandidateBatch,
    regeneration: X1DFeedbackRegenerationResult,
) -> dict[str, Any]:
    selected_id = str(regeneration.final_selected_candidate_id or "")
    for attempt in reversed(regeneration.attempts):
        if attempt.repaired_candidate_id == selected_id:
            return dict(attempt.repaired_candidate)
    return _candidate_packet_by_id(batch, selected_id)


def _campaign(validated_request: ValidatedRequest) -> Mapping[str, Any]:
    campaign = _app_payload(validated_request).get("campaign") or {}
    return campaign if isinstance(campaign, Mapping) else {}


def _routing_policy(validated_request: ValidatedRequest) -> Mapping[str, Any]:
    routing = _app_payload(validated_request).get("routing_policy") or {}
    return routing if isinstance(routing, Mapping) else {}


def _effective_channel(validated_request: ValidatedRequest) -> str:
    inputs = _personalization_inputs(validated_request)
    envelope = inputs.get("linkedin_route_envelope")
    if isinstance(envelope, Mapping) and str(envelope.get("channel") or "").strip():
        return str(envelope.get("channel") or "").strip()
    return str(_campaign(validated_request).get("channel") or "linkedin")


def _lead_profile(validated_request: ValidatedRequest) -> Mapping[str, Any]:
    lead = (_app_payload(validated_request).get("entity_refs") or {}).get("lead_profile") or {}
    return lead if isinstance(lead, Mapping) else {}


def _build_w5_generation_request(
    *,
    route: RouteContract,
    l1_plan: L1PlanContract,
    validated_request: ValidatedRequest,
    c03: C03SenderProofResult,
    w4: W4CandidateBatchResult,
) -> WholeMessageGenerationRequest:
    store, documents = c0_readiness_store_from_validated_request(
        route=route,
        validated_request=validated_request,
    )
    recipient_derivation = derive_recipient_class_from_store(
        store,
        u0_recipient_class_hint=str(_lead_profile(validated_request).get("seniority_class") or ""),
    )
    inputs = _personalization_inputs(validated_request)
    campaign = _campaign(validated_request)
    request = build_whole_message_generation_request(
        recipient_derivation=recipient_derivation,
        message_gate_result=c03.message_gate_result,
        sender_proof_packet=c03.sender_proof_packet,
        opportunity_documents=documents,
        request_id=route.request_id,
        trace_root=route.trace_id,
        channel=_effective_channel(validated_request),
        outreach_mode=str(_routing_policy(validated_request).get("outreach_mode") or "cold"),
        send_mode="draft_only",
        campaign_objective=str(
            l1_plan.query_spec.get("campaign_objective")
            or campaign.get("campaign_objective")
            or ""
        ),
        desired_next_step=str(inputs.get(C03_DESIRED_NEXT_STEP_INPUT_KEY) or ""),
    )
    component_hash_map = {
        **dict(request.component_hash_map),
        "c03_sender_proof_packet": c03.proof_packet_id,
        "w4_candidate_batch": w4.proof_packet_id,
    }
    return replace(
        request,
        prompt_contract_id=w4.batch.prompt_contract_id,
        component_hash_map=component_hash_map,
    )


def materialize_w5_validation_exit(
    *,
    route: RouteContract,
    l1_plan: L1PlanContract,
    fec: FinalEvidenceContract,
    validated_request: ValidatedRequest,
    c03: C03SenderProofResult,
    w4: W4CandidateBatchResult,
    judge_results: Iterable[X1DJudgeResult] = (),
    x1d_judge_runner: Callable[
        [WholeMessageGenerationRequest, WholeMessageCandidate],
        Iterable[X1DJudgeResult],
    ]
    | None = None,
    x1d_repair_runner: RepairRunner | None = None,
    x1d_repair_max_iterations: int | None = None,
) -> W5ValidationExitResult:
    """Run app-owned X2/X1D validation Exit against the W4 candidate batch."""
    _ = fec
    request = _build_w5_generation_request(
        route=route,
        l1_plan=l1_plan,
        validated_request=validated_request,
        c03=c03,
        w4=w4,
    )
    inputs = _personalization_inputs(validated_request)
    proof = run_validation_exit(
        request,
        w4.batch,
        selected_candidate_id=w4.selected_candidate_id,
        judge_results=tuple(judge_results),
        x1d_judge_runner=x1d_judge_runner,
        application_status=str(inputs.get(C03_APPLICATION_STATUS_INPUT_KEY) or ""),
    )
    regeneration = run_x1d_judge_feedback_regeneration(
        request=request,
        batch=w4.batch,
        selected_candidate_id=w4.selected_candidate_id,
        initial_proof=proof,
        x1d_judge_runner=x1d_judge_runner,
        repair_runner=x1d_repair_runner,
        application_status=str(inputs.get(C03_APPLICATION_STATUS_INPUT_KEY) or ""),
        max_iterations=x1d_repair_max_iterations,
    )
    proof = regeneration.final_proof
    return W5ValidationExitResult(
        request_id=route.request_id,
        run_id=route.run_id,
        app_id=route.app_id,
        trace_id=route.trace_id,
        status=proof.status,
        disposition=proof.disposition,
        request=request,
        exit_proof_bundle=proof,
        selected_candidate_id=regeneration.final_selected_candidate_id,
        final_selected_candidate=_final_selected_candidate_packet(w4.batch, regeneration),
        x1d_regeneration=regeneration,
    )


def w5_validation_exit_clear(result: W5ValidationExitResult) -> bool:
    return result.clear


__all__ = [
    "APPS_LIC_W5_CERT_REF",
    "W5ValidationExitResult",
    "materialize_w5_validation_exit",
    "w5_validation_exit_clear",
]
