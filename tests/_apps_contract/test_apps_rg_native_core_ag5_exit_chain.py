"""W4: AG-5 Exit chain over native terminal envelope (normalize → X1 → X2 → X3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType
from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.native_contract_chain import (
    build_ag5_terminal_dict_for_native_proof,
    build_native_core_contract_chain_from_binding,
)
from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult, X1Item, X1Verdict
from agentic_core.runtime.exit.exit_disposition import X3D_ALLOW_FINISH
from agentic_core.runtime.exit.exit_review_normalizer import normalize_ag5_terminal_input
from agentic_core.runtime.exit.x1_checkout_runner import run_ag5_x1_checkout
from agentic_core.runtime.exit.x2_aggregation_result import X2AggregationResult
from agentic_core.runtime.exit.x2_aggregator import aggregate_x1_for_exit
from agentic_core.runtime.exit.x3_emitter import AG5ExitEmitError, emit_ag5_exit_disposition_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_native_binding_terminal_full_ag5_chain_single_x3(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    pkg = load_app_binding_package(FIXTURE_PKG)
    chain = build_native_core_contract_chain_from_binding(pkg, repo_root=REPO_ROOT)
    raw = build_ag5_terminal_dict_for_native_proof(chain)
    pkt = normalize_ag5_terminal_input(raw)
    x1 = run_ag5_x1_checkout(pkt)
    assert x1.is_overall_pass()
    x2 = aggregate_x1_for_exit(x1)
    receipt = emit_ag5_exit_disposition_receipt(
        packet=pkt,
        x1=x1,
        x2=x2,
        supplementary_refs={
            "user_visible_response_ref": "resp://native-core-e2e",
            "deterministic_digest": "digest://native-core-e2e",
            "gate_mesh_result_ref": "mesh://native-core-e2e",
        },
    )
    assert receipt.x3_code == X3D_ALLOW_FINISH
    assert not any(tmp_path.iterdir())


def test_unknown_verdict_not_overall_pass() -> None:
    checkout = X1CheckoutResult(
        x1a_todays_rules=X1Item(gate_id="X1A", verdict=X1Verdict.PASS),
        x1b_answered_it=X1Item(gate_id="X1B", verdict=X1Verdict.PASS),
        x1c_safe_to_leave=X1Item(gate_id="X1C", verdict=X1Verdict.PASS),
        x1d_answer_good=X1Item(
            gate_id="X1D",
            verdict=X1Verdict.UNKNOWN,
            decisive_reason="test",
            unknown_reason="cannot decide",
        ),
    )
    assert not checkout.is_overall_pass()


def test_deterministic_blocked_cannot_allow_finish() -> None:
    pkt = ExitReviewPacket(
        source_type=SourceType.APP_BINDING_COMPATIBILITY_PACKAGE,
        request_id="r",
        run_id="run",
        trace_root="t",
    )
    na = lambda gid: X1Item(
        gate_id=gid,
        verdict=X1Verdict.NOT_APPLICABLE,
        not_applicable_reason="na",
    )
    x1 = X1CheckoutResult(
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
    x2 = X2AggregationResult(
        disposition_candidate=X3D_ALLOW_FINISH,
        deterministic_blocked=True,
        policy_ref="test",
    )
    with pytest.raises(AG5ExitEmitError, match="deterministic_blocked"):
        emit_ag5_exit_disposition_receipt(
            packet=pkt,
            x1=x1,
            x2=x2,
            supplementary_refs={
                "user_visible_response_ref": "resp://x",
                "deterministic_digest": "digest://x",
            },
        )


def test_l6_current_run_rescue_blocked_at_emit() -> None:
    pkt = ExitReviewPacket(
        source_type=SourceType.APP_BINDING_COMPATIBILITY_PACKAGE,
        request_id="r",
        run_id="run",
        trace_root="t",
    )
    pkt.anomaly_flags.append("L6_CURRENT_RUN_RESCUE")
    na = lambda gid: X1Item(
        gate_id=gid,
        verdict=X1Verdict.NOT_APPLICABLE,
        not_applicable_reason="na",
    )
    x1 = X1CheckoutResult(
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
    x2 = X2AggregationResult(disposition_candidate=X3D_ALLOW_FINISH, policy_ref="t")
    with pytest.raises(AG5ExitEmitError, match="L6"):
        emit_ag5_exit_disposition_receipt(
            packet=pkt,
            x1=x1,
            x2=x2,
            supplementary_refs={
                "user_visible_response_ref": "resp://x",
                "deterministic_digest": "digest://x",
            },
        )
