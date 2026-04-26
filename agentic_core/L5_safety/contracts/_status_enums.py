"""Generated per-status enum value sets from L5 doctrine.

Each `<x>_status = a | b | c` declaration in `docs/reference/00_L5_Policy_Plane/`
becomes a ``StrEnum`` here. The corresponding ``L5Status`` subclass in
``parent.py`` / ``enforcement.py`` / ... validates ``status_value``
against ``allowed_values`` (also exposed as a ``ClassVar``).

Re-run ``python tools/l5_contracts/generate_contracts.py`` to regenerate.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class AdrStatus(StrEnum):
    """Doctrine value set for ``adr_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    PRESENT = "present"
    MISSING = "missing"
    STALE = "stale"
    INCOMPATIBLE = "incompatible"


class AuditBindingStatus(StrEnum):
    """Doctrine value set for ``audit_binding_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    HASH_GAP = "hash_gap"
    TRACE_GAP = "trace_gap"
    RECEIPT_GAP = "receipt_gap"


class AuthorityAttemptStatus(StrEnum):
    """Doctrine value set for ``authority_attempt_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    NONE = "none"
    ATTEMPTED = "attempted"
    BLOCKED = "blocked"
    UNRESOLVED = "unresolved"


class AuthorityContextStatus(StrEnum):
    """Doctrine value set for ``authority_context_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    BOUND = "bound"
    INCOMPLETE = "incomplete"
    STALE = "stale"
    MISMATCHED = "mismatched"
    SUBSTITUTED = "substituted"
    UNAUTHORIZED = "unauthorized"


class BlueprintBindingStatus(StrEnum):
    """Doctrine value set for ``blueprint_binding_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    CURRENT = "current"
    MISSING = "missing"
    STALE = "stale"
    MISMATCHED = "mismatched"


class BypassEvidenceStatus(StrEnum):
    """Doctrine value set for ``bypass_evidence_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    NONE = "none"
    HIDDEN_EGRESS = "hidden_egress"
    DIRECT_WRITE = "direct_write"
    DIRECT_PROVIDER = "direct_provider"
    DIRECT_CONNECTOR = "direct_connector"
    DIRECT_MEMORY_MUTATION = "direct_memory_mutation"


class CapabilityScopeStatus(StrEnum):
    """Doctrine value set for ``capability_scope_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    SUFFICIENT = "sufficient"
    MISSING = "missing"
    TOO_BROAD = "too_broad"
    TOO_NARROW = "too_narrow"
    EXPIRED = "expired"
    FORGED = "forged"


class CertificationEvidenceStatus(StrEnum):
    """Doctrine value set for ``certification_evidence_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    STALE = "stale"
    MISMATCHED = "mismatched"
    NON_REPLAYABLE = "non_replayable"
    AUDIT_GAP = "audit_gap"


class CertificationScopeStatus(StrEnum):
    """Doctrine value set for ``certification_scope_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    BOUND = "bound"
    MISSING = "missing"
    WIDENED = "widened"
    STALE = "stale"
    MISMATCHED = "mismatched"


class CertificationStatus(StrEnum):
    """Doctrine value set for ``certification_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    L5_CERTIFIED = "L5_CERTIFIED"
    L5_NOT_CERTIFIED = "L5_NOT_CERTIFIED"
    L5_REQUIRES_RECLEARANCE = "L5_REQUIRES_RECLEARANCE"
    L5_REQUIRES_REMEDIATION_EVIDENCE = "L5_REQUIRES_REMEDIATION_EVIDENCE"


class ClassificationStatus(StrEnum):
    """Doctrine value set for ``classification_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    CLASSIFIED = "classified"
    UNKNOWN = "unknown"
    CONFLICT_DETECTED = "conflict_detected"
    VIOLATION_DETECTED = "violation_detected"


