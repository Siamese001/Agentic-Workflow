"""Tests for §5.6 spec-named HITL contract receipts."""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6 import (
    FreezeReceipt,
    HITLDecision,
    HITLVerdict,
    HumanDecisionReceipt,
    HumanReviewPacket,
    L5ReclearanceRequest,
    build_freeze_receipt,
    build_human_decision_receipt,
    build_human_review_packet,
    build_l5_reclearance_request,
)

from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import base_packet


def test_freeze_receipt_carries_all_required_identity_and_hashes():
    packet = base_packet()
    receipt = build_freeze_receipt(
        packet,
        reason_codes=["HIGH_IMPACT_NEEDS_HITL"],
        frozen_artifact_refs=["sealed-1"],
        pending_state_diff_refs=["sd-1"],
        suspended_capability_refs=["cap-1"],
    )
    assert isinstance(receipt, FreezeReceipt)
    assert receipt.freeze_id.startswith("frz-")
    assert receipt.exit_review_packet_id.startswith("erp-")
    assert receipt.request_id == packet.request_id
    assert receipt.run_id == packet.run_id
    assert receipt.policy_hash == packet.policy_hash
    assert receipt.blueprint_hash == packet.blueprint_hash
    assert receipt.replay_key == packet.replay_key
    assert receipt.freeze_digest  # stable hex digest
    assert receipt.reason_codes == ["HIGH_IMPACT_NEEDS_HITL"]
    assert receipt.frozen_artifact_refs == ["sealed-1"]


def test_freeze_receipt_is_deterministic_for_same_packet():
    packet = base_packet()
    a = build_freeze_receipt(packet, reason_codes=["X"])
    b = build_freeze_receipt(packet, reason_codes=["X"])
    assert a.freeze_id == b.freeze_id
    assert a.freeze_digest == b.freeze_digest


def test_human_review_packet_includes_options_and_prohibited_actions():
    packet = base_packet()
    freeze = build_freeze_receipt(packet, reason_codes=["X"])
    rp = build_human_review_packet(
        packet,
        freeze,
        review_packet_id="hitl-abc",
        escalation_reason_codes=["WRITE_SCOPE_AMBIGUOUS"],
        minimal_context_refs=["ctx-1"],
        evidence_map_refs=["ev-1"],
        proposed_diff_refs=["diff-1"],
    )
    assert isinstance(rp, HumanReviewPacket)
    assert rp.freeze_id == freeze.freeze_id
    # options must include all H4 verdicts
    expected_options = {v.value for v in HITLVerdict}
    assert set(rp.human_decision_options) == expected_options
    # prohibited actions cover spec invariants
    forbidden = {
        "L4_DIRECT_WRITE",
        "POLICY_OVERRIDE",
        "SCOPE_WIDENING",
        "SECRET_LEAK",
        "AUTHORITY_CLAIM_ON_RETRIEVED_TEXT",
        "BYPASS_L5",
        "FORCE_UNSUPPORTED_FACT",
    }
    assert forbidden <= set(rp.prohibited_actions)
    assert rp.escalation_reason_codes == ["WRITE_SCOPE_AMBIGUOUS"]
    assert rp.packet_hash


def test_human_decision_receipt_marks_data_not_authority():
    review_packet_id = "hitl-abc"
    decision = HITLDecision(
        verdict=HITLVerdict.APPROVE,
        rationale="looks good",
        reviewer_id="alice",
        decision_at_ms=1700000000000,
    )
    rec = build_human_decision_receipt(review_packet_id, decision)
    assert isinstance(rec, HumanDecisionReceipt)
    assert rec.human_decision_id.startswith("hd-")
    assert rec.review_packet_id == review_packet_id
    assert rec.reviewer_id_ref == "alice"
    assert rec.decision == "APPROVE"
    assert rec.data_not_authority_assertion is True
    assert rec.timestamp == 1700000000000


def test_human_decision_receipt_marks_modification_when_packet_modified():
    packet = base_packet()
    decision = HITLDecision(
        verdict=HITLVerdict.MODIFY_DIFF,
        modified_packet=packet,
        rationale="adjusted diff",
        reviewer_id="bob",
        decision_at_ms=1700000000000,
    )
    rec = build_human_decision_receipt("hitl-x", decision)
    assert rec.modification_diff_ref == "modified"
    assert rec.decision == "MODIFY_DIFF"


def test_l5_reclearance_request_carries_authority_label_manifest():
    packet = base_packet()
    decision_receipt = HumanDecisionReceipt(
        human_decision_id="hd-zzz",
        review_packet_id="hitl-abc",
        reviewer_id_ref="alice",
        decision="MODIFY_DIFF",
        modification_diff_ref="modified",
    )
    req = build_l5_reclearance_request(
        packet,
        decision_receipt,
        required_rechecks=["X1A", "X1C", "X1F", "X1J"],
    )
    assert isinstance(req, L5ReclearanceRequest)
    assert req.reclearance_request_id.startswith("recl-")
    assert req.human_decision_receipt_ref == "hd-zzz"
    assert req.policy_hash == packet.policy_hash
    assert req.replay_key == packet.replay_key
    # spec invariant: human/retrieved are data, not authority
    assert req.authority_label_manifest["human_review_data"] == "data_not_authority"
    assert req.authority_label_manifest["retrieved_text"] == "data_not_authority"
    assert req.origin_trust_manifest["data_not_authority_assertion"] is True
    assert req.required_rechecks == ["X1A", "X1C", "X1F", "X1J"]
    assert req.modified_packet_ref == "modified"
    assert req.digest


def test_l5_reclearance_request_deterministic_for_same_input():
    packet = base_packet()
    decision_receipt = HumanDecisionReceipt(
        human_decision_id="hd-zzz",
        review_packet_id="hitl-abc",
        reviewer_id_ref="alice",
        decision="APPROVE",
    )
    a = build_l5_reclearance_request(packet, decision_receipt, required_rechecks=["X1A"])
    b = build_l5_reclearance_request(packet, decision_receipt, required_rechecks=["X1A"])
    assert a.reclearance_request_id == b.reclearance_request_id
    assert a.digest == b.digest
