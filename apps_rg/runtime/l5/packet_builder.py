"""apps_rg L5CertificationPacket builder, runtime binding, and verification."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from agentic_core.L5_safety.certification.l5_packet_producer import L5PacketProducer
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    ChildCertifierReceipt,
    EgressCertificationReceipt,
    L5CertificationPacket,
)

from apps_rg.runtime.l5.child_receipts import (
    build_child_certifier_receipts,
    stamp_child_receipt_context,
)
from apps_rg.runtime.l5.egress_receipts import receipt_digest, receipt_ref
from apps_rg.runtime.l5.governance_profile import (
    AppsRgL5GovernanceProfile,
    load_l5_governance_profile,
)

PLACEHOLDER_TEST_L5_CERT_REF = "test:valid:w6"
L5_PACKET_REF_PREFIX = "l5_packet:"
RUNTIME_OBJECT_BINDING_DOMAIN = "runtime_object_binding"


@dataclass(frozen=True, slots=True)
class L5CertificationBuildResult:
    packet: L5CertificationPacket
    packet_ref: str
    packet_digest: str
    status: str
    runtime_binding_digest: str


@dataclass(frozen=True, slots=True)
class L5PacketVerificationResult:
    verified: bool
    reason_codes: tuple[str, ...]
    verification_digest: str
    runtime_binding_digest: str


def _getattr_str(value: Any, name: str) -> str:
    return str(getattr(value, name, "") or "")


def _canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _is_hex64(value: str) -> bool:
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _run_context(
    *,
    sealed: Any = None,
    prompt_artifact: Any = None,
    validated_request: Any = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    ctx: dict[str, Any] = dict(extra or {})
    for field in ("request_id", "run_id", "app_id", "trace_id", "tenant_id"):
        if field not in ctx or not str(ctx.get(field) or ""):
            for src in (sealed, prompt_artifact, validated_request):
                if src is not None and _getattr_str(src, field):
                    ctx[field] = _getattr_str(src, field)
                    break
    if not str(ctx.get("replay_key") or ""):
        for src in (sealed, prompt_artifact, validated_request):
            if src is not None and _getattr_str(src, "replay_key"):
                ctx["replay_key"] = _getattr_str(src, "replay_key")
                break
    if not str(ctx.get("l5_certification_ref") or ""):
        for src in (sealed, prompt_artifact, validated_request):
            if src is not None and _getattr_str(src, "l5_certification_ref"):
                ctx["l5_certification_ref"] = _getattr_str(src, "l5_certification_ref")
                break
    return ctx


def _packet_ref(packet: L5CertificationPacket) -> str:
    return f"{L5_PACKET_REF_PREFIX}{packet.digest_sha256}"


def _runtime_binding_payload(
    *,
    sealed: Any = None,
    prompt_artifact: Any = None,
    validated_request: Any = None,
    fec: Any = None,
    run_context: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    ctx = _run_context(
        sealed=sealed,
        prompt_artifact=prompt_artifact,
        validated_request=validated_request,
        extra=run_context,
    )
    prompt_digest = _getattr_str(prompt_artifact, "compilation_hash")
    if not prompt_digest:
        prompt_digest = _getattr_str(sealed, "l5_prompt_artifact_digest")

    evidence_digest = ""
    if fec is not None:
        evidence_digest = _getattr_str(fec, "compilation_hash") or _getattr_str(
            fec, "final_evidence_digest"
        )
    if not evidence_digest:
        evidence_digest = _getattr_str(prompt_artifact, "evidence_digest")
    if not evidence_digest:
        evidence_digest = _getattr_str(sealed, "l5_evidence_contract_digest")

    return {
        "request_id": str(ctx.get("request_id") or ""),
        "run_id": str(ctx.get("run_id") or ""),
        "trace_id": str(ctx.get("trace_id") or ""),
        "replay_key": str(ctx.get("replay_key") or ""),
        "l5_certification_ref": str(ctx.get("l5_certification_ref") or ""),
        "sealed_artifact_digest": _getattr_str(sealed, "compilation_hash"),
        "prompt_artifact_digest": prompt_digest,
        "evidence_contract_digest": evidence_digest,
    }


def runtime_binding_digest(
    *,
    sealed: Any = None,
    prompt_artifact: Any = None,
    validated_request: Any = None,
    fec: Any = None,
    run_context: Mapping[str, Any] | None = None,
) -> str:
    return _canonical_digest(
        _runtime_binding_payload(
            sealed=sealed,
            prompt_artifact=prompt_artifact,
            validated_request=validated_request,
            fec=fec,
            run_context=run_context,
        )
    )


def _runtime_binding_receipt(
    *,
    sealed: Any,
    prompt_artifact: Any,
    validated_request: Any,
    fec: Any,
    run_context: Mapping[str, Any],
) -> ChildCertifierReceipt:
    payload = _runtime_binding_payload(
        sealed=sealed,
        prompt_artifact=prompt_artifact,
        validated_request=validated_request,
        fec=fec,
        run_context=run_context,
    )
    required = [
        "request_id",
        "run_id",
        "trace_id",
        "replay_key",
        "l5_certification_ref",
        "sealed_artifact_digest",
    ]
    if prompt_artifact is not None:
        required.extend(("prompt_artifact_digest", "evidence_contract_digest"))
    missing = tuple(
        f"missing_runtime_binding:{field}" for field in required if not payload[field]
    )
    return ChildCertifierReceipt(
        domain=RUNTIME_OBJECT_BINDING_DOMAIN,
        applicability="REQUIRED",
        certified=not missing,
        evidence_digest=_canonical_digest(payload),
        evidence_ref="urn:apps-rg:l5:runtime-object-binding:v1",
        reason_codes=missing,
    )


def _stamp_egress_context(
    receipts: Sequence[EgressCertificationReceipt],
    *,
    l5_governance_context_digest: str,
) -> tuple[EgressCertificationReceipt, ...]:
    return tuple(
        replace(receipt, l5_governance_context_digest=l5_governance_context_digest)
        if not receipt.l5_governance_context_digest
        else receipt
        for receipt in receipts
    )


def _expected_packet_digest(packet: L5CertificationPacket) -> str:
    # apps_rg currently emits unchained packets, so prior_packet_digest is empty.
    return _canonical_digest(
        {
            "governance_context_digest": packet.l5_governance_context_digest,
            "certification_status": packet.certification_status,
            "reason_codes": sorted(packet.reason_codes),
            "prior_packet_digest": "",
            "producer_ref": packet.producer_ref,
            "policy_ref": packet.policy_ref,
            "certifier_version": packet.certifier_version,
        }
    )


def compute_l5_packet_verification_digest(
    *,
    request_id: str,
    run_id: str,
    trace_id: str,
    packet_ref: str,
    packet_digest: str,
    status: str,
    runtime_binding_digest_value: str,
) -> str:
    return _canonical_digest(
        {
            "request_id": request_id,
            "run_id": run_id,
            "trace_id": trace_id,
            "packet_ref": packet_ref,
            "packet_digest": packet_digest,
            "status": status,
            "runtime_binding_digest": runtime_binding_digest_value,
        }
    )


def verify_l5_packet_against_runtime(
    sealed: Any,
    *,
    prompt_artifact: Any = None,
    fec: Any = None,
    allow_test_l5_cert_ref: bool = False,
    require_stored_verification: bool = False,
) -> L5PacketVerificationResult:
    reasons: list[str] = []
    packet = getattr(sealed, "l5_certification_packet", None)
    packet_ref = _getattr_str(sealed, "l5_certification_packet_ref")
    packet_digest = _getattr_str(sealed, "l5_certification_packet_digest")
    status = _getattr_str(sealed, "l5_certification_status")
    stored_binding_digest = _getattr_str(sealed, "l5_runtime_binding_digest")
    old_ref = _getattr_str(sealed, "l5_certification_ref")

    if old_ref == PLACEHOLDER_TEST_L5_CERT_REF and not allow_test_l5_cert_ref:
        reasons.append("placeholder_l5_cert_ref_rejected")
    if not isinstance(packet, L5CertificationPacket):
        reasons.append("missing_or_invalid_l5_certification_packet")
    if not _is_hex64(packet_digest):
        reasons.append("malformed_l5_certification_packet_digest")
    if packet_ref != f"{L5_PACKET_REF_PREFIX}{packet_digest}":
        reasons.append("l5_packet_ref_digest_mismatch")
    if status != "L5_CERTIFIED":
        reasons.append(f"l5_certification_status:{status or 'missing'}")

    expected_binding = runtime_binding_digest(
        sealed=sealed,
        prompt_artifact=prompt_artifact,
        fec=fec,
    )
    if not _is_hex64(stored_binding_digest):
        reasons.append("missing_or_malformed_runtime_binding_digest")
    elif stored_binding_digest != expected_binding:
        reasons.append("runtime_binding_digest_mismatch")

    if isinstance(packet, L5CertificationPacket):
        if packet.digest_sha256 != packet_digest:
            reasons.append("packet_object_digest_field_mismatch")
        if _expected_packet_digest(packet) != packet.digest_sha256:
            reasons.append("packet_integrity_digest_mismatch")
        if packet.certification_status != status:
            reasons.append("packet_status_field_mismatch")
        if packet.run_id != _getattr_str(sealed, "run_id"):
            reasons.append("packet_run_id_mismatch")
        if packet.trace_id != _getattr_str(sealed, "trace_id"):
            reasons.append("packet_trace_id_mismatch")
        context_digest = packet.l5_governance_context_digest
        if not _is_hex64(context_digest):
            reasons.append("malformed_governance_context_digest")
        if not packet.evidence_refs or packet.evidence_refs[0] != context_digest:
            reasons.append("packet_evidence_context_ref_mismatch")
        for receipt in packet.child_receipts:
            if receipt.l5_governance_context_digest != context_digest:
                reasons.append(f"child_context_digest_mismatch:{receipt.domain}")
        for receipt in packet.egress_receipts:
            if receipt.l5_governance_context_digest != context_digest:
                reasons.append(f"egress_context_digest_mismatch:{receipt.provider_ref}")
        binding_receipts = [
            receipt
            for receipt in packet.child_receipts
            if receipt.domain == RUNTIME_OBJECT_BINDING_DOMAIN
        ]
        if len(binding_receipts) != 1:
            reasons.append("runtime_object_binding_receipt_count_invalid")
        elif binding_receipts[0].evidence_digest != expected_binding:
            reasons.append("runtime_object_binding_receipt_mismatch")
        if packet.reason_codes:
            reasons.append("certified_packet_has_reason_codes")

    verification_digest = compute_l5_packet_verification_digest(
        request_id=_getattr_str(sealed, "request_id"),
        run_id=_getattr_str(sealed, "run_id"),
        trace_id=_getattr_str(sealed, "trace_id"),
        packet_ref=packet_ref,
        packet_digest=packet_digest,
        status=status,
        runtime_binding_digest_value=stored_binding_digest,
    )
    if require_stored_verification:
        if not bool(getattr(sealed, "l5_certification_verified", False)):
            reasons.append("stored_l5_verification_not_true")
        stored_verification = _getattr_str(
            sealed, "l5_certification_verification_digest"
        )
        if stored_verification != verification_digest:
            reasons.append("stored_l5_verification_digest_mismatch")

    return L5PacketVerificationResult(
        verified=not reasons,
        reason_codes=tuple(dict.fromkeys(reasons)),
        verification_digest=verification_digest,
        runtime_binding_digest=expected_binding,
    )


def build_l5_certification_packet(
    *,
    profile: AppsRgL5GovernanceProfile | None = None,
    sealed: Any = None,
    prompt_artifact: Any = None,
    validated_request: Any = None,
    fec: Any = None,
    egress_receipts: Sequence[EgressCertificationReceipt] = (),
    run_context: Mapping[str, Any] | None = None,
    allow_test_l5_cert_ref: bool = False,
) -> L5CertificationBuildResult:
    """Build exactly one evidence-only apps_rg L5CertificationPacket."""

    active_profile = profile or load_l5_governance_profile(strict=False)
    ctx = _run_context(
        sealed=sealed,
        prompt_artifact=prompt_artifact,
        validated_request=validated_request,
        extra=run_context,
    )
    ctx["allow_test_l5_cert_ref"] = allow_test_l5_cert_ref or bool(
        ctx.get("allow_test_l5_cert_ref")
    )
    if "recleared_hitl_packet" not in ctx:
        for src in (sealed, prompt_artifact, validated_request):
            if src is not None and hasattr(src, "recleared_hitl_packet"):
                ctx["recleared_hitl_packet"] = getattr(src, "recleared_hitl_packet")
                break

    egress_tuple = tuple(egress_receipts)
    if not egress_tuple and sealed is not None:
        egress_tuple = tuple(getattr(sealed, "l5_egress_receipts", ()) or ())

    child_receipts = list(
        build_child_certifier_receipts(
            profile=active_profile,
            run_context=ctx,
            egress_occurred=bool(egress_tuple),
            egress_certified=bool(egress_tuple)
            and all(r.certified for r in egress_tuple),
        )
    )
    binding_receipt = _runtime_binding_receipt(
        sealed=sealed,
        prompt_artifact=prompt_artifact,
        validated_request=validated_request,
        fec=fec,
        run_context=ctx,
    )
    child_receipts = [
        replace(
            receipt,
            certified=receipt.certified and binding_receipt.certified,
            evidence_digest=_canonical_digest(
                {
                    "profile_evidence_digest": receipt.evidence_digest,
                    "runtime_binding_digest": binding_receipt.evidence_digest,
                }
            ),
            reason_codes=tuple(
                dict.fromkeys(receipt.reason_codes + binding_receipt.reason_codes)
            ),
        )
        if receipt.domain == "runtime_certification_binding"
        else receipt
        for receipt in child_receipts
    ]
    child_receipts.append(binding_receipt)

    producer = L5PacketProducer()
    common = dict(
        certified_object_ref=(
            f"urn:apps-rg:l5:sealed:{_getattr_str(sealed, 'compilation_hash')}"
            if sealed is not None
            else f"urn:apps-rg:l5:run:{ctx.get('run_id', '')}"
        ),
        policy_ref=str(
            active_profile.section("safety_enforcement").get("policy_ref") or ""
        ),
        blueprint_ref=str(
            active_profile.section("safety_enforcement").get("blueprint_ref") or ""
        ),
        registry_ref=str(
            active_profile.section("authority_context").get("registry_ref") or ""
        ),
        authority_ref="urn:apps-rg:l5:authority-context:v1",
        replay_ref=str(
            active_profile.section("replay_audit").get("replay_manifest_ref") or ""
        ),
        audit_ref=str(
            active_profile.section("replay_audit").get("audit_manifest_ref") or ""
        ),
        static_ref=str(
            active_profile.section("static_governance").get("structure_blueprint_ref")
            or ""
        ),
        runtime_ref=str(
            active_profile.section("runtime_certification").get(
                "cert_route_registry_ref"
            )
            or ""
        ),
        producer_ref="apps_rg.runtime.l5.packet_builder:v2",
        certifier_version="apps_rg_l5_runtime_certification.v2",
        run_id=str(ctx.get("run_id") or ""),
        trace_id=str(ctx.get("trace_id") or ""),
    )

    first_packet = producer.produce_packet(
        child_receipts=tuple(child_receipts),
        egress_receipts=egress_tuple,
        **common,
    )
    context_digest = first_packet.l5_governance_context_digest
    final_children = stamp_child_receipt_context(
        tuple(child_receipts),
        l5_governance_context_digest=context_digest,
    )
    final_egress = _stamp_egress_context(
        egress_tuple,
        l5_governance_context_digest=context_digest,
    )
    final_packet = producer.produce_packet(
        child_receipts=final_children,
        egress_receipts=final_egress,
        **common,
    )
    return L5CertificationBuildResult(
        packet=final_packet,
        packet_ref=_packet_ref(final_packet),
        packet_digest=final_packet.digest_sha256,
        status=final_packet.certification_status,
        runtime_binding_digest=binding_receipt.evidence_digest,
    )


def attach_l5_packet_to_sealed(
    sealed: Any,
    result: L5CertificationBuildResult,
    *,
    prompt_artifact: Any = None,
    fec: Any = None,
) -> Any:
    """Attach the full packet and verified refs without using gate_verdict_refs."""

    egress_receipts = tuple(result.packet.egress_receipts)
    values = {
        "l5_certification_packet": result.packet,
        "l5_certification_packet_ref": result.packet_ref,
        "l5_certification_packet_digest": result.packet_digest,
        "l5_certification_status": result.status,
        "l5_runtime_binding_digest": result.runtime_binding_digest,
        "l5_prompt_artifact_digest": _getattr_str(prompt_artifact, "compilation_hash"),
        "l5_evidence_contract_digest": _getattr_str(prompt_artifact, "evidence_digest")
        or _getattr_str(fec, "final_evidence_digest")
        or _getattr_str(fec, "compilation_hash"),
        "l5_egress_receipts": egress_receipts,
        "l5_egress_receipt_refs": tuple(receipt_ref(r) for r in egress_receipts),
        "l5_egress_receipt_digests": tuple(receipt_digest(r) for r in egress_receipts),
    }
    try:
        attached = replace(sealed, **values)
    except (TypeError, ValueError):
        for name, value in values.items():
            object.__setattr__(sealed, name, value)
        attached = sealed

    verification = verify_l5_packet_against_runtime(
        attached,
        prompt_artifact=prompt_artifact,
        fec=fec,
        require_stored_verification=False,
    )
    verification_values = {
        "l5_certification_verified": verification.verified,
        "l5_certification_verification_digest": verification.verification_digest,
    }
    try:
        return replace(attached, **verification_values)
    except (TypeError, ValueError):
        for name, value in verification_values.items():
            object.__setattr__(attached, name, value)
        return attached


def is_valid_l5_packet_digest(value: str) -> bool:
    return _is_hex64(value)


__all__ = [
    "L5CertificationBuildResult",
    "L5PacketVerificationResult",
    "L5_PACKET_REF_PREFIX",
    "PLACEHOLDER_TEST_L5_CERT_REF",
    "RUNTIME_OBJECT_BINDING_DOMAIN",
    "attach_l5_packet_to_sealed",
    "build_l5_certification_packet",
    "compute_l5_packet_verification_digest",
    "is_valid_l5_packet_digest",
    "runtime_binding_digest",
    "verify_l5_packet_against_runtime",
]
