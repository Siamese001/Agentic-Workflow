"""Tests for v6 X2 aggregate matrix, X3 packet builders, and HITL flow."""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6 import (
    AggregateDecision,
    GateResult,
    GateVerdict,
    HITLDecision,
    HITLVerdict,
    V6Disposition,
    X3CommitRequestPacket,
    aggregate_decision,
    build_x3_packet,
    build_x3a_deny,
    build_x3b_escalate,
    build_x3c_commit_request,
    build_x3d_allow,
    build_x3e_safe_abstain,
    materialize_review_packet,
    run_all_x1_gates,
    run_l5_reclearance,
)

from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import base_packet as _base_packet

_CERT_REF = "l5:cert:hitl"


def base_packet(**overrides: object):
    return _base_packet(l5_certification_refs=(_CERT_REF,), **overrides)


# ---- X2 aggregate matrix ----


def test_x2_clean_answer_only_allows() -> None:
    p = base_packet()
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    assert decision.disposition is V6Disposition.ALLOW


def test_x2_hard_fail_routes_to_deny() -> None:
    p = base_packet(sandbox_envelope={"isolation_intact": False})
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    assert decision.disposition is V6Disposition.DENY
    assert "SANDBOX_BREACH" in decision.reason_codes
    assert "X1C" in decision.failed_gate_ids


def test_x2_unauthorized_mutation_routes_to_deny() -> None:
    p = base_packet(state_diff={"direct_l4_write_caller": "L2"})
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    assert decision.disposition is V6Disposition.DENY
    assert "UNAUTHORIZED_MUTATION" in decision.reason_codes


def test_x2_judge_abstain_routes_to_escalate() -> None:
    p = base_packet(
        evidence_bundle={"sources": ["doc-1"]},
        final_evidence_contract={"c0_status": "PASS"},
        output={"text": "x", "judge_abstained": True},
    )
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    assert decision.disposition is V6Disposition.ESCALATE


def test_x2_evidence_empty_routes_to_safe_abstain() -> None:
    p = base_packet(
        evidence_bundle={"sources": []},
        final_evidence_contract={"c0_status": "EMPTY"},
    )
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    assert decision.disposition is V6Disposition.SAFE_ABSTAIN
    assert "EVIDENCE_EMPTY" in decision.reason_codes


def test_x2_commit_path_clear() -> None:
    p = base_packet(
        terminal_class="with_state_diff",
        write_intent_class="user_update",
        state_diff={
            "complete": True,
            "bounded": True,
            "blast_radius": "low",
            "uwg_routed": True,
        },
        capability_token={"authorizes_write": True, "expired": False},
        grader_composition={
            "roster": ["x"],
            "threshold_profile": "p",
            "consistency": {"pass_power_estimate": 0.98, "theta": 0.95, "sample_quality": "ok"},
        },
    )
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    assert decision.disposition is V6Disposition.COMMIT_REQUEST
    assert decision.requires_uwg_handoff


def test_x2_commit_path_blocked_by_x1g_unknown() -> None:
    p = base_packet(
        terminal_class="with_state_diff",
        write_intent_class="user_update",
        state_diff={
            "complete": True,
            "bounded": True,
            "blast_radius": "low",
            "uwg_routed": True,
        },
        capability_token={"authorizes_write": True},
    )  # no consistency receipt -> X1G UNKNOWN
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    # X1G UNKNOWN escalates per spec invariant 25.
    assert decision.disposition is V6Disposition.ESCALATE


# ---- X3 packet builders ----


def test_x3a_deny_packet_shape() -> None:
    p = base_packet()
    decision = AggregateDecision(
        disposition=V6Disposition.DENY,
        failed_gate_ids=["X1C"],
        reason_codes=["SANDBOX_BREACH"],
        rationale="hard_fail_condition",
    )
    pkt = build_x3a_deny(p, decision)
    assert pkt.disposition is V6Disposition.DENY
    assert pkt.sub_disposition == "DENY_STOP"
    assert "SANDBOX_BREACH" in pkt.reason_codes
    assert pkt.user_safe_message  # non-empty
    assert pkt.trace_root == "trace-1"


def test_x3b_escalate_packet_includes_freeze_state() -> None:
    p = base_packet()
    decision = AggregateDecision(
        disposition=V6Disposition.ESCALATE,
        reason_codes=["JUDGE_ABSTAINED"],
        rationale="escalation_required",
    )
    pkt = build_x3b_escalate(p, decision, h1_freeze_state={"auth_state": "FROZEN"})
    assert pkt.disposition is V6Disposition.ESCALATE
    assert "JUDGE_ABSTAINED" in pkt.trigger_reasons
    assert pkt.review_packet_id.startswith("hitl-")
    assert pkt.h1_freeze_state["auth_state"] == "FROZEN"


