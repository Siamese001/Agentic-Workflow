"""Generated L5 contract dataclasses for ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00.5_L5_Egress_and_Provider_Governance_detailed.md``
Module: ``agentic_core.L5_safety.contracts.egress``
Generated count: 108 contracts

Every class below is an evidence-only frozen dataclass. L5 contracts must
not emit runtime dispositions. See ``_base.py`` for the kind hierarchy
and ``_vocab.py`` for the controlled vocabularies.

Re-run ``python tools/l5_contracts/generate_contracts.py`` to regenerate.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class ArgumentSchemaRef(L5Ref):
    """L5 doctrine output ``argument_schema_ref`` (kind=ref).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: argument_schema_ref.
    """

    output_name: ClassVar[str] = "argument_schema_ref"
    output_names: ClassVar[tuple[str, ...]] = ("argument_schema_ref",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class BootEgressGovernanceReport(L5Report):
    """L5 doctrine output ``boot_egress_governance_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: boot_egress_governance_report.
    """

    output_name: ClassVar[str] = "boot_egress_governance_report"
    output_names: ClassVar[tuple[str, ...]] = ("boot_egress_governance_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BroadNetworkScopeReport(L5Report):
    """L5 doctrine output ``broad_network_scope_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: broad_network_scope_report.
    """

    output_name: ClassVar[str] = "broad_network_scope_report"
    output_names: ClassVar[tuple[str, ...]] = ("broad_network_scope_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CertificationStatus(L5Status):
    """L5 doctrine output ``certification_status`` (kind=status).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: certification_status.
    """

    output_name: ClassVar[str] = "certification_status"
    output_names: ClassVar[tuple[str, ...]] = ("certification_status",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class ConnectorAuditReceipt(L5Receipt):
    """L5 doctrine output ``connector_audit_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: connector_audit_receipt.
    """

    output_name: ClassVar[str] = "connector_audit_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_audit_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorEgressReceipt(L5Receipt):
    """L5 doctrine output ``ConnectorEgressReceipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: ConnectorEgressReceipt, connector_egress_receipt.
    """

    output_name: ClassVar[str] = "ConnectorEgressReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "ConnectorEgressReceipt",
        "connector_egress_receipt",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorGrantGapReport(L5Report):
    """L5 doctrine output ``connector_grant_gap_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: connector_grant_gap_report.
    """

    output_name: ClassVar[str] = "connector_grant_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_grant_gap_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorGrantRef(L5Ref):
    """L5 doctrine output ``connector_grant_ref`` (kind=ref).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: connector_grant_ref.
    """

    output_name: ClassVar[str] = "connector_grant_ref"
    output_names: ClassVar[tuple[str, ...]] = ("connector_grant_ref",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ConnectorReplayReceipt(L5Receipt):
    """L5 doctrine output ``connector_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: connector_replay_receipt.
    """

    output_name: ClassVar[str] = "connector_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_replay_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorRetentionReceipt(L5Receipt):
    """L5 doctrine output ``connector_retention_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: connector_retention_receipt.
    """

    output_name: ClassVar[str] = "connector_retention_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_retention_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorScopeStaticReport(L5Report):
    """L5 doctrine output ``connector_scope_static_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: connector_scope_static_report.
    """

    output_name: ClassVar[str] = "connector_scope_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_scope_static_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CredentialAuditReceipt(L5Receipt):
    """L5 doctrine output ``credential_audit_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_audit_receipt.
    """

    output_name: ClassVar[str] = "credential_audit_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("credential_audit_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CredentialExpirationReceipt(L5Receipt):
    """L5 doctrine output ``credential_expiration_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_expiration_receipt.
    """

    output_name: ClassVar[str] = "credential_expiration_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("credential_expiration_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CredentialExposureRiskReport(L5Report):
    """L5 doctrine output ``credential_exposure_risk_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_exposure_risk_report.
    """

    output_name: ClassVar[str] = "credential_exposure_risk_report"
    output_names: ClassVar[tuple[str, ...]] = ("credential_exposure_risk_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CredentialIssuerReceipt(L5Receipt):
    """L5 doctrine output ``credential_issuer_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_issuer_receipt.
    """

    output_name: ClassVar[str] = "credential_issuer_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("credential_issuer_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CredentialMinimizationReceipt(L5Receipt):
    """L5 doctrine output ``credential_minimization_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_minimization_receipt.
    """

    output_name: ClassVar[str] = "credential_minimization_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("credential_minimization_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CredentialPolicyReceipt(L5Receipt):
    """L5 doctrine output ``credential_policy_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_policy_receipt.
    """

    output_name: ClassVar[str] = "credential_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("credential_policy_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CredentialRedactionReceipt(L5Receipt):
    """L5 doctrine output ``credential_redaction_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_redaction_receipt.
    """

    output_name: ClassVar[str] = "credential_redaction_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("credential_redaction_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CredentialScopeReceipt(L5Receipt):
    """L5 doctrine output ``CredentialScopeReceipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: CredentialScopeReceipt, credential_scope_receipt.
    """

    output_name: ClassVar[str] = "CredentialScopeReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "CredentialScopeReceipt",
        "credential_scope_receipt",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CredentialScopeRef(L5Ref):
    """L5 doctrine output ``credential_scope_ref`` (kind=ref).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_scope_ref.
    """

    output_name: ClassVar[str] = "credential_scope_ref"
    output_names: ClassVar[tuple[str, ...]] = ("credential_scope_ref",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class CredentialSubstitutionReport(L5Report):
    """L5 doctrine output ``credential_substitution_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: credential_substitution_report.
    """

    output_name: ClassVar[str] = "credential_substitution_report"
    output_names: ClassVar[tuple[str, ...]] = ("credential_substitution_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CriticalEgressGapReport(L5Report):
    """L5 doctrine output ``critical_egress_gap_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: critical_egress_gap_report.
    """

    output_name: ClassVar[str] = "critical_egress_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("critical_egress_gap_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DataMinimizationReceipt(L5Receipt):
    """L5 doctrine output ``data_minimization_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: data_minimization_receipt.
    """

    output_name: ClassVar[str] = "data_minimization_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("data_minimization_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class DirectApiKeyUsageReport(L5Report):
    """L5 doctrine output ``direct_api_key_usage_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: direct_api_key_usage_report.
    """

    output_name: ClassVar[str] = "direct_api_key_usage_report"
    output_names: ClassVar[tuple[str, ...]] = ("direct_api_key_usage_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DirectSDKBypassReport(L5Report):
    """L5 doctrine output ``DirectSDKBypassReport`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: DirectSDKBypassReport.
    """

    output_name: ClassVar[str] = "DirectSDKBypassReport"
    output_names: ClassVar[tuple[str, ...]] = ("DirectSDKBypassReport",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DirectSdkBypassEvidenceRef(L5Ref):
    """L5 doctrine output ``direct_sdk_bypass_evidence_ref`` (kind=ref).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: direct_sdk_bypass_evidence_ref.
    """

    output_name: ClassVar[str] = "direct_sdk_bypass_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("direct_sdk_bypass_evidence_ref",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class EgressAuditGapReport(L5Report):
    """L5 doctrine output ``egress_audit_gap_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_audit_gap_report.
    """

    output_name: ClassVar[str] = "egress_audit_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("egress_audit_gap_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class EgressAuditPolicyReceipt(L5Receipt):
    """L5 doctrine output ``egress_audit_policy_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_audit_policy_receipt.
    """

    output_name: ClassVar[str] = "egress_audit_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("egress_audit_policy_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressAuditReceipt(L5Receipt):
    """L5 doctrine output ``EgressAuditReceipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: EgressAuditReceipt, egress_audit_receipt.
    """

    output_name: ClassVar[str] = "EgressAuditReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "EgressAuditReceipt",
        "egress_audit_receipt",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressCertificationGapReport(L5Report):
    """L5 doctrine output ``egress_certification_gap_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_certification_gap_report.
    """

    output_name: ClassVar[str] = "egress_certification_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("egress_certification_gap_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class EgressCertificationHashReceipt(L5Receipt):
    """L5 doctrine output ``egress_certification_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_certification_hash_receipt.
    """

    output_name: ClassVar[str] = "egress_certification_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("egress_certification_hash_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressCertificationReceipt(L5Receipt):
    """L5 doctrine output ``EgressCertificationReceipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: EgressCertificationReceipt, egress_certification_receipt.
    """

    output_name: ClassVar[str] = "EgressCertificationReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "EgressCertificationReceipt",
        "egress_certification_receipt",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressCertificationScopeReceipt(L5Receipt):
    """L5 doctrine output ``egress_certification_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_certification_scope_receipt.
    """

    output_name: ClassVar[str] = "egress_certification_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("egress_certification_scope_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressCertificationStatus(L5Status):
    """L5 doctrine output ``egress_certification_status`` (kind=status).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_certification_status.
    """

    output_name: ClassVar[str] = "egress_certification_status"
    output_names: ClassVar[tuple[str, ...]] = ("egress_certification_status",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class EgressClassReceipt(L5Receipt):
    """L5 doctrine output ``egress_class_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_class_receipt.
    """

    output_name: ClassVar[str] = "egress_class_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("egress_class_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressHashChainReceipt(L5Receipt):
    """L5 doctrine output ``egress_hash_chain_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_hash_chain_receipt.
    """

    output_name: ClassVar[str] = "egress_hash_chain_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("egress_hash_chain_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressPayloadBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``egress_payload_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_payload_boundary_receipt.
    """

    output_name: ClassVar[str] = "egress_payload_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("egress_payload_boundary_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressReconstructionReport(L5Report):
    """L5 doctrine output ``egress_reconstruction_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_reconstruction_report.
    """

    output_name: ClassVar[str] = "egress_reconstruction_report"
    output_names: ClassVar[tuple[str, ...]] = ("egress_reconstruction_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class EgressReplayGapReport(L5Report):
    """L5 doctrine output ``egress_replay_gap_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_replay_gap_report.
    """

    output_name: ClassVar[str] = "egress_replay_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("egress_replay_gap_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class EgressReplayReceipt(L5Receipt):
    """L5 doctrine output ``EgressReplayReceipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: EgressReplayReceipt, egress_replay_receipt.
    """

    output_name: ClassVar[str] = "EgressReplayReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "EgressReplayReceipt",
        "egress_replay_receipt",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressRequestGapReport(L5Report):
    """L5 doctrine output ``egress_request_gap_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_request_gap_report.
    """

    output_name: ClassVar[str] = "egress_request_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("egress_request_gap_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class EgressRequestReceipt(L5Receipt):
    """L5 doctrine output ``egress_request_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_request_receipt.
    """

    output_name: ClassVar[str] = "egress_request_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("egress_request_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressTargetIdentityReceipt(L5Receipt):
    """L5 doctrine output ``egress_target_identity_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_target_identity_receipt.
    """

    output_name: ClassVar[str] = "egress_target_identity_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("egress_target_identity_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EgressWrapperBypassEvidenceRef(L5Ref):
    """L5 doctrine output ``egress_wrapper_bypass_evidence_ref`` (kind=ref).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_wrapper_bypass_evidence_ref.
    """

    output_name: ClassVar[str] = "egress_wrapper_bypass_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("egress_wrapper_bypass_evidence_ref",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class EgressWrapperBypassReport(L5Report):
    """L5 doctrine output ``egress_wrapper_bypass_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: egress_wrapper_bypass_report.
    """

    output_name: ClassVar[str] = "egress_wrapper_bypass_report"
    output_names: ClassVar[tuple[str, ...]] = ("egress_wrapper_bypass_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ExternalCommitAuditReceipt(L5Receipt):
    """L5 doctrine output ``external_commit_audit_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: external_commit_audit_receipt.
    """

    output_name: ClassVar[str] = "external_commit_audit_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("external_commit_audit_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ExternalCommitDownstreamReviewReceipt(L5Receipt):
    """L5 doctrine output ``external_commit_downstream_review_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: external_commit_downstream_review_receipt.
    """

    output_name: ClassVar[str] = "external_commit_downstream_review_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("external_commit_downstream_review_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ExternalCommitEgressReceipt(L5Receipt):
    """L5 doctrine output ``external_commit_egress_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: external_commit_egress_receipt.
    """

    output_name: ClassVar[str] = "external_commit_egress_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("external_commit_egress_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ExternalCommitHumanReviewRequirementReceipt(L5Receipt):
    """L5 doctrine output ``external_commit_human_review_requirement_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: external_commit_human_review_requirement_receipt.
    """

    output_name: ClassVar[str] = "external_commit_human_review_requirement_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("external_commit_human_review_requirement_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ExternalCommitReplayReceipt(L5Receipt):
    """L5 doctrine output ``external_commit_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: external_commit_replay_receipt.
    """

    output_name: ClassVar[str] = "external_commit_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("external_commit_replay_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ExternalCommitScopeReceipt(L5Receipt):
    """L5 doctrine output ``external_commit_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: external_commit_scope_receipt.
    """

    output_name: ClassVar[str] = "external_commit_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("external_commit_scope_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class FallbackCandidateReceipt(L5Receipt):
    """L5 doctrine output ``fallback_candidate_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: fallback_candidate_receipt.
    """

    output_name: ClassVar[str] = "fallback_candidate_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("fallback_candidate_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class FallbackPolicyReceipt(L5Receipt):
    """L5 doctrine output ``fallback_policy_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: fallback_policy_receipt.
    """

    output_name: ClassVar[str] = "fallback_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("fallback_policy_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class FallbackRecertificationRequiredReport(L5Report):
    """L5 doctrine output ``fallback_recertification_required_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: fallback_recertification_required_report.
    """

    output_name: ClassVar[str] = "fallback_recertification_required_report"
    output_names: ClassVar[tuple[str, ...]] = ("fallback_recertification_required_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HardcodedModelLiteralReport(L5Report):
    """L5 doctrine output ``hardcoded_model_literal_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: hardcoded_model_literal_report.
    """

    output_name: ClassVar[str] = "hardcoded_model_literal_report"
    output_names: ClassVar[tuple[str, ...]] = ("hardcoded_model_literal_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HiddenEgressCertificationImpactReport(L5Report):
    """L5 doctrine output ``hidden_egress_certification_impact_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: hidden_egress_certification_impact_report.
    """

    output_name: ClassVar[str] = "hidden_egress_certification_impact_report"
    output_names: ClassVar[tuple[str, ...]] = ("hidden_egress_certification_impact_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class IrreversibleActionEvidenceReport(L5Report):
    """L5 doctrine output ``irreversible_action_evidence_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: irreversible_action_evidence_report.
    """

    output_name: ClassVar[str] = "irreversible_action_evidence_report"
    output_names: ClassVar[tuple[str, ...]] = ("irreversible_action_evidence_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ModelAllowlistReceipt(L5Receipt):
    """L5 doctrine output ``model_allowlist_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: model_allowlist_receipt.
    """

    output_name: ClassVar[str] = "model_allowlist_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("model_allowlist_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ModelAuditReceipt(L5Receipt):
    """L5 doctrine output ``model_audit_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: model_audit_receipt.
    """

    output_name: ClassVar[str] = "model_audit_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("model_audit_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ModelCredentialExposureReport(L5Report):
    """L5 doctrine output ``model_credential_exposure_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: model_credential_exposure_report.
    """

    output_name: ClassVar[str] = "model_credential_exposure_report"
    output_names: ClassVar[tuple[str, ...]] = ("model_credential_exposure_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ModelDirectBypassReport(L5Report):
    """L5 doctrine output ``model_direct_bypass_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: model_direct_bypass_report.
    """

    output_name: ClassVar[str] = "model_direct_bypass_report"
    output_names: ClassVar[tuple[str, ...]] = ("model_direct_bypass_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ModelReplayReceipt(L5Receipt):
    """L5 doctrine output ``model_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: model_replay_receipt.
    """

    output_name: ClassVar[str] = "model_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("model_replay_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ModelResolutionMapReceipt(L5Receipt):
    """L5 doctrine output ``model_resolution_map_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: model_resolution_map_receipt.
    """

    output_name: ClassVar[str] = "model_resolution_map_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("model_resolution_map_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkAuditReceipt(L5Receipt):
    """L5 doctrine output ``network_audit_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: network_audit_receipt.
    """

    output_name: ClassVar[str] = "network_audit_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("network_audit_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkBroadScopeReport(L5Report):
    """L5 doctrine output ``network_broad_scope_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: network_broad_scope_report.
    """

    output_name: ClassVar[str] = "network_broad_scope_report"
    output_names: ClassVar[tuple[str, ...]] = ("network_broad_scope_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class NetworkDestinationReceipt(L5Receipt):
    """L5 doctrine output ``network_destination_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: network_destination_receipt.
    """

    output_name: ClassVar[str] = "network_destination_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("network_destination_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkEgressReceipt(L5Receipt):
    """L5 doctrine output ``NetworkEgressReceipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: NetworkEgressReceipt, network_egress_receipt.
    """

    output_name: ClassVar[str] = "NetworkEgressReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "NetworkEgressReceipt",
        "network_egress_receipt",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkMethodReceipt(L5Receipt):
    """L5 doctrine output ``network_method_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: network_method_receipt.
    """

    output_name: ClassVar[str] = "network_method_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("network_method_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkRegionReceipt(L5Receipt):
    """L5 doctrine output ``network_region_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: network_region_receipt.
    """

    output_name: ClassVar[str] = "network_region_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("network_region_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkReplayReceipt(L5Receipt):
    """L5 doctrine output ``network_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: network_replay_receipt.
    """

    output_name: ClassVar[str] = "network_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("network_replay_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkSubstitutionReport(L5Report):
    """L5 doctrine output ``network_substitution_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: network_substitution_report.
    """

    output_name: ClassVar[str] = "network_substitution_report"
    output_names: ClassVar[tuple[str, ...]] = ("network_substitution_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class NoSilentFallbackReceipt(L5Receipt):
    """L5 doctrine output ``NoSilentFallbackReceipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: NoSilentFallbackReceipt, no_silent_fallback_receipt.
    """

    output_name: ClassVar[str] = "NoSilentFallbackReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "NoSilentFallbackReceipt",
        "no_silent_fallback_receipt",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class OldNewEgressTargetDiff(L5Diff):
    """L5 doctrine output ``old_new_egress_target_diff`` (kind=diff).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: old_new_egress_target_diff.
    """

    output_name: ClassVar[str] = "old_new_egress_target_diff"
    output_names: ClassVar[tuple[str, ...]] = ("old_new_egress_target_diff",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "diff"


@dataclass(frozen=True, slots=True)
class PayloadCrossPrincipalReport(L5Report):
    """L5 doctrine output ``payload_cross_principal_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: payload_cross_principal_report.
    """

    output_name: ClassVar[str] = "payload_cross_principal_report"
    output_names: ClassVar[tuple[str, ...]] = ("payload_cross_principal_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PayloadCrossTenantReport(L5Report):
    """L5 doctrine output ``payload_cross_tenant_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: payload_cross_tenant_report.
    """

    output_name: ClassVar[str] = "payload_cross_tenant_report"
    output_names: ClassVar[tuple[str, ...]] = ("payload_cross_tenant_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PayloadHashReceipt(L5Receipt):
    """L5 doctrine output ``payload_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: payload_hash_receipt.
    """

    output_name: ClassVar[str] = "payload_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("payload_hash_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PayloadScopeReceipt(L5Receipt):
    """L5 doctrine output ``payload_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: payload_scope_receipt.
    """

    output_name: ClassVar[str] = "payload_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("payload_scope_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PayloadSecretExposureReport(L5Report):
    """L5 doctrine output ``payload_secret_exposure_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: payload_secret_exposure_report.
    """

    output_name: ClassVar[str] = "payload_secret_exposure_report"
    output_names: ClassVar[tuple[str, ...]] = ("payload_secret_exposure_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptArtifactRef(L5Ref):
    """L5 doctrine output ``prompt_artifact_ref`` (kind=ref).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: prompt_artifact_ref.
    """

    output_name: ClassVar[str] = "prompt_artifact_ref"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_artifact_ref",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ProviderRegistryReceipt(L5Receipt):
    """L5 doctrine output ``provider_registry_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: provider_registry_receipt.
    """

    output_name: ClassVar[str] = "provider_registry_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("provider_registry_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ProviderSdkBypassStaticReport(L5Report):
    """L5 doctrine output ``provider_sdk_bypass_static_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: provider_sdk_bypass_static_report.
    """

    output_name: ClassVar[str] = "provider_sdk_bypass_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("provider_sdk_bypass_static_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ProviderSubstitutionReport(L5Report):
    """L5 doctrine output ``ProviderSubstitutionReport`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: ProviderSubstitutionReport, provider_substitution_report.
    """

    output_name: ClassVar[str] = "ProviderSubstitutionReport"
    output_names: ClassVar[tuple[str, ...]] = (
        "ProviderSubstitutionReport",
        "provider_substitution_report",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegionSubstitutionReport(L5Report):
    """L5 doctrine output ``region_substitution_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: region_substitution_report.
    """

    output_name: ClassVar[str] = "region_substitution_report"
    output_names: ClassVar[tuple[str, ...]] = ("region_substitution_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RuntimeConnectorEgressReceipt(L5Receipt):
    """L5 doctrine output ``runtime_connector_egress_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: runtime_connector_egress_receipt.
    """

    output_name: ClassVar[str] = "runtime_connector_egress_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_connector_egress_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeCredentialScopeReceipt(L5Receipt):
    """L5 doctrine output ``runtime_credential_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: runtime_credential_scope_receipt.
    """

    output_name: ClassVar[str] = "runtime_credential_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_credential_scope_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeEgressGapReport(L5Report):
    """L5 doctrine output ``runtime_egress_gap_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: runtime_egress_gap_report.
    """

    output_name: ClassVar[str] = "runtime_egress_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_egress_gap_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RuntimeEgressGovernanceReceipt(L5Receipt):
    """L5 doctrine output ``runtime_egress_governance_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: runtime_egress_governance_receipt.
    """

    output_name: ClassVar[str] = "runtime_egress_governance_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_egress_governance_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeFallbackReceipt(L5Receipt):
    """L5 doctrine output ``runtime_fallback_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: runtime_fallback_receipt.
    """

    output_name: ClassVar[str] = "runtime_fallback_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_fallback_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeModelEgressReceipt(L5Receipt):
    """L5 doctrine output ``runtime_model_egress_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: runtime_model_egress_receipt.
    """

    output_name: ClassVar[str] = "runtime_model_egress_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_model_egress_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeNetworkEgressReceipt(L5Receipt):
    """L5 doctrine output ``runtime_network_egress_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: runtime_network_egress_receipt.
    """

    output_name: ClassVar[str] = "runtime_network_egress_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_network_egress_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeToolEgressReceipt(L5Receipt):
    """L5 doctrine output ``runtime_tool_egress_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: runtime_tool_egress_receipt.
    """

    output_name: ClassVar[str] = "runtime_tool_egress_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_tool_egress_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SilentFallbackStaticReport(L5Report):
    """L5 doctrine output ``silent_fallback_static_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: silent_fallback_static_report.
    """

    output_name: ClassVar[str] = "silent_fallback_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("silent_fallback_static_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SsrfRiskEvidenceReport(L5Report):
    """L5 doctrine output ``ssrf_risk_evidence_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: ssrf_risk_evidence_report.
    """

    output_name: ClassVar[str] = "ssrf_risk_evidence_report"
    output_names: ClassVar[tuple[str, ...]] = ("ssrf_risk_evidence_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticEgressCertificationReadinessReport(L5Report):
    """L5 doctrine output ``static_egress_certification_readiness_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: static_egress_certification_readiness_report.
    """

    output_name: ClassVar[str] = "static_egress_certification_readiness_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_egress_certification_readiness_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticEgressEvidenceIntakeReceipt(L5Receipt):
    """L5 doctrine output ``static_egress_evidence_intake_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: static_egress_evidence_intake_receipt.
    """

    output_name: ClassVar[str] = "static_egress_evidence_intake_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_egress_evidence_intake_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticEgressEvidenceRefMap(L5Map):
    """L5 doctrine output ``static_egress_evidence_ref_map`` (kind=map).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: static_egress_evidence_ref_map.
    """

    output_name: ClassVar[str] = "static_egress_evidence_ref_map"
    output_names: ClassVar[tuple[str, ...]] = ("static_egress_evidence_ref_map",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class StaticEgressGapReport(L5Report):
    """L5 doctrine output ``static_egress_gap_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: static_egress_gap_report.
    """

    output_name: ClassVar[str] = "static_egress_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_egress_gap_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticEgressGovernanceReport(L5Report):
    """L5 doctrine output ``static_egress_governance_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: static_egress_governance_report.
    """

    output_name: ClassVar[str] = "static_egress_governance_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_egress_governance_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ToolAuditReceipt(L5Receipt):
    """L5 doctrine output ``tool_audit_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: tool_audit_receipt.
    """

    output_name: ClassVar[str] = "tool_audit_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("tool_audit_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ToolBroadScopeReport(L5Report):
    """L5 doctrine output ``tool_broad_scope_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: tool_broad_scope_report.
    """

    output_name: ClassVar[str] = "tool_broad_scope_report"
    output_names: ClassVar[tuple[str, ...]] = ("tool_broad_scope_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ToolEgressReceipt(L5Receipt):
    """L5 doctrine output ``ToolEgressReceipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: ToolEgressReceipt, tool_egress_receipt.
    """

    output_name: ClassVar[str] = "ToolEgressReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "ToolEgressReceipt",
        "tool_egress_receipt",
    )
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ToolReplayReceipt(L5Receipt):
    """L5 doctrine output ``tool_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: tool_replay_receipt.
    """

    output_name: ClassVar[str] = "tool_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("tool_replay_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ToolSchemaBindingReceipt(L5Receipt):
    """L5 doctrine output ``tool_schema_binding_receipt`` (kind=receipt).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: tool_schema_binding_receipt.
    """

    output_name: ClassVar[str] = "tool_schema_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("tool_schema_binding_receipt",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class UnauthorizedNetworkClientEvidenceRef(L5Ref):
    """L5 doctrine output ``unauthorized_network_client_evidence_ref`` (kind=ref).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: unauthorized_network_client_evidence_ref.
    """

    output_name: ClassVar[str] = "unauthorized_network_client_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("unauthorized_network_client_evidence_ref",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class UnauthorizedNetworkClientReport(L5Report):
    """L5 doctrine output ``unauthorized_network_client_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: unauthorized_network_client_report.
    """

    output_name: ClassVar[str] = "unauthorized_network_client_report"
    output_names: ClassVar[tuple[str, ...]] = ("unauthorized_network_client_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnauthorizedNetworkClientStaticReport(L5Report):
    """L5 doctrine output ``unauthorized_network_client_static_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: unauthorized_network_client_static_report.
    """

    output_name: ClassVar[str] = "unauthorized_network_client_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("unauthorized_network_client_static_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnauthorizedSecretAccessEvidenceRef(L5Ref):
    """L5 doctrine output ``unauthorized_secret_access_evidence_ref`` (kind=ref).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: unauthorized_secret_access_evidence_ref.
    """

    output_name: ClassVar[str] = "unauthorized_secret_access_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("unauthorized_secret_access_evidence_ref",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class UnauthorizedSecretAccessReport(L5Report):
    """L5 doctrine output ``unauthorized_secret_access_report`` (kind=report).

    Source doctrine: ``00.5_L5_Egress_and_Provider_Governance_detailed.md``.
    Canonical doctrine names: unauthorized_secret_access_report.
    """

    output_name: ClassVar[str] = "unauthorized_secret_access_report"
    output_names: ClassVar[tuple[str, ...]] = ("unauthorized_secret_access_report",)
    source_doc: ClassVar[str] = "00.5_L5_Egress_and_Provider_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


__all__ = [
    "ArgumentSchemaRef",
    "BootEgressGovernanceReport",
    "BroadNetworkScopeReport",
    "CertificationStatus",
    "ConnectorAuditReceipt",
    "ConnectorEgressReceipt",
    "ConnectorGrantGapReport",
    "ConnectorGrantRef",
    "ConnectorReplayReceipt",
    "ConnectorRetentionReceipt",
    "ConnectorScopeStaticReport",
    "CredentialAuditReceipt",
    "CredentialExpirationReceipt",
    "CredentialExposureRiskReport",
    "CredentialIssuerReceipt",
    "CredentialMinimizationReceipt",
    "CredentialPolicyReceipt",
    "CredentialRedactionReceipt",
    "CredentialScopeReceipt",
    "CredentialScopeRef",
    "CredentialSubstitutionReport",
    "CriticalEgressGapReport",
    "DataMinimizationReceipt",
    "DirectApiKeyUsageReport",
    "DirectSDKBypassReport",
    "DirectSdkBypassEvidenceRef",
    "EgressAuditGapReport",
    "EgressAuditPolicyReceipt",
    "EgressAuditReceipt",
    "EgressCertificationGapReport",
    "EgressCertificationHashReceipt",
    "EgressCertificationReceipt",
    "EgressCertificationScopeReceipt",
    "EgressCertificationStatus",
    "EgressClassReceipt",
    "EgressHashChainReceipt",
    "EgressPayloadBoundaryReceipt",
    "EgressReconstructionReport",
    "EgressReplayGapReport",
    "EgressReplayReceipt",
    "EgressRequestGapReport",
    "EgressRequestReceipt",
    "EgressTargetIdentityReceipt",
    "EgressWrapperBypassEvidenceRef",
    "EgressWrapperBypassReport",
    "ExternalCommitAuditReceipt",
    "ExternalCommitDownstreamReviewReceipt",
    "ExternalCommitEgressReceipt",
    "ExternalCommitHumanReviewRequirementReceipt",
    "ExternalCommitReplayReceipt",
    "ExternalCommitScopeReceipt",
    "FallbackCandidateReceipt",
    "FallbackPolicyReceipt",
    "FallbackRecertificationRequiredReport",
    "HardcodedModelLiteralReport",
    "HiddenEgressCertificationImpactReport",
    "IrreversibleActionEvidenceReport",
    "ModelAllowlistReceipt",
    "ModelAuditReceipt",
    "ModelCredentialExposureReport",
    "ModelDirectBypassReport",
    "ModelReplayReceipt",
    "ModelResolutionMapReceipt",
    "NetworkAuditReceipt",
    "NetworkBroadScopeReport",
    "NetworkDestinationReceipt",
    "NetworkEgressReceipt",
    "NetworkMethodReceipt",
    "NetworkRegionReceipt",
    "NetworkReplayReceipt",
    "NetworkSubstitutionReport",
    "NoSilentFallbackReceipt",
    "OldNewEgressTargetDiff",
    "PayloadCrossPrincipalReport",
    "PayloadCrossTenantReport",
    "PayloadHashReceipt",
    "PayloadScopeReceipt",
    "PayloadSecretExposureReport",
    "PromptArtifactRef",
    "ProviderRegistryReceipt",
    "ProviderSdkBypassStaticReport",
    "ProviderSubstitutionReport",
    "RegionSubstitutionReport",
    "RuntimeConnectorEgressReceipt",
    "RuntimeCredentialScopeReceipt",
    "RuntimeEgressGapReport",
    "RuntimeEgressGovernanceReceipt",
    "RuntimeFallbackReceipt",
    "RuntimeModelEgressReceipt",
    "RuntimeNetworkEgressReceipt",
    "RuntimeToolEgressReceipt",
    "SilentFallbackStaticReport",
    "SsrfRiskEvidenceReport",
    "StaticEgressCertificationReadinessReport",
    "StaticEgressEvidenceIntakeReceipt",
    "StaticEgressEvidenceRefMap",
    "StaticEgressGapReport",
    "StaticEgressGovernanceReport",
    "ToolAuditReceipt",
    "ToolBroadScopeReport",
    "ToolEgressReceipt",
    "ToolReplayReceipt",
    "ToolSchemaBindingReceipt",
    "UnauthorizedNetworkClientEvidenceRef",
    "UnauthorizedNetworkClientReport",
    "UnauthorizedNetworkClientStaticReport",
    "UnauthorizedSecretAccessEvidenceRef",
    "UnauthorizedSecretAccessReport",
]
