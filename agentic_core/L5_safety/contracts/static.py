"""Generated L5 contract dataclasses for ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``
Module: ``agentic_core.L5_safety.contracts.static``
Generated count: 128 contracts

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
    AdrStatus,
    BypassEvidenceStatus,
    PolicyDriftStatus,
    RegistryDriftStatus,
    StaticGovernanceStatus,
    StaticRegressionStatus,
    StructureDriftStatus,
    WaiverStatus,
)


@dataclass(frozen=True, slots=True)
class ADRRequiredReport(L5Report):
    """L5 doctrine output ``ADRRequiredReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: ADRRequiredReport.
    """

    output_name: ClassVar[str] = "ADRRequiredReport"
    output_names: ClassVar[tuple[str, ...]] = ("ADRRequiredReport",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AdgSnapshotRef(L5Ref):
    """L5 doctrine output ``adg_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: adg_snapshot_ref.
    """

    output_name: ClassVar[str] = "adg_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("adg_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class AdrRequiredReport(L5Report):
    """L5 doctrine output ``adr_required_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: adr_required_report.
    """

    output_name: ClassVar[str] = "adr_required_report"
    output_names: ClassVar[tuple[str, ...]] = ("adr_required_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AdrStatus(L5Status):
    """L5 doctrine output ``adr_status`` (kind=status).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: adr_status.
    """

    output_name: ClassVar[str] = "adr_status"
    output_names: ClassVar[tuple[str, ...]] = ("adr_status",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("not_required", "required", "present", "missing", "stale", "incompatible",)
    value_enum: ClassVar[type] = AdrStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class AffectedAuthoritySurfaceMap(L5Map):
    """L5 doctrine output ``affected_authority_surface_map`` (kind=map).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: affected_authority_surface_map.
    """

    output_name: ClassVar[str] = "affected_authority_surface_map"
    output_names: ClassVar[tuple[str, ...]] = ("affected_authority_surface_map",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class AgentRegistryDriftReport(L5Report):
    """L5 doctrine output ``agent_registry_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: agent_registry_drift_report.
    """

    output_name: ClassVar[str] = "agent_registry_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("agent_registry_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ArchitectureDriftGapReport(L5Report):
    """L5 doctrine output ``architecture_drift_gap_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: architecture_drift_gap_report.
    """

    output_name: ClassVar[str] = "architecture_drift_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("architecture_drift_gap_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ArchitectureDriftReport(L5Report):
    """L5 doctrine output ``ArchitectureDriftReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: ArchitectureDriftReport, architecture_drift_report.
    """

    output_name: ClassVar[str] = "ArchitectureDriftReport"
    output_names: ClassVar[tuple[str, ...]] = ("ArchitectureDriftReport", "architecture_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BranchOrCommitRef(L5Ref):
    """L5 doctrine output ``branch_or_commit_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: branch_or_commit_ref.
    """

    output_name: ClassVar[str] = "branch_or_commit_ref"
    output_names: ClassVar[tuple[str, ...]] = ("branch_or_commit_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class BypassEvidenceStatus(L5Status):
    """L5 doctrine output ``bypass_evidence_status`` (kind=status).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: bypass_evidence_status.
    """

    output_name: ClassVar[str] = "bypass_evidence_status"
    output_names: ClassVar[tuple[str, ...]] = ("bypass_evidence_status",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("none", "hidden_egress", "direct_write", "direct_provider", "direct_connector", "direct_memory_mutation",)
    value_enum: ClassVar[type] = BypassEvidenceStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class BypassWrapperWaiverReport(L5Report):
    """L5 doctrine output ``bypass_wrapper_waiver_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: bypass_wrapper_waiver_report.
    """

    output_name: ClassVar[str] = "bypass_wrapper_waiver_report"
    output_names: ClassVar[tuple[str, ...]] = ("bypass_wrapper_waiver_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConfigWithLogicStaticReport(L5Report):
    """L5 doctrine output ``config_with_logic_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: config_with_logic_static_report.
    """

    output_name: ClassVar[str] = "config_with_logic_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("config_with_logic_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorAuditRequirementDriftReport(L5Report):
    """L5 doctrine output ``connector_audit_requirement_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: connector_audit_requirement_drift_report.
    """

    output_name: ClassVar[str] = "connector_audit_requirement_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_audit_requirement_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorConfigDriftReport(L5Report):
    """L5 doctrine output ``ConnectorConfigDriftReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: ConnectorConfigDriftReport, connector_config_drift_report.
    """

    output_name: ClassVar[str] = "ConnectorConfigDriftReport"
    output_names: ClassVar[tuple[str, ...]] = ("ConnectorConfigDriftReport", "connector_config_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorCredentialPolicyDriftReport(L5Report):
    """L5 doctrine output ``connector_credential_policy_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: connector_credential_policy_drift_report.
    """

    output_name: ClassVar[str] = "connector_credential_policy_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_credential_policy_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorDomainDriftReport(L5Report):
    """L5 doctrine output ``connector_domain_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: connector_domain_drift_report.
    """

    output_name: ClassVar[str] = "connector_domain_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_domain_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorGrantDriftReport(L5Report):
    """L5 doctrine output ``connector_grant_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: connector_grant_drift_report.
    """

    output_name: ClassVar[str] = "connector_grant_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_grant_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorRegistryDriftReport(L5Report):
    """L5 doctrine output ``connector_registry_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: connector_registry_drift_report.
    """

    output_name: ClassVar[str] = "connector_registry_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_registry_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorRetentionDriftReport(L5Report):
    """L5 doctrine output ``connector_retention_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: connector_retention_drift_report.
    """

    output_name: ClassVar[str] = "connector_retention_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_retention_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorScopeWideningReport(L5Report):
    """L5 doctrine output ``connector_scope_widening_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: connector_scope_widening_report.
    """

    output_name: ClassVar[str] = "connector_scope_widening_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_scope_widening_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CurrentAdgSnapshotRef(L5Ref):
    """L5 doctrine output ``current_adg_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: current_adg_snapshot_ref.
    """

    output_name: ClassVar[str] = "current_adg_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("current_adg_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class DeletedGateStaticReport(L5Report):
    """L5 doctrine output ``deleted_gate_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: deleted_gate_static_report.
    """

    output_name: ClassVar[str] = "deleted_gate_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("deleted_gate_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DependencyDirectionDriftReport(L5Report):
    """L5 doctrine output ``dependency_direction_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: dependency_direction_drift_report.
    """

    output_name: ClassVar[str] = "dependency_direction_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("dependency_direction_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DirectExternalWriteStaticReport(L5Report):
    """L5 doctrine output ``direct_external_write_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: direct_external_write_static_report.
    """

    output_name: ClassVar[str] = "direct_external_write_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("direct_external_write_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DirectSdkBypassStaticReport(L5Report):
    """L5 doctrine output ``direct_sdk_bypass_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: direct_sdk_bypass_static_report.
    """

    output_name: ClassVar[str] = "direct_sdk_bypass_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("direct_sdk_bypass_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DirectWritePathStaticReport(L5Report):
    """L5 doctrine output ``DirectWritePathStaticReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: DirectWritePathStaticReport, direct_write_path_static_report.
    """

    output_name: ClassVar[str] = "DirectWritePathStaticReport"
    output_names: ClassVar[tuple[str, ...]] = ("DirectWritePathStaticReport", "direct_write_path_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DirectWriteWaiverReport(L5Report):
    """L5 doctrine output ``direct_write_waiver_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: direct_write_waiver_report.
    """

    output_name: ClassVar[str] = "direct_write_waiver_report"
    output_names: ClassVar[tuple[str, ...]] = ("direct_write_waiver_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DownstreamConsumerStaticReadinessMap(L5Map):
    """L5 doctrine output ``downstream_consumer_static_readiness_map`` (kind=map).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: downstream_consumer_static_readiness_map.
    """

    output_name: ClassVar[str] = "downstream_consumer_static_readiness_map"
    output_names: ClassVar[tuple[str, ...]] = ("downstream_consumer_static_readiness_map",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class DownstreamStaticImpactReport(L5Report):
    """L5 doctrine output ``downstream_static_impact_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: downstream_static_impact_report.
    """

    output_name: ClassVar[str] = "downstream_static_impact_report"
    output_names: ClassVar[tuple[str, ...]] = ("downstream_static_impact_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DownstreamStaticRegressionImpactReport(L5Report):
    """L5 doctrine output ``downstream_static_regression_impact_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: downstream_static_regression_impact_report.
    """

    output_name: ClassVar[str] = "downstream_static_regression_impact_report"
    output_names: ClassVar[tuple[str, ...]] = ("downstream_static_regression_impact_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DriftCategoryMap(L5Map):
    """L5 doctrine output ``drift_category_map`` (kind=map).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: drift_category_map.
    """

    output_name: ClassVar[str] = "drift_category_map"
    output_names: ClassVar[tuple[str, ...]] = ("drift_category_map",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class EgressWrapperStaticReport(L5Report):
    """L5 doctrine output ``egress_wrapper_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: egress_wrapper_static_report.
    """

    output_name: ClassVar[str] = "egress_wrapper_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("egress_wrapper_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ExceptionTaxonomyDriftReport(L5Report):
    """L5 doctrine output ``exception_taxonomy_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: exception_taxonomy_drift_report.
    """

    output_name: ClassVar[str] = "exception_taxonomy_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("exception_taxonomy_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class FallbackChainDriftReport(L5Report):
    """L5 doctrine output ``fallback_chain_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: fallback_chain_drift_report.
    """

    output_name: ClassVar[str] = "fallback_chain_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("fallback_chain_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class GoldenArchitectureSnapshotRef(L5Ref):
    """L5 doctrine output ``golden_architecture_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_architecture_snapshot_ref.
    """

    output_name: ClassVar[str] = "golden_architecture_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("golden_architecture_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class GoldenAuditReplaySnapshotRef(L5Ref):
    """L5 doctrine output ``golden_audit_replay_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_audit_replay_snapshot_ref.
    """

    output_name: ClassVar[str] = "golden_audit_replay_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("golden_audit_replay_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class GoldenConnectorSnapshotRef(L5Ref):
    """L5 doctrine output ``golden_connector_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_connector_snapshot_ref.
    """

    output_name: ClassVar[str] = "golden_connector_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("golden_connector_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class GoldenPolicySnapshotRef(L5Ref):
    """L5 doctrine output ``golden_policy_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_policy_snapshot_ref.
    """

    output_name: ClassVar[str] = "golden_policy_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("golden_policy_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class GoldenPromptSnapshotRef(L5Ref):
    """L5 doctrine output ``golden_prompt_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_prompt_snapshot_ref.
    """

    output_name: ClassVar[str] = "golden_prompt_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("golden_prompt_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class GoldenRegistrySnapshotRef(L5Ref):
    """L5 doctrine output ``golden_registry_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_registry_snapshot_ref.
    """

    output_name: ClassVar[str] = "golden_registry_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("golden_registry_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class GoldenRouteSnapshotRef(L5Ref):
    """L5 doctrine output ``golden_route_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_route_snapshot_ref.
    """

    output_name: ClassVar[str] = "golden_route_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("golden_route_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class GoldenSnapshotComparisonReport(L5Report):
    """L5 doctrine output ``GoldenSnapshotComparisonReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: GoldenSnapshotComparisonReport, golden_snapshot_comparison_report.
    """

    output_name: ClassVar[str] = "GoldenSnapshotComparisonReport"
    output_names: ClassVar[tuple[str, ...]] = ("GoldenSnapshotComparisonReport", "golden_snapshot_comparison_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class GoldenSnapshotGapReport(L5Report):
    """L5 doctrine output ``golden_snapshot_gap_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_snapshot_gap_report.
    """

    output_name: ClassVar[str] = "golden_snapshot_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("golden_snapshot_gap_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class GoldenSnapshotRef(L5Ref):
    """L5 doctrine output ``golden_snapshot_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: golden_snapshot_ref.
    """

    output_name: ClassVar[str] = "golden_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("golden_snapshot_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HardConstraintChangeReport(L5Report):
    """L5 doctrine output ``hard_constraint_change_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: hard_constraint_change_report.
    """

    output_name: ClassVar[str] = "hard_constraint_change_report"
    output_names: ClassVar[tuple[str, ...]] = ("hard_constraint_change_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HardcodedModelLiteralStaticReport(L5Report):
    """L5 doctrine output ``hardcoded_model_literal_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: hardcoded_model_literal_static_report.
    """

    output_name: ClassVar[str] = "hardcoded_model_literal_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("hardcoded_model_literal_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HiddenEgressStaticReport(L5Report):
    """L5 doctrine output ``HiddenEgressStaticReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: HiddenEgressStaticReport, hidden_egress_static_report.
    """

    output_name: ClassVar[str] = "HiddenEgressStaticReport"
    output_names: ClassVar[tuple[str, ...]] = ("HiddenEgressStaticReport", "hidden_egress_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HiddenEgressWaiverReport(L5Report):
    """L5 doctrine output ``hidden_egress_waiver_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: hidden_egress_waiver_report.
    """

    output_name: ClassVar[str] = "hidden_egress_waiver_report"
    output_names: ClassVar[tuple[str, ...]] = ("hidden_egress_waiver_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HitlDirectWriteStaticReport(L5Report):
    """L5 doctrine output ``hitl_direct_write_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: hitl_direct_write_static_report.
    """

    output_name: ClassVar[str] = "hitl_direct_write_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_direct_write_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HitlThresholdDriftReport(L5Report):
    """L5 doctrine output ``hitl_threshold_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: hitl_threshold_drift_report.
    """

    output_name: ClassVar[str] = "hitl_threshold_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_threshold_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class L4DirectWriteReport(L5Report):
    """L5 doctrine output ``l4_direct_write_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: l4_direct_write_report.
    """

    output_name: ClassVar[str] = "l4_direct_write_report"
    output_names: ClassVar[tuple[str, ...]] = ("l4_direct_write_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class L6CurrentRunMutationStaticReport(L5Report):
    """L5 doctrine output ``l6_current_run_mutation_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: l6_current_run_mutation_static_report.
    """

    output_name: ClassVar[str] = "l6_current_run_mutation_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("l6_current_run_mutation_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class LayerBoundaryDriftReport(L5Report):
    """L5 doctrine output ``layer_boundary_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: layer_boundary_drift_report.
    """

    output_name: ClassVar[str] = "layer_boundary_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("layer_boundary_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class LearningBoundaryDriftReport(L5Report):
    """L5 doctrine output ``learning_boundary_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: learning_boundary_drift_report.
    """

    output_name: ClassVar[str] = "learning_boundary_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("learning_boundary_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ManagedWorkflowAutonomyDriftReport(L5Report):
    """L5 doctrine output ``managed_workflow_autonomy_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: managed_workflow_autonomy_drift_report.
    """

    output_name: ClassVar[str] = "managed_workflow_autonomy_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("managed_workflow_autonomy_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class MissingAuditMetadataReport(L5Report):
    """L5 doctrine output ``missing_audit_metadata_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: missing_audit_metadata_report.
    """

    output_name: ClassVar[str] = "missing_audit_metadata_report"
    output_names: ClassVar[tuple[str, ...]] = ("missing_audit_metadata_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class MissingReplayMetadataReport(L5Report):
    """L5 doctrine output ``missing_replay_metadata_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: missing_replay_metadata_report.
    """

    output_name: ClassVar[str] = "missing_replay_metadata_report"
    output_names: ClassVar[tuple[str, ...]] = ("missing_replay_metadata_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class NewlyIntroducedBypassReport(L5Report):
    """L5 doctrine output ``newly_introduced_bypass_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: newly_introduced_bypass_report.
    """

    output_name: ClassVar[str] = "newly_introduced_bypass_report"
    output_names: ClassVar[tuple[str, ...]] = ("newly_introduced_bypass_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class OrphanRegistryRef(L5Ref):
    """L5 doctrine output ``orphan_registry_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: orphan_registry_ref.
    """

    output_name: ClassVar[str] = "orphan_registry_ref"
    output_names: ClassVar[tuple[str, ...]] = ("orphan_registry_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class OrphanRegistryReferenceReport(L5Report):
    """L5 doctrine output ``orphan_registry_reference_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: orphan_registry_reference_report.
    """

    output_name: ClassVar[str] = "orphan_registry_reference_report"
    output_names: ClassVar[tuple[str, ...]] = ("orphan_registry_reference_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PolicyDriftStatus(L5Status):
    """L5 doctrine output ``policy_drift_status`` (kind=status).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: policy_drift_status.
    """

    output_name: ClassVar[str] = "policy_drift_status"
    output_names: ClassVar[tuple[str, ...]] = ("policy_drift_status",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("none", "weakened", "stale", "missing", "mismatched",)
    value_enum: ClassVar[type] = PolicyDriftStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class PolicyWeakeningReport(L5Report):
    """L5 doctrine output ``PolicyWeakeningReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: PolicyWeakeningReport, policy_weakening_report.
    """

    output_name: ClassVar[str] = "PolicyWeakeningReport"
    output_names: ClassVar[tuple[str, ...]] = ("PolicyWeakeningReport", "policy_weakening_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PolicyWeakeningWaiverReport(L5Report):
    """L5 doctrine output ``policy_weakening_waiver_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: policy_weakening_waiver_report.
    """

    output_name: ClassVar[str] = "policy_weakening_waiver_report"
    output_names: ClassVar[tuple[str, ...]] = ("policy_weakening_waiver_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptAssemblyBoundaryDriftReport(L5Report):
    """L5 doctrine output ``prompt_assembly_boundary_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: prompt_assembly_boundary_drift_report.
    """

    output_name: ClassVar[str] = "prompt_assembly_boundary_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_assembly_boundary_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptAuthorityBoundaryDriftReport(L5Report):
    """L5 doctrine output ``prompt_authority_boundary_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: prompt_authority_boundary_drift_report.
    """

    output_name: ClassVar[str] = "prompt_authority_boundary_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_authority_boundary_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptDriftReport(L5Report):
    """L5 doctrine output ``PromptDriftReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: PromptDriftReport, prompt_drift_report.
    """

    output_name: ClassVar[str] = "PromptDriftReport"
    output_names: ClassVar[tuple[str, ...]] = ("PromptDriftReport", "prompt_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptRegistryCompatibilityDriftReport(L5Report):
    """L5 doctrine output ``prompt_registry_compatibility_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: prompt_registry_compatibility_drift_report.
    """

    output_name: ClassVar[str] = "prompt_registry_compatibility_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_registry_compatibility_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptRegistryDriftReport(L5Report):
    """L5 doctrine output ``prompt_registry_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: prompt_registry_drift_report.
    """

    output_name: ClassVar[str] = "prompt_registry_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_registry_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptSchemaBindingDriftReport(L5Report):
    """L5 doctrine output ``prompt_schema_binding_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: prompt_schema_binding_drift_report.
    """

    output_name: ClassVar[str] = "prompt_schema_binding_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_schema_binding_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptShadowArtifactReport(L5Report):
    """L5 doctrine output ``prompt_shadow_artifact_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: prompt_shadow_artifact_report.
    """

    output_name: ClassVar[str] = "prompt_shadow_artifact_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_shadow_artifact_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptSlotMapDriftReport(L5Report):
    """L5 doctrine output ``prompt_slot_map_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: prompt_slot_map_drift_report.
    """

    output_name: ClassVar[str] = "prompt_slot_map_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_slot_map_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptStablePrefixDriftReport(L5Report):
    """L5 doctrine output ``prompt_stable_prefix_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: prompt_stable_prefix_drift_report.
    """

    output_name: ClassVar[str] = "prompt_stable_prefix_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_stable_prefix_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ProposedDiffBoundaryReport(L5Report):
    """L5 doctrine output ``proposed_diff_boundary_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: proposed_diff_boundary_report.
    """

    output_name: ClassVar[str] = "proposed_diff_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("proposed_diff_boundary_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RefusalTaxonomyDriftReport(L5Report):
    """L5 doctrine output ``refusal_taxonomy_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: refusal_taxonomy_drift_report.
    """

    output_name: ClassVar[str] = "refusal_taxonomy_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("refusal_taxonomy_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryDigestDriftReport(L5Report):
    """L5 doctrine output ``registry_digest_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: registry_digest_drift_report.
    """

    output_name: ClassVar[str] = "registry_digest_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_digest_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryDriftReport(L5Report):
    """L5 doctrine output ``RegistryDriftReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: RegistryDriftReport, registry_drift_report.
    """

    output_name: ClassVar[str] = "RegistryDriftReport"
    output_names: ClassVar[tuple[str, ...]] = ("RegistryDriftReport", "registry_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryDriftStatus(L5Status):
    """L5 doctrine output ``registry_drift_status`` (kind=status).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: registry_drift_status.
    """

    output_name: ClassVar[str] = "registry_drift_status"
    output_names: ClassVar[tuple[str, ...]] = ("registry_drift_status",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("none", "stale", "missing", "widened", "substituted", "orphaned",)
    value_enum: ClassVar[type] = RegistryDriftStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class RegistryScopeWideningReport(L5Report):
    """L5 doctrine output ``registry_scope_widening_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: registry_scope_widening_report.
    """

    output_name: ClassVar[str] = "registry_scope_widening_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_scope_widening_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistrySubstitutionStaticReport(L5Report):
    """L5 doctrine output ``registry_substitution_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: registry_substitution_static_report.
    """

    output_name: ClassVar[str] = "registry_substitution_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_substitution_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RelaxedScopeReport(L5Report):
    """L5 doctrine output ``relaxed_scope_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: relaxed_scope_report.
    """

    output_name: ClassVar[str] = "relaxed_scope_report"
    output_names: ClassVar[tuple[str, ...]] = ("relaxed_scope_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RetrievalBoundaryDriftReport(L5Report):
    """L5 doctrine output ``retrieval_boundary_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: retrieval_boundary_drift_report.
    """

    output_name: ClassVar[str] = "retrieval_boundary_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("retrieval_boundary_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RiskTierMappingDriftReport(L5Report):
    """L5 doctrine output ``risk_tier_mapping_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: risk_tier_mapping_drift_report.
    """

    output_name: ClassVar[str] = "risk_tier_mapping_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("risk_tier_mapping_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RollbackPlanReceipt(L5Receipt):
    """L5 doctrine output ``rollback_plan_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: rollback_plan_receipt.
    """

    output_name: ClassVar[str] = "rollback_plan_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("rollback_plan_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RouteBudgetDriftReport(L5Report):
    """L5 doctrine output ``route_budget_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: route_budget_drift_report.
    """

    output_name: ClassVar[str] = "route_budget_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("route_budget_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RouteContractIntegrityReport(L5Report):
    """L5 doctrine output ``route_contract_integrity_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: route_contract_integrity_report.
    """

    output_name: ClassVar[str] = "route_contract_integrity_report"
    output_names: ClassVar[tuple[str, ...]] = ("route_contract_integrity_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RouteTopologyDriftReport(L5Report):
    """L5 doctrine output ``route_topology_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: route_topology_drift_report.
    """

    output_name: ClassVar[str] = "route_topology_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("route_topology_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RouteTopologyStaticReport(L5Report):
    """L5 doctrine output ``route_topology_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: route_topology_static_report.
    """

    output_name: ClassVar[str] = "route_topology_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("route_topology_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RouteWorkflowDriftReport(L5Report):
    """L5 doctrine output ``RouteWorkflowDriftReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: RouteWorkflowDriftReport, route_workflow_drift_report.
    """

    output_name: ClassVar[str] = "RouteWorkflowDriftReport"
    output_names: ClassVar[tuple[str, ...]] = ("RouteWorkflowDriftReport", "route_workflow_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SectorOverlayDriftReport(L5Report):
    """L5 doctrine output ``sector_overlay_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: sector_overlay_drift_report.
    """

    output_name: ClassVar[str] = "sector_overlay_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("sector_overlay_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaleRegistryRef(L5Ref):
    """L5 doctrine output ``stale_registry_ref`` (kind=ref).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: stale_registry_ref.
    """

    output_name: ClassVar[str] = "stale_registry_ref"
    output_names: ClassVar[tuple[str, ...]] = ("stale_registry_ref",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class StaleWaiverReport(L5Report):
    """L5 doctrine output ``stale_waiver_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: stale_waiver_report.
    """

    output_name: ClassVar[str] = "stale_waiver_report"
    output_names: ClassVar[tuple[str, ...]] = ("stale_waiver_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StandardsFingerprintDriftReport(L5Report):
    """L5 doctrine output ``standards_fingerprint_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: standards_fingerprint_drift_report.
    """

    output_name: ClassVar[str] = "standards_fingerprint_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("standards_fingerprint_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticAuditGapReport(L5Report):
    """L5 doctrine output ``static_audit_gap_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_audit_gap_report.
    """

    output_name: ClassVar[str] = "static_audit_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_audit_gap_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticBypassWrapperReport(L5Report):
    """L5 doctrine output ``StaticBypassWrapperReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: StaticBypassWrapperReport, static_bypass_wrapper_report.
    """

    output_name: ClassVar[str] = "StaticBypassWrapperReport"
    output_names: ClassVar[tuple[str, ...]] = ("StaticBypassWrapperReport", "static_bypass_wrapper_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticCertificationReadinessReport(L5Report):
    """L5 doctrine output ``StaticCertificationReadinessReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: StaticCertificationReadinessReport, static_certification_readiness_report.
    """

    output_name: ClassVar[str] = "StaticCertificationReadinessReport"
    output_names: ClassVar[tuple[str, ...]] = ("StaticCertificationReadinessReport", "static_certification_readiness_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticDriftEvidencePacket(L5Packet):
    """L5 doctrine output ``StaticDriftEvidencePacket`` (kind=packet).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: StaticDriftEvidencePacket.
    """

    output_name: ClassVar[str] = "StaticDriftEvidencePacket"
    output_names: ClassVar[tuple[str, ...]] = ("StaticDriftEvidencePacket",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class StaticDriftHashReceipt(L5Receipt):
    """L5 doctrine output ``static_drift_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_drift_hash_receipt.
    """

    output_name: ClassVar[str] = "static_drift_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_drift_hash_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticDriftReport(L5Report):
    """L5 doctrine output ``static_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_drift_report.
    """

    output_name: ClassVar[str] = "static_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticGovernanceAuditReceipt(L5Receipt):
    """L5 doctrine output ``static_governance_audit_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_governance_audit_receipt.
    """

    output_name: ClassVar[str] = "static_governance_audit_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_governance_audit_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticGovernanceReplayReceipt(L5Receipt):
    """L5 doctrine output ``static_governance_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_governance_replay_receipt.
    """

    output_name: ClassVar[str] = "static_governance_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_governance_replay_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticGovernanceReviewPacket(L5Packet):
    """L5 doctrine output ``StaticGovernanceReviewPacket`` (kind=packet).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: StaticGovernanceReviewPacket.
    """

    output_name: ClassVar[str] = "StaticGovernanceReviewPacket"
    output_names: ClassVar[tuple[str, ...]] = ("StaticGovernanceReviewPacket",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class StaticGovernanceStatus(L5Status):
    """L5 doctrine output ``static_governance_status`` (kind=status).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_governance_status.
    """

    output_name: ClassVar[str] = "static_governance_status"
    output_names: ClassVar[tuple[str, ...]] = ("static_governance_status",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("clean", "drift_detected", "weakening_detected", "waiver_required", "adr_required", "unresolved",)
    value_enum: ClassVar[type] = StaticGovernanceStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class StaticReadinessStatusReceipt(L5Receipt):
    """L5 doctrine output ``static_readiness_status_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_readiness_status_receipt.
    """

    output_name: ClassVar[str] = "static_readiness_status_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_readiness_status_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticReconstructionPacket(L5Packet):
    """L5 doctrine output ``static_reconstruction_packet`` (kind=packet).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_reconstruction_packet.
    """

    output_name: ClassVar[str] = "static_reconstruction_packet"
    output_names: ClassVar[tuple[str, ...]] = ("static_reconstruction_packet",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class StaticRegressionEvidenceReport(L5Report):
    """L5 doctrine output ``StaticRegressionEvidenceReport`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: StaticRegressionEvidenceReport, static_regression_evidence_report.
    """

    output_name: ClassVar[str] = "StaticRegressionEvidenceReport"
    output_names: ClassVar[tuple[str, ...]] = ("StaticRegressionEvidenceReport", "static_regression_evidence_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticRegressionGapReport(L5Report):
    """L5 doctrine output ``static_regression_gap_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_regression_gap_report.
    """

    output_name: ClassVar[str] = "static_regression_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_regression_gap_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticRegressionHashReceipt(L5Receipt):
    """L5 doctrine output ``static_regression_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_regression_hash_receipt.
    """

    output_name: ClassVar[str] = "static_regression_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_regression_hash_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticRegressionStatus(L5Status):
    """L5 doctrine output ``static_regression_status`` (kind=status).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_regression_status.
    """

    output_name: ClassVar[str] = "static_regression_status"
    output_names: ClassVar[tuple[str, ...]] = ("static_regression_status",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("clean", "regression_detected", "baseline_missing", "comparison_incomplete",)
    value_enum: ClassVar[type] = StaticRegressionStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class StaticReplayGapReport(L5Report):
    """L5 doctrine output ``static_replay_gap_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_replay_gap_report.
    """

    output_name: ClassVar[str] = "static_replay_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_replay_gap_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticReportHashChainReceipt(L5Receipt):
    """L5 doctrine output ``static_report_hash_chain_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_report_hash_chain_receipt.
    """

    output_name: ClassVar[str] = "static_report_hash_chain_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_report_hash_chain_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticReviewGapReport(L5Report):
    """L5 doctrine output ``static_review_gap_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_review_gap_report.
    """

    output_name: ClassVar[str] = "static_review_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_review_gap_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticReviewPacketHashReceipt(L5Receipt):
    """L5 doctrine output ``static_review_packet_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_review_packet_hash_receipt.
    """

    output_name: ClassVar[str] = "static_review_packet_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_review_packet_hash_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticReviewPacketReceipt(L5Receipt):
    """L5 doctrine output ``static_review_packet_receipt`` (kind=receipt).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: static_review_packet_receipt.
    """

    output_name: ClassVar[str] = "static_review_packet_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_review_packet_receipt",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StructureDriftStatus(L5Status):
    """L5 doctrine output ``structure_drift_status`` (kind=status).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: structure_drift_status.
    """

    output_name: ClassVar[str] = "structure_drift_status"
    output_names: ClassVar[tuple[str, ...]] = ("structure_drift_status",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("none", "detected", "unresolved", "waiver_required",)
    value_enum: ClassVar[type] = StructureDriftStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class ToolRegistryDriftReport(L5Report):
    """L5 doctrine output ``tool_registry_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: tool_registry_drift_report.
    """

    output_name: ClassVar[str] = "tool_registry_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("tool_registry_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnauthorizedConnectorClientReport(L5Report):
    """L5 doctrine output ``unauthorized_connector_client_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: unauthorized_connector_client_report.
    """

    output_name: ClassVar[str] = "unauthorized_connector_client_report"
    output_names: ClassVar[tuple[str, ...]] = ("unauthorized_connector_client_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnauthorizedHttpClientReport(L5Report):
    """L5 doctrine output ``unauthorized_http_client_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: unauthorized_http_client_report.
    """

    output_name: ClassVar[str] = "unauthorized_http_client_report"
    output_names: ClassVar[tuple[str, ...]] = ("unauthorized_http_client_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnresolvedStaticGapReport(L5Report):
    """L5 doctrine output ``unresolved_static_gap_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: unresolved_static_gap_report.
    """

    output_name: ClassVar[str] = "unresolved_static_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("unresolved_static_gap_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UwgBypassStaticReport(L5Report):
    """L5 doctrine output ``uwg_bypass_static_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: uwg_bypass_static_report.
    """

    output_name: ClassVar[str] = "uwg_bypass_static_report"
    output_names: ClassVar[tuple[str, ...]] = ("uwg_bypass_static_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WaiverCompatibilityReport(L5Report):
    """L5 doctrine output ``waiver_compatibility_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: waiver_compatibility_report.
    """

    output_name: ClassVar[str] = "waiver_compatibility_report"
    output_names: ClassVar[tuple[str, ...]] = ("waiver_compatibility_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WaiverPresenceReport(L5Report):
    """L5 doctrine output ``waiver_presence_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: waiver_presence_report.
    """

    output_name: ClassVar[str] = "waiver_presence_report"
    output_names: ClassVar[tuple[str, ...]] = ("waiver_presence_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WaiverScopeMismatchReport(L5Report):
    """L5 doctrine output ``waiver_scope_mismatch_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: waiver_scope_mismatch_report.
    """

    output_name: ClassVar[str] = "waiver_scope_mismatch_report"
    output_names: ClassVar[tuple[str, ...]] = ("waiver_scope_mismatch_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WaiverStatus(L5Status):
    """L5 doctrine output ``waiver_status`` (kind=status).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: waiver_status.
    """

    output_name: ClassVar[str] = "waiver_status"
    output_names: ClassVar[tuple[str, ...]] = ("waiver_status",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = ("not_required", "required", "present", "missing", "stale", "incompatible",)
    value_enum: ClassVar[type] = WaiverStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class WeakenedDefaultReport(L5Report):
    """L5 doctrine output ``weakened_default_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: weakened_default_report.
    """

    output_name: ClassVar[str] = "weakened_default_report"
    output_names: ClassVar[tuple[str, ...]] = ("weakened_default_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WorkflowBoundaryDriftReport(L5Report):
    """L5 doctrine output ``workflow_boundary_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: workflow_boundary_drift_report.
    """

    output_name: ClassVar[str] = "workflow_boundary_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("workflow_boundary_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WrapperAuthorityExpansionReport(L5Report):
    """L5 doctrine output ``wrapper_authority_expansion_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: wrapper_authority_expansion_report.
    """

    output_name: ClassVar[str] = "wrapper_authority_expansion_report"
    output_names: ClassVar[tuple[str, ...]] = ("wrapper_authority_expansion_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WrapperTargetResolutionReport(L5Report):
    """L5 doctrine output ``wrapper_target_resolution_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: wrapper_target_resolution_report.
    """

    output_name: ClassVar[str] = "wrapper_target_resolution_report"
    output_names: ClassVar[tuple[str, ...]] = ("wrapper_target_resolution_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WritePathDriftReport(L5Report):
    """L5 doctrine output ``write_path_drift_report`` (kind=report).

    Source doctrine: ``00.7_L5_Static_Governance_and_Structure_Drift_detailed.md``.
    Canonical doctrine names: write_path_drift_report.
    """

    output_name: ClassVar[str] = "write_path_drift_report"
    output_names: ClassVar[tuple[str, ...]] = ("write_path_drift_report",)
    source_doc: ClassVar[str] = "00.7_L5_Static_Governance_and_Structure_Drift_detailed.md"
    output_kind: ClassVar[str] = "report"


__all__ = [
    "ADRRequiredReport",
    "AdgSnapshotRef",
    "AdrRequiredReport",
    "AdrStatus",
    "AffectedAuthoritySurfaceMap",
    "AgentRegistryDriftReport",
    "ArchitectureDriftGapReport",
    "ArchitectureDriftReport",
    "BranchOrCommitRef",
    "BypassEvidenceStatus",
    "BypassWrapperWaiverReport",
    "ConfigWithLogicStaticReport",
    "ConnectorAuditRequirementDriftReport",
    "ConnectorConfigDriftReport",
    "ConnectorCredentialPolicyDriftReport",
    "ConnectorDomainDriftReport",
    "ConnectorGrantDriftReport",
    "ConnectorRegistryDriftReport",
    "ConnectorRetentionDriftReport",
    "ConnectorScopeWideningReport",
    "CurrentAdgSnapshotRef",
    "DeletedGateStaticReport",
    "DependencyDirectionDriftReport",
    "DirectExternalWriteStaticReport",
    "DirectSdkBypassStaticReport",
    "DirectWritePathStaticReport",
    "DirectWriteWaiverReport",
    "DownstreamConsumerStaticReadinessMap",
    "DownstreamStaticImpactReport",
    "DownstreamStaticRegressionImpactReport",
    "DriftCategoryMap",
    "EgressWrapperStaticReport",
    "ExceptionTaxonomyDriftReport",
    "FallbackChainDriftReport",
    "GoldenArchitectureSnapshotRef",
    "GoldenAuditReplaySnapshotRef",
    "GoldenConnectorSnapshotRef",
    "GoldenPolicySnapshotRef",
    "GoldenPromptSnapshotRef",
    "GoldenRegistrySnapshotRef",
    "GoldenRouteSnapshotRef",
    "GoldenSnapshotComparisonReport",
    "GoldenSnapshotGapReport",
    "GoldenSnapshotRef",
    "HardConstraintChangeReport",
    "HardcodedModelLiteralStaticReport",
    "HiddenEgressStaticReport",
    "HiddenEgressWaiverReport",
    "HitlDirectWriteStaticReport",
    "HitlThresholdDriftReport",
    "L4DirectWriteReport",
    "L6CurrentRunMutationStaticReport",
    "LayerBoundaryDriftReport",
    "LearningBoundaryDriftReport",
    "ManagedWorkflowAutonomyDriftReport",
    "MissingAuditMetadataReport",
    "MissingReplayMetadataReport",
    "NewlyIntroducedBypassReport",
    "OrphanRegistryRef",
    "OrphanRegistryReferenceReport",
    "PolicyDriftStatus",
    "PolicyWeakeningReport",
    "PolicyWeakeningWaiverReport",
    "PromptAssemblyBoundaryDriftReport",
    "PromptAuthorityBoundaryDriftReport",
    "PromptDriftReport",
    "PromptRegistryCompatibilityDriftReport",
    "PromptRegistryDriftReport",
    "PromptSchemaBindingDriftReport",
    "PromptShadowArtifactReport",
    "PromptSlotMapDriftReport",
    "PromptStablePrefixDriftReport",
    "ProposedDiffBoundaryReport",
    "RefusalTaxonomyDriftReport",
    "RegistryDigestDriftReport",
    "RegistryDriftReport",
    "RegistryDriftStatus",
    "RegistryScopeWideningReport",
    "RegistrySubstitutionStaticReport",
    "RelaxedScopeReport",
    "RetrievalBoundaryDriftReport",
    "RiskTierMappingDriftReport",
    "RollbackPlanReceipt",
    "RouteBudgetDriftReport",
    "RouteContractIntegrityReport",
    "RouteTopologyDriftReport",
    "RouteTopologyStaticReport",
    "RouteWorkflowDriftReport",
    "SectorOverlayDriftReport",
    "StaleRegistryRef",
    "StaleWaiverReport",
    "StandardsFingerprintDriftReport",
    "StaticAuditGapReport",
    "StaticBypassWrapperReport",
    "StaticCertificationReadinessReport",
    "StaticDriftEvidencePacket",
    "StaticDriftHashReceipt",
    "StaticDriftReport",
    "StaticGovernanceAuditReceipt",
    "StaticGovernanceReplayReceipt",
    "StaticGovernanceReviewPacket",
    "StaticGovernanceStatus",
    "StaticReadinessStatusReceipt",
    "StaticReconstructionPacket",
    "StaticRegressionEvidenceReport",
    "StaticRegressionGapReport",
    "StaticRegressionHashReceipt",
    "StaticRegressionStatus",
    "StaticReplayGapReport",
    "StaticReportHashChainReceipt",
    "StaticReviewGapReport",
    "StaticReviewPacketHashReceipt",
    "StaticReviewPacketReceipt",
    "StructureDriftStatus",
    "ToolRegistryDriftReport",
    "UnauthorizedConnectorClientReport",
    "UnauthorizedHttpClientReport",
    "UnresolvedStaticGapReport",
    "UwgBypassStaticReport",
    "WaiverCompatibilityReport",
    "WaiverPresenceReport",
    "WaiverScopeMismatchReport",
    "WaiverStatus",
    "WeakenedDefaultReport",
    "WorkflowBoundaryDriftReport",
    "WrapperAuthorityExpansionReport",
    "WrapperTargetResolutionReport",
    "WritePathDriftReport",
]
