"""U0 ingress validator binding for the apps_lic 'outreach_message' task class.

U0 is the FIRST stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit
pipeline. Its job is to:

    1. Accept an AppsLicRequestEnvelope from the apps_lic CLI/runner.
    2. Synthesize a raw JSON dict from the envelope (bridge until apps_lic/
       __main__.py emits the contract dict directly).
    3. Run apps_lic_u0_adapt over that dict — validates schema, enforces all
       E1-E9 exit conditions, walks every JSON Pointer through the field-map
       SSOT, fails closed on any silently_dropped or unknown_mappings.
    4. Return a ValidatedRequest carrying:
         - app_payload: full apps_lic domain payload
         - reflection_receipt: proof of pointer coverage (AppsLicU0ReflectionReceipt)
         - authority_validation_receipt: governance + Pydantic pass receipt
         - audit_refs += "reflection:<input_digest_prefix16>"

Pattern: pure function. No state. No I/O beyond the adapter's deterministic
field-map load. No provider calls. No L1/L0/C0/PA/L2/Exit calls.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W3)
"""
from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone

from agentic_core.runtime.contracts.apps_lic_ingress_payload import AppsLicRequestEnvelope
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.u0.apps_lic_u0_adapter import (
    AppsLicU0AdapterError,
    AppsLicU0ReflectionReceipt,
    apps_lic_u0_adapt,
)


APPS_LIC_TASK_CLASS: str = "outreach_message"
APPS_LIC_U0_CERT_REF: str = "u0-apps-lic-outreach-message-reflection-f3c2e1"


def _envelope_to_raw_json(envelope: AppsLicRequestEnvelope) -> dict:
    """Convert an AppsLicRequestEnvelope to the raw JSON dict expected by the adapter.

    Bridge function — maps the flat dataclass fields to the nested contract
    sections (transport, campaign, entity_refs, …) that AppsLicIngressContractV1
    expects. Once apps_lic/__main__.py is updated to emit the contract directly,
    this synthesizer can be replaced by a direct pass-through.
    """
    payload = envelope.payload
    return {
        "apps_lic_contract_version": "v1",
        "transport": {
            "app_id": payload.app_id,
            "task_class": payload.task_class,
            "request_id": envelope.request_id or "",
            "run_id": envelope.run_id or "",
            "tenant_id": envelope.tenant_id or payload.app_id,
            "trace_id": envelope.trace_id or "",
            "submitted_at": envelope.submitted_at or datetime.now(timezone.utc).isoformat(),
        },
        "campaign": {
            "request_type": payload.request_type,
            "campaign_objective": payload.campaign_objective or "outreach_draft",
            "channel": payload.channel,
            "audience_segment": payload.audience_segment,
            "action_required": payload.action_required,
            "workflow_required": payload.workflow_required,
            "grounding_required": payload.grounding_required,
            "side_effect_class": payload.side_effect_class,
        },
        "forbidden_send_modes": {
            "modes": list(payload.forbidden_send_modes),
        },
        "entity_refs": {
            "lead_profile": dict(payload.lead_profile) if payload.lead_profile else None,
            "lead_ref": payload.lead_ref,
            "sender_profile": dict(payload.sender_profile) if payload.sender_profile else None,
            "sender_ref": payload.sender_ref,
            "company_profile": dict(payload.company_profile) if payload.company_profile else None,
            "company_ref": payload.company_ref,
        },
        "personalization": {
            "inputs": dict(payload.personalization_inputs),
        },
        "generation_hints": dict(payload.generation_hints),
        "tone_constraints": dict(payload.tone_constraints),
        "output_format": dict(payload.required_output_format),
        "research_requirements": dict(payload.research_requirements),
        "routing_policy": dict(payload.routing_policy),
        "validation_policy": dict(payload.validation_policy),
        "gate_decision_policy": {
            **dict(payload.gate_decision_policy),
            # Ensure the governance default is present if caller omitted it
            "halt_on_validation_failure": payload.gate_decision_policy.get(
                "halt_on_validation_failure", True
            ),
        },
        "qa_report": dict(payload.qa_report_requirement),
        "integration_target": payload.integration_target,
        "hitl_policy": dict(payload.hitl_policy),
        "pii_policy": {
            "pii_detection_mode": "strict",
            "redact_on_warn": True,
            "fail_on_pii_detect": True,
            **dict(payload.pii_policy),
        },
        "governance_shield": {
            "shield_required": True,
            **dict(payload.governance_shield_policy),
        },
        "antipattern_policy": {
            "enabled": True,
            **dict(payload.antipattern_policy),
        },
        "source_lineage": {
            "source_lineage_required": True,
            **dict(payload.source_lineage_requirements),
        },
        "ab_test": {
            "ab_test_profile": payload.ab_test_profile,
            "learning_profile_ref": payload.learning_profile_ref,
        },
        "replay_audit": {
            "idempotency_key": payload.idempotency_key,
            "replay_refs": list(payload.replay_refs),
            "audit_refs": list(payload.audit_refs),
        },
        "payload_digest": payload.payload_digest,
    }


def u0_validate_apps_lic(envelope: AppsLicRequestEnvelope) -> ValidatedRequest:
    """Validate an AppsLicRequestEnvelope and produce a ValidatedRequest.

    Pipeline:
        1. Synthesize AppsLicIngressContractV1 JSON from envelope.
        2. Run apps_lic_u0_adapt — schema + E1-E9 + reflection + governance.
        3. Thread audit_ref into the returned ValidatedRequest.
        4. Return the merged ValidatedRequest.

    Args:
        envelope: The AppsLicRequestEnvelope produced by apps_lic CLI/runner.

    Returns:
        ValidatedRequest carrying:
          - app_payload (full apps_lic domain content)
          - reflection_receipt (AppsLicU0ReflectionReceipt, proof of coverage)
          - authority_validation_receipt
          - audit_refs += "lic_reflection:<digest_prefix>"
          - l5_certification_ref = APPS_LIC_U0_CERT_REF

    Raises:
        AppsLicU0AdapterError (and subclasses): fail-closed — must not proceed past U0.
        TypeError: if envelope is not an AppsLicRequestEnvelope.
    """
    if not isinstance(envelope, AppsLicRequestEnvelope):
        raise TypeError(
            f"u0_validate_apps_lic expected AppsLicRequestEnvelope, "
            f"got {type(envelope).__name__}"
        )

    contract_json = _envelope_to_raw_json(envelope)

    validated_request, reflection_receipt = apps_lic_u0_adapt(
        contract_json,
        request_id=envelope.request_id or None,
        run_id=envelope.run_id or None,
    )

    digest_prefix = reflection_receipt.input_payload_digest[:16]
    merged_audit_refs: tuple[str, ...] = (
        *validated_request.audit_refs,
        f"lic_reflection:{digest_prefix}",
    )

    return replace(
        validated_request,
        audit_refs=merged_audit_refs,
        l5_certification_ref=APPS_LIC_U0_CERT_REF,
    )


__all__ = [
    "APPS_LIC_TASK_CLASS",
    "APPS_LIC_U0_CERT_REF",
    "u0_validate_apps_lic",
]
