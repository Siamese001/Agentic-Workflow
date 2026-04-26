"""Generated L5 contract dataclasses for ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00.1_L5_Safety_Enforcement_Plane_detailed.md``
Module: ``agentic_core.L5_safety.contracts.enforcement``
Generated count: 72 contracts

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
class AgentProfileReceipt(L5Receipt):
    """L5 doctrine output ``agent_profile_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: agent_profile_receipt.
    """

    output_name: ClassVar[str] = "agent_profile_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("agent_profile_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AgentRegistryValidationReport(L5Report):
    """L5 doctrine output ``agent_registry_validation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: agent_registry_validation_report.
    """

    output_name: ClassVar[str] = "agent_registry_validation_report"
    output_names: ClassVar[tuple[str, ...]] = ("agent_registry_validation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AgentRegistryViolationReport(L5Report):
    """L5 doctrine output ``agent_registry_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: agent_registry_violation_report.
    """

    output_name: ClassVar[str] = "agent_registry_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("agent_registry_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AllowedConnectorReceipt(L5Receipt):
    """L5 doctrine output ``allowed_connector_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: allowed_connector_receipt.
    """

    output_name: ClassVar[str] = "allowed_connector_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("allowed_connector_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AllowedModelReceipt(L5Receipt):
    """L5 doctrine output ``allowed_model_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: allowed_model_receipt.
    """

    output_name: ClassVar[str] = "allowed_model_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("allowed_model_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AllowedToolReceipt(L5Receipt):
    """L5 doctrine output ``allowed_tool_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: allowed_tool_receipt.
    """

    output_name: ClassVar[str] = "allowed_tool_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("allowed_tool_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuditChainIntegrityReport(L5Report):
    """L5 doctrine output ``audit_chain_integrity_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: audit_chain_integrity_report.
    """

    output_name: ClassVar[str] = "audit_chain_integrity_report"
    output_names: ClassVar[tuple[str, ...]] = ("audit_chain_integrity_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BootL5EnforcementReport(L5Report):
    """L5 doctrine output ``boot_l5_enforcement_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: boot_l5_enforcement_report.
    """

    output_name: ClassVar[str] = "boot_l5_enforcement_report"
    output_names: ClassVar[tuple[str, ...]] = ("boot_l5_enforcement_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CapabilityScopeReceipt(L5Receipt):
    """L5 doctrine output ``capability_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: capability_scope_receipt.
    """

    output_name: ClassVar[str] = "capability_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("capability_scope_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ClassificationCacheReport(L5Report):
    """L5 doctrine output ``classification_cache_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: classification_cache_report.
    """

    output_name: ClassVar[str] = "classification_cache_report"
    output_names: ClassVar[tuple[str, ...]] = ("classification_cache_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ClassificationReport(L5Report):
    """L5 doctrine output ``classification_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: classification_report.
    """

    output_name: ClassVar[str] = "classification_report"
    output_names: ClassVar[tuple[str, ...]] = ("classification_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ClassificationStatus(L5Status):
    """L5 doctrine output ``classification_status`` (kind=status).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: classification_status.
    """

    output_name: ClassVar[str] = "classification_status"
    output_names: ClassVar[tuple[str, ...]] = ("classification_status",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class ClassifierErrorReport(L5Report):
    """L5 doctrine output ``classifier_error_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: classifier_error_report.
    """

    output_name: ClassVar[str] = "classifier_error_report"
    output_names: ClassVar[tuple[str, ...]] = ("classifier_error_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CompileTimeL5EnforcementReport(L5Report):
    """L5 doctrine output ``compile_time_l5_enforcement_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: compile_time_l5_enforcement_report.
    """

    output_name: ClassVar[str] = "compile_time_l5_enforcement_report"
    output_names: ClassVar[tuple[str, ...]] = ("compile_time_l5_enforcement_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ComponentStaticRegressionReport(L5Report):
    """L5 doctrine output ``component_static_regression_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: component_static_regression_report.
    """

    output_name: ClassVar[str] = "component_static_regression_report"
    output_names: ClassVar[tuple[str, ...]] = ("component_static_regression_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConfigWithLogicReport(L5Report):
    """L5 doctrine output ``config_with_logic_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: config_with_logic_report.
    """

    output_name: ClassVar[str] = "config_with_logic_report"
    output_names: ClassVar[tuple[str, ...]] = ("config_with_logic_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorScopeViolationReport(L5Report):
    """L5 doctrine output ``connector_scope_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: connector_scope_violation_report.
    """

    output_name: ClassVar[str] = "connector_scope_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_scope_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CriticalRegistryGapReport(L5Report):
    """L5 doctrine output ``critical_registry_gap_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: critical_registry_gap_report.
    """

    output_name: ClassVar[str] = "critical_registry_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("critical_registry_gap_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DelegationDepthViolationReport(L5Report):
    """L5 doctrine output ``delegation_depth_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: delegation_depth_violation_report.
    """

    output_name: ClassVar[str] = "delegation_depth_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("delegation_depth_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DelegationScopeReceipt(L5Receipt):
    """L5 doctrine output ``delegation_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: delegation_scope_receipt.
    """

    output_name: ClassVar[str] = "delegation_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("delegation_scope_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class DirectBypassAbsenceReceipt(L5Receipt):
    """L5 doctrine output ``direct_bypass_absence_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: direct_bypass_absence_receipt.
    """

    output_name: ClassVar[str] = "direct_bypass_absence_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("direct_bypass_absence_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class DirectSdkBypassReport(L5Report):
    """L5 doctrine output ``direct_sdk_bypass_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: direct_sdk_bypass_report.
    """

    output_name: ClassVar[str] = "direct_sdk_bypass_report"
    output_names: ClassVar[tuple[str, ...]] = ("direct_sdk_bypass_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DirectWritePathReport(L5Report):
    """L5 doctrine output ``direct_write_path_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: direct_write_path_report.
    """

    output_name: ClassVar[str] = "direct_write_path_report"
    output_names: ClassVar[tuple[str, ...]] = ("direct_write_path_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DualTagConflictReport(L5Report):
    """L5 doctrine output ``dual_tag_conflict_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: dual_tag_conflict_report.
    """

    output_name: ClassVar[str] = "dual_tag_conflict_report"
    output_names: ClassVar[tuple[str, ...]] = ("dual_tag_conflict_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class EgressEvidenceStatus(L5Status):
    """L5 doctrine output ``egress_evidence_status`` (kind=status).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: egress_evidence_status.
    """

    output_name: ClassVar[str] = "egress_evidence_status"
    output_names: ClassVar[tuple[str, ...]] = ("egress_evidence_status",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class EnforcementReceiptStatus(L5Status):
    """L5 doctrine output ``enforcement_receipt_status`` (kind=status).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: enforcement_receipt_status.
    """

    output_name: ClassVar[str] = "enforcement_receipt_status"
    output_names: ClassVar[tuple[str, ...]] = ("enforcement_receipt_status",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class ExecutionModeReceipt(L5Receipt):
    """L5 doctrine output ``execution_mode_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: execution_mode_receipt.
    """

    output_name: ClassVar[str] = "execution_mode_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("execution_mode_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ExecutionModeViolationReport(L5Report):
    """L5 doctrine output ``execution_mode_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: execution_mode_violation_report.
    """

    output_name: ClassVar[str] = "execution_mode_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("execution_mode_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class GatewayAuditLog(L5Log):
    """L5 doctrine output ``gateway_audit_log`` (kind=log).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: gateway_audit_log.
    """

    output_name: ClassVar[str] = "gateway_audit_log"
    output_names: ClassVar[tuple[str, ...]] = ("gateway_audit_log",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "log"


@dataclass(frozen=True, slots=True)
class GatewayInitReceipt(L5Receipt):
    """L5 doctrine output ``gateway_init_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: gateway_init_receipt.
    """

    output_name: ClassVar[str] = "gateway_init_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("gateway_init_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class GatewayStatus(L5Status):
    """L5 doctrine output ``gateway_status`` (kind=status).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: gateway_status.
    """

    output_name: ClassVar[str] = "gateway_status"
    output_names: ClassVar[tuple[str, ...]] = ("gateway_status",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class HiddenEgressPathReport(L5Report):
    """L5 doctrine output ``HiddenEgressPathReport`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: HiddenEgressPathReport, hidden_egress_path_report.
    """

    output_name: ClassVar[str] = "HiddenEgressPathReport"
    output_names: ClassVar[tuple[str, ...]] = ("HiddenEgressPathReport", "hidden_egress_path_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HybridAuthoritySmellReport(L5Report):
    """L5 doctrine output ``hybrid_authority_smell_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: hybrid_authority_smell_report.
    """

    output_name: ClassVar[str] = "hybrid_authority_smell_report"
    output_names: ClassVar[tuple[str, ...]] = ("hybrid_authority_smell_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ImportBoundaryReport(L5Report):
    """L5 doctrine output ``import_boundary_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: import_boundary_report.
    """

    output_name: ClassVar[str] = "import_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("import_boundary_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class InjectionScanReport(L5Report):
    """L5 doctrine output ``injection_scan_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: injection_scan_report.
    """

    output_name: ClassVar[str] = "injection_scan_report"
    output_names: ClassVar[tuple[str, ...]] = ("injection_scan_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class L5EnforcementViolationReport(L5Report):
    """L5 doctrine output ``l5_enforcement_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: l5_enforcement_violation_report.
    """

    output_name: ClassVar[str] = "l5_enforcement_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("l5_enforcement_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class LlmGatewayValidationReceipt(L5Receipt):
    """L5 doctrine output ``llm_gateway_validation_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: llm_gateway_validation_receipt.
    """

    output_name: ClassVar[str] = "llm_gateway_validation_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("llm_gateway_validation_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ModelEgressReceipt(L5Receipt):
    """L5 doctrine output ``ModelEgressReceipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: ModelEgressReceipt, model_egress_receipt.
    """

    output_name: ClassVar[str] = "ModelEgressReceipt"
    output_names: ClassVar[tuple[str, ...]] = ("ModelEgressReceipt", "model_egress_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ModelResolutionReceipt(L5Receipt):
    """L5 doctrine output ``model_resolution_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: model_resolution_receipt.
    """

    output_name: ClassVar[str] = "model_resolution_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("model_resolution_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ModelScopeReceipt(L5Receipt):
    """L5 doctrine output ``model_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: model_scope_receipt.
    """

    output_name: ClassVar[str] = "model_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("model_scope_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ModelScopeViolationReport(L5Report):
    """L5 doctrine output ``model_scope_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: model_scope_violation_report.
    """

    output_name: ClassVar[str] = "model_scope_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("model_scope_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ModelSubstitutionReport(L5Report):
    """L5 doctrine output ``ModelSubstitutionReport`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: ModelSubstitutionReport, model_substitution_report.
    """

    output_name: ClassVar[str] = "ModelSubstitutionReport"
    output_names: ClassVar[tuple[str, ...]] = ("ModelSubstitutionReport", "model_substitution_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PathValidationReport(L5Report):
    """L5 doctrine output ``path_validation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: path_validation_report.
    """

    output_name: ClassVar[str] = "path_validation_report"
    output_names: ClassVar[tuple[str, ...]] = ("path_validation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptHashReceipt(L5Receipt):
    """L5 doctrine output ``prompt_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: prompt_hash_receipt.
    """

    output_name: ClassVar[str] = "prompt_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_hash_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PromptRef(L5Ref):
    """L5 doctrine output ``prompt_ref`` (kind=ref).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: prompt_ref.
    """

    output_name: ClassVar[str] = "prompt_ref"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_ref",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ProviderBypassScanReport(L5Report):
    """L5 doctrine output ``provider_bypass_scan_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: provider_bypass_scan_report.
    """

    output_name: ClassVar[str] = "provider_bypass_scan_report"
    output_names: ClassVar[tuple[str, ...]] = ("provider_bypass_scan_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ProviderHealthReport(L5Report):
    """L5 doctrine output ``provider_health_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: provider_health_report.
    """

    output_name: ClassVar[str] = "provider_health_report"
    output_names: ClassVar[tuple[str, ...]] = ("provider_health_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ProviderLaneReceipt(L5Receipt):
    """L5 doctrine output ``ProviderLaneReceipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: ProviderLaneReceipt, provider_lane_receipt.
    """

    output_name: ClassVar[str] = "ProviderLaneReceipt"
    output_names: ClassVar[tuple[str, ...]] = ("ProviderLaneReceipt", "provider_lane_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ProviderResolutionMapReceipt(L5Receipt):
    """L5 doctrine output ``provider_resolution_map_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: provider_resolution_map_receipt.
    """

    output_name: ClassVar[str] = "provider_resolution_map_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("provider_resolution_map_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RegistryDigestReceipt(L5Receipt):
    """L5 doctrine output ``registry_digest_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: registry_digest_receipt.
    """

    output_name: ClassVar[str] = "registry_digest_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("registry_digest_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RegistryFreezeReceipt(L5Receipt):
    """L5 doctrine output ``registry_freeze_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: registry_freeze_receipt.
    """

    output_name: ClassVar[str] = "registry_freeze_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("registry_freeze_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RegistryIntegrityViolationReport(L5Report):
    """L5 doctrine output ``registry_integrity_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: registry_integrity_violation_report.
    """

    output_name: ClassVar[str] = "registry_integrity_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_integrity_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryStatus(L5Status):
    """L5 doctrine output ``registry_status`` (kind=status).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: registry_status.
    """

    output_name: ClassVar[str] = "registry_status"
    output_names: ClassVar[tuple[str, ...]] = ("registry_status",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class RegistrySubstitutionReport(L5Report):
    """L5 doctrine output ``registry_substitution_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: registry_substitution_report.
    """

    output_name: ClassVar[str] = "registry_substitution_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_substitution_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryValidationReport(L5Report):
    """L5 doctrine output ``registry_validation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: registry_validation_report.
    """

    output_name: ClassVar[str] = "registry_validation_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_validation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReplayBindingReceipt(L5Receipt):
    """L5 doctrine output ``replay_binding_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: replay_binding_receipt.
    """

    output_name: ClassVar[str] = "replay_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("replay_binding_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReplayGatewayViolationReport(L5Report):
    """L5 doctrine output ``replay_gateway_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: replay_gateway_violation_report.
    """

    output_name: ClassVar[str] = "replay_gateway_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("replay_gateway_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReplayModeReceipt(L5Receipt):
    """L5 doctrine output ``replay_mode_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: replay_mode_receipt.
    """

    output_name: ClassVar[str] = "replay_mode_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("replay_mode_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RootProtectionReport(L5Report):
    """L5 doctrine output ``root_protection_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: root_protection_report.
    """

    output_name: ClassVar[str] = "root_protection_report"
    output_names: ClassVar[tuple[str, ...]] = ("root_protection_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RuntimeL5EnforcementReceipt(L5Receipt):
    """L5 doctrine output ``runtime_l5_enforcement_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: runtime_l5_enforcement_receipt.
    """

    output_name: ClassVar[str] = "runtime_l5_enforcement_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_l5_enforcement_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SafeExtractionReceipt(L5Receipt):
    """L5 doctrine output ``safe_extraction_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: safe_extraction_receipt.
    """

    output_name: ClassVar[str] = "safe_extraction_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("safe_extraction_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SandboxEnvelope(L5Envelope):
    """L5 doctrine output ``sandbox_envelope`` (kind=envelope).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: sandbox_envelope.
    """

    output_name: ClassVar[str] = "sandbox_envelope"
    output_names: ClassVar[tuple[str, ...]] = ("sandbox_envelope",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "envelope"


@dataclass(frozen=True, slots=True)
class SandboxScopeReceipt(L5Receipt):
    """L5 doctrine output ``sandbox_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: sandbox_scope_receipt.
    """

    output_name: ClassVar[str] = "sandbox_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("sandbox_scope_receipt",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SanitizedPromptRef(L5Ref):
    """L5 doctrine output ``sanitized_prompt_ref`` (kind=ref).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: sanitized_prompt_ref.
    """

    output_name: ClassVar[str] = "sanitized_prompt_ref"
    output_names: ClassVar[tuple[str, ...]] = ("sanitized_prompt_ref",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class SovereignKernelIntegrityReport(L5Report):
    """L5 doctrine output ``sovereign_kernel_integrity_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: sovereign_kernel_integrity_report.
    """

    output_name: ClassVar[str] = "sovereign_kernel_integrity_report"
    output_names: ClassVar[tuple[str, ...]] = ("sovereign_kernel_integrity_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StructureStatus(L5Status):
    """L5 doctrine output ``structure_status`` (kind=status).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: structure_status.
    """

    output_name: ClassVar[str] = "structure_status"
    output_names: ClassVar[tuple[str, ...]] = ("structure_status",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class StructureValidationReport(L5Report):
    """L5 doctrine output ``structure_validation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: structure_validation_report.
    """

    output_name: ClassVar[str] = "structure_validation_report"
    output_names: ClassVar[tuple[str, ...]] = ("structure_validation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TestPlacementReport(L5Report):
    """L5 doctrine output ``test_placement_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: test_placement_report.
    """

    output_name: ClassVar[str] = "test_placement_report"
    output_names: ClassVar[tuple[str, ...]] = ("test_placement_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ToolScopeViolationReport(L5Report):
    """L5 doctrine output ``tool_scope_violation_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: tool_scope_violation_report.
    """

    output_name: ClassVar[str] = "tool_scope_violation_report"
    output_names: ClassVar[tuple[str, ...]] = ("tool_scope_violation_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TypeSsotReport(L5Report):
    """L5 doctrine output ``type_ssot_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: type_ssot_report.
    """

    output_name: ClassVar[str] = "type_ssot_report"
    output_names: ClassVar[tuple[str, ...]] = ("type_ssot_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnknownClassificationReport(L5Report):
    """L5 doctrine output ``unknown_classification_report`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: unknown_classification_report.
    """

    output_name: ClassVar[str] = "unknown_classification_report"
    output_names: ClassVar[tuple[str, ...]] = ("unknown_classification_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WaiverRequiredReport(L5Report):
    """L5 doctrine output ``WaiverRequiredReport`` (kind=report).

    Source doctrine: ``00.1_L5_Safety_Enforcement_Plane_detailed.md``.
    Canonical doctrine names: WaiverRequiredReport, waiver_required_report.
    """

    output_name: ClassVar[str] = "WaiverRequiredReport"
    output_names: ClassVar[tuple[str, ...]] = ("WaiverRequiredReport", "waiver_required_report",)
    source_doc: ClassVar[str] = "00.1_L5_Safety_Enforcement_Plane_detailed.md"
    output_kind: ClassVar[str] = "report"


__all__ = [
    "AgentProfileReceipt",
    "AgentRegistryValidationReport",
    "AgentRegistryViolationReport",
    "AllowedConnectorReceipt",
    "AllowedModelReceipt",
    "AllowedToolReceipt",
    "AuditChainIntegrityReport",
    "BootL5EnforcementReport",
    "CapabilityScopeReceipt",
    "ClassificationCacheReport",
    "ClassificationReport",
    "ClassificationStatus",
    "ClassifierErrorReport",
    "CompileTimeL5EnforcementReport",
    "ComponentStaticRegressionReport",
    "ConfigWithLogicReport",
    "ConnectorScopeViolationReport",
    "CriticalRegistryGapReport",
    "DelegationDepthViolationReport",
    "DelegationScopeReceipt",
    "DirectBypassAbsenceReceipt",
    "DirectSdkBypassReport",
    "DirectWritePathReport",
    "DualTagConflictReport",
    "EgressEvidenceStatus",
    "EnforcementReceiptStatus",
    "ExecutionModeReceipt",
    "ExecutionModeViolationReport",
    "GatewayAuditLog",
    "GatewayInitReceipt",
    "GatewayStatus",
    "HiddenEgressPathReport",
    "HybridAuthoritySmellReport",
    "ImportBoundaryReport",
    "InjectionScanReport",
    "L5EnforcementViolationReport",
    "LlmGatewayValidationReceipt",
    "ModelEgressReceipt",
    "ModelResolutionReceipt",
    "ModelScopeReceipt",
    "ModelScopeViolationReport",
    "ModelSubstitutionReport",
    "PathValidationReport",
    "PromptHashReceipt",
    "PromptRef",
    "ProviderBypassScanReport",
    "ProviderHealthReport",
    "ProviderLaneReceipt",
    "ProviderResolutionMapReceipt",
    "RegistryDigestReceipt",
    "RegistryFreezeReceipt",
    "RegistryIntegrityViolationReport",
    "RegistryStatus",
    "RegistrySubstitutionReport",
    "RegistryValidationReport",
    "ReplayBindingReceipt",
    "ReplayGatewayViolationReport",
    "ReplayModeReceipt",
    "RootProtectionReport",
    "RuntimeL5EnforcementReceipt",
    "SafeExtractionReceipt",
    "SandboxEnvelope",
    "SandboxScopeReceipt",
    "SanitizedPromptRef",
    "SovereignKernelIntegrityReport",
    "StructureStatus",
    "StructureValidationReport",
    "TestPlacementReport",
    "ToolScopeViolationReport",
    "TypeSsotReport",
    "UnknownClassificationReport",
    "WaiverRequiredReport",
]
