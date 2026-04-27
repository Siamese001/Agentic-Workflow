"""L5 Runtime Certification Binding (00A.8) — G1 closure.

Implements the runtime binding contract that L2 E1 receives, E2 verifies,
Exit consumes for HITL re-clearance, and UWG requires for durable mutation
admission. Emits L5-plane evidence only — never a Runtime-Gate disposition.

Doctrine: ``docs/reference/00A_L5_Governance_Safety/00A.8_L5_Runtime_Certification_Binding.md``
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from agentic_core.L5_safety.v5.types import (
    DecisionVerdict,
    MatchStatus,
    ReasonCode,
)


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sorted_strings(values: tuple[str, ...]) -> list[str]:
    return sorted(values)


# =============================================================================
# 00A.8 §3.1 — L5CertificationEvidenceRefSet (11 evidence refs)
# =============================================================================


@dataclass(frozen=True)
class L5CertificationEvidenceRefSet:
    """11 evidence refs that downstream layers can dereference for forensic review."""

    policy_ref: str
    blueprint_ref: str
    registry_ref: str
    authority_context_ref: str
    capability_scope_ref: str
    sandbox_scope_ref: str
    origin_trust_ref: str
    egress_cert_ref: str
    hitl_reclearance_ref: str
    replay_audit_ref: str
    static_governance_ref: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "authority_context_ref": self.authority_context_ref,
            "blueprint_ref": self.blueprint_ref,
            "capability_scope_ref": self.capability_scope_ref,
            "egress_cert_ref": self.egress_cert_ref,
            "hitl_reclearance_ref": self.hitl_reclearance_ref,
            "origin_trust_ref": self.origin_trust_ref,
            "policy_ref": self.policy_ref,
            "registry_ref": self.registry_ref,
            "replay_audit_ref": self.replay_audit_ref,
            "sandbox_scope_ref": self.sandbox_scope_ref,
            "static_governance_ref": self.static_governance_ref,
        }


# =============================================================================
# 00A.8 §3.2 — L5RuntimeCertificationBinding (20 fields)
# =============================================================================


@dataclass(frozen=True)
class L5RuntimeCertificationBinding:
    """20-field runtime certification binding emitted alongside `GovernanceResult`.

    L2 E1 receives this; E2 verifies presence + hash match against active
    snapshot; Exit may require it for HITL-modified packets; UWG may require
    it for durable mutation admission.
    """

    binding_id: str
    request_id: str
    run_id: str
    trace_root: str
    route_contract_ref: str
    packet_ref: str
    policy_hash: str
    blueprint_hash: str
    registry_digest_set: tuple[str, ...]
    principal_ref: str
    capability_token_ref: str
    sandbox_envelope_ref: str
    origin_trust_manifest_ref: str
    egress_cert_ref: str
    replay_envelope_ref: str
    audit_manifest_ref: str
    certification_scope: str
    certification_status: str  # L5_CERTIFIED | L5_NOT_CERTIFIED | L5_REQUIRES_RECLEARANCE | ...
    evidence_refs: L5CertificationEvidenceRefSet
    deterministic_digest: str = ""

    def __post_init__(self) -> None:
        if not self.binding_id:
            raise ValueError("L5RuntimeCertificationBinding: binding_id required")
        if not self.policy_hash:
            raise ValueError(
                "L5RuntimeCertificationBinding: policy_hash required "
                "(00A.8 §4 — L2 E1 must receive policy/blueprint/registry refs)",
            )
        if not self.blueprint_hash:
            raise ValueError(
                "L5RuntimeCertificationBinding: blueprint_hash required",
            )
        if not self.registry_digest_set:
            raise ValueError(
                "L5RuntimeCertificationBinding: registry_digest_set required",
            )
        # Compute deterministic digest if absent
        if not self.deterministic_digest:
            payload = _canonical_json(
                {
                    "binding_id": self.binding_id,
                    "policy_hash": self.policy_hash,
                    "blueprint_hash": self.blueprint_hash,
                    "registry_digest_set": _sorted_strings(self.registry_digest_set),
                    "capability_token_ref": self.capability_token_ref,
                    "sandbox_envelope_ref": self.sandbox_envelope_ref,
                    "replay_envelope_ref": self.replay_envelope_ref,
                    "certification_status": self.certification_status,
                }
            )
            object.__setattr__(self, "deterministic_digest", _sha256_hex(payload))

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_manifest_ref": self.audit_manifest_ref,
            "binding_id": self.binding_id,
            "blueprint_hash": self.blueprint_hash,
            "capability_token_ref": self.capability_token_ref,
            "certification_scope": self.certification_scope,
            "certification_status": self.certification_status,
            "deterministic_digest": self.deterministic_digest,
            "egress_cert_ref": self.egress_cert_ref,
            "evidence_refs": self.evidence_refs.to_dict(),
            "origin_trust_manifest_ref": self.origin_trust_manifest_ref,
            "packet_ref": self.packet_ref,
            "policy_hash": self.policy_hash,
            "principal_ref": self.principal_ref,
            "registry_digest_set": _sorted_strings(self.registry_digest_set),
            "replay_envelope_ref": self.replay_envelope_ref,
            "request_id": self.request_id,
            "route_contract_ref": self.route_contract_ref,
            "run_id": self.run_id,
            "sandbox_envelope_ref": self.sandbox_envelope_ref,
            "trace_root": self.trace_root,
        }


# =============================================================================
# 00A.8 §3.3 — L5SnapshotVerificationReceipt (12 fields)
# =============================================================================


@dataclass(frozen=True)
class L5SnapshotVerificationReceipt:
    """Detects policy/blueprint/registry drift between binding and active snapshot."""

    snapshot_receipt_id: str
    active_policy_hash: str
    packet_policy_hash: str
    active_blueprint_hash: str
    packet_blueprint_hash: str
    active_registry_digest_set: tuple[str, ...]
    packet_registry_digest_set: tuple[str, ...]
    replay_snapshot_ref: str
    live_snapshot_ref: str
    match_status: MatchStatus
    mismatch_reason_codes: tuple[ReasonCode, ...]
    severity: str  # info | warn | critical
    generated_at: str

    def __post_init__(self) -> None:
        if self.severity not in {"info", "warn", "critical"}:
            raise ValueError(
                f"L5SnapshotVerificationReceipt: severity must be info|warn|critical, "
                f"got {self.severity!r}",
            )
        if self.match_status == MatchStatus.MISMATCH and not self.mismatch_reason_codes:
            raise ValueError(
                "L5SnapshotVerificationReceipt: MISMATCH requires non-empty "
                "mismatch_reason_codes",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_blueprint_hash": self.active_blueprint_hash,
            "active_policy_hash": self.active_policy_hash,
            "active_registry_digest_set": _sorted_strings(self.active_registry_digest_set),
            "generated_at": self.generated_at,
            "live_snapshot_ref": self.live_snapshot_ref,
            "match_status": self.match_status.value,
            "mismatch_reason_codes": sorted(c.value for c in self.mismatch_reason_codes),
            "packet_blueprint_hash": self.packet_blueprint_hash,
            "packet_policy_hash": self.packet_policy_hash,
            "packet_registry_digest_set": _sorted_strings(self.packet_registry_digest_set),
            "replay_snapshot_ref": self.replay_snapshot_ref,
            "severity": self.severity,
            "snapshot_receipt_id": self.snapshot_receipt_id,
        }


# =============================================================================
# 00A.8 §3.4 — L5ReclearanceBinding (HITL-modified packets)
# =============================================================================


@dataclass(frozen=True)
class L5ReclearanceBinding:
    """Re-clearance binding for human-modified packets (00A.8 §4 — Exit gate)."""

    binding_id: str
    original_binding_ref: str
    human_modification_diff_ref: str
    human_review_packet_ref: str
    reclearance_status: str  # CLEARED | REJECTED | REQUIRES_RE_REVIEW
    reclearance_evidence_refs: tuple[str, ...]
    re_certified_at: str

    def __post_init__(self) -> None:
        if self.reclearance_status not in {"CLEARED", "REJECTED", "REQUIRES_RE_REVIEW"}:
            raise ValueError(
                f"L5ReclearanceBinding: reclearance_status must be "
                f"CLEARED|REJECTED|REQUIRES_RE_REVIEW, got {self.reclearance_status!r}",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "binding_id": self.binding_id,
            "human_modification_diff_ref": self.human_modification_diff_ref,
            "human_review_packet_ref": self.human_review_packet_ref,
            "original_binding_ref": self.original_binding_ref,
            "re_certified_at": self.re_certified_at,
            "reclearance_evidence_refs": _sorted_strings(self.reclearance_evidence_refs),
            "reclearance_status": self.reclearance_status,
        }


# =============================================================================
# Helpers — build binding from GovernanceResult; verify snapshot
# =============================================================================


def emit_runtime_binding(
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
    route_contract_ref: str,
    packet_ref: str,
    policy_hash: str,
    blueprint_hash: str,
    registry_digest_set: tuple[str, ...],
    principal_ref: str,
    capability_token_ref: str,
    sandbox_envelope_ref: str,
    origin_trust_manifest_ref: str,
    replay_envelope_ref: str,
    audit_manifest_ref: str,
    certification_scope: str,
    certification_status: str,
    egress_cert_ref: str = "",
    hitl_reclearance_ref: str = "",
    static_governance_ref: str = "",
    authority_context_ref: str = "",
) -> L5RuntimeCertificationBinding:
    """Build a runtime binding from already-resolved evidence references.

    L5 governance plane is the only emitter; downstream layers consume but
    never construct.
    """

    binding_id = _sha256_hex(f"{request_id}|{run_id}|{trace_root}|{certification_scope}")[:16]
    evidence_refs = L5CertificationEvidenceRefSet(
        policy_ref=policy_hash,
        blueprint_ref=blueprint_hash,
        registry_ref=",".join(sorted(registry_digest_set)),
        authority_context_ref=authority_context_ref,
        capability_scope_ref=capability_token_ref,
        sandbox_scope_ref=sandbox_envelope_ref,
        origin_trust_ref=origin_trust_manifest_ref,
        egress_cert_ref=egress_cert_ref,
        hitl_reclearance_ref=hitl_reclearance_ref,
        replay_audit_ref=replay_envelope_ref,
        static_governance_ref=static_governance_ref,
    )
    return L5RuntimeCertificationBinding(
        binding_id=binding_id,
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        route_contract_ref=route_contract_ref,
        packet_ref=packet_ref,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        registry_digest_set=registry_digest_set,
        principal_ref=principal_ref,
        capability_token_ref=capability_token_ref,
        sandbox_envelope_ref=sandbox_envelope_ref,
        origin_trust_manifest_ref=origin_trust_manifest_ref,
        egress_cert_ref=egress_cert_ref,
        replay_envelope_ref=replay_envelope_ref,
        audit_manifest_ref=audit_manifest_ref,
        certification_scope=certification_scope,
        certification_status=certification_status,
        evidence_refs=evidence_refs,
    )


def verify_snapshot(
    *,
    binding: L5RuntimeCertificationBinding,
    active_policy_hash: str,
    active_blueprint_hash: str,
    active_registry_digest_set: tuple[str, ...],
    snapshot_receipt_id: str,
    replay_snapshot_ref: str = "",
    live_snapshot_ref: str = "",
    generated_at: str = "",
) -> L5SnapshotVerificationReceipt:
    """Compare binding's pinned hashes against active snapshot.

    `MatchStatus.REPLAY_APPROVED` is reserved for an explicit upstream
    replay-grant and is not produced by this function (callers may construct
    that variant directly when reconstructing a historical run).
    """

    mismatch: list[ReasonCode] = []
    if binding.policy_hash != active_policy_hash:
        mismatch.append(ReasonCode.POLICY_VIOLATION)
    if binding.blueprint_hash != active_blueprint_hash:
        mismatch.append(ReasonCode.POLICY_VIOLATION)
    if set(binding.registry_digest_set) != set(active_registry_digest_set):
        mismatch.append(ReasonCode.REGISTRY_MISMATCH)

    if mismatch:
        match_status = MatchStatus.MISMATCH
        severity = "critical"
    else:
        match_status = MatchStatus.MATCH
        severity = "info"

    return L5SnapshotVerificationReceipt(
        snapshot_receipt_id=snapshot_receipt_id,
        active_policy_hash=active_policy_hash,
        packet_policy_hash=binding.policy_hash,
        active_blueprint_hash=active_blueprint_hash,
        packet_blueprint_hash=binding.blueprint_hash,
        active_registry_digest_set=active_registry_digest_set,
        packet_registry_digest_set=binding.registry_digest_set,
        replay_snapshot_ref=replay_snapshot_ref,
        live_snapshot_ref=live_snapshot_ref,
        match_status=match_status,
        mismatch_reason_codes=tuple(mismatch),
        severity=severity,
        generated_at=generated_at,
    )


__all__ = [
    "L5CertificationEvidenceRefSet",
    "L5ReclearanceBinding",
    "L5RuntimeCertificationBinding",
    "L5SnapshotVerificationReceipt",
    "emit_runtime_binding",
    "verify_snapshot",
]
