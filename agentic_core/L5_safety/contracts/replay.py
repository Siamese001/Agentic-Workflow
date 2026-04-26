"""Generated L5 contract dataclasses for ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``
Module: ``agentic_core.L5_safety.contracts.replay``
Generated count: 103 contracts

Every class below is an evidence-only frozen dataclass. L5 contracts must
not emit runtime dispositions. See ``_base.py`` for the kind hierarchy,
``_vocab.py`` for the controlled vocabularies, and ``_status_enums.py``
for per-status field value sets.

Re-run ``python tools/l5_contracts/generate_contracts.py`` to regenerate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from ._base import (
    L5OutputBase,
    L5Packet,
    L5Receipt,
    L5Report,
    L5Manifest,
    L5Log,
    L5Diff,
    L5Envelope,
    L5Result,
    L5Map,
    L5Status,
    L5Ref,
    L5Context,
    L5Token,
)
from ._status_enums import (
    AuditBindingStatus,
    CertificationEvidenceStatus,
    CertificationScopeStatus,
    HashBindingStatus,
    ReconstructionStatus,
    TraceBindingStatus,
)


@dataclass(frozen=True, slots=True)
class AffectedConsumerReport(L5Report):
    """L5 doctrine output ``affected_consumer_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: affected_consumer_report.
    """

    output_name: ClassVar[str] = "affected_consumer_report"
    output_names: ClassVar[tuple[str, ...]] = ("affected_consumer_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AuditBindingStatus(L5Status):
    """L5 doctrine output ``audit_binding_status`` (kind=status).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_binding_status.
    """

    output_name: ClassVar[str] = "audit_binding_status"
    output_names: ClassVar[tuple[str, ...]] = ("audit_binding_status",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("complete", "incomplete", "hash_gap", "trace_gap", "receipt_gap",)
    value_enum: ClassVar[type] = AuditBindingStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class AuditGapReport(L5Report):
    """L5 doctrine output ``audit_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_gap_report.
    """

    output_name: ClassVar[str] = "audit_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("audit_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AuditHashChainReceipt(L5Receipt):
    """L5 doctrine output ``audit_hash_chain_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_hash_chain_receipt.
    """

    output_name: ClassVar[str] = "audit_hash_chain_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("audit_hash_chain_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuditLogEventRef(L5Ref):
    """L5 doctrine output ``audit_log_event_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_log_event_ref.
    """

    output_name: ClassVar[str] = "audit_log_event_ref"
    output_names: ClassVar[tuple[str, ...]] = ("audit_log_event_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class AuditManifest(L5Manifest):
    """L5 doctrine output ``audit_manifest`` (kind=manifest).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_manifest.
    """

    output_name: ClassVar[str] = "audit_manifest"
    output_names: ClassVar[tuple[str, ...]] = ("audit_manifest",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "manifest"


@dataclass(frozen=True, slots=True)
class AuditManifestHashReceipt(L5Receipt):
    """L5 doctrine output ``audit_manifest_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_manifest_hash_receipt.
    """

    output_name: ClassVar[str] = "audit_manifest_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("audit_manifest_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuditManifestReceipt(L5Receipt):
    """L5 doctrine output ``audit_manifest_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_manifest_receipt.
    """

    output_name: ClassVar[str] = "audit_manifest_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("audit_manifest_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuditManifestRef(L5Ref):
    """L5 doctrine output ``audit_manifest_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_manifest_ref.
    """

    output_name: ClassVar[str] = "audit_manifest_ref"
    output_names: ClassVar[tuple[str, ...]] = ("audit_manifest_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class AuditRedactionReceipt(L5Receipt):
    """L5 doctrine output ``audit_redaction_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_redaction_receipt.
    """

    output_name: ClassVar[str] = "audit_redaction_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("audit_redaction_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuditSchemaReceipt(L5Receipt):
    """L5 doctrine output ``audit_schema_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_schema_receipt.
    """

    output_name: ClassVar[str] = "audit_schema_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("audit_schema_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuditSecretExposureStaticReport(L5Report):
    """L5 doctrine output ``audit_secret_exposure_static_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_secret_exposure_static_report.
    """

    output_name: ClassVar[str] = "audit_secret_exposure_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("audit_secret_exposure_static_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AuditSinkReceipt(L5Receipt):
    """L5 doctrine output ``audit_sink_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: audit_sink_receipt.
    """

    output_name: ClassVar[str] = "audit_sink_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("audit_sink_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuthorityContextRef(L5Ref):
    """L5 doctrine output ``authority_context_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: authority_context_ref.
    """

    output_name: ClassVar[str] = "authority_context_ref"
    output_names: ClassVar[tuple[str, ...]] = ("authority_context_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class AuthorityReconstructionPacket(L5Packet):
    """L5 doctrine output ``authority_reconstruction_packet`` (kind=packet).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: authority_reconstruction_packet.
    """

    output_name: ClassVar[str] = "authority_reconstruction_packet"
    output_names: ClassVar[tuple[str, ...]] = ("authority_reconstruction_packet",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class BootReplayAuditGovernanceReport(L5Report):
    """L5 doctrine output ``boot_replay_audit_governance_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: boot_replay_audit_governance_report.
    """

    output_name: ClassVar[str] = "boot_replay_audit_governance_report"
    output_names: ClassVar[tuple[str, ...]] = ("boot_replay_audit_governance_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CanonicalSerializationReceipt(L5Receipt):
    """L5 doctrine output ``canonical_serialization_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: canonical_serialization_receipt.
    """

    output_name: ClassVar[str] = "canonical_serialization_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("canonical_serialization_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CertificationEvidenceStatus(L5Status):
    """L5 doctrine output ``certification_evidence_status`` (kind=status).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_evidence_status.
    """

    output_name: ClassVar[str] = "certification_evidence_status"
    output_names: ClassVar[tuple[str, ...]] = ("certification_evidence_status",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("complete", "incomplete", "stale", "mismatched", "non_replayable", "audit_gap",)
    value_enum: ClassVar[type] = CertificationEvidenceStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class CertificationGapReport(L5Report):
    """L5 doctrine output ``certification_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_gap_report.
    """

    output_name: ClassVar[str] = "certification_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("certification_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CertificationPacketGapReport(L5Report):
    """L5 doctrine output ``certification_packet_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_packet_gap_report.
    """

    output_name: ClassVar[str] = "certification_packet_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("certification_packet_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CertificationPacketHashReceipt(L5Receipt):
    """L5 doctrine output ``certification_packet_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_packet_hash_receipt.
    """

    output_name: ClassVar[str] = "certification_packet_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("certification_packet_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CertificationPacketReceipt(L5Receipt):
    """L5 doctrine output ``certification_packet_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_packet_receipt.
    """

    output_name: ClassVar[str] = "certification_packet_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("certification_packet_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CertificationResult(L5Result):
    """L5 doctrine output ``certification_result`` (kind=result).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_result.
    """

    output_name: ClassVar[str] = "certification_result"
    output_names: ClassVar[tuple[str, ...]] = ("certification_result",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "result"


@dataclass(frozen=True, slots=True)
class CertificationResultHashReceipt(L5Receipt):
    """L5 doctrine output ``certification_result_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_result_hash_receipt.
    """

    output_name: ClassVar[str] = "certification_result_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("certification_result_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CertificationResultReceipt(L5Receipt):
    """L5 doctrine output ``certification_result_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_result_receipt.
    """

    output_name: ClassVar[str] = "certification_result_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("certification_result_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CertificationReuseViolationReport(L5Report):
    """L5 doctrine output ``certification_reuse_violation_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_reuse_violation_report.
    """

    output_name: ClassVar[str] = "certification_reuse_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("certification_reuse_violation_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CertificationSchemaAuditReadinessReport(L5Report):
    """L5 doctrine output ``certification_schema_audit_readiness_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_schema_audit_readiness_report.
    """

    output_name: ClassVar[str] = "certification_schema_audit_readiness_report"
    output_names: ClassVar[tuple[str, ...]] = ("certification_schema_audit_readiness_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CertificationSchemaIntegrityReport(L5Report):
    """L5 doctrine output ``certification_schema_integrity_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_schema_integrity_report.
    """

    output_name: ClassVar[str] = "certification_schema_integrity_report"
    output_names: ClassVar[tuple[str, ...]] = ("certification_schema_integrity_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CertificationSchemaReceipt(L5Receipt):
    """L5 doctrine output ``certification_schema_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_schema_receipt.
    """

    output_name: ClassVar[str] = "certification_schema_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("certification_schema_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CertificationSchemaReplayReadinessReport(L5Report):
    """L5 doctrine output ``certification_schema_replay_readiness_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_schema_replay_readiness_report.
    """

    output_name: ClassVar[str] = "certification_schema_replay_readiness_report"
    output_names: ClassVar[tuple[str, ...]] = ("certification_schema_replay_readiness_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CertificationScopeGapReport(L5Report):
    """L5 doctrine output ``certification_scope_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_scope_gap_report.
    """

    output_name: ClassVar[str] = "certification_scope_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("certification_scope_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CertificationScopeHashReceipt(L5Receipt):
    """L5 doctrine output ``certification_scope_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_scope_hash_receipt.
    """

    output_name: ClassVar[str] = "certification_scope_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("certification_scope_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CertificationScopeReceipt(L5Receipt):
    """L5 doctrine output ``certification_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_scope_receipt.
    """

    output_name: ClassVar[str] = "certification_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("certification_scope_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CertificationScopeStatus(L5Status):
    """L5 doctrine output ``certification_scope_status`` (kind=status).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_scope_status.
    """

    output_name: ClassVar[str] = "certification_scope_status"
    output_names: ClassVar[tuple[str, ...]] = ("certification_scope_status",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("bound", "missing", "widened", "stale", "mismatched",)
    value_enum: ClassVar[type] = CertificationScopeStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class CertificationScopeWideningReport(L5Report):
    """L5 doctrine output ``certification_scope_widening_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: certification_scope_widening_report.
    """

    output_name: ClassVar[str] = "certification_scope_widening_report"
    output_names: ClassVar[tuple[str, ...]] = ("certification_scope_widening_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ComplianceHashGapReport(L5Report):
    """L5 doctrine output ``compliance_hash_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: compliance_hash_gap_report.
    """

    output_name: ClassVar[str] = "compliance_hash_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("compliance_hash_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ComplianceHashReceipt(L5Receipt):
    """L5 doctrine output ``compliance_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: compliance_hash_receipt.
    """

    output_name: ClassVar[str] = "compliance_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("compliance_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ContextHashReceipt(L5Receipt):
    """L5 doctrine output ``context_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: context_hash_receipt.
    """

    output_name: ClassVar[str] = "context_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("context_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CriticalReplayAuditGapReport(L5Report):
    """L5 doctrine output ``critical_replay_audit_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: critical_replay_audit_gap_report.
    """

    output_name: ClassVar[str] = "critical_replay_audit_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("critical_replay_audit_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DownstreamReviewEvidenceRef(L5Ref):
    """L5 doctrine output ``downstream_review_evidence_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: downstream_review_evidence_ref.
    """

    output_name: ClassVar[str] = "downstream_review_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("downstream_review_evidence_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class EvidenceContractHashReceipt(L5Receipt):
    """L5 doctrine output ``evidence_contract_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: evidence_contract_hash_receipt.
    """

    output_name: ClassVar[str] = "evidence_contract_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("evidence_contract_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EvidenceContractRef(L5Ref):
    """L5 doctrine output ``evidence_contract_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: evidence_contract_ref.
    """

    output_name: ClassVar[str] = "evidence_contract_ref"
    output_names: ClassVar[tuple[str, ...]] = ("evidence_contract_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ExpectedRef(L5Ref):
    """L5 doctrine output ``expected_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: expected_ref.
    """

    output_name: ClassVar[str] = "expected_ref"
    output_names: ClassVar[tuple[str, ...]] = ("expected_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ForbiddenDispositionAbsenceReceipt(L5Receipt):
    """L5 doctrine output ``forbidden_disposition_absence_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: forbidden_disposition_absence_receipt.
    """

    output_name: ClassVar[str] = "forbidden_disposition_absence_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("forbidden_disposition_absence_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ForbiddenDispositionFieldReport(L5Report):
    """L5 doctrine output ``forbidden_disposition_field_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: forbidden_disposition_field_report.
    """

    output_name: ClassVar[str] = "forbidden_disposition_field_report"
    output_names: ClassVar[tuple[str, ...]] = ("forbidden_disposition_field_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HardConstraintMap(L5Map):
    """L5 doctrine output ``hard_constraint_map`` (kind=map).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: hard_constraint_map.
    """

    output_name: ClassVar[str] = "hard_constraint_map"
    output_names: ClassVar[tuple[str, ...]] = ("hard_constraint_map",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class HashAlgorithmReceipt(L5Receipt):
    """L5 doctrine output ``hash_algorithm_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: hash_algorithm_receipt.
    """

    output_name: ClassVar[str] = "hash_algorithm_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("hash_algorithm_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HashBindingReportRef(L5Ref):
    """L5 doctrine output ``hash_binding_report_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: hash_binding_report_ref.
    """

    output_name: ClassVar[str] = "hash_binding_report_ref"
    output_names: ClassVar[tuple[str, ...]] = ("hash_binding_report_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HashBindingStatus(L5Status):
    """L5 doctrine output ``hash_binding_status`` (kind=status).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: hash_binding_status.
    """

    output_name: ClassVar[str] = "hash_binding_status"
    output_names: ClassVar[tuple[str, ...]] = ("hash_binding_status",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("complete", "missing_hash", "mismatched_hash", "unsealed", "tamper_evidence",)
    value_enum: ClassVar[type] = HashBindingStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class HashMismatchReport(L5Report):
    """L5 doctrine output ``hash_mismatch_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: hash_mismatch_report.
    """

    output_name: ClassVar[str] = "hash_mismatch_report"
    output_names: ClassVar[tuple[str, ...]] = ("hash_mismatch_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HmacConfigReceipt(L5Receipt):
    """L5 doctrine output ``hmac_config_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: hmac_config_receipt.
    """

    output_name: ClassVar[str] = "hmac_config_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("hmac_config_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HmacSignatureReceipt(L5Receipt):
    """L5 doctrine output ``hmac_signature_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: hmac_signature_receipt.
    """

    output_name: ClassVar[str] = "hmac_signature_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("hmac_signature_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class L5CertificationPacket(L5Packet):
    """L5 doctrine output ``L5CertificationPacket`` (kind=packet).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: L5CertificationPacket.
    """

    output_name: ClassVar[str] = "L5CertificationPacket"
    output_names: ClassVar[tuple[str, ...]] = ("L5CertificationPacket",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class L5CertificationResult(L5Result):
    """L5 doctrine output ``L5CertificationResult`` (kind=result).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: L5CertificationResult.
    """

    output_name: ClassVar[str] = "L5CertificationResult"
    output_names: ClassVar[tuple[str, ...]] = ("L5CertificationResult",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "result"


@dataclass(frozen=True, slots=True)
class MissingAuditRefStaticReport(L5Report):
    """L5 doctrine output ``missing_audit_ref_static_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: missing_audit_ref_static_report.
    """

    output_name: ClassVar[str] = "missing_audit_ref_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("missing_audit_ref_static_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class MissingReceiptReport(L5Report):
    """L5 doctrine output ``missing_receipt_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: missing_receipt_report.
    """

    output_name: ClassVar[str] = "missing_receipt_report"
    output_names: ClassVar[tuple[str, ...]] = ("missing_receipt_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class MissingReplayRefStaticReport(L5Report):
    """L5 doctrine output ``missing_replay_ref_static_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: missing_replay_ref_static_report.
    """

    output_name: ClassVar[str] = "missing_replay_ref_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("missing_replay_ref_static_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ObservedRef(L5Ref):
    """L5 doctrine output ``observed_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: observed_ref.
    """

    output_name: ClassVar[str] = "observed_ref"
    output_names: ClassVar[tuple[str, ...]] = ("observed_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class OriginTrustManifestReceipt(L5Receipt):
    """L5 doctrine output ``origin_trust_manifest_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: origin_trust_manifest_receipt.
    """

    output_name: ClassVar[str] = "origin_trust_manifest_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("origin_trust_manifest_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class OrphanArtifactReport(L5Report):
    """L5 doctrine output ``orphan_artifact_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: orphan_artifact_report.
    """

    output_name: ClassVar[str] = "orphan_artifact_report"
    output_names: ClassVar[tuple[str, ...]] = ("orphan_artifact_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class OrphanReceiptReport(L5Report):
    """L5 doctrine output ``orphan_receipt_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: orphan_receipt_report.
    """

    output_name: ClassVar[str] = "orphan_receipt_report"
    output_names: ClassVar[tuple[str, ...]] = ("orphan_receipt_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class OrphanSpanReport(L5Report):
    """L5 doctrine output ``orphan_span_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: orphan_span_report.
    """

    output_name: ClassVar[str] = "orphan_span_report"
    output_names: ClassVar[tuple[str, ...]] = ("orphan_span_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ProposedStateDiffHashReceipt(L5Receipt):
    """L5 doctrine output ``proposed_state_diff_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: proposed_state_diff_hash_receipt.
    """

    output_name: ClassVar[str] = "proposed_state_diff_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("proposed_state_diff_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReceiptChainCompletenessReceipt(L5Receipt):
    """L5 doctrine output ``receipt_chain_completeness_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: receipt_chain_completeness_receipt.
    """

    output_name: ClassVar[str] = "receipt_chain_completeness_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("receipt_chain_completeness_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReceiptChainReport(L5Report):
    """L5 doctrine output ``receipt_chain_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: receipt_chain_report.
    """

    output_name: ClassVar[str] = "receipt_chain_report"
    output_names: ClassVar[tuple[str, ...]] = ("receipt_chain_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReceiptChainReportRef(L5Ref):
    """L5 doctrine output ``receipt_chain_report_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: receipt_chain_report_ref.
    """

    output_name: ClassVar[str] = "receipt_chain_report_ref"
    output_names: ClassVar[tuple[str, ...]] = ("receipt_chain_report_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ReceiptCrossPrincipalReport(L5Report):
    """L5 doctrine output ``receipt_cross_principal_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: receipt_cross_principal_report.
    """

    output_name: ClassVar[str] = "receipt_cross_principal_report"
    output_names: ClassVar[tuple[str, ...]] = ("receipt_cross_principal_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReclearanceReceipt(L5Receipt):
    """L5 doctrine output ``reclearance_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: reclearance_receipt.
    """

    output_name: ClassVar[str] = "reclearance_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("reclearance_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReconstructionGapReport(L5Report):
    """L5 doctrine output ``reconstruction_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: reconstruction_gap_report.
    """

    output_name: ClassVar[str] = "reconstruction_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("reconstruction_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReconstructionPacketHashReceipt(L5Receipt):
    """L5 doctrine output ``reconstruction_packet_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: reconstruction_packet_hash_receipt.
    """

    output_name: ClassVar[str] = "reconstruction_packet_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("reconstruction_packet_hash_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReconstructionPacketReceipt(L5Receipt):
    """L5 doctrine output ``reconstruction_packet_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: reconstruction_packet_receipt.
    """

    output_name: ClassVar[str] = "reconstruction_packet_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("reconstruction_packet_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReconstructionStatus(L5Status):
    """L5 doctrine output ``reconstruction_status`` (kind=status).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: reconstruction_status.
    """

    output_name: ClassVar[str] = "reconstruction_status"
    output_names: ClassVar[tuple[str, ...]] = ("reconstruction_status",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("ready", "partial", "blocked_by_gap", "non_reconstructable",)
    value_enum: ClassVar[type] = ReconstructionStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class RedactionPolicyRef(L5Ref):
    """L5 doctrine output ``redaction_policy_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: redaction_policy_ref.
    """

    output_name: ClassVar[str] = "redaction_policy_ref"
    output_names: ClassVar[tuple[str, ...]] = ("redaction_policy_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ReplayEnvelopeReceipt(L5Receipt):
    """L5 doctrine output ``replay_envelope_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: replay_envelope_receipt.
    """

    output_name: ClassVar[str] = "replay_envelope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("replay_envelope_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReplayEnvelopeRef(L5Ref):
    """L5 doctrine output ``replay_envelope_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: replay_envelope_ref.
    """

    output_name: ClassVar[str] = "replay_envelope_ref"
    output_names: ClassVar[tuple[str, ...]] = ("replay_envelope_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ReplayGapReport(L5Report):
    """L5 doctrine output ``replay_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: replay_gap_report.
    """

    output_name: ClassVar[str] = "replay_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("replay_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReplayHashBindingReport(L5Report):
    """L5 doctrine output ``replay_hash_binding_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: replay_hash_binding_report.
    """

    output_name: ClassVar[str] = "replay_hash_binding_report"
    output_names: ClassVar[tuple[str, ...]] = ("replay_hash_binding_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReplaySchemaReceipt(L5Receipt):
    """L5 doctrine output ``replay_schema_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: replay_schema_receipt.
    """

    output_name: ClassVar[str] = "replay_schema_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("replay_schema_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReplayStorageReceipt(L5Receipt):
    """L5 doctrine output ``replay_storage_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: replay_storage_receipt.
    """

    output_name: ClassVar[str] = "replay_storage_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("replay_storage_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RequiredHashGapReport(L5Report):
    """L5 doctrine output ``required_hash_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: required_hash_gap_report.
    """

    output_name: ClassVar[str] = "required_hash_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("required_hash_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RouteContractRef(L5Ref):
    """L5 doctrine output ``route_contract_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: route_contract_ref.
    """

    output_name: ClassVar[str] = "route_contract_ref"
    output_names: ClassVar[tuple[str, ...]] = ("route_contract_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class RuntimeAuditManifestReceipt(L5Receipt):
    """L5 doctrine output ``runtime_audit_manifest_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: runtime_audit_manifest_receipt.
    """

    output_name: ClassVar[str] = "runtime_audit_manifest_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_audit_manifest_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeCertificationPacketReceipt(L5Receipt):
    """L5 doctrine output ``runtime_certification_packet_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: runtime_certification_packet_receipt.
    """

    output_name: ClassVar[str] = "runtime_certification_packet_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_certification_packet_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeHashBindingReport(L5Report):
    """L5 doctrine output ``runtime_hash_binding_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: runtime_hash_binding_report.
    """

    output_name: ClassVar[str] = "runtime_hash_binding_report"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_hash_binding_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RuntimeReconstructionReadinessReport(L5Report):
    """L5 doctrine output ``runtime_reconstruction_readiness_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: runtime_reconstruction_readiness_report.
    """

    output_name: ClassVar[str] = "runtime_reconstruction_readiness_report"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_reconstruction_readiness_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RuntimeReplayAuditCertificationReceipt(L5Receipt):
    """L5 doctrine output ``runtime_replay_audit_certification_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: runtime_replay_audit_certification_receipt.
    """

    output_name: ClassVar[str] = "runtime_replay_audit_certification_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_replay_audit_certification_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeReplayBindingReceipt(L5Receipt):
    """L5 doctrine output ``runtime_replay_binding_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: runtime_replay_binding_receipt.
    """

    output_name: ClassVar[str] = "runtime_replay_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_replay_binding_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeTraceCompletenessReport(L5Report):
    """L5 doctrine output ``runtime_trace_completeness_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: runtime_trace_completeness_report.
    """

    output_name: ClassVar[str] = "runtime_trace_completeness_report"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_trace_completeness_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SpanBindingReceipt(L5Receipt):
    """L5 doctrine output ``span_binding_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: span_binding_receipt.
    """

    output_name: ClassVar[str] = "span_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("span_binding_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaleReceiptReport(L5Report):
    """L5 doctrine output ``stale_receipt_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: stale_receipt_report.
    """

    output_name: ClassVar[str] = "stale_receipt_report"
    output_names: ClassVar[tuple[str, ...]] = ("stale_receipt_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StandardsFingerprintGapReport(L5Report):
    """L5 doctrine output ``standards_fingerprint_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: standards_fingerprint_gap_report.
    """

    output_name: ClassVar[str] = "standards_fingerprint_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("standards_fingerprint_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticReplayAuditEvidenceIntakeReceipt(L5Receipt):
    """L5 doctrine output ``static_replay_audit_evidence_intake_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: static_replay_audit_evidence_intake_receipt.
    """

    output_name: ClassVar[str] = "static_replay_audit_evidence_intake_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_replay_audit_evidence_intake_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticReplayAuditGapReport(L5Report):
    """L5 doctrine output ``static_replay_audit_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: static_replay_audit_gap_report.
    """

    output_name: ClassVar[str] = "static_replay_audit_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_replay_audit_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticReplayAuditGovernanceReport(L5Report):
    """L5 doctrine output ``static_replay_audit_governance_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: static_replay_audit_governance_report.
    """

    output_name: ClassVar[str] = "static_replay_audit_governance_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_replay_audit_governance_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TamperEvidenceReport(L5Report):
    """L5 doctrine output ``tamper_evidence_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: tamper_evidence_report.
    """

    output_name: ClassVar[str] = "tamper_evidence_report"
    output_names: ClassVar[tuple[str, ...]] = ("tamper_evidence_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TraceAuditBindingReceipt(L5Receipt):
    """L5 doctrine output ``trace_audit_binding_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: trace_audit_binding_receipt.
    """

    output_name: ClassVar[str] = "trace_audit_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("trace_audit_binding_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class TraceBindingStatus(L5Status):
    """L5 doctrine output ``trace_binding_status`` (kind=status).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: trace_binding_status.
    """

    output_name: ClassVar[str] = "trace_binding_status"
    output_names: ClassVar[tuple[str, ...]] = ("trace_binding_status",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("complete", "missing_trace", "missing_span", "orphan_span", "parent_gap",)
    value_enum: ClassVar[type] = TraceBindingStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class TraceCompletenessReport(L5Report):
    """L5 doctrine output ``trace_completeness_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: trace_completeness_report.
    """

    output_name: ClassVar[str] = "trace_completeness_report"
    output_names: ClassVar[tuple[str, ...]] = ("trace_completeness_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TraceCompletenessReportRef(L5Ref):
    """L5 doctrine output ``trace_completeness_report_ref`` (kind=ref).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: trace_completeness_report_ref.
    """

    output_name: ClassVar[str] = "trace_completeness_report_ref"
    output_names: ClassVar[tuple[str, ...]] = ("trace_completeness_report_ref",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class TraceCorrelationReceipt(L5Receipt):
    """L5 doctrine output ``trace_correlation_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: trace_correlation_receipt.
    """

    output_name: ClassVar[str] = "trace_correlation_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("trace_correlation_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class TraceGapReport(L5Report):
    """L5 doctrine output ``trace_gap_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: trace_gap_report.
    """

    output_name: ClassVar[str] = "trace_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("trace_gap_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TraceReplayBindingReceipt(L5Receipt):
    """L5 doctrine output ``trace_replay_binding_receipt`` (kind=receipt).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: trace_replay_binding_receipt.
    """

    output_name: ClassVar[str] = "trace_replay_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("trace_replay_binding_receipt",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class WallClockDecisionFieldReport(L5Report):
    """L5 doctrine output ``wall_clock_decision_field_report`` (kind=report).

    Source doctrine: ``00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md``.
    Canonical doctrine names: wall_clock_decision_field_report.
    """

    output_name: ClassVar[str] = "wall_clock_decision_field_report"
    output_names: ClassVar[tuple[str, ...]] = ("wall_clock_decision_field_report",)
    source_doc: ClassVar[str] = "00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md"
    output_kind: ClassVar[str] = "report"


__all__ = [
    "AffectedConsumerReport",
    "AuditBindingStatus",
    "AuditGapReport",
    "AuditHashChainReceipt",
    "AuditLogEventRef",
    "AuditManifest",
    "AuditManifestHashReceipt",
    "AuditManifestReceipt",
    "AuditManifestRef",
    "AuditRedactionReceipt",
    "AuditSchemaReceipt",
    "AuditSecretExposureStaticReport",
    "AuditSinkReceipt",
    "AuthorityContextRef",
    "AuthorityReconstructionPacket",
    "BootReplayAuditGovernanceReport",
    "CanonicalSerializationReceipt",
    "CertificationEvidenceStatus",
    "CertificationGapReport",
    "CertificationPacketGapReport",
    "CertificationPacketHashReceipt",
    "CertificationPacketReceipt",
    "CertificationResult",
    "CertificationResultHashReceipt",
    "CertificationResultReceipt",
    "CertificationReuseViolationReport",
    "CertificationSchemaAuditReadinessReport",
    "CertificationSchemaIntegrityReport",
    "CertificationSchemaReceipt",
    "CertificationSchemaReplayReadinessReport",
    "CertificationScopeGapReport",
    "CertificationScopeHashReceipt",
    "CertificationScopeReceipt",
    "CertificationScopeStatus",
    "CertificationScopeWideningReport",
    "ComplianceHashGapReport",
    "ComplianceHashReceipt",
    "ContextHashReceipt",
    "CriticalReplayAuditGapReport",
    "DownstreamReviewEvidenceRef",
    "EvidenceContractHashReceipt",
    "EvidenceContractRef",
    "ExpectedRef",
    "ForbiddenDispositionAbsenceReceipt",
    "ForbiddenDispositionFieldReport",
    "HardConstraintMap",
    "HashAlgorithmReceipt",
    "HashBindingReportRef",
    "HashBindingStatus",
    "HashMismatchReport",
    "HmacConfigReceipt",
    "HmacSignatureReceipt",
    "L5CertificationPacket",
    "L5CertificationResult",
    "MissingAuditRefStaticReport",
    "MissingReceiptReport",
    "MissingReplayRefStaticReport",
    "ObservedRef",
    "OriginTrustManifestReceipt",
    "OrphanArtifactReport",
    "OrphanReceiptReport",
    "OrphanSpanReport",
    "ProposedStateDiffHashReceipt",
    "ReceiptChainCompletenessReceipt",
    "ReceiptChainReport",
    "ReceiptChainReportRef",
    "ReceiptCrossPrincipalReport",
    "ReclearanceReceipt",
    "ReconstructionGapReport",
    "ReconstructionPacketHashReceipt",
    "ReconstructionPacketReceipt",
    "ReconstructionStatus",
    "RedactionPolicyRef",
    "ReplayEnvelopeReceipt",
    "ReplayEnvelopeRef",
    "ReplayGapReport",
    "ReplayHashBindingReport",
    "ReplaySchemaReceipt",
    "ReplayStorageReceipt",
    "RequiredHashGapReport",
    "RouteContractRef",
    "RuntimeAuditManifestReceipt",
    "RuntimeCertificationPacketReceipt",
    "RuntimeHashBindingReport",
    "RuntimeReconstructionReadinessReport",
    "RuntimeReplayAuditCertificationReceipt",
    "RuntimeReplayBindingReceipt",
    "RuntimeTraceCompletenessReport",
    "SpanBindingReceipt",
    "StaleReceiptReport",
    "StandardsFingerprintGapReport",
    "StaticReplayAuditEvidenceIntakeReceipt",
    "StaticReplayAuditGapReport",
    "StaticReplayAuditGovernanceReport",
    "TamperEvidenceReport",
    "TraceAuditBindingReceipt",
    "TraceBindingStatus",
    "TraceCompletenessReport",
    "TraceCompletenessReportRef",
    "TraceCorrelationReceipt",
    "TraceGapReport",
    "TraceReplayBindingReceipt",
    "WallClockDecisionFieldReport",
]