class ConnectorEgressStatus(StrEnum):
    """Doctrine value set for ``connector_egress_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    BOUND = "bound"
    MISSING = "missing"
    UNAUTHORIZED = "unauthorized"
    EXPIRED = "expired"
    SUBSTITUTED = "substituted"
    CREDENTIAL_GAP = "credential_gap"


class ContentBoundaryStatus(StrEnum):
    """Doctrine value set for ``content_boundary_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    INTACT = "intact"
    VIOLATED = "violated"
    UNKNOWN = "unknown"
    REQUIRES_SAFE_EXTRACTION = "requires_safe_extraction"


class CredentialScopeStatus(StrEnum):
    """Doctrine value set for ``credential_scope_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    MINIMAL = "minimal"
    MISSING = "missing"
    TOO_BROAD = "too_broad"
    EXPIRED = "expired"
    INCOMPATIBLE = "incompatible"
    EXPOSED = "exposed"


class EgressCertificationStatus(StrEnum):
    """Doctrine value set for ``egress_certification_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    CERTIFIED_EVIDENCE = "certified_evidence"
    INCOMPLETE = "incomplete"
    STALE = "stale"
    MISMATCHED = "mismatched"
    SUBSTITUTED = "substituted"
    UNAUTHORIZED = "unauthorized"


class EgressEvidenceStatus(StrEnum):
    """Doctrine value set for ``egress_evidence_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    CLEAN = "clean"
    BYPASS_DETECTED = "bypass_detected"
    SUBSTITUTION_DETECTED = "substitution_detected"
    UNSUPPORTED = "unsupported"


class EnforcementReceiptStatus(StrEnum):
    """Doctrine value set for ``enforcement_receipt_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    NON_REPLAYABLE = "non_replayable"
    AUDIT_GAP = "audit_gap"


class FallbackStatus(StrEnum):
    """Doctrine value set for ``fallback_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    NOT_REQUIRED = "not_required"
    CERTIFIED = "certified"
    UNCERTIFIED = "uncertified"
    SUBSTITUTION_DETECTED = "substitution_detected"
    RECERTIFICATION_REQUIRED = "recertification_required"


class GatewayStatus(StrEnum):
    """Doctrine value set for ``gateway_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    CERTIFIED_EVIDENCE = "certified_evidence"
    REGISTRY_GAP = "registry_gap"
    INJECTION_EVIDENCE = "injection_evidence"
    REPLAY_GAP = "replay_gap"
    AUDIT_GAP = "audit_gap"


class HashBindingStatus(StrEnum):
    """Doctrine value set for ``hash_binding_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    COMPLETE = "complete"
    MISSING_HASH = "missing_hash"
    MISMATCHED_HASH = "mismatched_hash"
    UNSEALED = "unsealed"
    TAMPER_EVIDENCE = "tamper_evidence"


class HitlAuditStatus(StrEnum):
    """Doctrine value set for ``hitl_audit_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (3 values).
    """

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    NON_REPLAYABLE = "non_replayable"


class HitlPacketStatus(StrEnum):
    """Doctrine value set for ``hitl_packet_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    FROZEN = "frozen"
    INCOMPLETE = "incomplete"
    INVALID = "invalid"
    STALE = "stale"
    MISMATCHED = "mismatched"


class HumanInputStatus(StrEnum):
    """Doctrine value set for ``human_input_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    RECEIVED = "received"
    MODIFIED = "modified"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"
    OUT_OF_SCOPE = "out_of_scope"


class HumanOriginStatus(StrEnum):
    """Doctrine value set for ``human_origin_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    LABELED = "labeled"
    UNLABELED = "unlabeled"
    MISLABELED = "mislabeled"
    REQUIRES_RECLEARANCE = "requires_reclearance"


class HumanScopeStatus(StrEnum):
    """Doctrine value set for ``human_scope_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    UNCHANGED = "unchanged"
    NARROWED = "narrowed"
    WIDENED = "widened"
    UNAUTHORIZED = "unauthorized"


class InstructionBoundaryStatus(StrEnum):
    """Doctrine value set for ``instruction_boundary_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    TRUSTED_INSTRUCTION = "trusted_instruction"
    UNTRUSTED_DATA = "untrusted_data"
    QUARANTINED = "quarantined"
    STRIPPED = "stripped"
    REJECTED_AS_AUTHORITY = "rejected_as_authority"


