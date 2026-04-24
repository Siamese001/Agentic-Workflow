"""Lane Audit Binding — L5 v4 Wave-M wire-in.

Extended audit sink that binds the full Wave-L `RuntimeLaneDecisionWithSweep`
(sweep + risk-tier + chokepoint + handoff) into a single forensic record.

Additive to Wave-W5 `emit_principal_audit_record`: that original W5 sink
keeps working unchanged for callers that only need the minimal
(token + verification + writes + egresses) record. Wave-M is the
full-fidelity sink for v4-aware call sites that want the entire lane
decision preserved for replay.

Design invariants:
- Audit digest binds: attribution + lane decision + writes + egresses +
  registry_digest + policy_version. ANY mutation = different digest.
- Fields sorted in canonical JSON → deterministic digest across Python
  runs.
- `reconstruct_lane_audit_digest` lets the independent replay verifier
  recompute the digest off a serialized record.

Reference:
  - audit_binding.py (Wave W5 base)
  - runtime_entry_sweep.py (Wave-L source of RuntimeLaneDecisionWithSweep)
  - docs/reference/00_L5_Policy_Plane/calibration_assurance_planes.md §4
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.interfaces.principal_aware_egress import PrincipalEgressEnvelope
from agentic_core.interfaces.principal_aware_write import PrincipalAttachedWrite
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.principal_verifier import principal_attribution
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
)


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class LaneAuditRecord:
    """Full-fidelity audit row for a v4 runtime-lane invocation.

    One row per certified action. Carries every gate signal the lane
    produced so forensic replay can reassemble the decision exactly.
    """

    token_v4_trace_id: str
    token_v3_trace_id: str
    policy_version: str
    registry_digest: str
    attribution: dict[str, Any]
    lane_decision: dict[str, Any]
    writes: tuple[dict[str, Any], ...]
    egresses: tuple[dict[str, Any], ...]
    audit_digest: str

    def __post_init__(self) -> None:
        if not self.token_v4_trace_id:
            raise ValueError("LaneAuditRecord: token_v4_trace_id required")
        if not self.token_v3_trace_id:
            raise ValueError("LaneAuditRecord: token_v3_trace_id required")
        if not self.audit_digest:
            raise ValueError("LaneAuditRecord: audit_digest required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "attribution": self.attribution,
            "audit_digest": self.audit_digest,
            "egresses": list(self.egresses),
            "lane_decision": self.lane_decision,
            "policy_version": self.policy_version,
            "registry_digest": self.registry_digest,
            "token_v3_trace_id": self.token_v3_trace_id,
            "token_v4_trace_id": self.token_v4_trace_id,
            "writes": list(self.writes),
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_dict())


def emit_lane_audit_record(
    *,
    token: CapabilityTokenV4Artifact,
    lane_decision: RuntimeLaneDecisionWithSweep,
    writes: tuple[PrincipalAttachedWrite, ...] = (),
    egresses: tuple[PrincipalEgressEnvelope, ...] = (),
) -> LaneAuditRecord:
    """Produce a LaneAuditRecord from a Wave-L runtime-lane decision."""
    attribution = principal_attribution(token)
    lane_dict = lane_decision.to_dict()
    write_dicts = tuple(w.to_dict() for w in writes)
    egress_dicts = tuple(e.to_dict() for e in egresses)

    pre_payload = {
        "attribution": attribution,
        "egresses": list(egress_dicts),
        "lane_decision": lane_dict,
        "policy_version": token.policy_version,
        "registry_digest": token.registry_digest,
        "token_v3_trace_id": token.v3_artifact.trace_id,
        "token_v4_trace_id": token.v4_trace_id,
        "writes": list(write_dicts),
    }
    audit_digest = hashlib.sha256(
        _canonical_json(pre_payload).encode("utf-8"),
    ).hexdigest()

    return LaneAuditRecord(
        token_v4_trace_id=token.v4_trace_id,
        token_v3_trace_id=token.v3_artifact.trace_id,
        policy_version=token.policy_version,
        registry_digest=token.registry_digest,
        attribution=attribution,
        lane_decision=lane_dict,
        writes=write_dicts,
        egresses=egress_dicts,
        audit_digest=audit_digest,
    )


def reconstruct_lane_audit_digest(record_dict: dict[str, Any]) -> str:
    """Independent-verifier helper: recompute digest from a serialized record."""
    pre_payload = {k: v for k, v in record_dict.items() if k != "audit_digest"}
    return hashlib.sha256(
        _canonical_json(pre_payload).encode("utf-8"),
    ).hexdigest()


__all__ = [
    "LaneAuditRecord",
    "emit_lane_audit_record",
    "reconstruct_lane_audit_digest",
]
