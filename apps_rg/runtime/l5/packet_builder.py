"""apps_rg L5CertificationPacket builder and sealed-artifact attachment."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from agentic_core.L5_safety.certification.l5_packet_producer import L5PacketProducer
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
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


@dataclass(frozen=True, slots=True)
class L5CertificationBuildResult:
    packet: L5CertificationPacket
    packet_ref: str
    packet_digest: str
    status: str


def _getattr_str(value: Any, name: str) -> str:
    return str(getattr(value, name, "") or "")


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

    del fec
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

    child_receipts = build_child_certifier_receipts(
        profile=active_profile,
        run_context=ctx,
        egress_occurred=bool(egress_tuple),
        egress_certified=bool(egress_tuple) and all(r.certified for r in egress_tuple),
    )

    producer = L5PacketProducer()
    common = dict(
        certified_object_ref=(
            f"urn:apps-rg:l5:sealed:{_getattr_str(sealed, 'compilation_hash')}"
            if sealed is not None
            else f"urn:apps-rg:l5:run:{ctx.get('run_id', '')}"
        ),
        policy_ref=str(active_profile.section("safety_enforcement").get("policy_ref") or ""),
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
            active_profile.section("static_governance").get(
                "structure_blueprint_ref"
            )
            or ""
        ),
        runtime_ref=str(
            active_profile.section("runtime_certification").get(
                "cert_route_registry_ref"
            )
            or ""
        ),
        producer_ref="apps_rg.runtime.l5.packet_builder:v1",
        certifier_version="apps_rg_l5_runtime_certification.v1",
        run_id=str(ctx.get("run_id") or ""),
        trace_id=str(ctx.get("trace_id") or ""),
    )

    first_packet = producer.produce_packet(
        child_receipts=child_receipts,
        egress_receipts=egress_tuple,
        **common,
    )
    context_digest = first_packet.l5_governance_context_digest
    final_children = stamp_child_receipt_context(
        child_receipts,
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
    )


def attach_l5_packet_to_sealed(
    sealed: Any,
    result: L5CertificationBuildResult,
) -> Any:
    """Attach packet refs to a sealed L2 artifact without using gate refs."""

    egress_receipts = tuple(result.packet.egress_receipts)
    values = {
        "l5_certification_packet_ref": result.packet_ref,
        "l5_certification_packet_digest": result.packet_digest,
        "l5_certification_status": result.status,
        "l5_egress_receipts": egress_receipts,
        "l5_egress_receipt_refs": tuple(receipt_ref(r) for r in egress_receipts),
        "l5_egress_receipt_digests": tuple(receipt_digest(r) for r in egress_receipts),
    }
    try:
        for name, value in values.items():
            object.__setattr__(sealed, name, value)
        return sealed
    except (AttributeError, TypeError):
        return replace(sealed, **values)


def is_valid_l5_packet_digest(value: str) -> bool:
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value)


__all__ = [
    "L5CertificationBuildResult",
    "L5_PACKET_REF_PREFIX",
    "PLACEHOLDER_TEST_L5_CERT_REF",
    "attach_l5_packet_to_sealed",
    "build_l5_certification_packet",
    "is_valid_l5_packet_digest",
]
