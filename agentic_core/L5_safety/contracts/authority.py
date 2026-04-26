"""Generated L5 contract dataclasses for ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``
Module: ``agentic_core.L5_safety.contracts.authority``
Generated count: 142 contracts

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
    AuthorityContextStatus,
    BlueprintBindingStatus,
    CapabilityScopeStatus,
    PolicyBindingStatus,
    PrincipalChainStatus,
    RecertificationStatus,
    RegistryBindingStatus,
    ReplayBindingStatus,
    SandboxBindingStatus,
)


@dataclass(frozen=True, slots=True)
class AffectedConsumersReport(L5Report):
    """L5 doctrine output ``affected_consumers_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: affected_consumers_report.
    """

    output_name: ClassVar[str] = "affected_consumers_report"
    output_names: ClassVar[tuple[str, ...]] = ("affected_consumers_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AgentDigestReceipt(L5Receipt):
    """L5 doctrine output ``agent_digest_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: agent_digest_receipt.
    """

    output_name: ClassVar[str] = "agent_digest_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("agent_digest_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AgentRegistryGapReport(L5Report):
    """L5 doctrine output ``agent_registry_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: agent_registry_gap_report.
    """

    output_name: ClassVar[str] = "agent_registry_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("agent_registry_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AgentRegistryReceipt(L5Receipt):
    """L5 doctrine output ``agent_registry_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: agent_registry_receipt.
    """

    output_name: ClassVar[str] = "agent_registry_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("agent_registry_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AgentScopeReceipt(L5Receipt):
    """L5 doctrine output ``agent_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: agent_scope_receipt.
    """

    output_name: ClassVar[str] = "agent_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("agent_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AgentSubstitutionReport(L5Report):
    """L5 doctrine output ``agent_substitution_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: agent_substitution_report.
    """

    output_name: ClassVar[str] = "agent_substitution_report"
    output_names: ClassVar[tuple[str, ...]] = ("agent_substitution_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AuthorityContextReceipt(L5Receipt):
    """L5 doctrine output ``authority_context_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: authority_context_receipt.
    """

    output_name: ClassVar[str] = "authority_context_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("authority_context_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuthorityContextStatus(L5Status):
    """L5 doctrine output ``authority_context_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: authority_context_status.
    """

    output_name: ClassVar[str] = "authority_context_status"
    output_names: ClassVar[tuple[str, ...]] = ("authority_context_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "bound",
        "incomplete",
        "stale",
        "mismatched",
        "substituted",
        "unauthorized",
    )
    value_enum: ClassVar[type] = AuthorityContextStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class AuthorityFieldIntegrityReport(L5Report):
    """L5 doctrine output ``authority_field_integrity_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: authority_field_integrity_report.
    """

    output_name: ClassVar[str] = "authority_field_integrity_report"
    output_names: ClassVar[tuple[str, ...]] = ("authority_field_integrity_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AuthorityGapReport(L5Report):
    """L5 doctrine output ``authority_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: authority_gap_report.
    """

    output_name: ClassVar[str] = "authority_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("authority_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AuthorityIssuerReceipt(L5Receipt):
    """L5 doctrine output ``authority_issuer_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: authority_issuer_receipt.
    """

    output_name: ClassVar[str] = "authority_issuer_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("authority_issuer_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuthoritySourceMap(L5Map):
    """L5 doctrine output ``authority_source_map`` (kind=map).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: authority_source_map.
    """

    output_name: ClassVar[str] = "authority_source_map"
    output_names: ClassVar[tuple[str, ...]] = ("authority_source_map",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class BlueprintBindingStatus(L5Status):
    """L5 doctrine output ``blueprint_binding_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: blueprint_binding_status.
    """

    output_name: ClassVar[str] = "blueprint_binding_status"
    output_names: ClassVar[tuple[str, ...]] = ("blueprint_binding_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "current",
        "missing",
        "stale",
        "mismatched",
    )
    value_enum: ClassVar[type] = BlueprintBindingStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class BlueprintHashReceipt(L5Receipt):
    """L5 doctrine output ``blueprint_hash_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: blueprint_hash_receipt.
    """

    output_name: ClassVar[str] = "blueprint_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("blueprint_hash_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class BlueprintLoadReceipt(L5Receipt):
    """L5 doctrine output ``blueprint_load_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: blueprint_load_receipt.
    """

    output_name: ClassVar[str] = "blueprint_load_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("blueprint_load_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class BlueprintMismatchReport(L5Report):
    """L5 doctrine output ``blueprint_mismatch_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: blueprint_mismatch_report.
    """

    output_name: ClassVar[str] = "blueprint_mismatch_report"
    output_names: ClassVar[tuple[str, ...]] = ("blueprint_mismatch_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BlueprintRegistryCompatibilityReport(L5Report):
    """L5 doctrine output ``blueprint_registry_compatibility_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: blueprint_registry_compatibility_report.
    """

    output_name: ClassVar[str] = "blueprint_registry_compatibility_report"
    output_names: ClassVar[tuple[str, ...]] = ("blueprint_registry_compatibility_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BootL5AuthorityReport(L5Report):
    """L5 doctrine output ``boot_l5_authority_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: boot_l5_authority_report.
    """

    output_name: ClassVar[str] = "boot_l5_authority_report"
    output_names: ClassVar[tuple[str, ...]] = ("boot_l5_authority_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BroadScopeReport(L5Report):
    """L5 doctrine output ``broad_scope_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: broad_scope_report.
    """

    output_name: ClassVar[str] = "broad_scope_report"
    output_names: ClassVar[tuple[str, ...]] = ("broad_scope_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CapabilityExpirationReceipt(L5Receipt):
    """L5 doctrine output ``capability_expiration_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: capability_expiration_receipt.
    """

    output_name: ClassVar[str] = "capability_expiration_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("capability_expiration_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CapabilityGapReport(L5Report):
    """L5 doctrine output ``capability_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: capability_gap_report.
    """

    output_name: ClassVar[str] = "capability_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("capability_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CapabilityScopeStatus(L5Status):
    """L5 doctrine output ``capability_scope_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: capability_scope_status.
    """

    output_name: ClassVar[str] = "capability_scope_status"
    output_names: ClassVar[tuple[str, ...]] = ("capability_scope_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "sufficient",
        "missing",
        "too_broad",
        "too_narrow",
        "expired",
        "forged",
    )
    value_enum: ClassVar[type] = CapabilityScopeStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class CapabilityTokenRef(L5Ref):
    """L5 doctrine output ``capability_token_ref`` (kind=ref).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: capability_token_ref.
    """

    output_name: ClassVar[str] = "capability_token_ref"
    output_names: ClassVar[tuple[str, ...]] = ("capability_token_ref",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class CapabilityWideningReport(L5Report):
    """L5 doctrine output ``capability_widening_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: capability_widening_report.
    """

    output_name: ClassVar[str] = "capability_widening_report"
    output_names: ClassVar[tuple[str, ...]] = ("capability_widening_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ChangedAuthorityFieldReport(L5Report):
    """L5 doctrine output ``changed_authority_field_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: changed_authority_field_report.
    """

    output_name: ClassVar[str] = "changed_authority_field_report"
    output_names: ClassVar[tuple[str, ...]] = ("changed_authority_field_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ClockPolicyReceipt(L5Receipt):
    """L5 doctrine output ``clock_policy_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: clock_policy_receipt.
    """

    output_name: ClassVar[str] = "clock_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("clock_policy_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class CompileTimeL5AuthorityReport(L5Report):
    """L5 doctrine output ``compile_time_l5_authority_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: compile_time_l5_authority_report.
    """

    output_name: ClassVar[str] = "compile_time_l5_authority_report"
    output_names: ClassVar[tuple[str, ...]] = ("compile_time_l5_authority_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorAllowlistReceipt(L5Receipt):
    """L5 doctrine output ``connector_allowlist_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: connector_allowlist_receipt.
    """

    output_name: ClassVar[str] = "connector_allowlist_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_allowlist_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorCredentialPolicyReceipt(L5Receipt):
    """L5 doctrine output ``connector_credential_policy_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: connector_credential_policy_receipt.
    """

    output_name: ClassVar[str] = "connector_credential_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_credential_policy_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorDomainReceipt(L5Receipt):
    """L5 doctrine output ``connector_domain_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: connector_domain_receipt.
    """

    output_name: ClassVar[str] = "connector_domain_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_domain_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorGrantReceipt(L5Receipt):
    """L5 doctrine output ``connector_grant_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: connector_grant_receipt.
    """

    output_name: ClassVar[str] = "connector_grant_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_grant_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorRegistryGapReport(L5Report):
    """L5 doctrine output ``connector_registry_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: connector_registry_gap_report.
    """

    output_name: ClassVar[str] = "connector_registry_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_registry_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ConnectorRegistryReceipt(L5Receipt):
    """L5 doctrine output ``connector_registry_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: connector_registry_receipt.
    """

    output_name: ClassVar[str] = "connector_registry_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_registry_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorScopeReceipt(L5Receipt):
    """L5 doctrine output ``connector_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: connector_scope_receipt.
    """

    output_name: ClassVar[str] = "connector_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("connector_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ConnectorSubstitutionReport(L5Report):
    """L5 doctrine output ``ConnectorSubstitutionReport`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: ConnectorSubstitutionReport, connector_substitution_report.
    """

    output_name: ClassVar[str] = "ConnectorSubstitutionReport"
    output_names: ClassVar[tuple[str, ...]] = (
        "ConnectorSubstitutionReport",
        "connector_substitution_report",
    )
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CriticalAuthorityGapReport(L5Report):
    """L5 doctrine output ``critical_authority_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: critical_authority_gap_report.
    """

    output_name: ClassVar[str] = "critical_authority_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("critical_authority_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CrossPrincipalBleedReport(L5Report):
    """L5 doctrine output ``cross_principal_bleed_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: cross_principal_bleed_report.
    """

    output_name: ClassVar[str] = "cross_principal_bleed_report"
    output_names: ClassVar[tuple[str, ...]] = ("cross_principal_bleed_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CrossTenantBleedReport(L5Report):
    """L5 doctrine output ``cross_tenant_bleed_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: cross_tenant_bleed_report.
    """

    output_name: ClassVar[str] = "cross_tenant_bleed_report"
    output_names: ClassVar[tuple[str, ...]] = ("cross_tenant_bleed_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DanglingRegistryReferenceReport(L5Report):
    """L5 doctrine output ``dangling_registry_reference_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: dangling_registry_reference_report.
    """

    output_name: ClassVar[str] = "dangling_registry_reference_report"
    output_names: ClassVar[tuple[str, ...]] = ("dangling_registry_reference_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DelegatedActorReceipt(L5Receipt):
    """L5 doctrine output ``delegated_actor_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: delegated_actor_receipt.
    """

    output_name: ClassVar[str] = "delegated_actor_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("delegated_actor_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class DelegationDepthReceipt(L5Receipt):
    """L5 doctrine output ``delegation_depth_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: delegation_depth_receipt.
    """

    output_name: ClassVar[str] = "delegation_depth_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("delegation_depth_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class DownstreamAuthorityConsumerMap(L5Map):
    """L5 doctrine output ``downstream_authority_consumer_map`` (kind=map).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: downstream_authority_consumer_map.
    """

    output_name: ClassVar[str] = "downstream_authority_consumer_map"
    output_names: ClassVar[tuple[str, ...]] = ("downstream_authority_consumer_map",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class DownstreamAuthorityOverwriteReport(L5Report):
    """L5 doctrine output ``downstream_authority_overwrite_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: downstream_authority_overwrite_report.
    """

    output_name: ClassVar[str] = "downstream_authority_overwrite_report"
    output_names: ClassVar[tuple[str, ...]] = ("downstream_authority_overwrite_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class EnvironmentDigestReceipt(L5Receipt):
    """L5 doctrine output ``environment_digest_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: environment_digest_receipt.
    """

    output_name: ClassVar[str] = "environment_digest_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("environment_digest_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class EscalationThresholdRef(L5Ref):
    """L5 doctrine output ``escalation_threshold_ref`` (kind=ref).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: escalation_threshold_ref.
    """

    output_name: ClassVar[str] = "escalation_threshold_ref"
    output_names: ClassVar[tuple[str, ...]] = ("escalation_threshold_ref",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ExternalCommitScopeReport(L5Report):
    """L5 doctrine output ``external_commit_scope_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: external_commit_scope_report.
    """

    output_name: ClassVar[str] = "external_commit_scope_report"
    output_names: ClassVar[tuple[str, ...]] = ("external_commit_scope_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class FilesystemScopeReceipt(L5Receipt):
    """L5 doctrine output ``filesystem_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: filesystem_scope_receipt.
    """

    output_name: ClassVar[str] = "filesystem_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("filesystem_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class GovernedValidationContext(L5Context):
    """L5 doctrine output ``GovernedValidationContext`` (kind=context).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: GovernedValidationContext.
    """

    output_name: ClassVar[str] = "GovernedValidationContext"
    output_names: ClassVar[tuple[str, ...]] = ("GovernedValidationContext",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "context"


@dataclass(frozen=True, slots=True)
class HITLReentryPacket(L5Packet):
    """L5 doctrine output ``HITLReentryPacket`` (kind=packet).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: HITLReentryPacket.
    """

    output_name: ClassVar[str] = "HITLReentryPacket"
    output_names: ClassVar[tuple[str, ...]] = ("HITLReentryPacket",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class HardConstraintMapRef(L5Ref):
    """L5 doctrine output ``hard_constraint_map_ref`` (kind=ref).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: hard_constraint_map_ref.
    """

    output_name: ClassVar[str] = "hard_constraint_map_ref"
    output_names: ClassVar[tuple[str, ...]] = ("hard_constraint_map_ref",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HashBindingReport(L5Report):
    """L5 doctrine output ``hash_binding_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: hash_binding_report.
    """

    output_name: ClassVar[str] = "hash_binding_report"
    output_names: ClassVar[tuple[str, ...]] = ("hash_binding_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HitlAuthorityBindingReceipt(L5Receipt):
    """L5 doctrine output ``hitl_authority_binding_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: hitl_authority_binding_receipt.
    """

    output_name: ClassVar[str] = "hitl_authority_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_authority_binding_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanActorReceipt(L5Receipt):
    """L5 doctrine output ``human_actor_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: human_actor_receipt.
    """

    output_name: ClassVar[str] = "human_actor_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_actor_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanAuthorityGapReport(L5Report):
    """L5 doctrine output ``human_authority_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: human_authority_gap_report.
    """

    output_name: ClassVar[str] = "human_authority_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_authority_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanDiffBindingReceipt(L5Receipt):
    """L5 doctrine output ``human_diff_binding_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: human_diff_binding_receipt.
    """

    output_name: ClassVar[str] = "human_diff_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_diff_binding_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReentryReplayReceipt(L5Receipt):
    """L5 doctrine output ``human_reentry_replay_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: human_reentry_replay_receipt.
    """

    output_name: ClassVar[str] = "human_reentry_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_reentry_replay_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewScopeReceipt(L5Receipt):
    """L5 doctrine output ``HumanReviewScopeReceipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: HumanReviewScopeReceipt, human_review_scope_receipt.
    """

    output_name: ClassVar[str] = "HumanReviewScopeReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "HumanReviewScopeReceipt",
        "human_review_scope_receipt",
    )
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewThresholdRef(L5Ref):
    """L5 doctrine output ``human_review_threshold_ref`` (kind=ref).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: human_review_threshold_ref.
    """

    output_name: ClassVar[str] = "human_review_threshold_ref"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_threshold_ref",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HumanReviewerScopeReceipt(L5Receipt):
    """L5 doctrine output ``human_reviewer_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: human_reviewer_scope_receipt.
    """

    output_name: ClassVar[str] = "human_reviewer_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_reviewer_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanScopeWideningReport(L5Report):
    """L5 doctrine output ``human_scope_widening_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: human_scope_widening_report.
    """

    output_name: ClassVar[str] = "human_scope_widening_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_scope_widening_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class IncidentReviewPacket(L5Packet):
    """L5 doctrine output ``IncidentReviewPacket`` (kind=packet).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: IncidentReviewPacket.
    """

    output_name: ClassVar[str] = "IncidentReviewPacket"
    output_names: ClassVar[tuple[str, ...]] = ("IncidentReviewPacket",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class InvariantMapReceipt(L5Receipt):
    """L5 doctrine output ``invariant_map_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: invariant_map_receipt.
    """

    output_name: ClassVar[str] = "invariant_map_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("invariant_map_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class LayerAuthorityGapReport(L5Report):
    """L5 doctrine output ``layer_authority_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: layer_authority_gap_report.
    """

    output_name: ClassVar[str] = "layer_authority_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("layer_authority_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class LayerAuthorityMatrixReceipt(L5Receipt):
    """L5 doctrine output ``layer_authority_matrix_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: layer_authority_matrix_receipt.
    """

    output_name: ClassVar[str] = "layer_authority_matrix_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("layer_authority_matrix_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class MemoryScopeReceipt(L5Receipt):
    """L5 doctrine output ``memory_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: memory_scope_receipt.
    """

    output_name: ClassVar[str] = "memory_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("memory_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkAllowlistReceipt(L5Receipt):
    """L5 doctrine output ``network_allowlist_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: network_allowlist_receipt.
    """

    output_name: ClassVar[str] = "network_allowlist_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("network_allowlist_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NetworkScopeReceipt(L5Receipt):
    """L5 doctrine output ``network_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: network_scope_receipt.
    """

    output_name: ClassVar[str] = "network_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("network_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NoImpliedAuthorityReceipt(L5Receipt):
    """L5 doctrine output ``no_implied_authority_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: no_implied_authority_receipt.
    """

    output_name: ClassVar[str] = "no_implied_authority_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("no_implied_authority_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class NonReplayableGapReport(L5Report):
    """L5 doctrine output ``non_replayable_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: non_replayable_gap_report.
    """

    output_name: ClassVar[str] = "non_replayable_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("non_replayable_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class OldNewAuthorityBindingDiff(L5Diff):
    """L5 doctrine output ``old_new_authority_binding_diff`` (kind=diff).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: old_new_authority_binding_diff.
    """

    output_name: ClassVar[str] = "old_new_authority_binding_diff"
    output_names: ClassVar[tuple[str, ...]] = ("old_new_authority_binding_diff",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "diff"


@dataclass(frozen=True, slots=True)
class OriginTrustManifest(L5Manifest):
    """L5 doctrine output ``OriginTrustManifest`` (kind=manifest).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: OriginTrustManifest, origin_trust_manifest.
    """

    output_name: ClassVar[str] = "OriginTrustManifest"
    output_names: ClassVar[tuple[str, ...]] = (
        "OriginTrustManifest",
        "origin_trust_manifest",
    )
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "manifest"


@dataclass(frozen=True, slots=True)
class OriginTrustManifestRef(L5Ref):
    """L5 doctrine output ``origin_trust_manifest_ref`` (kind=ref).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: origin_trust_manifest_ref.
    """

    output_name: ClassVar[str] = "origin_trust_manifest_ref"
    output_names: ClassVar[tuple[str, ...]] = ("origin_trust_manifest_ref",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class OriginalPrincipalReceipt(L5Receipt):
    """L5 doctrine output ``original_principal_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: original_principal_receipt.
    """

    output_name: ClassVar[str] = "original_principal_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("original_principal_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PacketAuthorityContextReceipt(L5Receipt):
    """L5 doctrine output ``packet_authority_context_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: packet_authority_context_receipt.
    """

    output_name: ClassVar[str] = "packet_authority_context_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("packet_authority_context_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PacketAuthorityGapReport(L5Report):
    """L5 doctrine output ``packet_authority_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: packet_authority_gap_report.
    """

    output_name: ClassVar[str] = "packet_authority_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("packet_authority_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PolicyBindingGapReport(L5Report):
    """L5 doctrine output ``policy_binding_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_binding_gap_report.
    """

    output_name: ClassVar[str] = "policy_binding_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("policy_binding_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PolicyBindingStatus(L5Status):
    """L5 doctrine output ``policy_binding_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_binding_status.
    """

    output_name: ClassVar[str] = "policy_binding_status"
    output_names: ClassVar[tuple[str, ...]] = ("policy_binding_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "current",
        "missing",
        "stale",
        "mismatched",
    )
    value_enum: ClassVar[type] = PolicyBindingStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class PolicyBundleReceipt(L5Receipt):
    """L5 doctrine output ``policy_bundle_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_bundle_receipt.
    """

    output_name: ClassVar[str] = "policy_bundle_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("policy_bundle_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PolicyEffectiveTimeReceipt(L5Receipt):
    """L5 doctrine output ``policy_effective_time_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_effective_time_receipt.
    """

    output_name: ClassVar[str] = "policy_effective_time_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("policy_effective_time_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PolicyHashReceipt(L5Receipt):
    """L5 doctrine output ``policy_hash_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_hash_receipt.
    """

    output_name: ClassVar[str] = "policy_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("policy_hash_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PolicyLoadReceipt(L5Receipt):
    """L5 doctrine output ``policy_load_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_load_receipt.
    """

    output_name: ClassVar[str] = "policy_load_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("policy_load_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PolicyMismatchReport(L5Report):
    """L5 doctrine output ``policy_mismatch_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_mismatch_report.
    """

    output_name: ClassVar[str] = "policy_mismatch_report"
    output_names: ClassVar[tuple[str, ...]] = ("policy_mismatch_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PolicyRegistryCompatibilityReport(L5Report):
    """L5 doctrine output ``policy_registry_compatibility_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_registry_compatibility_report.
    """

    output_name: ClassVar[str] = "policy_registry_compatibility_report"
    output_names: ClassVar[tuple[str, ...]] = ("policy_registry_compatibility_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PolicyStalenessReport(L5Report):
    """L5 doctrine output ``policy_staleness_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: policy_staleness_report.
    """

    output_name: ClassVar[str] = "policy_staleness_report"
    output_names: ClassVar[tuple[str, ...]] = ("policy_staleness_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PrincipalChainGapReport(L5Report):
    """L5 doctrine output ``principal_chain_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: principal_chain_gap_report.
    """

    output_name: ClassVar[str] = "principal_chain_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("principal_chain_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PrincipalChainReceipt(L5Receipt):
    """L5 doctrine output ``principal_chain_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: principal_chain_receipt.
    """

    output_name: ClassVar[str] = "principal_chain_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("principal_chain_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PrincipalChainStatus(L5Status):
    """L5 doctrine output ``principal_chain_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: principal_chain_status.
    """

    output_name: ClassVar[str] = "principal_chain_status"
    output_names: ClassVar[tuple[str, ...]] = ("principal_chain_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "valid",
        "missing",
        "ambiguous",
        "cross_principal_bleed",
        "cross_tenant_bleed",
    )
    value_enum: ClassVar[type] = PrincipalChainStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class PrincipalScopeWideningReport(L5Report):
    """L5 doctrine output ``principal_scope_widening_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: principal_scope_widening_report.
    """

    output_name: ClassVar[str] = "principal_scope_widening_report"
    output_names: ClassVar[tuple[str, ...]] = ("principal_scope_widening_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptPolicyCompatibilityReceipt(L5Receipt):
    """L5 doctrine output ``prompt_policy_compatibility_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: prompt_policy_compatibility_receipt.
    """

    output_name: ClassVar[str] = "prompt_policy_compatibility_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_policy_compatibility_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PromptRegistryGapReport(L5Report):
    """L5 doctrine output ``prompt_registry_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: prompt_registry_gap_report.
    """

    output_name: ClassVar[str] = "prompt_registry_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_registry_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptRegistryReceipt(L5Receipt):
    """L5 doctrine output ``prompt_registry_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: prompt_registry_receipt.
    """

    output_name: ClassVar[str] = "prompt_registry_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_registry_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PromptSlotMapReceipt(L5Receipt):
    """L5 doctrine output ``prompt_slot_map_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: prompt_slot_map_receipt.
    """

    output_name: ClassVar[str] = "prompt_slot_map_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_slot_map_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PromptSubstitutionReport(L5Report):
    """L5 doctrine output ``prompt_substitution_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: prompt_substitution_report.
    """

    output_name: ClassVar[str] = "prompt_substitution_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_substitution_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptVersionReceipt(L5Receipt):
    """L5 doctrine output ``prompt_version_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: prompt_version_receipt.
    """

    output_name: ClassVar[str] = "prompt_version_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_version_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ProviderAllowlistReceipt(L5Receipt):
    """L5 doctrine output ``provider_allowlist_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: provider_allowlist_receipt.
    """

    output_name: ClassVar[str] = "provider_allowlist_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("provider_allowlist_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReCertificationRequiredReceipt(L5Receipt):
    """L5 doctrine output ``re_certification_required_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: re_certification_required_receipt.
    """

    output_name: ClassVar[str] = "re_certification_required_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("re_certification_required_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReCertificationRequiredReport(L5Report):
    """L5 doctrine output ``re_certification_required_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: re_certification_required_report.
    """

    output_name: ClassVar[str] = "re_certification_required_report"
    output_names: ClassVar[tuple[str, ...]] = ("re_certification_required_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReadScopeReceipt(L5Receipt):
    """L5 doctrine output ``read_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: read_scope_receipt.
    """

    output_name: ClassVar[str] = "read_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("read_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RecertificationStatus(L5Status):
    """L5 doctrine output ``recertification_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: recertification_status.
    """

    output_name: ClassVar[str] = "recertification_status"
    output_names: ClassVar[tuple[str, ...]] = ("recertification_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "not_required",
        "required_due_to_authority_change",
    )
    value_enum: ClassVar[type] = RecertificationStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class RecertificationTriggerReport(L5Report):
    """L5 doctrine output ``recertification_trigger_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: recertification_trigger_report.
    """

    output_name: ClassVar[str] = "recertification_trigger_report"
    output_names: ClassVar[tuple[str, ...]] = ("recertification_trigger_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryBindingStatus(L5Status):
    """L5 doctrine output ``registry_binding_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: registry_binding_status.
    """

    output_name: ClassVar[str] = "registry_binding_status"
    output_names: ClassVar[tuple[str, ...]] = ("registry_binding_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "compatible",
        "missing",
        "stale",
        "mismatched",
        "substituted",
    )
    value_enum: ClassVar[type] = RegistryBindingStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class RegistryCompatibilityReport(L5Report):
    """L5 doctrine output ``registry_compatibility_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: registry_compatibility_report.
    """

    output_name: ClassVar[str] = "registry_compatibility_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_compatibility_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryCompatibilityStatus(L5Status):
    """L5 doctrine output ``registry_compatibility_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: registry_compatibility_status.
    """

    output_name: ClassVar[str] = "registry_compatibility_status"
    output_names: ClassVar[tuple[str, ...]] = ("registry_compatibility_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class RegistryDigestSetReceipt(L5Receipt):
    """L5 doctrine output ``registry_digest_set_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: registry_digest_set_receipt.
    """

    output_name: ClassVar[str] = "registry_digest_set_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("registry_digest_set_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RegistryFreshnessReport(L5Report):
    """L5 doctrine output ``registry_freshness_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: registry_freshness_report.
    """

    output_name: ClassVar[str] = "registry_freshness_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_freshness_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryGapReport(L5Report):
    """L5 doctrine output ``registry_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: registry_gap_report.
    """

    output_name: ClassVar[str] = "registry_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RegistryIntegrityReport(L5Report):
    """L5 doctrine output ``registry_integrity_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: registry_integrity_report.
    """

    output_name: ClassVar[str] = "registry_integrity_report"
    output_names: ClassVar[tuple[str, ...]] = ("registry_integrity_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReplayAuthorityMismatchReport(L5Report):
    """L5 doctrine output ``replay_authority_mismatch_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: replay_authority_mismatch_report.
    """

    output_name: ClassVar[str] = "replay_authority_mismatch_report"
    output_names: ClassVar[tuple[str, ...]] = ("replay_authority_mismatch_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReplayBindingStatus(L5Status):
    """L5 doctrine output ``replay_binding_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: replay_binding_status.
    """

    output_name: ClassVar[str] = "replay_binding_status"
    output_names: ClassVar[tuple[str, ...]] = ("replay_binding_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "bound",
        "missing",
        "incomplete",
        "non_replayable",
        "mismatched",
    )
    value_enum: ClassVar[type] = ReplayBindingStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class ReplayEnvelope(L5Envelope):
    """L5 doctrine output ``replay_envelope`` (kind=envelope).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: replay_envelope.
    """

    output_name: ClassVar[str] = "replay_envelope"
    output_names: ClassVar[tuple[str, ...]] = ("replay_envelope",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "envelope"


@dataclass(frozen=True, slots=True)
class ReplayKeyReceipt(L5Receipt):
    """L5 doctrine output ``replay_key_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: replay_key_receipt.
    """

    output_name: ClassVar[str] = "replay_key_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("replay_key_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RequestEnvelope(L5Envelope):
    """L5 doctrine output ``RequestEnvelope`` (kind=envelope).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: RequestEnvelope.
    """

    output_name: ClassVar[str] = "RequestEnvelope"
    output_names: ClassVar[tuple[str, ...]] = ("RequestEnvelope",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "envelope"


@dataclass(frozen=True, slots=True)
class RequiredFieldGapReport(L5Report):
    """L5 doctrine output ``required_field_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: required_field_gap_report.
    """

    output_name: ClassVar[str] = "required_field_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("required_field_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RouteTopologyMismatchReport(L5Report):
    """L5 doctrine output ``route_topology_mismatch_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: route_topology_mismatch_report.
    """

    output_name: ClassVar[str] = "route_topology_mismatch_report"
    output_names: ClassVar[tuple[str, ...]] = ("route_topology_mismatch_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RouteTopologyReceipt(L5Receipt):
    """L5 doctrine output ``route_topology_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: route_topology_receipt.
    """

    output_name: ClassVar[str] = "route_topology_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("route_topology_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeL5AuthorityReceipt(L5Receipt):
    """L5 doctrine output ``runtime_l5_authority_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: runtime_l5_authority_receipt.
    """

    output_name: ClassVar[str] = "runtime_l5_authority_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_l5_authority_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SandboxBindingStatus(L5Status):
    """L5 doctrine output ``sandbox_binding_status`` (kind=status).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: sandbox_binding_status.
    """

    output_name: ClassVar[str] = "sandbox_binding_status"
    output_names: ClassVar[tuple[str, ...]] = ("sandbox_binding_status",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "bound",
        "missing",
        "stale",
        "incompatible",
        "widened",
    )
    value_enum: ClassVar[type] = SandboxBindingStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class SandboxGapReport(L5Report):
    """L5 doctrine output ``sandbox_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: sandbox_gap_report.
    """

    output_name: ClassVar[str] = "sandbox_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("sandbox_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SandboxWideningReport(L5Report):
    """L5 doctrine output ``sandbox_widening_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: sandbox_widening_report.
    """

    output_name: ClassVar[str] = "sandbox_widening_report"
    output_names: ClassVar[tuple[str, ...]] = ("sandbox_widening_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ScopeCeilingReceipt(L5Receipt):
    """L5 doctrine output ``scope_ceiling_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: scope_ceiling_receipt.
    """

    output_name: ClassVar[str] = "scope_ceiling_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("scope_ceiling_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SecretsScopeReceipt(L5Receipt):
    """L5 doctrine output ``secrets_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: secrets_scope_receipt.
    """

    output_name: ClassVar[str] = "secrets_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("secrets_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SectorOverlayReceipt(L5Receipt):
    """L5 doctrine output ``sector_overlay_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: sector_overlay_receipt.
    """

    output_name: ClassVar[str] = "sector_overlay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("sector_overlay_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SideEffectBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``side_effect_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: side_effect_boundary_receipt.
    """

    output_name: ClassVar[str] = "side_effect_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("side_effect_boundary_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SideEffectClassReceipt(L5Receipt):
    """L5 doctrine output ``side_effect_class_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: side_effect_class_receipt.
    """

    output_name: ClassVar[str] = "side_effect_class_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("side_effect_class_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SideEffectMismatchReport(L5Report):
    """L5 doctrine output ``side_effect_mismatch_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: side_effect_mismatch_report.
    """

    output_name: ClassVar[str] = "side_effect_mismatch_report"
    output_names: ClassVar[tuple[str, ...]] = ("side_effect_mismatch_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SnapshotManifest(L5Manifest):
    """L5 doctrine output ``snapshot_manifest`` (kind=manifest).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: snapshot_manifest.
    """

    output_name: ClassVar[str] = "snapshot_manifest"
    output_names: ClassVar[tuple[str, ...]] = ("snapshot_manifest",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "manifest"


@dataclass(frozen=True, slots=True)
class SnapshotManifestReceipt(L5Receipt):
    """L5 doctrine output ``snapshot_manifest_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: snapshot_manifest_receipt.
    """

    output_name: ClassVar[str] = "snapshot_manifest_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("snapshot_manifest_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StandardsFingerprintReceipt(L5Receipt):
    """L5 doctrine output ``standards_fingerprint_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: standards_fingerprint_receipt.
    """

    output_name: ClassVar[str] = "standards_fingerprint_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("standards_fingerprint_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StructureBlueprintReceipt(L5Receipt):
    """L5 doctrine output ``structure_blueprint_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: structure_blueprint_receipt.
    """

    output_name: ClassVar[str] = "structure_blueprint_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("structure_blueprint_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class TargetSubstitutionReport(L5Report):
    """L5 doctrine output ``target_substitution_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: target_substitution_report.
    """

    output_name: ClassVar[str] = "target_substitution_report"
    output_names: ClassVar[tuple[str, ...]] = ("target_substitution_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ToolRegistryGapReport(L5Report):
    """L5 doctrine output ``tool_registry_gap_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: tool_registry_gap_report.
    """

    output_name: ClassVar[str] = "tool_registry_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("tool_registry_gap_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ToolRegistryReceipt(L5Receipt):
    """L5 doctrine output ``tool_registry_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: tool_registry_receipt.
    """

    output_name: ClassVar[str] = "tool_registry_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("tool_registry_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ToolSchemaReceipt(L5Receipt):
    """L5 doctrine output ``tool_schema_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: tool_schema_receipt.
    """

    output_name: ClassVar[str] = "tool_schema_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("tool_schema_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ToolScopeReceipt(L5Receipt):
    """L5 doctrine output ``tool_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: tool_scope_receipt.
    """

    output_name: ClassVar[str] = "tool_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("tool_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ToolSideEffectReceipt(L5Receipt):
    """L5 doctrine output ``tool_side_effect_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: tool_side_effect_receipt.
    """

    output_name: ClassVar[str] = "tool_side_effect_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("tool_side_effect_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ToolSubstitutionReport(L5Report):
    """L5 doctrine output ``ToolSubstitutionReport`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: ToolSubstitutionReport, tool_substitution_report.
    """

    output_name: ClassVar[str] = "ToolSubstitutionReport"
    output_names: ClassVar[tuple[str, ...]] = (
        "ToolSubstitutionReport",
        "tool_substitution_report",
    )
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TranscriptBindingReceipt(L5Receipt):
    """L5 doctrine output ``transcript_binding_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: transcript_binding_receipt.
    """

    output_name: ClassVar[str] = "transcript_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("transcript_binding_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class TranscriptRef(L5Ref):
    """L5 doctrine output ``transcript_ref`` (kind=ref).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: transcript_ref.
    """

    output_name: ClassVar[str] = "transcript_ref"
    output_names: ClassVar[tuple[str, ...]] = ("transcript_ref",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class UnderstatedAuthorityReport(L5Report):
    """L5 doctrine output ``understated_authority_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: understated_authority_report.
    """

    output_name: ClassVar[str] = "understated_authority_report"
    output_names: ClassVar[tuple[str, ...]] = ("understated_authority_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UntrustedAuthorityAttemptReport(L5Report):
    """L5 doctrine output ``untrusted_authority_attempt_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: untrusted_authority_attempt_report.
    """

    output_name: ClassVar[str] = "untrusted_authority_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("untrusted_authority_attempt_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WriteIntentSmugglingReport(L5Report):
    """L5 doctrine output ``write_intent_smuggling_report`` (kind=report).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: write_intent_smuggling_report.
    """

    output_name: ClassVar[str] = "write_intent_smuggling_report"
    output_names: ClassVar[tuple[str, ...]] = ("write_intent_smuggling_report",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class WriteScopeReceipt(L5Receipt):
    """L5 doctrine output ``write_scope_receipt`` (kind=receipt).

    Source doctrine: ``00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md``.
    Canonical doctrine names: write_scope_receipt.
    """

    output_name: ClassVar[str] = "write_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("write_scope_receipt",)
    source_doc: ClassVar[str] = "00A.2_L5_Authority_Context_and_Registry_Binding_detailed.md"
    output_kind: ClassVar[str] = "receipt"


__all__ = [
    "AffectedConsumersReport",
    "AgentDigestReceipt",
    "AgentRegistryGapReport",
    "AgentRegistryReceipt",
    "AgentScopeReceipt",
    "AgentSubstitutionReport",
    "AuthorityContextReceipt",
    "AuthorityContextStatus",
    "AuthorityFieldIntegrityReport",
    "AuthorityGapReport",
    "AuthorityIssuerReceipt",
    "AuthoritySourceMap",
    "BlueprintBindingStatus",
    "BlueprintHashReceipt",
    "BlueprintLoadReceipt",
    "BlueprintMismatchReport",
    "BlueprintRegistryCompatibilityReport",
    "BootL5AuthorityReport",
    "BroadScopeReport",
    "CapabilityExpirationReceipt",
    "CapabilityGapReport",
    "CapabilityScopeStatus",
    "CapabilityTokenRef",
    "CapabilityWideningReport",
    "ChangedAuthorityFieldReport",
    "ClockPolicyReceipt",
    "CompileTimeL5AuthorityReport",
    "ConnectorAllowlistReceipt",
    "ConnectorCredentialPolicyReceipt",
    "ConnectorDomainReceipt",
    "ConnectorGrantReceipt",
    "ConnectorRegistryGapReport",
    "ConnectorRegistryReceipt",
    "ConnectorScopeReceipt",
    "ConnectorSubstitutionReport",
    "CriticalAuthorityGapReport",
    "CrossPrincipalBleedReport",
    "CrossTenantBleedReport",
    "DanglingRegistryReferenceReport",
    "DelegatedActorReceipt",
    "DelegationDepthReceipt",
    "DownstreamAuthorityConsumerMap",
    "DownstreamAuthorityOverwriteReport",
    "EnvironmentDigestReceipt",
    "EscalationThresholdRef",
    "ExternalCommitScopeReport",
    "FilesystemScopeReceipt",
    "GovernedValidationContext",
    "HITLReentryPacket",
    "HardConstraintMapRef",
    "HashBindingReport",
    "HitlAuthorityBindingReceipt",
    "HumanActorReceipt",
    "HumanAuthorityGapReport",
    "HumanDiffBindingReceipt",
    "HumanReentryReplayReceipt",
    "HumanReviewScopeReceipt",
    "HumanReviewThresholdRef",
    "HumanReviewerScopeReceipt",
    "HumanScopeWideningReport",
    "IncidentReviewPacket",
    "InvariantMapReceipt",
    "LayerAuthorityGapReport",
    "LayerAuthorityMatrixReceipt",
    "MemoryScopeReceipt",
    "NetworkAllowlistReceipt",
    "NetworkScopeReceipt",
    "NoImpliedAuthorityReceipt",
    "NonReplayableGapReport",
    "OldNewAuthorityBindingDiff",
    "OriginTrustManifest",
    "OriginTrustManifestRef",
    "OriginalPrincipalReceipt",
    "PacketAuthorityContextReceipt",
    "PacketAuthorityGapReport",
    "PolicyBindingGapReport",
    "PolicyBindingStatus",
    "PolicyBundleReceipt",
    "PolicyEffectiveTimeReceipt",
    "PolicyHashReceipt",
    "PolicyLoadReceipt",
    "PolicyMismatchReport",
    "PolicyRegistryCompatibilityReport",
    "PolicyStalenessReport",
    "PrincipalChainGapReport",
    "PrincipalChainReceipt",
    "PrincipalChainStatus",
    "PrincipalScopeWideningReport",
    "PromptPolicyCompatibilityReceipt",
    "PromptRegistryGapReport",
    "PromptRegistryReceipt",
    "PromptSlotMapReceipt",
    "PromptSubstitutionReport",
    "PromptVersionReceipt",
    "ProviderAllowlistReceipt",
    "ReCertificationRequiredReceipt",
    "ReCertificationRequiredReport",
    "ReadScopeReceipt",
    "RecertificationStatus",
    "RecertificationTriggerReport",
    "RegistryBindingStatus",
    "RegistryCompatibilityReport",
    "RegistryCompatibilityStatus",
    "RegistryDigestSetReceipt",
    "RegistryFreshnessReport",
    "RegistryGapReport",
    "RegistryIntegrityReport",
    "ReplayAuthorityMismatchReport",
    "ReplayBindingStatus",
    "ReplayEnvelope",
    "ReplayKeyReceipt",
    "RequestEnvelope",
    "RequiredFieldGapReport",
    "RouteTopologyMismatchReport",
    "RouteTopologyReceipt",
    "RuntimeL5AuthorityReceipt",
    "SandboxBindingStatus",
    "SandboxGapReport",
    "SandboxWideningReport",
    "ScopeCeilingReceipt",
    "SecretsScopeReceipt",
    "SectorOverlayReceipt",
    "SideEffectBoundaryReceipt",
    "SideEffectClassReceipt",
    "SideEffectMismatchReport",
    "SnapshotManifest",
    "SnapshotManifestReceipt",
    "StandardsFingerprintReceipt",
    "StructureBlueprintReceipt",
    "TargetSubstitutionReport",
    "ToolRegistryGapReport",
    "ToolRegistryReceipt",
    "ToolSchemaReceipt",
    "ToolScopeReceipt",
    "ToolSideEffectReceipt",
    "ToolSubstitutionReport",
    "TranscriptBindingReceipt",
    "TranscriptRef",
    "UnderstatedAuthorityReport",
    "UntrustedAuthorityAttemptReport",
    "WriteIntentSmugglingReport",
    "WriteScopeReceipt",
]