class MatchStatus(StrEnum):
    """Doctrine value set for ``match_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class ModelEgressStatus(StrEnum):
    """Doctrine value set for ``model_egress_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    BOUND = "bound"
    MISSING = "missing"
    UNAUTHORIZED = "unauthorized"
    SUBSTITUTED = "substituted"
    REPLAY_GAP = "replay_gap"
    AUDIT_GAP = "audit_gap"


class NetworkEgressStatus(StrEnum):
    """Doctrine value set for ``network_egress_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    BOUND = "bound"
    MISSING = "missing"
    UNAUTHORIZED_DESTINATION = "unauthorized_destination"
    BROAD_SCOPE = "broad_scope"
    CREDENTIAL_GAP = "credential_gap"


class OriginLabelStatus(StrEnum):
    """Doctrine value set for ``origin_label_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    LABELED = "labeled"
    UNLABELED = "unlabeled"
    AMBIGUOUS = "ambiguous"
    INVALID = "invalid"


class OriginManifestStatus(StrEnum):
    """Doctrine value set for ``origin_manifest_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    STALE = "stale"
    MISMATCHED = "mismatched"


class PolicyBindingStatus(StrEnum):
    """Doctrine value set for ``policy_binding_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    CURRENT = "current"
    MISSING = "missing"
    STALE = "stale"
    MISMATCHED = "mismatched"


class PolicyDriftStatus(StrEnum):
    """Doctrine value set for ``policy_drift_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    NONE = "none"
    WEAKENED = "weakened"
    STALE = "stale"
    MISSING = "missing"
    MISMATCHED = "mismatched"


class PrincipalChainStatus(StrEnum):
    """Doctrine value set for ``principal_chain_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    VALID = "valid"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"
    CROSS_PRINCIPAL_BLEED = "cross_principal_bleed"
    CROSS_TENANT_BLEED = "cross_tenant_bleed"


class ProviderLaneStatus(StrEnum):
    """Doctrine value set for ``provider_lane_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    CURRENT = "current"
    UNAVAILABLE = "unavailable"
    SUBSTITUTED = "substituted"
    INCOMPATIBLE = "incompatible"
    UNCERTIFIED_FALLBACK = "uncertified_fallback"


class QuarantineStatus(StrEnum):
    """Doctrine value set for ``quarantine_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    APPLIED = "applied"
    FAILED = "failed"


class RecertificationStatus(StrEnum):
    """Doctrine value set for ``recertification_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (2 values).
    """

    NOT_REQUIRED = "not_required"
    REQUIRED_DUE_TO_AUTHORITY_CHANGE = "required_due_to_authority_change"


class ReclearanceStatus(StrEnum):
    """Doctrine value set for ``reclearance_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    REQUIRED = "required"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    FAILED = "failed"


class ReconstructionStatus(StrEnum):
    """Doctrine value set for ``reconstruction_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    READY = "ready"
    PARTIAL = "partial"
    BLOCKED_BY_GAP = "blocked_by_gap"
    NON_RECONSTRUCTABLE = "non_reconstructable"


class RegistryBindingStatus(StrEnum):
    """Doctrine value set for ``registry_binding_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    COMPATIBLE = "compatible"
    MISSING = "missing"
    STALE = "stale"
    MISMATCHED = "mismatched"
    SUBSTITUTED = "substituted"


class RegistryDriftStatus(StrEnum):
    """Doctrine value set for ``registry_drift_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    NONE = "none"
    STALE = "stale"
    MISSING = "missing"
    WIDENED = "widened"
    SUBSTITUTED = "substituted"
    ORPHANED = "orphaned"


