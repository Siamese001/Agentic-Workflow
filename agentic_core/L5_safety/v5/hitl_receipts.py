"""L5 HITL Receipt Family (00A.4) — G4 closure.

Implements the 7 doctrine-named contracts that together govern human input
as data, not authority. Complements existing ``HITLDispositionPacket``.

Doctrine: ``docs/reference/00A_L5_Governance_Safety/00A.4_L5_HITL_Reclearance_Human_Input_Gov.md``
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _sorted_strings(values: tuple[str, ...]) -> list[str]:
    return sorted(values)


# =============================================================================
# 00A.4 §6.1 contract 1 — HITLFreezePacket
# =============================================================================


@dataclass(frozen=True)
class HITLFreezePacket:
    """Bounded packet emitted when L5 freezes execution for human review.

    Carries reviewer-visible scope (NOT execution authority). Frozen authority
    means: no token issued, no capability granted, no execution proceeds until
    re-clearance.
    """

    freeze_id: str
    request_id: str
    trace_id: str
    reviewer_visible_scope: tuple[str, ...]
    freeze_reason: str
    proposed_action: str
    risk_summary: str
    alternatives: tuple[str, ...]
    bounded_response_types: tuple[str, ...]  # APPROVE | MODIFY_DIFF | REJECT | REQUEST_MORE_INFO
    frozen_at: str

    def __post_init__(self) -> None:
        if not self.bounded_response_types:
            raise ValueError(
                "HITLFreezePacket: bounded_response_types required (00A.4 §11)",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "alternatives": _sorted_strings(self.alternatives),
            "bounded_response_types": _sorted_strings(self.bounded_response_types),
            "freeze_id": self.freeze_id,
            "freeze_reason": self.freeze_reason,
            "frozen_at": self.frozen_at,
            "proposed_action": self.proposed_action,
            "request_id": self.request_id,
            "reviewer_visible_scope": _sorted_strings(self.reviewer_visible_scope),
            "risk_summary": self.risk_summary,
            "trace_id": self.trace_id,
        }


# =============================================================================
# 00A.4 §6.1 contract 2 — HumanReviewEvidencePacket
# =============================================================================


@dataclass(frozen=True)
class HumanReviewEvidencePacket:
    """Evidence packet carrying human-provided artifacts as data, not authority."""

    evidence_id: str
    review_id: str
    reviewer_id: str
    reviewer_role: str
    evidence_payload_hash: str
    evidence_origin_label: str  # always "human_review"
    boundary_classification: str  # always "untrusted_data" until re-cleared
    submitted_at: str

    def __post_init__(self) -> None:
        if self.evidence_origin_label != "human_review":
            raise ValueError(
                "HumanReviewEvidencePacket: evidence_origin_label MUST be "
                "'human_review' (00A.4 §11)",
            )
        if self.boundary_classification not in {"untrusted_data", "quarantined"}:
            raise ValueError(
                "HumanReviewEvidencePacket: boundary_classification MUST be "
                "untrusted_data or quarantined (00A.4 §6.2 — human input is "
                "data until re-cleared)",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_classification": self.boundary_classification,
            "evidence_id": self.evidence_id,
            "evidence_origin_label": self.evidence_origin_label,
            "evidence_payload_hash": self.evidence_payload_hash,
            "review_id": self.review_id,
            "reviewer_id": self.reviewer_id,
            "reviewer_role": self.reviewer_role,
            "submitted_at": self.submitted_at,
        }


# =============================================================================
# 00A.4 §6.1 contract 3 — HumanModificationDiff
# =============================================================================


@dataclass(frozen=True)
class HumanModificationDiff:
    """Deterministic diff between original packet and human-modified version."""

    diff_id: str
    review_id: str
    original_packet_hash: str
    modified_packet_hash: str
    changed_fields: tuple[str, ...]
    added_authority_fields: tuple[str, ...]  # scope-widening detection
    removed_authority_fields: tuple[str, ...]
    diff_serialization: str  # canonical JSON diff
    generated_at: str

    @property
    def widens_scope(self) -> bool:
        return bool(self.added_authority_fields)

    def to_dict(self) -> dict[str, Any]:
        return {
            "added_authority_fields": _sorted_strings(self.added_authority_fields),
            "changed_fields": _sorted_strings(self.changed_fields),
            "diff_id": self.diff_id,
            "diff_serialization": self.diff_serialization,
            "generated_at": self.generated_at,
            "modified_packet_hash": self.modified_packet_hash,
            "original_packet_hash": self.original_packet_hash,
            "removed_authority_fields": _sorted_strings(self.removed_authority_fields),
            "review_id": self.review_id,
            "widens_scope": self.widens_scope,
        }


# =============================================================================
# 00A.4 §6.1 contract 4 — HumanReviewScopeReceipt
# =============================================================================


@dataclass(frozen=True)
class HumanReviewScopeReceipt:
    """Receipt detecting whether human review widened scope beyond original packet."""

    receipt_id: str
    review_id: str
    original_requested_authority: tuple[str, ...]
    modified_requested_authority: tuple[str, ...]
    widened_scopes: tuple[str, ...]
    narrowed_scopes: tuple[str, ...]

    @property
    def widening_detected(self) -> bool:
        return bool(self.widened_scopes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "modified_requested_authority": _sorted_strings(self.modified_requested_authority),
            "narrowed_scopes": _sorted_strings(self.narrowed_scopes),
            "original_requested_authority": _sorted_strings(self.original_requested_authority),
            "receipt_id": self.receipt_id,
            "review_id": self.review_id,
            "widened_scopes": _sorted_strings(self.widened_scopes),
            "widening_detected": self.widening_detected,
        }


# =============================================================================
# 00A.4 §6.1 contract 5 — ResumeAuthorityReceipt
# =============================================================================


@dataclass(frozen=True)
class ResumeAuthorityReceipt:
    """Authority binding for resuming execution after human review."""

    receipt_id: str
    review_id: str
    pre_review_capability_token_hash: str
    post_review_capability_token_hash: str  # may differ if re-issued
    sandbox_envelope_hash: str
    resume_scope: tuple[str, ...]
    reclearance_status: str  # CLEARED | REJECTED | REQUIRES_RE_REVIEW
    resume_replay_ref: str
    resume_audit_ref: str
    resumed_at: str

    def __post_init__(self) -> None:
        if self.reclearance_status not in {"CLEARED", "REJECTED", "REQUIRES_RE_REVIEW"}:
            raise ValueError(
                f"ResumeAuthorityReceipt: reclearance_status must be "
                f"CLEARED|REJECTED|REQUIRES_RE_REVIEW, got {self.reclearance_status!r}",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "post_review_capability_token_hash": self.post_review_capability_token_hash,
            "pre_review_capability_token_hash": self.pre_review_capability_token_hash,
            "receipt_id": self.receipt_id,
            "reclearance_status": self.reclearance_status,
            "resume_audit_ref": self.resume_audit_ref,
            "resume_replay_ref": self.resume_replay_ref,
            "resume_scope": _sorted_strings(self.resume_scope),
            "resumed_at": self.resumed_at,
            "review_id": self.review_id,
            "sandbox_envelope_hash": self.sandbox_envelope_hash,
        }


# =============================================================================
# 00A.4 §6.1 contract 6 — HumanInputOriginReceipt
# =============================================================================


@dataclass(frozen=True)
class HumanInputOriginReceipt:
    """Receipt that human input was correctly labeled `human_review` at ingress."""

    receipt_id: str
    review_id: str
    field_paths: tuple[str, ...]
    origin_label: str = "human_review"
    boundary_classification: str = "untrusted_data"

    def __post_init__(self) -> None:
        if self.origin_label != "human_review":
            raise ValueError(
                "HumanInputOriginReceipt: origin_label MUST be 'human_review'",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_classification": self.boundary_classification,
            "field_paths": _sorted_strings(self.field_paths),
            "origin_label": self.origin_label,
            "receipt_id": self.receipt_id,
            "review_id": self.review_id,
        }


# =============================================================================
# 00A.4 §6.1 contract 7 — HITLAuditReceipt
# =============================================================================


@dataclass(frozen=True)
class HITLAuditReceipt:
    """Hash-bound, replay-aware HITL audit receipt."""

    receipt_id: str
    review_id: str
    freeze_packet_hash: str
    response_packet_hash: str
    diff_hash: str
    reclearance_hash: str
    resume_authority_hash: str
    replay_envelope_ref: str
    audit_event_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_event_hash": self.audit_event_hash,
            "diff_hash": self.diff_hash,
            "freeze_packet_hash": self.freeze_packet_hash,
            "receipt_id": self.receipt_id,
            "reclearance_hash": self.reclearance_hash,
            "replay_envelope_ref": self.replay_envelope_ref,
            "response_packet_hash": self.response_packet_hash,
            "resume_authority_hash": self.resume_authority_hash,
            "review_id": self.review_id,
        }


__all__ = [
    "HITLAuditReceipt",
    "HITLFreezePacket",
    "HumanInputOriginReceipt",
    "HumanModificationDiff",
    "HumanReviewEvidencePacket",
    "HumanReviewScopeReceipt",
    "ResumeAuthorityReceipt",
]
