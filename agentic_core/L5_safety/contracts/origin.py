"""Generated L5 contract dataclasses for ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``
Module: ``agentic_core.L5_safety.contracts.origin``
Generated count: 123 contracts

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
class AuthorityAttemptStatus(L5Status):
    """L5 doctrine output ``authority_attempt_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: authority_attempt_status.
    """

    output_name: ClassVar[str] = "authority_attempt_status"
    output_names: ClassVar[tuple[str, ...]] = ("authority_attempt_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class AuthorityLabelMap(L5Map):
    """L5 doctrine output ``authority_label_map`` (kind=map).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: authority_label_map.
    """

    output_name: ClassVar[str] = "authority_label_map"
    output_names: ClassVar[tuple[str, ...]] = ("authority_label_map",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class AuthorityOverrideAttemptReport(L5Report):
    """L5 doctrine output ``authority_override_attempt_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: authority_override_attempt_report.
    """

    output_name: ClassVar[str] = "authority_override_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("authority_override_attempt_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class AuthoritySmugglingReport(L5Report):
    """L5 doctrine output ``authority_smuggling_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: authority_smuggling_report.
    """

    output_name: ClassVar[str] = "authority_smuggling_report"
    output_names: ClassVar[tuple[str, ...]] = ("authority_smuggling_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BootOriginTrustReport(L5Report):
    """L5 doctrine output ``boot_origin_trust_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: boot_origin_trust_report.
    """

    output_name: ClassVar[str] = "boot_origin_trust_report"
    output_names: ClassVar[tuple[str, ...]] = ("boot_origin_trust_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BoundaryRuleReceipt(L5Receipt):
    """L5 doctrine output ``boundary_rule_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: boundary_rule_receipt.
    """

    output_name: ClassVar[str] = "boundary_rule_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("boundary_rule_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class BoundaryTransitionReport(L5Report):
    """L5 doctrine output ``boundary_transition_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: boundary_transition_report.
    """

    output_name: ClassVar[str] = "boundary_transition_report"
    output_names: ClassVar[tuple[str, ...]] = ("boundary_transition_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CitationOrSpanRef(L5Ref):
    """L5 doctrine output ``citation_or_span_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: citation_or_span_ref.
    """

    output_name: ClassVar[str] = "citation_or_span_ref"
    output_names: ClassVar[tuple[str, ...]] = ("citation_or_span_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ConnectorOriginPolicyReport(L5Report):
    """L5 doctrine output ``connector_origin_policy_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: connector_origin_policy_report.
    """

    output_name: ClassVar[str] = "connector_origin_policy_report"
    output_names: ClassVar[tuple[str, ...]] = ("connector_origin_policy_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ContentAuthorityHierarchyReceipt(L5Receipt):
    """L5 doctrine output ``content_authority_hierarchy_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: content_authority_hierarchy_receipt.
    """

    output_name: ClassVar[str] = "content_authority_hierarchy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("content_authority_hierarchy_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ContentAuthorityIntegrityReport(L5Report):
    """L5 doctrine output ``content_authority_integrity_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: content_authority_integrity_report.
    """

    output_name: ClassVar[str] = "content_authority_integrity_report"
    output_names: ClassVar[tuple[str, ...]] = ("content_authority_integrity_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ContentBoundaryStatus(L5Status):
    """L5 doctrine output ``content_boundary_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: content_boundary_status.
    """

    output_name: ClassVar[str] = "content_boundary_status"
    output_names: ClassVar[tuple[str, ...]] = ("content_boundary_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class CredentialLikePayloadReport(L5Report):
    """L5 doctrine output ``credential_like_payload_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: credential_like_payload_report.
    """

    output_name: ClassVar[str] = "credential_like_payload_report"
    output_names: ClassVar[tuple[str, ...]] = ("credential_like_payload_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CriticalOriginTrustGapReport(L5Report):
    """L5 doctrine output ``critical_origin_trust_gap_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: critical_origin_trust_gap_report.
    """

    output_name: ClassVar[str] = "critical_origin_trust_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("critical_origin_trust_gap_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CrossPrincipalContentBoundaryReport(L5Report):
    """L5 doctrine output ``cross_principal_content_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: cross_principal_content_boundary_report.
    """

    output_name: ClassVar[str] = "cross_principal_content_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("cross_principal_content_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CrossTenantContentBoundaryReport(L5Report):
    """L5 doctrine output ``cross_tenant_content_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: cross_tenant_content_boundary_report.
    """

    output_name: ClassVar[str] = "cross_tenant_content_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("cross_tenant_content_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DataClassBoundaryReport(L5Report):
    """L5 doctrine output ``data_class_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: data_class_boundary_report.
    """

    output_name: ClassVar[str] = "data_class_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("data_class_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class EvidenceBundleRef(L5Ref):
    """L5 doctrine output ``evidence_bundle_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: evidence_bundle_ref.
    """

    output_name: ClassVar[str] = "evidence_bundle_ref"
    output_names: ClassVar[tuple[str, ...]] = ("evidence_bundle_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ExemplarAuthorityReport(L5Report):
    """L5 doctrine output ``exemplar_authority_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: exemplar_authority_report.
    """

    output_name: ClassVar[str] = "exemplar_authority_report"
    output_names: ClassVar[tuple[str, ...]] = ("exemplar_authority_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ExtractedPayloadRef(L5Ref):
    """L5 doctrine output ``extracted_payload_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: extracted_payload_ref.
    """

    output_name: ClassVar[str] = "extracted_payload_ref"
    output_names: ClassVar[tuple[str, ...]] = ("extracted_payload_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ExtractionTransformLog(L5Log):
    """L5 doctrine output ``extraction_transform_log`` (kind=log).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: extraction_transform_log.
    """

    output_name: ClassVar[str] = "extraction_transform_log"
    output_names: ClassVar[tuple[str, ...]] = ("extraction_transform_log",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "log"


@dataclass(frozen=True, slots=True)
class FencedDataReceipt(L5Receipt):
    """L5 doctrine output ``fenced_data_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: fenced_data_receipt.
    """

    output_name: ClassVar[str] = "fenced_data_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("fenced_data_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class FreshnessStatus(L5Status):
    """L5 doctrine output ``freshness_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: freshness_status.
    """

    output_name: ClassVar[str] = "freshness_status"
    output_names: ClassVar[tuple[str, ...]] = ("freshness_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class GatewayReceiptRef(L5Ref):
    """L5 doctrine output ``gateway_receipt_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: gateway_receipt_ref.
    """

    output_name: ClassVar[str] = "gateway_receipt_ref"
    output_names: ClassVar[tuple[str, ...]] = ("gateway_receipt_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HallucinatedAuthorityReport(L5Report):
    """L5 doctrine output ``hallucinated_authority_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: hallucinated_authority_report.
    """

    output_name: ClassVar[str] = "hallucinated_authority_report"
    output_names: ClassVar[tuple[str, ...]] = ("hallucinated_authority_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanInstructionAttemptReport(L5Report):
    """L5 doctrine output ``human_instruction_attempt_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: human_instruction_attempt_report.
    """

    output_name: ClassVar[str] = "human_instruction_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_instruction_attempt_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanReclearanceRequiredReceipt(L5Receipt):
    """L5 doctrine output ``human_reclearance_required_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: human_reclearance_required_receipt.
    """

    output_name: ClassVar[str] = "human_reclearance_required_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_reclearance_required_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``human_review_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: human_review_boundary_receipt.
    """

    output_name: ClassVar[str] = "human_review_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_boundary_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewOriginGapReport(L5Report):
    """L5 doctrine output ``human_review_origin_gap_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: human_review_origin_gap_report.
    """

    output_name: ClassVar[str] = "human_review_origin_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_origin_gap_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanReviewRef(L5Ref):
    """L5 doctrine output ``human_review_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: human_review_ref.
    """

    output_name: ClassVar[str] = "human_review_ref"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class InstructionBoundaryStatus(L5Status):
    """L5 doctrine output ``instruction_boundary_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: instruction_boundary_status.
    """

    output_name: ClassVar[str] = "instruction_boundary_status"
    output_names: ClassVar[tuple[str, ...]] = ("instruction_boundary_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class InstructionDataBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``instruction_data_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: instruction_data_boundary_receipt.
    """

    output_name: ClassVar[str] = "instruction_data_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("instruction_data_boundary_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class LowerAuthorityOverwriteReport(L5Report):
    """L5 doctrine output ``lower_authority_overwrite_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: lower_authority_overwrite_report.
    """

    output_name: ClassVar[str] = "lower_authority_overwrite_report"
    output_names: ClassVar[tuple[str, ...]] = ("lower_authority_overwrite_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ModelAuthorityAttemptReport(L5Report):
    """L5 doctrine output ``model_authority_attempt_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: model_authority_attempt_report.
    """

    output_name: ClassVar[str] = "model_authority_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("model_authority_attempt_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ModelOutputBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``model_output_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: model_output_boundary_receipt.
    """

    output_name: ClassVar[str] = "model_output_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("model_output_boundary_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ModelOutputRef(L5Ref):
    """L5 doctrine output ``model_output_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: model_output_ref.
    """

    output_name: ClassVar[str] = "model_output_ref"
    output_names: ClassVar[tuple[str, ...]] = ("model_output_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ModelToolProposalBoundaryReport(L5Report):
    """L5 doctrine output ``model_tool_proposal_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: model_tool_proposal_boundary_report.
    """

    output_name: ClassVar[str] = "model_tool_proposal_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("model_tool_proposal_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ModelWriteProposalBoundaryReport(L5Report):
    """L5 doctrine output ``model_write_proposal_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: model_write_proposal_boundary_report.
    """

    output_name: ClassVar[str] = "model_write_proposal_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("model_write_proposal_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class NoUntrustedAuthorityReceipt(L5Receipt):
    """L5 doctrine output ``no_untrusted_authority_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: no_untrusted_authority_receipt.
    """

    output_name: ClassVar[str] = "no_untrusted_authority_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("no_untrusted_authority_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class OmittedSpanReport(L5Report):
    """L5 doctrine output ``omitted_span_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: omitted_span_report.
    """

    output_name: ClassVar[str] = "omitted_span_report"
    output_names: ClassVar[tuple[str, ...]] = ("omitted_span_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class OriginLabelCatalogReceipt(L5Receipt):
    """L5 doctrine output ``origin_label_catalog_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_label_catalog_receipt.
    """

    output_name: ClassVar[str] = "origin_label_catalog_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("origin_label_catalog_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class OriginLabelConflictReport(L5Report):
    """L5 doctrine output ``origin_label_conflict_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_label_conflict_report.
    """

    output_name: ClassVar[str] = "origin_label_conflict_report"
    output_names: ClassVar[tuple[str, ...]] = ("origin_label_conflict_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class OriginLabelMap(L5Map):
    """L5 doctrine output ``origin_label_map`` (kind=map).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_label_map.
    """

    output_name: ClassVar[str] = "origin_label_map"
    output_names: ClassVar[tuple[str, ...]] = ("origin_label_map",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class OriginLabelStatus(L5Status):
    """L5 doctrine output ``origin_label_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_label_status.
    """

    output_name: ClassVar[str] = "origin_label_status"
    output_names: ClassVar[tuple[str, ...]] = ("origin_label_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class OriginManifestGapReport(L5Report):
    """L5 doctrine output ``origin_manifest_gap_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_manifest_gap_report.
    """

    output_name: ClassVar[str] = "origin_manifest_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("origin_manifest_gap_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class OriginManifestHashReceipt(L5Receipt):
    """L5 doctrine output ``origin_manifest_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_manifest_hash_receipt.
    """

    output_name: ClassVar[str] = "origin_manifest_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("origin_manifest_hash_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class OriginManifestReceipt(L5Receipt):
    """L5 doctrine output ``origin_manifest_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_manifest_receipt.
    """

    output_name: ClassVar[str] = "origin_manifest_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("origin_manifest_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class OriginManifestStatus(L5Status):
    """L5 doctrine output ``origin_manifest_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_manifest_status.
    """

    output_name: ClassVar[str] = "origin_manifest_status"
    output_names: ClassVar[tuple[str, ...]] = ("origin_manifest_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class OriginTrustStaticReadinessReport(L5Report):
    """L5 doctrine output ``origin_trust_static_readiness_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: origin_trust_static_readiness_report.
    """

    output_name: ClassVar[str] = "origin_trust_static_readiness_report"
    output_names: ClassVar[tuple[str, ...]] = ("origin_trust_static_readiness_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class OutputSchemaRef(L5Ref):
    """L5 doctrine output ``output_schema_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: output_schema_ref.
    """

    output_name: ClassVar[str] = "output_schema_ref"
    output_names: ClassVar[tuple[str, ...]] = ("output_schema_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ParentArtifactRef(L5Ref):
    """L5 doctrine output ``parent_artifact_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: parent_artifact_ref.
    """

    output_name: ClassVar[str] = "parent_artifact_ref"
    output_names: ClassVar[tuple[str, ...]] = ("parent_artifact_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class PolicyCompatibilityStatus(L5Status):
    """L5 doctrine output ``policy_compatibility_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: policy_compatibility_status.
    """

    output_name: ClassVar[str] = "policy_compatibility_status"
    output_names: ClassVar[tuple[str, ...]] = ("policy_compatibility_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class PrincipalChainRef(L5Ref):
    """L5 doctrine output ``principal_chain_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: principal_chain_ref.
    """

    output_name: ClassVar[str] = "principal_chain_ref"
    output_names: ClassVar[tuple[str, ...]] = ("principal_chain_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class PriorArtifactBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``prior_artifact_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: prior_artifact_boundary_receipt.
    """

    output_name: ClassVar[str] = "prior_artifact_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("prior_artifact_boundary_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class PriorArtifactFreshnessReport(L5Report):
    """L5 doctrine output ``prior_artifact_freshness_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: prior_artifact_freshness_report.
    """

    output_name: ClassVar[str] = "prior_artifact_freshness_report"
    output_names: ClassVar[tuple[str, ...]] = ("prior_artifact_freshness_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PriorArtifactLineageGapReport(L5Report):
    """L5 doctrine output ``prior_artifact_lineage_gap_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: prior_artifact_lineage_gap_report.
    """

    output_name: ClassVar[str] = "prior_artifact_lineage_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("prior_artifact_lineage_gap_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PriorArtifactPolicyCompatibilityReport(L5Report):
    """L5 doctrine output ``prior_artifact_policy_compatibility_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: prior_artifact_policy_compatibility_report.
    """

    output_name: ClassVar[str] = "prior_artifact_policy_compatibility_report"
    output_names: ClassVar[tuple[str, ...]] = ("prior_artifact_policy_compatibility_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PriorPacketRef(L5Ref):
    """L5 doctrine output ``prior_packet_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: prior_packet_ref.
    """

    output_name: ClassVar[str] = "prior_packet_ref"
    output_names: ClassVar[tuple[str, ...]] = ("prior_packet_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class PromptLikeContentReport(L5Report):
    """L5 doctrine output ``prompt_like_content_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: prompt_like_content_report.
    """

    output_name: ClassVar[str] = "prompt_like_content_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_like_content_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class PromptTemplateBoundaryReport(L5Report):
    """L5 doctrine output ``prompt_template_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: prompt_template_boundary_report.
    """

    output_name: ClassVar[str] = "prompt_template_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("prompt_template_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ProposedDiffRef(L5Ref):
    """L5 doctrine output ``proposed_diff_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: proposed_diff_ref.
    """

    output_name: ClassVar[str] = "proposed_diff_ref"
    output_names: ClassVar[tuple[str, ...]] = ("proposed_diff_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ProposedStateDiff(L5Diff):
    """L5 doctrine output ``proposed_state_diff`` (kind=diff).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: proposed_state_diff.
    """

    output_name: ClassVar[str] = "proposed_state_diff"
    output_names: ClassVar[tuple[str, ...]] = ("proposed_state_diff",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "diff"


@dataclass(frozen=True, slots=True)
class QuarantineFailureReport(L5Report):
    """L5 doctrine output ``quarantine_failure_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: quarantine_failure_report.
    """

    output_name: ClassVar[str] = "quarantine_failure_report"
    output_names: ClassVar[tuple[str, ...]] = ("quarantine_failure_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class QuarantineMap(L5Map):
    """L5 doctrine output ``quarantine_map`` (kind=map).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: quarantine_map.
    """

    output_name: ClassVar[str] = "quarantine_map"
    output_names: ClassVar[tuple[str, ...]] = ("quarantine_map",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class QuarantinePolicyReceipt(L5Receipt):
    """L5 doctrine output ``quarantine_policy_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: quarantine_policy_receipt.
    """

    output_name: ClassVar[str] = "quarantine_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("quarantine_policy_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class QuarantineReasonMap(L5Map):
    """L5 doctrine output ``quarantine_reason_map`` (kind=map).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: quarantine_reason_map.
    """

    output_name: ClassVar[str] = "quarantine_reason_map"
    output_names: ClassVar[tuple[str, ...]] = ("quarantine_reason_map",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class QuarantineReceipt(L5Receipt):
    """L5 doctrine output ``quarantine_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: quarantine_receipt.
    """

    output_name: ClassVar[str] = "quarantine_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("quarantine_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class QuarantineReport(L5Report):
    """L5 doctrine output ``quarantine_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: quarantine_report.
    """

    output_name: ClassVar[str] = "quarantine_report"
    output_names: ClassVar[tuple[str, ...]] = ("quarantine_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class QuarantineStatus(L5Status):
    """L5 doctrine output ``quarantine_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: quarantine_status.
    """

    output_name: ClassVar[str] = "quarantine_status"
    output_names: ClassVar[tuple[str, ...]] = ("quarantine_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class QuotedContentOriginReport(L5Report):
    """L5 doctrine output ``quoted_content_origin_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: quoted_content_origin_report.
    """

    output_name: ClassVar[str] = "quoted_content_origin_report"
    output_names: ClassVar[tuple[str, ...]] = ("quoted_content_origin_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RedactionPolicyReceipt(L5Receipt):
    """L5 doctrine output ``redaction_policy_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: redaction_policy_receipt.
    """

    output_name: ClassVar[str] = "redaction_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("redaction_policy_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RedactionReceipt(L5Receipt):
    """L5 doctrine output ``redaction_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: redaction_receipt.
    """

    output_name: ClassVar[str] = "redaction_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("redaction_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RegionScopeBoundaryReport(L5Report):
    """L5 doctrine output ``region_scope_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: region_scope_boundary_report.
    """

    output_name: ClassVar[str] = "region_scope_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("region_scope_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ResidualRiskReport(L5Report):
    """L5 doctrine output ``residual_risk_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: residual_risk_report.
    """

    output_name: ClassVar[str] = "residual_risk_report"
    output_names: ClassVar[tuple[str, ...]] = ("residual_risk_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RetrievedContentBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``retrieved_content_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: retrieved_content_boundary_receipt.
    """

    output_name: ClassVar[str] = "retrieved_content_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("retrieved_content_boundary_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RetrievedContentFencingReport(L5Report):
    """L5 doctrine output ``retrieved_content_fencing_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: retrieved_content_fencing_report.
    """

    output_name: ClassVar[str] = "retrieved_content_fencing_report"
    output_names: ClassVar[tuple[str, ...]] = ("retrieved_content_fencing_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RetrievedInstructionAttemptReport(L5Report):
    """L5 doctrine output ``retrieved_instruction_attempt_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: retrieved_instruction_attempt_report.
    """

    output_name: ClassVar[str] = "retrieved_instruction_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("retrieved_instruction_attempt_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RetrievedLineageGapReport(L5Report):
    """L5 doctrine output ``retrieved_lineage_gap_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: retrieved_lineage_gap_report.
    """

    output_name: ClassVar[str] = "retrieved_lineage_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("retrieved_lineage_gap_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RetrievedStalenessBoundaryReport(L5Report):
    """L5 doctrine output ``retrieved_staleness_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: retrieved_staleness_boundary_report.
    """

    output_name: ClassVar[str] = "retrieved_staleness_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("retrieved_staleness_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RuntimeOriginTrustReceipt(L5Receipt):
    """L5 doctrine output ``runtime_origin_trust_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: runtime_origin_trust_receipt.
    """

    output_name: ClassVar[str] = "runtime_origin_trust_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_origin_trust_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeQuarantineReport(L5Report):
    """L5 doctrine output ``runtime_quarantine_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: runtime_quarantine_report.
    """

    output_name: ClassVar[str] = "runtime_quarantine_report"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_quarantine_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RuntimeSafeExtractionReport(L5Report):
    """L5 doctrine output ``runtime_safe_extraction_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: runtime_safe_extraction_report.
    """

    output_name: ClassVar[str] = "runtime_safe_extraction_report"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_safe_extraction_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SafeExtractionFailureReport(L5Report):
    """L5 doctrine output ``safe_extraction_failure_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: safe_extraction_failure_report.
    """

    output_name: ClassVar[str] = "safe_extraction_failure_report"
    output_names: ClassVar[tuple[str, ...]] = ("safe_extraction_failure_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SafeExtractionMap(L5Map):
    """L5 doctrine output ``safe_extraction_map`` (kind=map).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: safe_extraction_map.
    """

    output_name: ClassVar[str] = "safe_extraction_map"
    output_names: ClassVar[tuple[str, ...]] = ("safe_extraction_map",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class SafeExtractionPolicyReceipt(L5Receipt):
    """L5 doctrine output ``safe_extraction_policy_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: safe_extraction_policy_receipt.
    """

    output_name: ClassVar[str] = "safe_extraction_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("safe_extraction_policy_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SafeExtractionReceiptRef(L5Ref):
    """L5 doctrine output ``safe_extraction_receipt_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: safe_extraction_receipt_ref.
    """

    output_name: ClassVar[str] = "safe_extraction_receipt_ref"
    output_names: ClassVar[tuple[str, ...]] = ("safe_extraction_receipt_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class SafeExtractionStatus(L5Status):
    """L5 doctrine output ``safe_extraction_status`` (kind=status).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: safe_extraction_status.
    """

    output_name: ClassVar[str] = "safe_extraction_status"
    output_names: ClassVar[tuple[str, ...]] = ("safe_extraction_status",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class SandboxEnvelopeRef(L5Ref):
    """L5 doctrine output ``sandbox_envelope_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: sandbox_envelope_ref.
    """

    output_name: ClassVar[str] = "sandbox_envelope_ref"
    output_names: ClassVar[tuple[str, ...]] = ("sandbox_envelope_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class SanitizedPayloadGapReport(L5Report):
    """L5 doctrine output ``sanitized_payload_gap_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: sanitized_payload_gap_report.
    """

    output_name: ClassVar[str] = "sanitized_payload_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("sanitized_payload_gap_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SanitizedPayloadMap(L5Map):
    """L5 doctrine output ``sanitized_payload_map`` (kind=map).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: sanitized_payload_map.
    """

    output_name: ClassVar[str] = "sanitized_payload_map"
    output_names: ClassVar[tuple[str, ...]] = ("sanitized_payload_map",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class SecretDetectionReport(L5Report):
    """L5 doctrine output ``secret_detection_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: secret_detection_report.
    """

    output_name: ClassVar[str] = "secret_detection_report"
    output_names: ClassVar[tuple[str, ...]] = ("secret_detection_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SecretQuarantineReceipt(L5Receipt):
    """L5 doctrine output ``secret_quarantine_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: secret_quarantine_receipt.
    """

    output_name: ClassVar[str] = "secret_quarantine_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("secret_quarantine_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class SensitiveDataBoundaryReport(L5Report):
    """L5 doctrine output ``sensitive_data_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: sensitive_data_boundary_report.
    """

    output_name: ClassVar[str] = "sensitive_data_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("sensitive_data_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SessionScopeBoundaryReport(L5Report):
    """L5 doctrine output ``session_scope_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: session_scope_boundary_report.
    """

    output_name: ClassVar[str] = "session_scope_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("session_scope_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SourceRef(L5Ref):
    """L5 doctrine output ``source_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: source_ref.
    """

    output_name: ClassVar[str] = "source_ref"
    output_names: ClassVar[tuple[str, ...]] = ("source_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class SpanRef(L5Ref):
    """L5 doctrine output ``span_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: span_ref.
    """

    output_name: ClassVar[str] = "span_ref"
    output_names: ClassVar[tuple[str, ...]] = ("span_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class StaleArtifactAuthorityAttemptReport(L5Report):
    """L5 doctrine output ``stale_artifact_authority_attempt_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: stale_artifact_authority_attempt_report.
    """

    output_name: ClassVar[str] = "stale_artifact_authority_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("stale_artifact_authority_attempt_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaleAuthoritySourceReport(L5Report):
    """L5 doctrine output ``stale_authority_source_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: stale_authority_source_report.
    """

    output_name: ClassVar[str] = "stale_authority_source_report"
    output_names: ClassVar[tuple[str, ...]] = ("stale_authority_source_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticHiddenInstructionReport(L5Report):
    """L5 doctrine output ``static_hidden_instruction_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: static_hidden_instruction_report.
    """

    output_name: ClassVar[str] = "static_hidden_instruction_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_hidden_instruction_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticOriginTrustEvidenceIntakeReceipt(L5Receipt):
    """L5 doctrine output ``static_origin_trust_evidence_intake_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: static_origin_trust_evidence_intake_receipt.
    """

    output_name: ClassVar[str] = "static_origin_trust_evidence_intake_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_origin_trust_evidence_intake_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticOriginTrustGapRefMap(L5Map):
    """L5 doctrine output ``static_origin_trust_gap_ref_map`` (kind=map).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: static_origin_trust_gap_ref_map.
    """

    output_name: ClassVar[str] = "static_origin_trust_gap_ref_map"
    output_names: ClassVar[tuple[str, ...]] = ("static_origin_trust_gap_ref_map",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class StaticOriginTrustReport(L5Report):
    """L5 doctrine output ``static_origin_trust_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: static_origin_trust_report.
    """

    output_name: ClassVar[str] = "static_origin_trust_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_origin_trust_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class SupportTargetRef(L5Ref):
    """L5 doctrine output ``support_target_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: support_target_ref.
    """

    output_name: ClassVar[str] = "support_target_ref"
    output_names: ClassVar[tuple[str, ...]] = ("support_target_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ToolInvocationRef(L5Ref):
    """L5 doctrine output ``tool_invocation_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: tool_invocation_ref.
    """

    output_name: ClassVar[str] = "tool_invocation_ref"
    output_names: ClassVar[tuple[str, ...]] = ("tool_invocation_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ToolOutputBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``tool_output_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: tool_output_boundary_receipt.
    """

    output_name: ClassVar[str] = "tool_output_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("tool_output_boundary_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ToolOutputInstructionAttemptReport(L5Report):
    """L5 doctrine output ``tool_output_instruction_attempt_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: tool_output_instruction_attempt_report.
    """

    output_name: ClassVar[str] = "tool_output_instruction_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("tool_output_instruction_attempt_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ToolOutputQuarantineReport(L5Report):
    """L5 doctrine output ``tool_output_quarantine_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: tool_output_quarantine_report.
    """

    output_name: ClassVar[str] = "tool_output_quarantine_report"
    output_names: ClassVar[tuple[str, ...]] = ("tool_output_quarantine_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ToolOutputSchemaBoundaryReport(L5Report):
    """L5 doctrine output ``tool_output_schema_boundary_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: tool_output_schema_boundary_report.
    """

    output_name: ClassVar[str] = "tool_output_schema_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("tool_output_schema_boundary_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ToolOutputSecretReport(L5Report):
    """L5 doctrine output ``tool_output_secret_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: tool_output_secret_report.
    """

    output_name: ClassVar[str] = "tool_output_secret_report"
    output_names: ClassVar[tuple[str, ...]] = ("tool_output_secret_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TransformationHashReceipt(L5Receipt):
    """L5 doctrine output ``transformation_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: transformation_hash_receipt.
    """

    output_name: ClassVar[str] = "transformation_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("transformation_hash_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class TransformationReceipt(L5Receipt):
    """L5 doctrine output ``transformation_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: transformation_receipt.
    """

    output_name: ClassVar[str] = "transformation_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("transformation_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class TrustBoundaryMap(L5Map):
    """L5 doctrine output ``trust_boundary_map`` (kind=map).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: trust_boundary_map.
    """

    output_name: ClassVar[str] = "trust_boundary_map"
    output_names: ClassVar[tuple[str, ...]] = ("trust_boundary_map",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class TrustClassMappingReceipt(L5Receipt):
    """L5 doctrine output ``trust_class_mapping_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: trust_class_mapping_receipt.
    """

    output_name: ClassVar[str] = "trust_class_mapping_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("trust_class_mapping_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class TrustClassMismatchReport(L5Report):
    """L5 doctrine output ``trust_class_mismatch_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: trust_class_mismatch_report.
    """

    output_name: ClassVar[str] = "trust_class_mismatch_report"
    output_names: ClassVar[tuple[str, ...]] = ("trust_class_mismatch_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class TrustClassReceipt(L5Receipt):
    """L5 doctrine output ``trust_class_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: trust_class_receipt.
    """

    output_name: ClassVar[str] = "trust_class_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("trust_class_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class TrustClassificationReport(L5Report):
    """L5 doctrine output ``trust_classification_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: trust_classification_report.
    """

    output_name: ClassVar[str] = "trust_classification_report"
    output_names: ClassVar[tuple[str, ...]] = ("trust_classification_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnknownOriginLabelReport(L5Report):
    """L5 doctrine output ``unknown_origin_label_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: unknown_origin_label_report.
    """

    output_name: ClassVar[str] = "unknown_origin_label_report"
    output_names: ClassVar[tuple[str, ...]] = ("unknown_origin_label_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnknownTrustClassReport(L5Report):
    """L5 doctrine output ``unknown_trust_class_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: unknown_trust_class_report.
    """

    output_name: ClassVar[str] = "unknown_trust_class_report"
    output_names: ClassVar[tuple[str, ...]] = ("unknown_trust_class_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UnsupportedOriginLabelReport(L5Report):
    """L5 doctrine output ``unsupported_origin_label_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: unsupported_origin_label_report.
    """

    output_name: ClassVar[str] = "unsupported_origin_label_report"
    output_names: ClassVar[tuple[str, ...]] = ("unsupported_origin_label_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UntrustedInstructionAttemptReport(L5Report):
    """L5 doctrine output ``untrusted_instruction_attempt_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: untrusted_instruction_attempt_report.
    """

    output_name: ClassVar[str] = "untrusted_instruction_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("untrusted_instruction_attempt_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UserAuthorityAttemptReport(L5Report):
    """L5 doctrine output ``user_authority_attempt_report`` (kind=report).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: user_authority_attempt_report.
    """

    output_name: ClassVar[str] = "user_authority_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("user_authority_attempt_report",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class UserIntentExtractionRef(L5Ref):
    """L5 doctrine output ``user_intent_extraction_ref`` (kind=ref).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: user_intent_extraction_ref.
    """

    output_name: ClassVar[str] = "user_intent_extraction_ref"
    output_names: ClassVar[tuple[str, ...]] = ("user_intent_extraction_ref",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class UserTurnBoundaryReceipt(L5Receipt):
    """L5 doctrine output ``user_turn_boundary_receipt`` (kind=receipt).

    Source doctrine: ``00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md``.
    Canonical doctrine names: user_turn_boundary_receipt.
    """

    output_name: ClassVar[str] = "user_turn_boundary_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("user_turn_boundary_receipt",)
    source_doc: ClassVar[str] = "00.3_L5_Origin_Trust_and_Content_Boundary_detailed.md"
    output_kind: ClassVar[str] = "receipt"


__all__ = [
    "AuthorityAttemptStatus",
    "AuthorityLabelMap",
    "AuthorityOverrideAttemptReport",
    "AuthoritySmugglingReport",
    "BootOriginTrustReport",
    "BoundaryRuleReceipt",
    "BoundaryTransitionReport",
    "CitationOrSpanRef",
    "ConnectorOriginPolicyReport",
    "ContentAuthorityHierarchyReceipt",
    "ContentAuthorityIntegrityReport",
    "ContentBoundaryStatus",
    "CredentialLikePayloadReport",
    "CriticalOriginTrustGapReport",
    "CrossPrincipalContentBoundaryReport",
    "CrossTenantContentBoundaryReport",
    "DataClassBoundaryReport",
    "EvidenceBundleRef",
    "ExemplarAuthorityReport",
    "ExtractedPayloadRef",
    "ExtractionTransformLog",
    "FencedDataReceipt",
    "FreshnessStatus",
    "GatewayReceiptRef",
    "HallucinatedAuthorityReport",
    "HumanInstructionAttemptReport",
    "HumanReclearanceRequiredReceipt",
    "HumanReviewBoundaryReceipt",
    "HumanReviewOriginGapReport",
    "HumanReviewRef",
    "InstructionBoundaryStatus",
    "InstructionDataBoundaryReceipt",
    "LowerAuthorityOverwriteReport",
    "ModelAuthorityAttemptReport",
    "ModelOutputBoundaryReceipt",
    "ModelOutputRef",
    "ModelToolProposalBoundaryReport",
    "ModelWriteProposalBoundaryReport",
    "NoUntrustedAuthorityReceipt",
    "OmittedSpanReport",
    "OriginLabelCatalogReceipt",
    "OriginLabelConflictReport",
    "OriginLabelMap",
    "OriginLabelStatus",
    "OriginManifestGapReport",
    "OriginManifestHashReceipt",
    "OriginManifestReceipt",
    "OriginManifestStatus",
    "OriginTrustStaticReadinessReport",
    "OutputSchemaRef",
    "ParentArtifactRef",
    "PolicyCompatibilityStatus",
    "PrincipalChainRef",
    "PriorArtifactBoundaryReceipt",
    "PriorArtifactFreshnessReport",
    "PriorArtifactLineageGapReport",
    "PriorArtifactPolicyCompatibilityReport",
    "PriorPacketRef",
    "PromptLikeContentReport",
    "PromptTemplateBoundaryReport",
    "ProposedDiffRef",
    "ProposedStateDiff",
    "QuarantineFailureReport",
    "QuarantineMap",
    "QuarantinePolicyReceipt",
    "QuarantineReasonMap",
    "QuarantineReceipt",
    "QuarantineReport",
    "QuarantineStatus",
    "QuotedContentOriginReport",
    "RedactionPolicyReceipt",
    "RedactionReceipt",
    "RegionScopeBoundaryReport",
    "ResidualRiskReport",
    "RetrievedContentBoundaryReceipt",
    "RetrievedContentFencingReport",
    "RetrievedInstructionAttemptReport",
    "RetrievedLineageGapReport",
    "RetrievedStalenessBoundaryReport",
    "RuntimeOriginTrustReceipt",
    "RuntimeQuarantineReport",
    "RuntimeSafeExtractionReport",
    "SafeExtractionFailureReport",
    "SafeExtractionMap",
    "SafeExtractionPolicyReceipt",
    "SafeExtractionReceiptRef",
    "SafeExtractionStatus",
    "SandboxEnvelopeRef",
    "SanitizedPayloadGapReport",
    "SanitizedPayloadMap",
    "SecretDetectionReport",
    "SecretQuarantineReceipt",
    "SensitiveDataBoundaryReport",
    "SessionScopeBoundaryReport",
    "SourceRef",
    "SpanRef",
    "StaleArtifactAuthorityAttemptReport",
    "StaleAuthoritySourceReport",
    "StaticHiddenInstructionReport",
    "StaticOriginTrustEvidenceIntakeReceipt",
    "StaticOriginTrustGapRefMap",
    "StaticOriginTrustReport",
    "SupportTargetRef",
    "ToolInvocationRef",
    "ToolOutputBoundaryReceipt",
    "ToolOutputInstructionAttemptReport",
    "ToolOutputQuarantineReport",
    "ToolOutputSchemaBoundaryReport",
    "ToolOutputSecretReport",
    "TransformationHashReceipt",
    "TransformationReceipt",
    "TrustBoundaryMap",
    "TrustClassMappingReceipt",
    "TrustClassMismatchReport",
    "TrustClassReceipt",
    "TrustClassificationReport",
    "UnknownOriginLabelReport",
    "UnknownTrustClassReport",
    "UnsupportedOriginLabelReport",
    "UntrustedInstructionAttemptReport",
    "UserAuthorityAttemptReport",
    "UserIntentExtractionRef",
    "UserTurnBoundaryReceipt",
]
