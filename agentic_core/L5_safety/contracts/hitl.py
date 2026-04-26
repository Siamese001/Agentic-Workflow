"""Generated L5 contract dataclasses for ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``
Module: ``agentic_core.L5_safety.contracts.hitl``
Generated count: 75 contracts

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
class AllowedResponseTypeReceipt(L5Receipt):
    """L5 doctrine output ``allowed_response_type_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: allowed_response_type_receipt.
    """

    output_name: ClassVar[str] = "allowed_response_type_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("allowed_response_type_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuthorityFreezeReceipt(L5Receipt):
    """L5 doctrine output ``authority_freeze_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: authority_freeze_receipt.
    """

    output_name: ClassVar[str] = "authority_freeze_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("authority_freeze_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class AuthorityImpactingHumanDiffReport(L5Report):
    """L5 doctrine output ``authority_impacting_human_diff_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: authority_impacting_human_diff_report.
    """

    output_name: ClassVar[str] = "authority_impacting_human_diff_report"
    output_names: ClassVar[tuple[str, ...]] = ("authority_impacting_human_diff_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class BootHitlGovernanceReport(L5Report):
    """L5 doctrine output ``boot_hitl_governance_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: boot_hitl_governance_report.
    """

    output_name: ClassVar[str] = "boot_hitl_governance_report"
    output_names: ClassVar[tuple[str, ...]] = ("boot_hitl_governance_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class CriticalHitlGapReport(L5Report):
    """L5 doctrine output ``critical_hitl_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: critical_hitl_gap_report.
    """

    output_name: ClassVar[str] = "critical_hitl_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("critical_hitl_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class DirectHumanWritePathReport(L5Report):
    """L5 doctrine output ``direct_human_write_path_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: direct_human_write_path_report.
    """

    output_name: ClassVar[str] = "direct_human_write_path_report"
    output_names: ClassVar[tuple[str, ...]] = ("direct_human_write_path_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class FreezeReplayBindingReceipt(L5Receipt):
    """L5 doctrine output ``freeze_replay_binding_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: freeze_replay_binding_receipt.
    """

    output_name: ClassVar[str] = "freeze_replay_binding_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("freeze_replay_binding_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class FrozenEvidenceBundleReceipt(L5Receipt):
    """L5 doctrine output ``frozen_evidence_bundle_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: frozen_evidence_bundle_receipt.
    """

    output_name: ClassVar[str] = "frozen_evidence_bundle_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("frozen_evidence_bundle_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class FrozenPacketHashReceipt(L5Receipt):
    """L5 doctrine output ``frozen_packet_hash_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: frozen_packet_hash_receipt.
    """

    output_name: ClassVar[str] = "frozen_packet_hash_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("frozen_packet_hash_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class FrozenPacketRef(L5Ref):
    """L5 doctrine output ``frozen_packet_ref`` (kind=ref).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: frozen_packet_ref.
    """

    output_name: ClassVar[str] = "frozen_packet_ref"
    output_names: ClassVar[tuple[str, ...]] = ("frozen_packet_ref",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HITLAuditReceipt(L5Receipt):
    """L5 doctrine output ``HITLAuditReceipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: HITLAuditReceipt.
    """

    output_name: ClassVar[str] = "HITLAuditReceipt"
    output_names: ClassVar[tuple[str, ...]] = ("HITLAuditReceipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HITLFreezePacket(L5Packet):
    """L5 doctrine output ``HITLFreezePacket`` (kind=packet).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: HITLFreezePacket.
    """

    output_name: ClassVar[str] = "HITLFreezePacket"
    output_names: ClassVar[tuple[str, ...]] = ("HITLFreezePacket",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class HardConstraintHumanOverrideReport(L5Report):
    """L5 doctrine output ``hard_constraint_human_override_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: hard_constraint_human_override_report.
    """

    output_name: ClassVar[str] = "hard_constraint_human_override_report"
    output_names: ClassVar[tuple[str, ...]] = ("hard_constraint_human_override_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HitlAuditGapReport(L5Report):
    """L5 doctrine output ``hitl_audit_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: hitl_audit_gap_report.
    """

    output_name: ClassVar[str] = "hitl_audit_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_audit_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HitlFreezeGapReport(L5Report):
    """L5 doctrine output ``hitl_freeze_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: hitl_freeze_gap_report.
    """

    output_name: ClassVar[str] = "hitl_freeze_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_freeze_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HitlFreezeReceipt(L5Receipt):
    """L5 doctrine output ``hitl_freeze_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: hitl_freeze_receipt.
    """

    output_name: ClassVar[str] = "hitl_freeze_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_freeze_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HitlStaticGapRefMap(L5Map):
    """L5 doctrine output ``hitl_static_gap_ref_map`` (kind=map).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: hitl_static_gap_ref_map.
    """

    output_name: ClassVar[str] = "hitl_static_gap_ref_map"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_static_gap_ref_map",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class HitlStaticGapReport(L5Report):
    """L5 doctrine output ``hitl_static_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: hitl_static_gap_report.
    """

    output_name: ClassVar[str] = "hitl_static_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_static_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HitlTemplateGovernanceReadinessReport(L5Report):
    """L5 doctrine output ``hitl_template_governance_readiness_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: hitl_template_governance_readiness_report.
    """

    output_name: ClassVar[str] = "hitl_template_governance_readiness_report"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_template_governance_readiness_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanAddedEvidenceClaimReport(L5Report):
    """L5 doctrine output ``human_added_evidence_claim_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_added_evidence_claim_report.
    """

    output_name: ClassVar[str] = "human_added_evidence_claim_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_added_evidence_claim_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanAuthorityAttemptReport(L5Report):
    """L5 doctrine output ``human_authority_attempt_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_authority_attempt_report.
    """

    output_name: ClassVar[str] = "human_authority_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_authority_attempt_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanAuthorityWideningAttemptReport(L5Report):
    """L5 doctrine output ``human_authority_widening_attempt_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_authority_widening_attempt_report.
    """

    output_name: ClassVar[str] = "human_authority_widening_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_authority_widening_attempt_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanDiffReceipt(L5Receipt):
    """L5 doctrine output ``human_diff_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_diff_receipt.
    """

    output_name: ClassVar[str] = "human_diff_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_diff_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanDiffRef(L5Ref):
    """L5 doctrine output ``human_diff_ref`` (kind=ref).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_diff_ref.
    """

    output_name: ClassVar[str] = "human_diff_ref"
    output_names: ClassVar[tuple[str, ...]] = ("human_diff_ref",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HumanDiffReplayReceipt(L5Receipt):
    """L5 doctrine output ``human_diff_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_diff_replay_receipt.
    """

    output_name: ClassVar[str] = "human_diff_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_diff_replay_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanInputOriginReceipt(L5Receipt):
    """L5 doctrine output ``HumanInputOriginReceipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: HumanInputOriginReceipt, human_input_origin_receipt.
    """

    output_name: ClassVar[str] = "HumanInputOriginReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "HumanInputOriginReceipt",
        "human_input_origin_receipt",
    )
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanModificationDiff(L5Diff):
    """L5 doctrine output ``HumanModificationDiff`` (kind=diff).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: HumanModificationDiff.
    """

    output_name: ClassVar[str] = "HumanModificationDiff"
    output_names: ClassVar[tuple[str, ...]] = ("HumanModificationDiff",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "diff"


@dataclass(frozen=True, slots=True)
class HumanModificationDiffReceipt(L5Receipt):
    """L5 doctrine output ``human_modification_diff_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_modification_diff_receipt.
    """

    output_name: ClassVar[str] = "human_modification_diff_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_modification_diff_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanOriginGapReport(L5Report):
    """L5 doctrine output ``human_origin_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_origin_gap_report.
    """

    output_name: ClassVar[str] = "human_origin_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_origin_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanOverrideAttemptReport(L5Report):
    """L5 doctrine output ``human_override_attempt_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_override_attempt_report.
    """

    output_name: ClassVar[str] = "human_override_attempt_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_override_attempt_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanOverrideLimitReceipt(L5Receipt):
    """L5 doctrine output ``human_override_limit_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_override_limit_receipt.
    """

    output_name: ClassVar[str] = "human_override_limit_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_override_limit_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanPolicyExceptionRequestReport(L5Report):
    """L5 doctrine output ``human_policy_exception_request_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_policy_exception_request_report.
    """

    output_name: ClassVar[str] = "human_policy_exception_request_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_policy_exception_request_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanPromptLikeContentReport(L5Report):
    """L5 doctrine output ``human_prompt_like_content_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_prompt_like_content_report.
    """

    output_name: ClassVar[str] = "human_prompt_like_content_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_prompt_like_content_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanProvidedFactReport(L5Report):
    """L5 doctrine output ``human_provided_fact_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_provided_fact_report.
    """

    output_name: ClassVar[str] = "human_provided_fact_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_provided_fact_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanProvidedSourceReport(L5Report):
    """L5 doctrine output ``human_provided_source_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_provided_source_report.
    """

    output_name: ClassVar[str] = "human_provided_source_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_provided_source_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanReclearanceReceipt(L5Receipt):
    """L5 doctrine output ``HumanReclearanceReceipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: HumanReclearanceReceipt.
    """

    output_name: ClassVar[str] = "HumanReclearanceReceipt"
    output_names: ClassVar[tuple[str, ...]] = ("HumanReclearanceReceipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReclearanceTriggerReport(L5Report):
    """L5 doctrine output ``human_reclearance_trigger_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_reclearance_trigger_report.
    """

    output_name: ClassVar[str] = "human_reclearance_trigger_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_reclearance_trigger_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanResponseReceipt(L5Receipt):
    """L5 doctrine output ``human_response_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_response_receipt.
    """

    output_name: ClassVar[str] = "human_response_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_response_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewContextBoundaryReport(L5Report):
    """L5 doctrine output ``human_review_context_boundary_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_context_boundary_report.
    """

    output_name: ClassVar[str] = "human_review_context_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_context_boundary_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanReviewEvidencePacket(L5Packet):
    """L5 doctrine output ``HumanReviewEvidencePacket`` (kind=packet).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: HumanReviewEvidencePacket.
    """

    output_name: ClassVar[str] = "HumanReviewEvidencePacket"
    output_names: ClassVar[tuple[str, ...]] = ("HumanReviewEvidencePacket",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class HumanReviewHashChainReceipt(L5Receipt):
    """L5 doctrine output ``human_review_hash_chain_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_hash_chain_receipt.
    """

    output_name: ClassVar[str] = "human_review_hash_chain_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_hash_chain_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewOriginLabelReport(L5Report):
    """L5 doctrine output ``human_review_origin_label_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_origin_label_report.
    """

    output_name: ClassVar[str] = "human_review_origin_label_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_origin_label_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanReviewPacketGapReport(L5Report):
    """L5 doctrine output ``human_review_packet_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_packet_gap_report.
    """

    output_name: ClassVar[str] = "human_review_packet_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_packet_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanReviewPacketReceipt(L5Receipt):
    """L5 doctrine output ``human_review_packet_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_packet_receipt.
    """

    output_name: ClassVar[str] = "human_review_packet_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_packet_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewPolicyReceipt(L5Receipt):
    """L5 doctrine output ``human_review_policy_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_policy_receipt.
    """

    output_name: ClassVar[str] = "human_review_policy_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_policy_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewReconstructionReport(L5Report):
    """L5 doctrine output ``human_review_reconstruction_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_reconstruction_report.
    """

    output_name: ClassVar[str] = "human_review_reconstruction_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_reconstruction_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanReviewReplayReceipt(L5Receipt):
    """L5 doctrine output ``human_review_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_replay_receipt.
    """

    output_name: ClassVar[str] = "human_review_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_replay_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class HumanReviewTemplateBoundaryReport(L5Report):
    """L5 doctrine output ``human_review_template_boundary_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_review_template_boundary_report.
    """

    output_name: ClassVar[str] = "human_review_template_boundary_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_review_template_boundary_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanScopeGapReport(L5Report):
    """L5 doctrine output ``human_scope_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_scope_gap_report.
    """

    output_name: ClassVar[str] = "human_scope_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_scope_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanSourceOriginGapReport(L5Report):
    """L5 doctrine output ``human_source_origin_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_source_origin_gap_report.
    """

    output_name: ClassVar[str] = "human_source_origin_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("human_source_origin_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class HumanSourceValidationNeededReceipt(L5Receipt):
    """L5 doctrine output ``human_source_validation_needed_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: human_source_validation_needed_receipt.
    """

    output_name: ClassVar[str] = "human_source_validation_needed_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("human_source_validation_needed_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class L5ReclearanceReceipt(L5Receipt):
    """L5 doctrine output ``L5ReclearanceReceipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: L5ReclearanceReceipt.
    """

    output_name: ClassVar[str] = "L5ReclearanceReceipt"
    output_names: ClassVar[tuple[str, ...]] = ("L5ReclearanceReceipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class L5ReclearanceRequiredReceipt(L5Receipt):
    """L5 doctrine output ``L5ReclearanceRequiredReceipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: L5ReclearanceRequiredReceipt.
    """

    output_name: ClassVar[str] = "L5ReclearanceRequiredReceipt"
    output_names: ClassVar[tuple[str, ...]] = ("L5ReclearanceRequiredReceipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class OldNewScopeDiff(L5Diff):
    """L5 doctrine output ``old_new_scope_diff`` (kind=diff).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: old_new_scope_diff.
    """

    output_name: ClassVar[str] = "old_new_scope_diff"
    output_names: ClassVar[tuple[str, ...]] = ("old_new_scope_diff",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "diff"


@dataclass(frozen=True, slots=True)
class OperatorOverridePolicyReport(L5Report):
    """L5 doctrine output ``operator_override_policy_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: operator_override_policy_report.
    """

    output_name: ClassVar[str] = "operator_override_policy_report"
    output_names: ClassVar[tuple[str, ...]] = ("operator_override_policy_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ProhibitedResponseTypeReceipt(L5Receipt):
    """L5 doctrine output ``prohibited_response_type_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: prohibited_response_type_receipt.
    """

    output_name: ClassVar[str] = "prohibited_response_type_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("prohibited_response_type_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReClearanceRequiredReceipt(L5Receipt):
    """L5 doctrine output ``re_clearance_required_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: re_clearance_required_receipt.
    """

    output_name: ClassVar[str] = "re_clearance_required_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("re_clearance_required_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReClearanceStatus(L5Status):
    """L5 doctrine output ``re_clearance_status`` (kind=status).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: re_clearance_status.
    """

    output_name: ClassVar[str] = "re_clearance_status"
    output_names: ClassVar[tuple[str, ...]] = ("re_clearance_status",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class ReclearanceGapReport(L5Report):
    """L5 doctrine output ``reclearance_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: reclearance_gap_report.
    """

    output_name: ClassVar[str] = "reclearance_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("reclearance_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ReclearanceReceiptRef(L5Ref):
    """L5 doctrine output ``reclearance_receipt_ref`` (kind=ref).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: reclearance_receipt_ref.
    """

    output_name: ClassVar[str] = "reclearance_receipt_ref"
    output_names: ClassVar[tuple[str, ...]] = ("reclearance_receipt_ref",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ReclearanceRequiredReceipt(L5Receipt):
    """L5 doctrine output ``reclearance_required_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: reclearance_required_receipt.
    """

    output_name: ClassVar[str] = "reclearance_required_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("reclearance_required_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReclearanceRuleReceipt(L5Receipt):
    """L5 doctrine output ``reclearance_rule_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: reclearance_rule_receipt.
    """

    output_name: ClassVar[str] = "reclearance_rule_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("reclearance_rule_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReclearanceStatusReport(L5Report):
    """L5 doctrine output ``reclearance_status_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: reclearance_status_report.
    """

    output_name: ClassVar[str] = "reclearance_status_report"
    output_names: ClassVar[tuple[str, ...]] = ("reclearance_status_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ResumeAuthorityReceipt(L5Receipt):
    """L5 doctrine output ``ResumeAuthorityReceipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: ResumeAuthorityReceipt, resume_authority_receipt.
    """

    output_name: ClassVar[str] = "ResumeAuthorityReceipt"
    output_names: ClassVar[tuple[str, ...]] = (
        "ResumeAuthorityReceipt",
        "resume_authority_receipt",
    )
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ResumeGapReport(L5Report):
    """L5 doctrine output ``resume_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: resume_gap_report.
    """

    output_name: ClassVar[str] = "resume_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("resume_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class ResumeReplayReceipt(L5Receipt):
    """L5 doctrine output ``resume_replay_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: resume_replay_receipt.
    """

    output_name: ClassVar[str] = "resume_replay_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("resume_replay_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ResumeScopeReceipt(L5Receipt):
    """L5 doctrine output ``resume_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: resume_scope_receipt.
    """

    output_name: ClassVar[str] = "resume_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("resume_scope_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ResumedPacketRef(L5Ref):
    """L5 doctrine output ``resumed_packet_ref`` (kind=ref).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: resumed_packet_ref.
    """

    output_name: ClassVar[str] = "resumed_packet_ref"
    output_names: ClassVar[tuple[str, ...]] = ("resumed_packet_ref",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ReviewerRoleMapReceipt(L5Receipt):
    """L5 doctrine output ``reviewer_role_map_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: reviewer_role_map_receipt.
    """

    output_name: ClassVar[str] = "reviewer_role_map_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("reviewer_role_map_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ReviewerVisibleScopeReceipt(L5Receipt):
    """L5 doctrine output ``reviewer_visible_scope_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: reviewer_visible_scope_receipt.
    """

    output_name: ClassVar[str] = "reviewer_visible_scope_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("reviewer_visible_scope_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class RuntimeHitlGapReport(L5Report):
    """L5 doctrine output ``runtime_hitl_gap_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: runtime_hitl_gap_report.
    """

    output_name: ClassVar[str] = "runtime_hitl_gap_report"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_hitl_gap_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class RuntimeHitlGovernanceReceipt(L5Receipt):
    """L5 doctrine output ``runtime_hitl_governance_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: runtime_hitl_governance_receipt.
    """

    output_name: ClassVar[str] = "runtime_hitl_governance_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("runtime_hitl_governance_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class ScopeImpactingHumanDiffReport(L5Report):
    """L5 doctrine output ``scope_impacting_human_diff_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: scope_impacting_human_diff_report.
    """

    output_name: ClassVar[str] = "scope_impacting_human_diff_report"
    output_names: ClassVar[tuple[str, ...]] = ("scope_impacting_human_diff_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class StaticHitlEvidenceIntakeReceipt(L5Receipt):
    """L5 doctrine output ``static_hitl_evidence_intake_receipt`` (kind=receipt).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: static_hitl_evidence_intake_receipt.
    """

    output_name: ClassVar[str] = "static_hitl_evidence_intake_receipt"
    output_names: ClassVar[tuple[str, ...]] = ("static_hitl_evidence_intake_receipt",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class StaticHitlGovernanceReport(L5Report):
    """L5 doctrine output ``static_hitl_governance_report`` (kind=report).

    Source doctrine: ``00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md``.
    Canonical doctrine names: static_hitl_governance_report.
    """

    output_name: ClassVar[str] = "static_hitl_governance_report"
    output_names: ClassVar[tuple[str, ...]] = ("static_hitl_governance_report",)
    source_doc: ClassVar[str] = "00.4_L5_HITL_Reclearance_and_Human_Input_Governance_detailed.md"
    output_kind: ClassVar[str] = "report"


__all__ = [
    "AllowedResponseTypeReceipt",
    "AuthorityFreezeReceipt",
    "AuthorityImpactingHumanDiffReport",
    "BootHitlGovernanceReport",
    "CriticalHitlGapReport",
    "DirectHumanWritePathReport",
    "FreezeReplayBindingReceipt",
    "FrozenEvidenceBundleReceipt",
    "FrozenPacketHashReceipt",
    "FrozenPacketRef",
    "HITLAuditReceipt",
    "HITLFreezePacket",
    "HardConstraintHumanOverrideReport",
    "HitlAuditGapReport",
    "HitlFreezeGapReport",
    "HitlFreezeReceipt",
    "HitlStaticGapRefMap",
    "HitlStaticGapReport",
    "HitlTemplateGovernanceReadinessReport",
    "HumanAddedEvidenceClaimReport",
    "HumanAuthorityAttemptReport",
    "HumanAuthorityWideningAttemptReport",
    "HumanDiffReceipt",
    "HumanDiffRef",
    "HumanDiffReplayReceipt",
    "HumanInputOriginReceipt",
    "HumanModificationDiff",
    "HumanModificationDiffReceipt",
    "HumanOriginGapReport",
    "HumanOverrideAttemptReport",
    "HumanOverrideLimitReceipt",
    "HumanPolicyExceptionRequestReport",
    "HumanPromptLikeContentReport",
    "HumanProvidedFactReport",
    "HumanProvidedSourceReport",
    "HumanReclearanceReceipt",
    "HumanReclearanceTriggerReport",
    "HumanResponseReceipt",
    "HumanReviewContextBoundaryReport",
    "HumanReviewEvidencePacket",
    "HumanReviewHashChainReceipt",
    "HumanReviewOriginLabelReport",
    "HumanReviewPacketGapReport",
    "HumanReviewPacketReceipt",
    "HumanReviewPolicyReceipt",
    "HumanReviewReconstructionReport",
    "HumanReviewReplayReceipt",
    "HumanReviewTemplateBoundaryReport",
    "HumanScopeGapReport",
    "HumanSourceOriginGapReport",
    "HumanSourceValidationNeededReceipt",
    "L5ReclearanceReceipt",
    "L5ReclearanceRequiredReceipt",
    "OldNewScopeDiff",
    "OperatorOverridePolicyReport",
    "ProhibitedResponseTypeReceipt",
    "ReClearanceRequiredReceipt",
    "ReClearanceStatus",
    "ReclearanceGapReport",
    "ReclearanceReceiptRef",
    "ReclearanceRequiredReceipt",
    "ReclearanceRuleReceipt",
    "ReclearanceStatusReport",
    "ResumeAuthorityReceipt",
    "ResumeGapReport",
    "ResumeReplayReceipt",
    "ResumeScopeReceipt",
    "ResumedPacketRef",
    "ReviewerRoleMapReceipt",
    "ReviewerVisibleScopeReceipt",
    "RuntimeHitlGapReport",
    "RuntimeHitlGovernanceReceipt",
    "ScopeImpactingHumanDiffReport",
    "StaticHitlEvidenceIntakeReceipt",
    "StaticHitlGovernanceReport",
]
