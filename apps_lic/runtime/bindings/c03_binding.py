"""C0.3 sender proof binding for apps_lic canonical outreach."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_lic.engines.message_type_requirement_gate import (
    STATUS_REQUIREMENTS_PASS,
    MessageRequirementGateResult,
    evaluate_message_requirements_from_store,
)
from apps_lic.engines.message_intelligence_packet import (
    MessageIntelligencePacket,
    build_message_intelligence_packet,
)
from apps_lic.engines.recipient_classification import (
    STATUS_DERIVED as RECIPIENT_CLASS_DERIVED,
    derive_recipient_class_from_store,
)
from apps_lic.engines.sender_proof_graph import (
    STATUS_PROOF_GRAPH_READY,
    SenderProofGraphPacket,
    build_pa_sender_proof_envelope,
    build_sender_proof_graph_packet_from_store,
)
from apps_lic.engines.whole_message_generation import LengthBudget, resolve_length_budget
from apps_lic.runtime.bindings.c0_binding import (
    c0_readiness_store_from_validated_request,
    c0_recipient_class_status_from_fec,
    c0_recipient_class_value_from_fec,
)


APPS_LIC_C03_CERT_REF = "c03-apps-lic-sender-proof-graph-w3a-4c9d2a"
C03_STATUS_READY = "C03_READY"
C03_STATUS_BLOCKED = "C03_BLOCKED"
C03_MESSAGE_TYPE_INPUT_KEY = "message_type_hint"
C03_MESSAGE_MODIFIERS_INPUT_KEY = "message_modifiers"
C03_APPLICATION_STATUS_INPUT_KEY = "application_status"
C03_DESIRED_NEXT_STEP_INPUT_KEY = "desired_next_step"


@dataclass(frozen=True)
class C03SenderProofResult:
    request_id: str
    run_id: str
    app_id: str
    trace_id: str
    recipient_class: str
    message_gate_result: MessageRequirementGateResult
    sender_proof_packet: SenderProofGraphPacket
    pa_sender_proof_envelope: Mapping[str, Any]
    length_budget: LengthBudget
    message_intelligence_packet: MessageIntelligencePacket
    source_snapshot_ids: tuple[str, ...]
    l5_certification_ref: str = APPS_LIC_C03_CERT_REF

    @property
    def ready(self) -> bool:
        return (
            self.message_gate_result.status == STATUS_REQUIREMENTS_PASS
            and self.sender_proof_packet.status == STATUS_PROOF_GRAPH_READY
            and self.sender_proof_packet.ready
            and self.message_intelligence_packet.ready
        )

    @property
    def status(self) -> str:
        return C03_STATUS_READY if self.ready else C03_STATUS_BLOCKED

    @property
    def proof_packet_id(self) -> str:
        return self.sender_proof_packet.proof_packet_id

    @property
    def blocking_reasons(self) -> tuple[str, ...]:
        reasons: list[str] = []
        if self.message_gate_result.status != STATUS_REQUIREMENTS_PASS:
            reasons.extend(self.message_gate_result.missing_fields)
        if self.sender_proof_packet.status != STATUS_PROOF_GRAPH_READY:
            reasons.extend(self.sender_proof_packet.reason_codes)
        if not self.message_intelligence_packet.ready:
            reasons.extend(self.message_intelligence_packet.blocking_reasons)
        return tuple(dict.fromkeys(str(reason) for reason in reasons if str(reason)))

    def to_receipt_payload(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.c03_runtime_binding.v1",
            "status": self.status,
            "ready": self.ready,
            "recipient_class": self.recipient_class,
            "message_type": self.message_gate_result.message_type,
            "message_requirement_gate": self.message_gate_result.to_packet(),
            "sender_proof_packet": self.sender_proof_packet.to_packet(),
            "pa_sender_proof_envelope": dict(self.pa_sender_proof_envelope),
            "proof_packet_id": self.proof_packet_id,
            "allowed_claim_ids": list(self.sender_proof_packet.proof_ids),
            "length_budget": self.length_budget.to_packet(),
            "message_intelligence_packet": self.message_intelligence_packet.to_packet(),
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "blocking_reasons": list(self.blocking_reasons),
            "l5_certification_ref": self.l5_certification_ref,
        }


def _personalization_inputs(validated_request: ValidatedRequest) -> Mapping[str, Any]:
    app_payload = validated_request.app_payload or {}
    inputs = (app_payload.get("personalization") or {}).get("inputs") or {}
    return inputs if isinstance(inputs, Mapping) else {}


def _campaign(validated_request: ValidatedRequest) -> Mapping[str, Any]:
    app_payload = validated_request.app_payload or {}
    campaign = app_payload.get("campaign") or {}
    return campaign if isinstance(campaign, Mapping) else {}


def _routing_policy(validated_request: ValidatedRequest) -> Mapping[str, Any]:
    app_payload = validated_request.app_payload or {}
    routing_policy = app_payload.get("routing_policy") or {}
    return routing_policy if isinstance(routing_policy, Mapping) else {}


def _effective_channel(validated_request: ValidatedRequest) -> str:
    inputs = _personalization_inputs(validated_request)
    envelope = inputs.get("linkedin_route_envelope")
    if isinstance(envelope, Mapping) and str(envelope.get("channel") or "").strip():
        return str(envelope.get("channel") or "").strip()
    return str(_campaign(validated_request).get("channel") or "linkedin")


def _coerce_modifiers(value: Any) -> Mapping[str, bool] | None:
    if not isinstance(value, Mapping):
        return None
    return {str(key): bool(val) for key, val in value.items()}


def _intent_text(
    *,
    l1_plan: L1PlanContract,
    validated_request: ValidatedRequest,
) -> str:
    inputs = _personalization_inputs(validated_request)
    campaign = _campaign(validated_request)
    return " ".join(
        str(part or "").strip()
        for part in (
            l1_plan.query_spec.get("campaign_objective", ""),
            campaign.get("audience_segment", ""),
            inputs.get("manual_brief", ""),
        )
        if str(part or "").strip()
    )


def _company_context(validated_request: ValidatedRequest) -> str:
    app_payload = validated_request.app_payload or {}
    entity_refs = app_payload.get("entity_refs") or {}
    company_profile = entity_refs.get("company_profile") or {}
    if isinstance(company_profile, Mapping):
        return " ".join(
            str(part or "").strip()
            for part in (
                company_profile.get("company_name", ""),
                company_profile.get("industry", ""),
                company_profile.get("recent_news_summary", ""),
            )
            if str(part or "").strip()
        )
    return ""


def build_c03_sender_proof_for_pa(
    *,
    route: RouteContract,
    l1_plan: L1PlanContract,
    fec: FinalEvidenceContract,
    validated_request: ValidatedRequest,
) -> C03SenderProofResult:
    store, documents = c0_readiness_store_from_validated_request(
        route=route,
        validated_request=validated_request,
    )
    inputs = _personalization_inputs(validated_request)
    lead_profile = (
        (validated_request.app_payload or {}).get("entity_refs") or {}
    ).get("lead_profile") or {}
    u0_hint = str(lead_profile.get("seniority_class") or "")
    recipient_derivation = derive_recipient_class_from_store(
        store,
        u0_recipient_class_hint=u0_hint,
    )

    c0_class = c0_recipient_class_value_from_fec(fec)
    c0_status = c0_recipient_class_status_from_fec(fec)
    if (
        c0_status == RECIPIENT_CLASS_DERIVED
        and recipient_derivation.derived_recipient_class != c0_class
    ):
        raise ValueError(
            "C0.3 recipient-class derivation mismatch with C0 FEC: "
            f"fec={c0_class!r} c03={recipient_derivation.derived_recipient_class!r}"
        )

    message_type_hint = str(
        inputs.get(C03_MESSAGE_TYPE_INPUT_KEY)
        or inputs.get("message_type")
        or ""
    )
    message_gate = evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=recipient_derivation,
        intent_text=_intent_text(l1_plan=l1_plan, validated_request=validated_request),
        message_type_hint=message_type_hint,
        explicit_modifiers=_coerce_modifiers(
            inputs.get(C03_MESSAGE_MODIFIERS_INPUT_KEY)
        ),
        application_status=str(inputs.get(C03_APPLICATION_STATUS_INPUT_KEY) or ""),
    )
    proof_packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=recipient_derivation,
        message_gate_result=message_gate,
        campaign_objective=str(l1_plan.query_spec.get("campaign_objective", "") or ""),
        company_context=_company_context(validated_request),
        desired_next_step=str(inputs.get(C03_DESIRED_NEXT_STEP_INPUT_KEY) or ""),
    )
    envelope = build_pa_sender_proof_envelope(proof_packet) if proof_packet.ready else {}
    length_budget = resolve_length_budget(
        recipient_class=recipient_derivation.derived_recipient_class,
        message_type=message_gate.message_type,
        modifiers=message_gate.modifiers,
        channel=_effective_channel(validated_request),
    )
    target_context = {}
    jd_fields = {}
    for doc in documents:
        metadata = dict(doc.metadata)
        if doc.namespace == "apps_lic_contact_facts":
            target_context.setdefault("name", str(metadata.get("name") or ""))
            target_context.setdefault("title", str(metadata.get("title") or ""))
            target_context.setdefault("company", str(metadata.get("company") or ""))
        elif doc.namespace == "apps_lic_company_facts":
            target_context.setdefault("company", str(metadata.get("company") or ""))
            target_context.setdefault("company_context", doc.fact_text)
        elif doc.namespace == "apps_lic_company_trigger_facts":
            target_context.setdefault(
                "company_trigger",
                str(metadata.get("trigger_text") or doc.fact_text),
            )
        elif doc.namespace == "apps_lic_role_ownership_facts":
            target_context.setdefault(
                "role_ownership_signal",
                str(metadata.get("ownership_signal") or doc.fact_text),
            )
        elif doc.namespace == "apps_lic_jd_facts":
            for key in ("position_name", "job_title", "requisition_number", "company", "role_family"):
                value = str(metadata.get(key) or "").strip()
                if value:
                    jd_fields.setdefault(key, value)
            if "company" in jd_fields:
                target_context.setdefault("company", jd_fields["company"])
    message_intelligence_packet = build_message_intelligence_packet(
        recipient_class=recipient_derivation.derived_recipient_class,
        message_type=message_gate.message_type,
        channel=_effective_channel(validated_request),
        outreach_mode=str(_routing_policy(validated_request).get("outreach_mode") or "cold"),
        opportunity_documents=documents,
        target_context=target_context,
        jd_fields=jd_fields,
        proof_packet=proof_packet,
        campaign_objective=str(l1_plan.query_spec.get("campaign_objective", "") or ""),
        desired_next_step=str(inputs.get(C03_DESIRED_NEXT_STEP_INPUT_KEY) or ""),
    )
    source_snapshot_ids = tuple(
        dict.fromkeys(
            (
                *(doc.source_snapshot_id for doc in documents),
                *message_gate.source_snapshot_ids,
                *proof_packet.source_snapshot_ids,
                *message_intelligence_packet.source_refs,
            )
        )
    )
    return C03SenderProofResult(
        request_id=route.request_id,
        run_id=route.run_id,
        app_id=route.app_id,
        trace_id=route.trace_id,
        recipient_class=recipient_derivation.derived_recipient_class,
        message_gate_result=message_gate,
        sender_proof_packet=proof_packet,
        pa_sender_proof_envelope=envelope,
        length_budget=length_budget,
        message_intelligence_packet=message_intelligence_packet,
        source_snapshot_ids=source_snapshot_ids,
    )


def c03_ready_for_pa(c03: C03SenderProofResult) -> bool:
    return c03.ready


__all__ = [
    "APPS_LIC_C03_CERT_REF",
    "C03_APPLICATION_STATUS_INPUT_KEY",
    "C03_DESIRED_NEXT_STEP_INPUT_KEY",
    "C03_MESSAGE_MODIFIERS_INPUT_KEY",
    "C03_MESSAGE_TYPE_INPUT_KEY",
    "C03_STATUS_BLOCKED",
    "C03_STATUS_READY",
    "C03SenderProofResult",
    "build_c03_sender_proof_for_pa",
    "c03_ready_for_pa",
]
