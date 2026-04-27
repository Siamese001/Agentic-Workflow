"""Tests for `hitl_receipts.py` (G4 — 00A.4 HITL Receipt Family)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5 import (
    HITLAuditReceipt,
    HITLFreezePacket,
    HumanInputOriginReceipt,
    HumanModificationDiff,
    HumanReviewEvidencePacket,
    HumanReviewScopeReceipt,
    ResumeAuthorityReceipt,
)


def test_freeze_packet_requires_bounded_response_types() -> None:
    with pytest.raises(ValueError, match="bounded_response_types"):
        HITLFreezePacket(
            freeze_id="f",
            request_id="r",
            trace_id="t",
            reviewer_visible_scope=(),
            freeze_reason="x",
            proposed_action="y",
            risk_summary="z",
            alternatives=(),
            bounded_response_types=(),
            frozen_at="",
        )


def test_review_evidence_packet_must_be_human_review_origin() -> None:
    with pytest.raises(ValueError, match="origin_label"):
        HumanReviewEvidencePacket(
            evidence_id="e",
            review_id="r",
            reviewer_id="rv",
            reviewer_role="ops",
            evidence_payload_hash="h",
            evidence_origin_label="user_turn",  # forbidden
            boundary_classification="untrusted_data",
            submitted_at="",
        )


def test_review_evidence_packet_must_be_data_until_recleared() -> None:
    with pytest.raises(ValueError, match="boundary_classification"):
        HumanReviewEvidencePacket(
            evidence_id="e",
            review_id="r",
            reviewer_id="rv",
            reviewer_role="ops",
            evidence_payload_hash="h",
            evidence_origin_label="human_review",
            boundary_classification="trusted_instruction",  # forbidden
            submitted_at="",
        )


def test_modification_diff_detects_scope_widening() -> None:
    diff = HumanModificationDiff(
        diff_id="d",
        review_id="r",
        original_packet_hash="oh",
        modified_packet_hash="mh",
        changed_fields=("requested_authority",),
        added_authority_fields=("connector:notion",),
        removed_authority_fields=(),
        diff_serialization="{}",
        generated_at="",
    )
    assert diff.widens_scope is True
    diff_no_widen = HumanModificationDiff(
        diff_id="d2",
        review_id="r",
        original_packet_hash="oh",
        modified_packet_hash="mh",
        changed_fields=("comment",),
        added_authority_fields=(),
        removed_authority_fields=(),
        diff_serialization="{}",
        generated_at="",
    )
    assert diff_no_widen.widens_scope is False


def test_review_scope_receipt_widening_detection() -> None:
    receipt = HumanReviewScopeReceipt(
        receipt_id="rs",
        review_id="r",
        original_requested_authority=("read:doc",),
        modified_requested_authority=("read:doc", "write:doc"),
        widened_scopes=("write:doc",),
        narrowed_scopes=(),
    )
    assert receipt.widening_detected is True


def test_resume_authority_receipt_validates_status() -> None:
    with pytest.raises(ValueError, match="reclearance_status"):
        ResumeAuthorityReceipt(
            receipt_id="ra",
            review_id="r",
            pre_review_capability_token_hash="x",
            post_review_capability_token_hash="y",
            sandbox_envelope_hash="s",
            resume_scope=(),
            reclearance_status="BOGUS",
            resume_replay_ref="",
            resume_audit_ref="",
            resumed_at="",
        )


def test_human_input_origin_receipt_enforces_label() -> None:
    with pytest.raises(ValueError, match="origin_label"):
        HumanInputOriginReceipt(
            receipt_id="r",
            review_id="r",
            field_paths=(),
            origin_label="user_turn",
        )


def test_hitl_audit_receipt_serializes() -> None:
    r = HITLAuditReceipt(
        receipt_id="x",
        review_id="r",
        freeze_packet_hash="fh",
        response_packet_hash="rh",
        diff_hash="dh",
        reclearance_hash="rch",
        resume_authority_hash="rah",
        replay_envelope_ref="rep",
    )
    d = r.to_dict()
    assert d["receipt_id"] == "x"
    assert d["replay_envelope_ref"] == "rep"
