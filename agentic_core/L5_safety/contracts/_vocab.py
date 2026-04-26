"""Controlled vocabularies pulled from L5 doctrine parent (00).

These are evidence/certification terms only. They never represent runtime
dispositions (per parent ``00_L5_Governance_Safety_detailed.md``).
"""
from __future__ import annotations

from enum import Enum


class L5CertificationStatus(str, Enum):
    """Top-level certification status set defined by the L5 parent doc."""

    L5_CERTIFIED = "L5_CERTIFIED"
    L5_NOT_CERTIFIED = "L5_NOT_CERTIFIED"
    L5_REQUIRES_RECLEARANCE = "L5_REQUIRES_RECLEARANCE"
    L5_REQUIRES_REMEDIATION_EVIDENCE = "L5_REQUIRES_REMEDIATION_EVIDENCE"
    L5_REQUIRES_HUMAN_REVIEW_PACKET = "L5_REQUIRES_HUMAN_REVIEW_PACKET"
    L5_INCIDENT_EVIDENCE_REQUIRED = "L5_INCIDENT_EVIDENCE_REQUIRED"
    L5_STATIC_VIOLATION_EVIDENCE = "L5_STATIC_VIOLATION_EVIDENCE"
    L5_AUTHORITY_GAP_EVIDENCE = "L5_AUTHORITY_GAP_EVIDENCE"
    L5_EGRESS_GAP_EVIDENCE = "L5_EGRESS_GAP_EVIDENCE"
    L5_REPLAY_AUDIT_GAP_EVIDENCE = "L5_REPLAY_AUDIT_GAP_EVIDENCE"


class L5ReasonCode(str, Enum):
    """Reason codes attached to certification results."""

    POLICY_VIOLATION_EVIDENCE = "policy_violation_evidence"
    HARD_CONSTRAINT_BREACH_EVIDENCE = "hard_constraint_breach_evidence"
    MISSING_AUTHORITY_EVIDENCE = "missing_authority_evidence"
    REGISTRY_MISMATCH_EVIDENCE = "registry_mismatch_evidence"
    ROUTE_MISMATCH_EVIDENCE = "route_mismatch_evidence"
    INJECTION_EVIDENCE = "injection_evidence"
    CONTEXT_BLEED_EVIDENCE = "context_bleed_evidence"
    CROSS_TENANT_RISK_EVIDENCE = "cross_tenant_risk_evidence"
    DATA_SENSITIVITY_RISK_EVIDENCE = "data_sensitivity_risk_evidence"
    EVIDENCE_WEAK_SIGNAL = "evidence_weak_signal"
    GROUNDEDNESS_REQUIRED_SIGNAL = "groundedness_required_signal"
    HUMAN_REVIEW_REQUIRED_SIGNAL = "human_review_required_signal"
    SANDBOX_INSUFFICIENT_EVIDENCE = "sandbox_insufficient_evidence"
    REPLAY_INCOMPLETE_EVIDENCE = "replay_incomplete_evidence"
    PROVIDER_MISMATCH_EVIDENCE = "provider_mismatch_evidence"
    TOOL_SCHEMA_MISMATCH_EVIDENCE = "tool_schema_mismatch_evidence"
    CONNECTOR_SCOPE_MISMATCH_EVIDENCE = "connector_scope_mismatch_evidence"
    BUDGET_RISK_EVIDENCE = "budget_risk_evidence"
    DRIFT_EVIDENCE = "drift_evidence"


class L5EvidenceRefKind(str, Enum):
    """Canonical evidence reference categories surfaced in certifications."""

    AUTHORITY_CONTEXT = "authority_context_evidence_ref"
    ORIGIN_TRUST = "origin_trust_evidence_ref"
    STATIC_GOVERNANCE = "static_governance_evidence_ref"
    EGRESS_CERTIFICATION = "egress_certification_evidence_ref"
    HUMAN_RECLEARANCE = "human_reclearance_evidence_ref"
    REPLAY_AUDIT = "replay_audit_evidence_ref"
    CERTIFICATION_GAP = "certification_gap_evidence_ref"


# Forbidden runtime-disposition tokens that L5 contracts must never emit.
FORBIDDEN_RUNTIME_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "ALLOW",
        "DENY",
        "CLARIFY",
        "ABSTAIN",
        "REROUTE",
        "SHRINK_SCOPE",
        "RETRY",
        "HEAL",
        "ESCALATE_HITL",
        "QUARANTINE",
        "REDACT",
        "SAFE_FALLBACK",
        "MARK_DEGRADED",
        "COMMIT_REQUEST",
        "BLOCK_COMMIT",
        "ALLOW_FINISH",
        "downstream_disposition",
        "allow_l2_execution",
        "allow_model_call",
        "allow_tool_call",
        "allow_connector_call",
        "require_HITL",
        "require_UWG_commit_review",
        "incident_lockdown",
    }
)


__all__ = [
    "L5CertificationStatus",
    "L5ReasonCode",
    "L5EvidenceRefKind",
    "FORBIDDEN_RUNTIME_DISPOSITIONS",
]
