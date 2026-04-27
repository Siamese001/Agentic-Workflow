"""L5 Certification Evidence — sealed L5_NOT_CERTIFIED record on mismatch.

Maps to: docs/reference/00A_L5_Governance_Safety/00A.7a_L5_Governance_Context_Invariant.md
Phase 6 SEALED L5_NOT_CERTIFIED EVIDENCE.

Contains:
  - `L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID` constant
  - `ParticipatingDigests` frozen dataclass
  - `L5CertificationEvidence` frozen dataclass (sealed record body)

This module is pure data. The gate raises `L5GovernanceContextMismatchError`
which carries an `L5CertificationEvidence` instance.
"""

from __future__ import annotations

from dataclasses import dataclass

L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID: str = "L5_GOVERNANCE_CONTEXT_MISMATCH"


@dataclass(frozen=True, slots=True)
class ParticipatingDigests:
    """Snapshot of every per-child digest seen during the compare step.

    Each field is the hex digest emitted by the corresponding 00A child,
    or "" when that child has not yet emitted (or is not applicable).
    """

    safety_enforcement_digest: str
    authority_binding_digest: str
    origin_trust_digest: str
    hitl_reclearance_digest: str
    egress_certification_digest: str
    replay_audit_digest: str
    static_governance_digest: str
    aggregate_governance_digest: str  # "" until aggregator emits

    def to_dict(self) -> dict[str, str]:
        return {
            "safety_enforcement_digest": self.safety_enforcement_digest,
            "authority_binding_digest": self.authority_binding_digest,
            "origin_trust_digest": self.origin_trust_digest,
            "hitl_reclearance_digest": self.hitl_reclearance_digest,
            "egress_certification_digest": self.egress_certification_digest,
            "replay_audit_digest": self.replay_audit_digest,
            "static_governance_digest": self.static_governance_digest,
            "aggregate_governance_digest": self.aggregate_governance_digest,
        }


@dataclass(frozen=True, slots=True)
class L5CertificationEvidence:
    """Sealed certification evidence — fail-closed on cross-child mismatch.

    Every field is what 00A.7a Phase 6 requires the sealed
    L5_NOT_CERTIFIED record to include.
    """

    decisive_rule_id: str  # = L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID
    certified: bool  # always False for evidence emitted on mismatch
    certification_scope: str  # "AGGREGATE"
    first_mismatched_field: str
    participating_digests: ParticipatingDigests
    trace_id: str
    request_id: str
    run_id: str
    route_id: str
    step_id: str
    tenant_id: str
    principal_id: str
    sealed_evidence_id: str
    reason: str
    downstream_recommendation: str  # "deny"
    dispatch_target: str  # "EXIT_CONTROL"

    def to_dict(self) -> dict[str, object]:
        return {
            "decisive_rule_id": self.decisive_rule_id,
            "certified": self.certified,
            "certification_scope": self.certification_scope,
            "first_mismatched_field": self.first_mismatched_field,
            "participating_digests": self.participating_digests.to_dict(),
            "trace_id": self.trace_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "route_id": self.route_id,
            "step_id": self.step_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "sealed_evidence_id": self.sealed_evidence_id,
            "reason": self.reason,
            "downstream_recommendation": self.downstream_recommendation,
            "dispatch_target": self.dispatch_target,
        }


class L5GovernanceContextMismatchError(Exception):
    """Raised by the L5 governance consistency gate on any INV-L5C-* violation.

    Upstream pipelines catch this and seal an L5_NOT_CERTIFIED record with
    terminal_class = L5_GOVERNANCE_CONTEXT_MISMATCH.
    """

    def __init__(self, evidence: L5CertificationEvidence) -> None:
        super().__init__(
            f"{evidence.decisive_rule_id}: {evidence.reason} "
            f"first_mismatched_field={evidence.first_mismatched_field!r} "
            f"trace_id={evidence.trace_id!r}"
        )
        self.evidence = evidence


__all__ = [
    "L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID",
    "L5CertificationEvidence",
    "L5GovernanceContextMismatchError",
    "ParticipatingDigests",
]
