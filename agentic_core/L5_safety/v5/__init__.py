"""L5 Governance & Safety — v5 plane (additive over v4).

Spec: ``docs/reference/00_L5_Policy_Plane/Governance & Safety v5.md``
ADR : ``docs/architecture/adr/ADR-051-l5-v5-governance-plane.md``
Plan: ``docs/archive/windsurf/legacy-tree/plans/l5-v5-governance-implementation-7d3a91.md``

Public API surface:

- types: enums for governance mode, review depth, risk band (incl. CRITICAL),
  origin labels, boundary classification, decision verdicts, reason codes.
- contracts: GovernanceReviewRequest, TriageReport, OriginTrustManifest,
  CapabilityTokenV5, SandboxEnvelope, ReplayEnvelope, StandardsFingerprint,
  GovernanceResult.
- pipeline: ``g0_entry.validate_entry_packet`` → ``g1_triage.triage_request``
  → ``g2a_origin_trust.classify_origins`` → ``decision_rail.emit_verdict``.
- façade: ``governance_plane.certify_packet`` composes the pipeline plus
  ``replay_audit.seal_replay_envelope`` and the v4 runtime-lane composer.
- invariants: ``out_of_band_invariants.assert_no_current_run_mutation``.

This package is additive. v4 callers keep using
``agentic_core.L5_safety.identity.runtime_entry.evaluate_runtime_lane``.
"""

from __future__ import annotations

from agentic_core.L5_safety.v5.contracts import (
    AuditManifest,
    CapabilityTokenV5,
    GovernanceResult,
    GovernanceReviewRequest,
    GuardrailFamilyRecord,
    HashBindingReport,
    HITLDispositionPacket,
    OriginTrustManifest,
    ReceiptChainCompletenessReport,
    ReconstructionReadinessReport,
    ReplayEnvelope,
    RuntimeRegressionReport,
    SandboxEnvelope,
    StandardsFingerprint,
    TraceCompletenessReport,
    TriageReport,
)
from agentic_core.L5_safety.v5.egress_receipts import (
    EgressCertificationReceipt,
    EgressCertificationRequest,
    HiddenEgressPathReport,
    NoSilentFallbackReceipt,
    SubstitutionReport,
    connector_substitution_report,
    model_substitution_report,
    provider_substitution_report,
    tool_substitution_report,
)
from agentic_core.L5_safety.v5.guardrail_registry import (
    all_families,
    get_family,
    hard_constraint_family_ids,
)
from agentic_core.L5_safety.v5.hitl_receipts import (
    HITLAuditReceipt,
    HITLFreezePacket,
    HumanInputOriginReceipt,
    HumanModificationDiff,
    HumanReviewEvidencePacket,
    HumanReviewScopeReceipt,
    ResumeAuthorityReceipt,
)
from agentic_core.L5_safety.v5.otel_spans import (
    ALL_SPAN_NAMES,
    RecordedSpan,
    emit_event,
    emit_span,
    get_recorded_spans,
)
from agentic_core.L5_safety.v5.promotion_receipt import PromotionReceipt
from agentic_core.L5_safety.v5.risk_tier_controls import (
    BandControls,
    apply_band_controls,
    assert_band_monotonicity,
)
from agentic_core.L5_safety.v5.runtime_binding import (
    L5CertificationEvidenceRefSet,
    L5ReclearanceBinding,
    L5RuntimeCertificationBinding,
    L5SnapshotVerificationReceipt,
    emit_runtime_binding,
    verify_snapshot,
)
from agentic_core.L5_safety.v5.static_drift import (
    ArchitectureDriftReport,
    GoldenSnapshotComparisonReport,
    PolicyWeakeningReport,
    StaticDriftEvidencePacket,
    StaticGovernanceReviewPacket,
)
from agentic_core.L5_safety.v5.bridges import (
    bridge_blueprint_paths,
    bridge_guardrail_bank,
    bridge_handoff_validation,
    bridge_policy_bundle,
    bridge_registry_token_match,
    map_v5_band_to_v4,
)
from agentic_core.L5_safety.v5.decision_rail import emit_verdict
from agentic_core.L5_safety.v5.g0_entry import (
    EntryValidationFailure,
    EntryValidationResult,
    validate_entry_packet,
)
from agentic_core.L5_safety.v5.g1_triage import triage_request
from agentic_core.L5_safety.v5.g2a_origin_trust import classify_origins
from agentic_core.L5_safety.v5.governance_plane import certify_packet
from agentic_core.L5_safety.v5.out_of_band_invariants import (
    OutOfBandMutationError,
    assert_no_current_run_mutation,
)
from agentic_core.L5_safety.v5.replay_audit import seal_replay_envelope
from agentic_core.L5_safety.v5.types import (
    BoundaryClassification,
    DecisionVerdict,
    GovernanceMode,
    NextLane,
    OriginLabel,
    PacketKind,
    ReasonCode,
    ReviewDepth,
    RiskTierBandV5,
    SideEffectClass,
    StandardsTag,
    TriageFlag,
)

