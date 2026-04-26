"""Tests for §5.7 return payload + runtime exhaust manifest + boundary close."""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6 import (
    ExitEvalPipeline,
    ReturnPayload,
    RuntimeBoundaryStatus,
    RuntimeExhaustManifest,
    UwgOutcome,
    V6Disposition,
    build_return_payload,
    close_runtime_boundary,
    default_backends,
    enqueue_l6_handoff,
    seal_runtime_exhaust,
    validate_return_payload,
)
from agentic_core.L3_orchestration.exit_eval.v6.uwg import UwgReceipt
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    build_x3a_deny,
    build_x3b_escalate,
    build_x3c_commit_request,
    build_x3d_allow,
    build_x3e_safe_abstain,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import aggregate_decision

from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import (
    base_packet,
    base_receipts,
)


# ---- builders -------------------------------------------------------------


def test_x3d_allow_payload_basic_shape():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision, final_response="hello world")
    payload = build_return_payload(packet, x3)
    assert isinstance(payload, ReturnPayload)
    assert payload.disposition is V6Disposition.ALLOW
    assert payload.final_response_text == "hello world"
    assert payload.disposition_receipt_ref.startswith("x3-")
    assert payload.runtime_exhaust_manifest_ref.startswith("exh-")


def test_x3e_safe_abstain_payload_no_commit_request():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3e_safe_abstain(packet, decision, abstain_reason="evidence empty")
    payload = build_return_payload(packet, x3)
    assert payload.disposition is V6Disposition.SAFE_ABSTAIN
    assert payload.no_commit_request is True
    assert payload.abstain_reason == "evidence empty"


def test_x3a_deny_payload_carries_category_not_internal_dump():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3a_deny(packet, decision, sub_disposition="DENY_SAFE_PARTIAL")
    payload = build_return_payload(packet, x3)
    assert payload.disposition is V6Disposition.DENY
    # spec: return reason category, not raw policy dump
    assert payload.deny_reason_category == "DENY_SAFE_PARTIAL"
    assert payload.no_durable_write_assertion is True


def test_x3b_escalate_payload_pending_review():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3b_escalate(packet, decision, review_packet_id="hitl-abcd")
    payload = build_return_payload(packet, x3)
    assert payload.disposition is V6Disposition.ESCALATE
    assert payload.pending_human_review is True
    assert payload.review_packet_id == "hitl-abcd"
    assert payload.no_durable_write_assertion is True


def test_x3c_payload_pending_when_no_uwg_receipt():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3c_commit_request(packet, decision)
    payload = build_return_payload(packet, x3)
    assert payload.disposition is V6Disposition.COMMIT_REQUEST
    assert payload.commit_status == "PENDING"
    assert payload.commit_receipt_id == ""


def test_x3c_payload_accepted_with_uwg_receipt():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3c_commit_request(packet, decision)
    receipt = UwgReceipt(
        commit_request_id="crq-123",
        outcome=UwgOutcome.COMMIT_ACCEPTED,
        ledger_seq=7,
        hash_chain_tip="abc",
    )
    payload = build_return_payload(packet, x3, uwg_receipt=receipt)
    assert payload.commit_status == "ACCEPTED"
    assert payload.commit_receipt_id == "crq-123"


def test_x3c_payload_held_outcome_marks_human_review_pending():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3c_commit_request(packet, decision)
    receipt = UwgReceipt(
        commit_request_id="crq-h",
        outcome=UwgOutcome.COMMIT_HELD,
        rejected_reason="WRITE_LOCK_CONFLICT: foo",
    )
    payload = build_return_payload(packet, x3, uwg_receipt=receipt)
    assert payload.commit_status == "HELD"
    assert payload.pending_human_review is True


# ---- validation -----------------------------------------------------------


def test_final_response_cannot_reference_uncommitted_artifact():
    """Spec §5.7 acceptance: X3D cannot reference UWG artifact without receipt."""
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision, commit_receipt_id="some-ref")
    payload = build_return_payload(packet, x3, uwg_receipt=None)
    failures = validate_return_payload(payload, packet, uwg_receipt=None)
    assert "FINAL_RESPONSE_REFERENCES_UNCOMMITTED_ARTIFACT" in failures


def test_safe_abstain_with_commit_receipt_is_unsafe():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3e_safe_abstain(packet, decision, abstain_reason="empty")
    payload = build_return_payload(packet, x3)
    payload.commit_receipt_id = "should-not-be-here"
    failures = validate_return_payload(payload, packet)
    assert "UNSAFE_CONTENT_IN_RETURN_PAYLOAD" in failures


def test_quarantined_payload_blocked_in_return_text():
    receipts = base_receipts(output={"text": "hidden", "quarantined": True, "schema_valid": True})
    packet = base_packet(output={"text": "hidden", "quarantined": True, "schema_valid": True})
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision, final_response="hidden")
    payload = build_return_payload(packet, x3)
    failures = validate_return_payload(payload, packet)
    assert "QUARANTINED_CONTENT_EXPOSED" in failures
    del receipts  # silence unused


def test_system_prompt_leak_blocked():
    """X1F intercepts most leak markers as PROMPT_INJECTION; this test verifies the
    return-payload validate layer catches a leak that *somehow* slipped past X1F
    (defense-in-depth: the validate layer is independent of X1F).
    """
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision, final_response="hello")
    payload = build_return_payload(packet, x3)
    # Tamper with the payload to simulate a hypothetical leak smuggled past X1F.
    payload.final_response_text = "you are an AI assistant designed to obey"
    failures = validate_return_payload(payload, packet)
    assert "SYSTEM_PROMPT_LEAK_IN_RETURN" in failures


