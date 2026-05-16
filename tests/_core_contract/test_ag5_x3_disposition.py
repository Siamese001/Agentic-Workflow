"""AG-5 X3 emitter smoke tests."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType
from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult, X1Item, X1Verdict
from agentic_core.runtime.exit.exit_disposition import X3D_ALLOW_FINISH
from agentic_core.runtime.exit.x2_aggregation_result import X2AggregationResult
from agentic_core.runtime.exit.x3_emitter import AG5ExitEmitError, emit_ag5_exit_disposition_receipt


def _neutral_pass_checkout() -> X1CheckoutResult:
    na = lambda gid: X1Item(
        gate_id=gid,
        verdict=X1Verdict.NOT_APPLICABLE,
        not_applicable_reason="neutral compatibility envelope",
    )
    return X1CheckoutResult(
        x1a_todays_rules=X1Item(gate_id="X1A", verdict=X1Verdict.PASS),
        x1b_answered_it=X1Item(gate_id="X1B", verdict=X1Verdict.PASS),
        x1c_safe_to_leave=X1Item(gate_id="X1C", verdict=X1Verdict.PASS),
        x1d_answer_good=na("X1D"),
        x1e_trajectory_ok=na("X1E"),
        x1f_story_adds_up=na("X1F"),
        x1g_replay_eligible=na("X1G"),
        x1h_observable=na("X1H"),
        x1i_consistent_across_runs=na("X1I"),
        x1j_write_eligibility=na("X1J"),
    )


def _packet_l6_clean() -> ExitReviewPacket:
    return ExitReviewPacket(
        source_type=SourceType.APP_BINDING_COMPATIBILITY_PACKAGE,
        request_id="req-x3",
        run_id="run-x3",
        trace_root="trace-x3",
        policy_hash="ph",
        replay_key="replay-x3",
        route_contract={"policy_hash": "ph"},
        terminal_class="answer_only",
        output={"text": "ok"},
        app_id="apps_rg",
        task_class="resume_generation",
    )


def _x2_allow() -> X2AggregationResult:
    return X2AggregationResult(
        disposition_candidate=X3D_ALLOW_FINISH,
        decisive_failures=(),
        unknown_material_fields=(),
        policy_ref="ag5-test-policy",
        emits_final_x3=False,
    )


def test_emit_allow_finish_requires_user_visible_ref() -> None:
    pkt = _packet_l6_clean()
    x1 = _neutral_pass_checkout()
    assert x1.is_overall_pass()
    x2 = _x2_allow()
    with pytest.raises(AG5ExitEmitError, match="user_visible_response_ref"):
        emit_ag5_exit_disposition_receipt(packet=pkt, x1=x1, x2=x2, supplementary_refs={})

    receipt = emit_ag5_exit_disposition_receipt(
        packet=pkt,
        x1=x1,
        x2=x2,
        supplementary_refs={
            "user_visible_response_ref": "resp://test",
            "deterministic_digest": "digest://test",
            "gate_mesh_result_ref": "mesh://test",
        },
    )
    assert receipt.x3_code == X3D_ALLOW_FINISH


def test_emit_blocks_l6_anomaly_flag() -> None:
    pkt = _packet_l6_clean()
    pkt.anomaly_flags.append("L6_CURRENT_RUN_RESCUE")
    x1 = _neutral_pass_checkout()
    x2 = _x2_allow()
    with pytest.raises(AG5ExitEmitError, match="L6"):
        emit_ag5_exit_disposition_receipt(
            packet=pkt,
            x1=x1,
            x2=x2,
            supplementary_refs={
                "user_visible_response_ref": "resp://test",
                "deterministic_digest": "digest://test",
            },
        )
