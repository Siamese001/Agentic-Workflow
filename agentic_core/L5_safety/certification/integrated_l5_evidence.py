"""Integrated-runtime L5 certification evidence (00A parent pack).

Emits ``runtime_certification_binding.json`` and ``l5_hitl_reclearance.json``
for W2 integrated-runtime chains. Evidence-only — no runtime dispositions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.L5_safety.certification.l5_parent_vocab import (
    internal_cert_status_to_parent,
)
from agentic_core.L5_safety.v5.runtime_binding import (
    L5ReclearanceBinding,
    emit_runtime_binding,
)


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_runtime_certification_binding_payload(
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
    policy_hash: str,
    blueprint_hash: str,
    registry_digest_set: tuple[str, ...] | list[str],
    route_contract_ref: str = "",
    packet_ref: str = "",
    capability_token_id: str = "",
    origin_trust_class: str = "TRUSTED_RUNTIME",
    certification_scope: str = "integrated_runtime",
    certification_status: str = "L5_CERTIFIED",
    principal_ref: str = "",
    sandbox_envelope_ref: str = "",
    replay_envelope_ref: str = "",
    audit_manifest_ref: str = "",
    egress_cert_ref: str = "",
    hitl_reclearance_ref: str = "",
    static_governance_ref: str = "",
    authority_context_ref: str = "",
) -> dict[str, Any]:
    """Build parent-aligned ``RuntimeCertificationBinding`` JSON for integrated runs."""

    reg = tuple(sorted(registry_digest_set))
    binding = emit_runtime_binding(
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        route_contract_ref=route_contract_ref or f"route:{run_id}",
        packet_ref=packet_ref or f"packet:{request_id}",
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        registry_digest_set=reg,
        principal_ref=principal_ref or f"principal:{request_id}",
        capability_token_ref=capability_token_id or f"capability:{request_id}",
        sandbox_envelope_ref=sandbox_envelope_ref or f"sandbox:{request_id}",
        origin_trust_manifest_ref=f"origin_trust:{origin_trust_class}",
        replay_envelope_ref=replay_envelope_ref or f"replay:{run_id}",
        audit_manifest_ref=audit_manifest_ref or f"audit:{run_id}",
        certification_scope=certification_scope,
        certification_status=certification_status,
        egress_cert_ref=egress_cert_ref,
        hitl_reclearance_ref=hitl_reclearance_ref,
        static_governance_ref=static_governance_ref,
        authority_context_ref=authority_context_ref,
    )
    payload = binding.to_dict()
    payload["req_id"] = "REQ-L5-RUNTIME-BIND-001"
    payload["capability_token_id"] = capability_token_id or binding.capability_token_ref
    payload["origin_trust_class"] = origin_trust_class
    payload["cert_status"] = internal_cert_status_to_parent(certification_status)
    payload["registry_digest_set"] = list(reg)
    return payload


@dataclass(frozen=True, slots=True)
class L5HITLReclearanceResult:
    """Parent 00A §5 ``L5HITLReclearanceResult`` shape (evidence-only)."""

    req_id: str
    request_id: str
    run_id: str
    cert_status: str
    human_response_hash: str
    human_text_treated_as_data: bool
    reclearance_binding: dict[str, Any]
    replay_key: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "req_id": self.req_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "cert_status": self.cert_status,
            "human_response_hash": self.human_response_hash,
            "human_text_treated_as_data": self.human_text_treated_as_data,
            "reclearance_binding": self.reclearance_binding,
            "replay_key": self.replay_key,
        }


def build_hitl_reclearance_not_applicable(
    *,
    request_id: str,
    run_id: str,
    replay_key: str = "",
    reason_code: str = "HITL_NOT_REQUIRED_FOR_ROUTE",
) -> dict[str, Any]:
    """Emit NA HITL reclearance certification when route does not require human input."""

    binding = L5ReclearanceBinding(
        binding_id=_sha256_hex(f"{request_id}|{run_id}|hitl-na")[:16],
        original_binding_ref=f"binding:{run_id}",
        human_modification_diff_ref="",
        human_review_packet_ref="",
        reclearance_status="REQUIRES_RE_REVIEW",
        reclearance_evidence_refs=(reason_code,),
        re_certified_at="",
    )
    result = L5HITLReclearanceResult(
        req_id="REQ-L5-HITL-RECLEAR-001",
        request_id=request_id,
        run_id=run_id,
        cert_status="not_certified",
        human_response_hash="",
        human_text_treated_as_data=True,
        reclearance_binding=binding.to_dict(),
        replay_key=replay_key,
    )
    out = result.to_dict()
    out["not_applicable"] = True
    out["reason_codes"] = [reason_code]
    return out


def build_hitl_reclearance_cleared(
    *,
    request_id: str,
    run_id: str,
    human_response_hash: str,
    human_review_packet_ref: str,
    original_binding_ref: str,
    human_modification_diff_ref: str = "",
    replay_key: str = "",
    re_certified_at: str = "",
) -> dict[str, Any]:
    """Emit cleared HITL reclearance certification (Exit may resume)."""

    binding = L5ReclearanceBinding(
        binding_id=_sha256_hex(f"{request_id}|{run_id}|hitl-cleared")[:16],
        original_binding_ref=original_binding_ref,
        human_modification_diff_ref=human_modification_diff_ref,
        human_review_packet_ref=human_review_packet_ref,
        reclearance_status="CLEARED",
        reclearance_evidence_refs=(human_review_packet_ref,),
        re_certified_at=re_certified_at,
    )
    result = L5HITLReclearanceResult(
        req_id="REQ-L5-HITL-RECLEAR-001",
        request_id=request_id,
        run_id=run_id,
        cert_status="certified",
        human_response_hash=human_response_hash,
        human_text_treated_as_data=True,
        reclearance_binding=binding.to_dict(),
        replay_key=replay_key,
    )
    return result.to_dict()


def binding_payload_from_identity(
    identity: Mapping[str, Any],
    *,
    certification_status: str = "L5_CERTIFIED",
    origin_trust_class: str = "TRUSTED_RUNTIME",
) -> dict[str, Any]:
    """Convenience: build binding JSON from ``runtime_identity_envelope`` dict."""

    reg = identity.get("registry_digest_set") or []
    if isinstance(reg, dict):
        reg = list(reg.values())
    return build_runtime_certification_binding_payload(
        request_id=str(identity["request_id"]),
        run_id=str(identity.get("run_id") or identity["request_id"]),
        trace_root=str(identity.get("trace_root") or identity["request_id"]),
        policy_hash=str(identity.get("policy_hash") or "no-policy"),
        blueprint_hash=str(identity.get("blueprint_hash") or "no-blueprint"),
        registry_digest_set=tuple(reg) if reg else ("registry:none",),
        route_contract_ref=str(identity.get("route_contract_id") or ""),
        replay_envelope_ref=str(identity.get("replay_key") or ""),
        origin_trust_class=origin_trust_class,
        certification_status=certification_status,
    )