__all__ = [
    "ALL_SPAN_NAMES",
    "ArchitectureDriftReport",
    "AuditManifest",
    "BandControls",
    "BoundaryClassification",
    "CapabilityTokenV5",
    "DecisionVerdict",
    "EgressCertificationReceipt",
    "EgressCertificationRequest",
    "EntryValidationFailure",
    "EntryValidationResult",
    "GoldenSnapshotComparisonReport",
    "GovernanceMode",
    "GovernanceResult",
    "GovernanceReviewRequest",
    "GuardrailFamilyRecord",
    "HashBindingReport",
    "HiddenEgressPathReport",
    "HITLAuditReceipt",
    "HITLDispositionPacket",
    "HITLFreezePacket",
    "HumanInputOriginReceipt",
    "HumanModificationDiff",
    "HumanReviewEvidencePacket",
    "HumanReviewScopeReceipt",
    "L5CertificationEvidenceRefSet",
    "L5ReclearanceBinding",
    "L5RuntimeCertificationBinding",
    "L5SnapshotVerificationReceipt",
    "NextLane",
    "NoSilentFallbackReceipt",
    "OriginLabel",
    "OriginTrustManifest",
    "OutOfBandMutationError",
    "PacketKind",
    "PolicyWeakeningReport",
    "PromotionReceipt",
    "ReasonCode",
    "ReceiptChainCompletenessReport",
    "ReconstructionReadinessReport",
    "RecordedSpan",
    "ReplayEnvelope",
    "ResumeAuthorityReceipt",
    "ReviewDepth",
    "RiskTierBandV5",
    "RuntimeRegressionReport",
    "SandboxEnvelope",
    "SideEffectClass",
    "StandardsFingerprint",
    "StandardsTag",
    "StaticDriftEvidencePacket",
    "StaticGovernanceReviewPacket",
    "SubstitutionReport",
    "TraceCompletenessReport",
    "TriageFlag",
    "TriageReport",
    "all_families",
    "apply_band_controls",
    "assert_band_monotonicity",
    "assert_no_current_run_mutation",
    "bridge_blueprint_paths",
    "bridge_guardrail_bank",
    "bridge_handoff_validation",
    "bridge_policy_bundle",
    "bridge_registry_token_match",
    "certify_packet",
    "classify_origins",
    "connector_substitution_report",
    "emit_event",
    "emit_runtime_binding",
    "emit_span",
    "emit_verdict",
    "get_family",
    "get_recorded_spans",
    "hard_constraint_family_ids",
    "map_v5_band_to_v4",
    "model_substitution_report",
    "provider_substitution_report",
    "seal_replay_envelope",
    "tool_substitution_report",
    "triage_request",
    "validate_entry_packet",
    "verify_snapshot",
]