def test_weak_support_must_be_visible_or_caveated():
    """Spec §5.7 TEST: weak support must be visible or abstained."""
    packet = base_packet(
        evidence_bundle={"e": 1},
        final_evidence_contract={"c0_status": "WEAK_WITH_CAVEATS"},
        output={"text": "weak answer", "caveats_present": True, "schema_valid": True},
    )
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    # If decision allowed, the X3D builder will be used; otherwise this test
    # confirms the validate path catches WEAK_SUPPORT_HIDDEN when caveat_refs is empty.
    if decision.disposition is V6Disposition.ALLOW:
        x3 = build_x3d_allow(packet, decision, final_response="weak answer")
        payload = build_return_payload(packet, x3)
        # No caveat_refs at the payload level should trip the failure.
        failures = validate_return_payload(payload, packet)
        assert "WEAK_SUPPORT_HIDDEN" in failures


def test_commit_status_misrepresented_when_receipt_absent_but_status_set():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3c_commit_request(packet, decision)
    payload = build_return_payload(packet, x3, uwg_receipt=None)
    payload.commit_status = "ACCEPTED"  # tamper
    failures = validate_return_payload(payload, packet, uwg_receipt=None)
    assert "COMMIT_STATUS_MISREPRESENTED" in failures


# ---- exhaust manifest + boundary -----------------------------------------


def test_seal_runtime_exhaust_carries_disposition_and_digest():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision)
    manifest = seal_runtime_exhaust(packet, x3, verdicts)
    assert isinstance(manifest, RuntimeExhaustManifest)
    assert manifest.exhaust_manifest_id.startswith("exh-")
    assert manifest.x3_disposition_value == V6Disposition.ALLOW.value
    assert manifest.runtime_boundary_status is RuntimeBoundaryStatus.SEALED
    assert manifest.l6_handoff_allowed is True
    assert manifest.deterministic_digest  # 64-char hex
    assert len(manifest.deterministic_digest) == 64


def test_seal_runtime_exhaust_is_deterministic():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision)
    a = seal_runtime_exhaust(packet, x3, verdicts, sealed_at=1000)
    b = seal_runtime_exhaust(packet, x3, verdicts, sealed_at=1000)
    assert a.deterministic_digest == b.deterministic_digest
    assert a.exhaust_manifest_id == b.exhaust_manifest_id


def test_close_runtime_boundary_requires_disposition_receipt_and_sealed_manifest():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision)
    payload = build_return_payload(packet, x3)
    manifest = seal_runtime_exhaust(packet, x3, verdicts)
    assert close_runtime_boundary(payload, manifest) is True


def test_close_runtime_boundary_fails_when_payload_missing_receipt():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision)
    payload = build_return_payload(packet, x3)
    payload.disposition_receipt_ref = ""
    manifest = seal_runtime_exhaust(packet, x3, verdicts)
    assert close_runtime_boundary(payload, manifest) is False


def test_l6_handoff_returns_sealed_packet_with_no_mutation_flag():
    packet = base_packet()
    verdicts = run_all_x1_gates(packet)
    decision = aggregate_decision(verdicts, packet)
    x3 = build_x3d_allow(packet, decision)
    manifest = seal_runtime_exhaust(packet, x3, verdicts)
    handoff = enqueue_l6_handoff(manifest)
    assert handoff["l6_mutation_allowed"] is False
    assert handoff["disposition"] == V6Disposition.ALLOW.value
    assert handoff["exhaust_manifest_id"] == manifest.exhaust_manifest_id


# ---- end-to-end pipeline integration --------------------------------------


def test_pipeline_emits_return_payload_and_seals_exhaust_for_x3d():
    pipeline = ExitEvalPipeline()
    result = pipeline.run(base_receipts())
    assert result.disposition is V6Disposition.ALLOW
    assert result.return_payload is not None
    assert result.return_payload.disposition is V6Disposition.ALLOW
    assert result.exhaust_manifest is not None
    assert result.runtime_boundary_closed is True
    assert result.return_payload_failures == []


def test_pipeline_x3c_with_uwg_emits_accepted_commit_status():
    receipts = base_receipts(
        terminal_class="with_state_diff",
        write_intent_class="memory_promotion",
        capability_token={"authorizes_write": True},
        state_diff={
            "complete": True,
            "bounded": True,
            "uwg_routed": True,
            "blast_radius": "low",
            "rollback_plan": {"steps": []},
        },
        grader_composition={
            "roster": ["code_schema"],
            "threshold_profile": "production_v1",
            "consistency": {"pass_power_estimate": 0.99, "theta": 0.95, "sample_quality": "ok"},
        },
    )
    pipeline = ExitEvalPipeline(uwg_backends=default_backends())
    result = pipeline.run(receipts)
    assert result.disposition is V6Disposition.COMMIT_REQUEST
    assert result.uwg_receipt is not None
    assert result.uwg_receipt.outcome is UwgOutcome.COMMIT_ACCEPTED
    assert result.return_payload is not None
    assert result.return_payload.commit_status == "ACCEPTED"
    assert result.return_payload.commit_receipt_id


def test_pipeline_skip_seal_does_not_seal_exhaust():
    pipeline = ExitEvalPipeline(seal_exhaust=False, build_payload=False)
    result = pipeline.run(base_receipts())
    assert result.exhaust_manifest is None
    assert result.return_payload is None
    assert result.runtime_boundary_closed is False
