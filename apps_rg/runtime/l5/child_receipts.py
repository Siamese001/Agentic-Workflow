"""apps_rg child certifier receipt materialization for L5 packets."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Any, Mapping

from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    ChildCertifierReceipt,
)

from apps_rg.runtime.l5.governance_profile import AppsRgL5GovernanceProfile
from apps_rg.runtime.l5.hitl_reclearance import (
    detect_human_modification_flags,
    validate_recleared_hitl_packet,
)

REQUIRED_CHILD_DOMAIN_TO_PROFILE_SECTION: Mapping[str, str] = {
    "safety_enforcement": "safety_enforcement",
    "authority_context_registry_binding": "authority_context",
    "origin_trust_content_boundary": "origin_trust",
    "replay_audit_certification_evidence": "replay_audit",
    "static_governance_structure_drift": "static_governance",
    "runtime_certification_binding": "runtime_certification",
}


def _sha256_hex(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _receipt(
    *,
    domain: str,
    profile: AppsRgL5GovernanceProfile,
    section_name: str,
    run_context: Mapping[str, Any],
    certified: bool,
    reason_codes: tuple[str, ...] = (),
    evidence_ref: str = "",
) -> ChildCertifierReceipt:
    section = profile.section(section_name)
    return ChildCertifierReceipt(
        domain=domain,
        applicability="REQUIRED",
        certified=certified,
        evidence_digest=_sha256_hex(
            {
                "profile_digest": profile.profile_digest,
                "section": section_name,
                "section_payload": section,
                "run_refs": {
                    "request_id": run_context.get("request_id", ""),
                    "run_id": run_context.get("run_id", ""),
                    "trace_id": run_context.get("trace_id", ""),
                    "replay_key": run_context.get("replay_key", ""),
                },
            }
        ),
        evidence_ref=evidence_ref or f"{profile.profile_ref}#{section_name}",
        reason_codes=reason_codes,
    )


def _required_receipt_for_domain(
    *,
    domain: str,
    section_name: str,
    profile: AppsRgL5GovernanceProfile,
    run_context: Mapping[str, Any],
) -> ChildCertifierReceipt:
    if section_name in profile.missing_sections:
        return _receipt(
            domain=domain,
            profile=profile,
            section_name=section_name,
            run_context=run_context,
            certified=False,
            reason_codes=(f"missing_profile_section:{section_name}",),
        )

    if domain == "replay_audit_certification_evidence" and not str(
        run_context.get("replay_key") or ""
    ).strip():
        return _receipt(
            domain=domain,
            profile=profile,
            section_name=section_name,
            run_context=run_context,
            certified=False,
            reason_codes=("missing_replay_key",),
            evidence_ref=str(profile.section(section_name).get("replay_manifest_ref") or ""),
        )

    if domain == "runtime_certification_binding":
        l5_ref = str(run_context.get("l5_certification_ref") or "").strip()
        allow_test = bool(run_context.get("allow_test_l5_cert_ref"))
        if l5_ref == "test:valid:w6" and not allow_test:
            return _receipt(
                domain=domain,
                profile=profile,
                section_name=section_name,
                run_context=run_context,
                certified=False,
                reason_codes=("placeholder_l5_cert_ref_rejected",),
            )

    return _receipt(
        domain=domain,
        profile=profile,
        section_name=section_name,
        run_context=run_context,
        certified=True,
    )


def _hitl_receipt(
    *,
    profile: AppsRgL5GovernanceProfile,
    run_context: Mapping[str, Any],
) -> ChildCertifierReceipt:
    posture = profile.section("hitl_posture")
    human_mod_enabled = bool(posture.get("human_modification_enabled", False))
    human_modified = detect_human_modification_flags(run_context)

    if not human_mod_enabled and not human_modified:
        return ChildCertifierReceipt(
            domain="hitl_reclearance",
            applicability="NOT_APPLICABLE",
            certified=False,
            evidence_digest=_sha256_hex(
                {"profile_digest": profile.profile_digest, "hitl_posture": posture}
            ),
            evidence_ref=f"{profile.profile_ref}#hitl_posture",
            not_applicable_reason="human_modification_enabled=false",
            deciding_policy_ref=str(posture.get("hitl_policy_ref") or ""),
            deciding_stage="apps_rg_l5_child_receipt_materialization",
        )

    recleared = run_context.get("recleared_hitl_packet")
    ok, reasons = validate_recleared_hitl_packet(recleared)
    return ChildCertifierReceipt(
        domain="hitl_reclearance",
        applicability="REQUIRED",
        certified=ok,
        evidence_digest=_sha256_hex(
            {
                "profile_digest": profile.profile_digest,
                "hitl_posture": posture,
                "recleared_hitl_packet": recleared or {},
            }
        ),
        evidence_ref=str(
            (recleared or {}).get("packet_ref") if isinstance(recleared, Mapping) else ""
        ),
        reason_codes=reasons,
    )


def _egress_child_receipt(
    *,
    profile: AppsRgL5GovernanceProfile,
    egress_occurred: bool,
    egress_certified: bool,
) -> ChildCertifierReceipt:
    section = profile.section("provider_egress")
    if not egress_occurred:
        return ChildCertifierReceipt(
            domain="egress_provider_governance",
            applicability="NOT_APPLICABLE",
            certified=False,
            evidence_digest=_sha256_hex(
                {"profile_digest": profile.profile_digest, "provider_egress": section}
            ),
            evidence_ref=f"{profile.profile_ref}#provider_egress",
            not_applicable_reason="no provider call occurred",
            deciding_policy_ref=str(section.get("provider_policy_ref") or ""),
            deciding_stage="apps_rg_l5_child_receipt_materialization",
        )
    return ChildCertifierReceipt(
        domain="egress_provider_governance",
        applicability="REQUIRED",
        certified=egress_certified,
        evidence_digest=_sha256_hex(
            {
                "profile_digest": profile.profile_digest,
                "provider_egress": section,
                "egress_certified": egress_certified,
            }
        ),
        evidence_ref=str(section.get("egress_certifier_lane") or ""),
        reason_codes=() if egress_certified else ("egress_receipt_missing_or_uncertified",),
    )


def build_child_certifier_receipts(
    *,
    profile: AppsRgL5GovernanceProfile,
    run_context: Mapping[str, Any],
    egress_occurred: bool = False,
    egress_certified: bool = False,
) -> tuple[ChildCertifierReceipt, ...]:
    """Build the required apps_rg child certifier receipts for one run."""

    receipts: list[ChildCertifierReceipt] = [
        _required_receipt_for_domain(
            domain=domain,
            section_name=section,
            profile=profile,
            run_context=run_context,
        )
        for domain, section in REQUIRED_CHILD_DOMAIN_TO_PROFILE_SECTION.items()
    ]
    receipts.append(_hitl_receipt(profile=profile, run_context=run_context))
    receipts.append(
        _egress_child_receipt(
            profile=profile,
            egress_occurred=egress_occurred,
            egress_certified=egress_certified,
        )
    )
    return tuple(receipts)


def stamp_child_receipt_context(
    receipts: tuple[ChildCertifierReceipt, ...],
    *,
    l5_governance_context_digest: str,
) -> tuple[ChildCertifierReceipt, ...]:
    """Attach the final packet context digest to child receipts."""

    return tuple(
        replace(receipt, l5_governance_context_digest=l5_governance_context_digest)
        for receipt in receipts
    )


__all__ = [
    "REQUIRED_CHILD_DOMAIN_TO_PROFILE_SECTION",
    "build_child_certifier_receipts",
    "stamp_child_receipt_context",
]