class RegistryStatus(StrEnum):
    """Doctrine value set for ``registry_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    VALID = "valid"
    MISSING = "missing"
    STALE = "stale"
    MISMATCHED = "mismatched"
    SUBSTITUTED = "substituted"


class ReplayBindingStatus(StrEnum):
    """Doctrine value set for ``replay_binding_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    BOUND = "bound"
    MISSING = "missing"
    INCOMPLETE = "incomplete"
    NON_REPLAYABLE = "non_replayable"
    MISMATCHED = "mismatched"


class ResumeAuthorityStatus(StrEnum):
    """Doctrine value set for ``resume_authority_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    BOUND = "bound"
    MISSING = "missing"
    STALE = "stale"
    MISMATCHED = "mismatched"
    WIDENED = "widened"


class SafeExtractionStatus(StrEnum):
    """Doctrine value set for ``safe_extraction_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    NOT_REQUIRED = "not_required"
    EXTRACTED = "extracted"
    PARTIAL = "partial"
    FAILED = "failed"


class SandboxBindingStatus(StrEnum):
    """Doctrine value set for ``sandbox_binding_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    BOUND = "bound"
    MISSING = "missing"
    STALE = "stale"
    INCOMPATIBLE = "incompatible"
    WIDENED = "widened"


class StaticGovernanceStatus(StrEnum):
    """Doctrine value set for ``static_governance_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    CLEAN = "clean"
    DRIFT_DETECTED = "drift_detected"
    WEAKENING_DETECTED = "weakening_detected"
    WAIVER_REQUIRED = "waiver_required"
    ADR_REQUIRED = "adr_required"
    UNRESOLVED = "unresolved"


class StaticRegressionStatus(StrEnum):
    """Doctrine value set for ``static_regression_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    CLEAN = "clean"
    REGRESSION_DETECTED = "regression_detected"
    BASELINE_MISSING = "baseline_missing"
    COMPARISON_INCOMPLETE = "comparison_incomplete"


class StructureDriftStatus(StrEnum):
    """Doctrine value set for ``structure_drift_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    NONE = "none"
    DETECTED = "detected"
    UNRESOLVED = "unresolved"
    WAIVER_REQUIRED = "waiver_required"


class StructureStatus(StrEnum):
    """Doctrine value set for ``structure_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (4 values).
    """

    CLEAN = "clean"
    VIOLATION_DETECTED = "violation_detected"
    WAIVER_REQUIRED = "waiver_required"
    UNRESOLVED = "unresolved"


