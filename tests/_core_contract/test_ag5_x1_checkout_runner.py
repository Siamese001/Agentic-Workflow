"""Smoke tests for ``run_ag5_x1_checkout``."""

from __future__ import annotations

from agentic_core.runtime.exit.exit_review_normalizer import normalize_ag5_terminal_input
from agentic_core.runtime.exit.x1_checkout_runner import run_ag5_x1_checkout


def _minimal_packet_dict() -> dict:
    return {
        "source_type": "APP_BINDING_COMPATIBILITY_PACKAGE",
        "route_contract_ref": "route://x1-checkout",
        "route_id": "R_TEST",
        "replay_key": "replay-x1",
        "terminal_class": "answer_only",
        "path_class": "neutral",
        "policy_hash": "aligned-ph",
        "route_contract": {"policy_hash": "aligned-ph"},
        "output": {"completion_score": 1.0},
        "otel_spans": {"spans": {k: {} for k in ("trace_root", "route_contract", "tool_invocations", "evidence_contracts", "step_outputs", "exit_disposition")}},
        "exec_trace": {"replay_receipts_present": True},
    }


def test_run_ag5_x1_checkout_overall_pass_neutral_envelope() -> None:
    pkt = normalize_ag5_terminal_input(_minimal_packet_dict())
    x1 = run_ag5_x1_checkout(pkt)
    assert x1.is_overall_pass()
