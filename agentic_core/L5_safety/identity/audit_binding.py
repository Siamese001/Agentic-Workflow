"""Audit Emission Principal Binding — L5 v4 G-04 W5.

Produces a forensic-grade audit record that binds a `CapabilityTokenV4Artifact`
(and its PrincipalChain) to the write-side and egress-side envelopes
emitted earlier in the run. Result: every audit row can be reconstructed
back to a specific `invoking_user` per SAIF Principle 3.

This module is the **minimum viable** replay_envelope binding:
- It does NOT replace the existing `safety_audit_emitter.py` at
  `agentic_core/L5_safety/audit/`. That emitter keeps running unchanged.
- It adds an additive wrapper that v4-aware call sites use to emit a
  replay-envelope-compatible record with full identity attribution.
- The full `replay_envelope` schema lives in
  `docs/reference/00_L5_Policy_Plane/calibration_assurance_planes.md §4.2`.
  This module emits the subset needed for W5 (principal + v4 token fields +
  the W2/W3 envelopes); extending to the full schema is W6-next work.

Reference:
  - docs/reference/00_L5_Policy_Plane/calibration_assurance_planes.md §4
  - docs/contracts/identity_propagation.md §6 (Forensic Reconstruction)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.interfaces.principal_aware_egress import PrincipalEgressEnvelope
from agentic_core.interfaces.principal_aware_write import PrincipalAttachedWrite
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.principal_verifier import (
    VerificationResult,
    principal_attribution,
)


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class PrincipalAuditRecord:
    """Immutable audit row emitted at end-of-action by a v4-compliant caller.

    One row per certified action. Linked by token_id to all other records
    (write envelopes, egress envelopes, verification results) so the
    forensic replayer can reassemble the full decision path from any single
    identifier.

    Invariants:
      - `token_v4_trace_id` is the canonical key.
      - `attribution` is derived from `principal_attribution(token)` at
        emission time; re-deriving on replay must produce byte-identical JSON.
      - `audit_digest` is SHA-256 over the canonical payload excluding itself.
    """

    token_v4_trace_id: str
    token_v3_trace_id: str
    policy_version: str
    registry_digest: str
    attribution: dict[str, Any]
    verification: dict[str, Any]
    writes: tuple[dict[str, Any], ...]
    egresses: tuple[dict[str, Any], ...]
    audit_digest: str

    def __post_init__(self) -> None:
        if not self.token_v4_trace_id:
            raise ValueError("PrincipalAuditRecord: token_v4_trace_id required")
        if not self.token_v3_trace_id:
            raise ValueError("PrincipalAuditRecord: token_v3_trace_id required")
        if not self.audit_digest:
            raise ValueError("PrincipalAuditRecord: audit_digest required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "attribution": self.attribution,
            "audit_digest": self.audit_digest,
            "egresses": list(self.egresses),
            "policy_version": self.policy_version,
            "registry_digest": self.registry_digest,
            "token_v3_trace_id": self.token_v3_trace_id,
            "token_v4_trace_id": self.token_v4_trace_id,
            "verification": self.verification,
            "writes": list(self.writes),
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_dict())


def emit_principal_audit_record(
    *,
    token: CapabilityTokenV4Artifact,
    verification: VerificationResult,
    writes: tuple[PrincipalAttachedWrite, ...] = (),
    egresses: tuple[PrincipalEgressEnvelope, ...] = (),
) -> PrincipalAuditRecord:
    """Produce a PrincipalAuditRecord for forensic replay_envelope inclusion.

    All inputs are carried verbatim into the record. The audit_digest binds
    them together: any mutation on replay (e.g., dropped write envelope,
    changed verification verdict) yields a different digest and is caught
    by the independent verifier (calibration_assurance_planes.md §4.4).
    """
    attribution = principal_attribution(token)
    verification_dict = verification.to_dict()
    write_dicts = tuple(w.to_dict() for w in writes)
    egress_dicts = tuple(e.to_dict() for e in egresses)

    pre_payload = {
        "attribution": attribution,
        "egresses": list(egress_dicts),
        "policy_version": token.policy_version,
        "registry_digest": token.registry_digest,
        "token_v3_trace_id": token.v3_artifact.trace_id,
        "token_v4_trace_id": token.v4_trace_id,
        "verification": verification_dict,
        "writes": list(write_dicts),
    }
    audit_digest = hashlib.sha256(
        _canonical_json(pre_payload).encode("utf-8"),
    ).hexdigest()

    return PrincipalAuditRecord(
        token_v4_trace_id=token.v4_trace_id,
        token_v3_trace_id=token.v3_artifact.trace_id,
        policy_version=token.policy_version,
        registry_digest=token.registry_digest,
        attribution=attribution,
        verification=verification_dict,
        writes=write_dicts,
        egresses=egress_dicts,
        audit_digest=audit_digest,
    )


def reconstruct_audit_digest(record_dict: dict[str, Any]) -> str:
    """Independent-verifier helper: recompute the digest from a serialized record.

    The independent replay verifier in the Audit/Forensic Plane reads a
    serialized PrincipalAuditRecord from disk, recomputes the digest over
    the non-digest payload, and compares. Divergence = forensic alert.
    """
    pre_payload = {k: v for k, v in record_dict.items() if k != "audit_digest"}
    return hashlib.sha256(
        _canonical_json(pre_payload).encode("utf-8"),
    ).hexdigest()


__all__ = [
    "PrincipalAuditRecord",
    "emit_principal_audit_record",
    "reconstruct_audit_digest",
]