class ToolEgressStatus(StrEnum):
    """Doctrine value set for ``tool_egress_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    BOUND = "bound"
    MISSING = "missing"
    UNAUTHORIZED = "unauthorized"
    SUBSTITUTED = "substituted"
    SCHEMA_GAP = "schema_gap"
    AUDIT_GAP = "audit_gap"


class TraceBindingStatus(StrEnum):
    """Doctrine value set for ``trace_binding_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (5 values).
    """

    COMPLETE = "complete"
    MISSING_TRACE = "missing_trace"
    MISSING_SPAN = "missing_span"
    ORPHAN_SPAN = "orphan_span"
    PARENT_GAP = "parent_gap"


class WaiverStatus(StrEnum):
    """Doctrine value set for ``waiver_status``.
    Source: ``docs/reference/00_L5_Policy_Plane/`` (6 values).
    """

    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    PRESENT = "present"
    MISSING = "missing"
    STALE = "stale"
    INCOMPATIBLE = "incompatible"


STATUS_ENUM_REGISTRY: Final[dict[str, type[StrEnum]]] = {
    "adr_status": AdrStatus,
    "audit_binding_status": AuditBindingStatus,
    "authority_attempt_status": AuthorityAttemptStatus,
    "authority_context_status": AuthorityContextStatus,
    "blueprint_binding_status": BlueprintBindingStatus,
    "bypass_evidence_status": BypassEvidenceStatus,
    "capability_scope_status": CapabilityScopeStatus,
    "certification_evidence_status": CertificationEvidenceStatus,
    "certification_scope_status": CertificationScopeStatus,
    "certification_status": CertificationStatus,
    "classification_status": ClassificationStatus,
    "connector_egress_status": ConnectorEgressStatus,
    "content_boundary_status": ContentBoundaryStatus,
    "credential_scope_status": CredentialScopeStatus,
    "egress_certification_status": EgressCertificationStatus,
    "egress_evidence_status": EgressEvidenceStatus,
    "enforcement_receipt_status": EnforcementReceiptStatus,
    "fallback_status": FallbackStatus,
    "gateway_status": GatewayStatus,
    "hash_binding_status": HashBindingStatus,
    "hitl_audit_status": HitlAuditStatus,
    "hitl_packet_status": HitlPacketStatus,
    "human_input_status": HumanInputStatus,
    "human_origin_status": HumanOriginStatus,
    "human_scope_status": HumanScopeStatus,
    "instruction_boundary_status": InstructionBoundaryStatus,
    "match_status": MatchStatus,
    "model_egress_status": ModelEgressStatus,
    "network_egress_status": NetworkEgressStatus,
    "origin_label_status": OriginLabelStatus,
    "origin_manifest_status": OriginManifestStatus,
    "policy_binding_status": PolicyBindingStatus,
    "policy_drift_status": PolicyDriftStatus,
    "principal_chain_status": PrincipalChainStatus,
    "provider_lane_status": ProviderLaneStatus,
    "quarantine_status": QuarantineStatus,
    "recertification_status": RecertificationStatus,
    "reclearance_status": ReclearanceStatus,
    "reconstruction_status": ReconstructionStatus,
    "registry_binding_status": RegistryBindingStatus,
    "registry_drift_status": RegistryDriftStatus,
    "registry_status": RegistryStatus,
    "replay_binding_status": ReplayBindingStatus,
    "resume_authority_status": ResumeAuthorityStatus,
    "safe_extraction_status": SafeExtractionStatus,
    "sandbox_binding_status": SandboxBindingStatus,
    "static_governance_status": StaticGovernanceStatus,
    "static_regression_status": StaticRegressionStatus,
    "structure_drift_status": StructureDriftStatus,
    "structure_status": StructureStatus,
    "tool_egress_status": ToolEgressStatus,
    "trace_binding_status": TraceBindingStatus,
    "waiver_status": WaiverStatus,
}

__all__ = [
    "AdrStatus",
    "AuditBindingStatus",
    "AuthorityAttemptStatus",
    "AuthorityContextStatus",
    "BlueprintBindingStatus",
    "BypassEvidenceStatus",
    "CapabilityScopeStatus",
    "CertificationEvidenceStatus",
    "CertificationScopeStatus",
    "CertificationStatus",
    "ClassificationStatus",
    "ConnectorEgressStatus",
    "ContentBoundaryStatus",
    "CredentialScopeStatus",
    "EgressCertificationStatus",
    "EgressEvidenceStatus",
    "EnforcementReceiptStatus",
    "FallbackStatus",
    "GatewayStatus",
    "HashBindingStatus",
    "HitlAuditStatus",
    "HitlPacketStatus",
    "HumanInputStatus",
    "HumanOriginStatus",
    "HumanScopeStatus",
    "InstructionBoundaryStatus",
    "MatchStatus",
    "ModelEgressStatus",
    "NetworkEgressStatus",
    "OriginLabelStatus",
    "OriginManifestStatus",
    "PolicyBindingStatus",
    "PolicyDriftStatus",
    "PrincipalChainStatus",
    "ProviderLaneStatus",
    "QuarantineStatus",
    "RecertificationStatus",
    "ReclearanceStatus",
    "ReconstructionStatus",
    "RegistryBindingStatus",
    "RegistryDriftStatus",
    "RegistryStatus",
    "ReplayBindingStatus",
    "ResumeAuthorityStatus",
    "SafeExtractionStatus",
    "SandboxBindingStatus",
    "StaticGovernanceStatus",
    "StaticRegressionStatus",
    "StructureDriftStatus",
    "StructureStatus",
    "ToolEgressStatus",
    "TraceBindingStatus",
    "WaiverStatus",
    "STATUS_ENUM_REGISTRY",
]