def test_x3c_commit_request_carries_full_handoff() -> None:
    p = base_packet(
        terminal_class="with_state_diff",
        write_intent_class="user_update",
        state_diff={
            "complete": True,
            "bounded": True,
            "blast_radius": "low",
            "uwg_routed": True,
            "before_snapshot": {"v": 1},
            "after_proposed_snapshot": {"v": 2},
            "rollback_plan": {"steps": ["restore"]},
        },
        capability_token={"authorizes_write": True},
    )
    decision = AggregateDecision(
        disposition=V6Disposition.COMMIT_REQUEST,
        rationale="commit_path_clear",
        requires_uwg_handoff=True,
    )
    pkt = build_x3c_commit_request(p, decision)
    assert isinstance(pkt, X3CommitRequestPacket)
    assert pkt.commit_request_id.startswith("crq-")
    assert pkt.policy_hash == "pol::v1"
    assert pkt.replay_key == "rk-1"
    assert pkt.write_intent_class == "user_update"
    assert pkt.before_snapshot == {"v": 1}
    assert pkt.rollback_plan == {"steps": ["restore"]}


def test_x3d_allow_packet_carries_response() -> None:
    p = base_packet()
    decision = AggregateDecision(disposition=V6Disposition.ALLOW, rationale="answer_only_clear")
    pkt = build_x3d_allow(p, decision)
    assert pkt.final_response == "Paris is the capital of France."
    assert pkt.schema_status == "valid"


def test_x3e_safe_abstain_packet() -> None:
    p = base_packet()
    decision = AggregateDecision(
        disposition=V6Disposition.SAFE_ABSTAIN,
        reason_codes=["EVIDENCE_EMPTY"],
        rationale="safe_abstain_evidence_class",
    )
    pkt = build_x3e_safe_abstain(p, decision)
    assert "EVIDENCE_EMPTY" in pkt.abstain_reason


def test_build_x3_packet_dispatches_correctly() -> None:
    p = base_packet()
    for disp, expected_cls in (
        (V6Disposition.DENY, "X3DenyPacket"),
        (V6Disposition.ESCALATE, "X3EscalatePacket"),
        (V6Disposition.ALLOW, "X3AllowPacket"),
        (V6Disposition.SAFE_ABSTAIN, "X3SafeAbstainPacket"),
    ):
        d = AggregateDecision(disposition=disp, rationale="test")
        pkt = build_x3_packet(p, d)
        assert type(pkt).__name__ == expected_cls


# ---- HITL flow ----


def test_materialize_review_packet_includes_required_fields() -> None:
    p = base_packet()
    verdicts = run_all_x1_gates(p)
    pkt = materialize_review_packet(p, verdicts, review_packet_id="hitl-1")
    assert pkt.review_packet_id == "hitl-1"
    # H1 freeze state must contain all enumerated fields
    for f in (
        "auth_state",
        "write_auth",
        "capability_token_status",
        "pending_diffs",
        "provider_egress",
        "external_action",
        "additional_retrieval",
        "durable_write",
    ):
        assert f in pkt.h1_freeze_state
    # Per-dimension scores enumerated for each X1 gate
    assert len(pkt.contents["per_dimension_scores"]) == 10


def test_l5_reclearance_reject_routes_to_deny() -> None:
    p = base_packet()
    decision = HITLDecision(verdict=HITLVerdict.REJECT, reviewer_id="r1")
    result = run_l5_reclearance(decision, p)
    assert result.next_disposition is V6Disposition.DENY


def test_l5_reclearance_return_to_l1_sets_reroute_target() -> None:
    p = base_packet()
    decision = HITLDecision(verdict=HITLVerdict.RETURN_TO_L1)
    result = run_l5_reclearance(decision, p)
    assert result.next_disposition is V6Disposition.DENY
    assert result.reroute_target == "L1"


def test_l5_reclearance_modify_diff_reruns_full_x1_subset() -> None:
    p = base_packet()
    decision = HITLDecision(verdict=HITLVerdict.MODIFY_DIFF, modified_packet=p)
    result = run_l5_reclearance(decision, p)
    # MODIFY_DIFF re-runs X1A,B,C,D,E,F,G,J = 8 gates.
    assert len(result.re_run_verdicts) == 8
    gate_ids = {v.gate_id for v in result.re_run_verdicts}
    assert gate_ids == {"X1A", "X1B", "X1C", "X1D", "X1E", "X1F", "X1G", "X1J"}


def test_l5_reclearance_request_replay_reruns_x1h_x1i() -> None:
    p = base_packet()
    decision = HITLDecision(verdict=HITLVerdict.REQUEST_REPLAY)
    result = run_l5_reclearance(decision, p)
    assert {v.gate_id for v in result.re_run_verdicts} == {"X1H", "X1I"}


# ---- end-to-end smoke ----


def test_end_to_end_clean_answer_only_emits_x3d() -> None:
    p = base_packet()
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    pkt = build_x3_packet(p, decision)
    assert decision.disposition is V6Disposition.ALLOW
    assert type(pkt).__name__ == "X3AllowPacket"


def test_end_to_end_l4_write_attempt_emits_x3a() -> None:
    p = base_packet(state_diff={"direct_l4_write_caller": "L2"})
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    pkt = build_x3_packet(p, decision)
    assert decision.disposition is V6Disposition.DENY
    assert type(pkt).__name__ == "X3DenyPacket"


def test_end_to_end_evidence_empty_emits_x3e() -> None:
    p = base_packet(
        evidence_bundle={"sources": []},
        final_evidence_contract={"c0_status": "EMPTY"},
    )
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    pkt = build_x3_packet(p, decision)
    assert decision.disposition is V6Disposition.SAFE_ABSTAIN
    assert type(pkt).__name__ == "X3SafeAbstainPacket"
