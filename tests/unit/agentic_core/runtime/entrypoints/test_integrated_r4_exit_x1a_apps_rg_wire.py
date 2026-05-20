"""R4 receipts must carry apps_rg SSOT exit_eval_wire so X1A clears (no fake ALLOW)."""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6.preflight import normalize_to_packet
from agentic_core.L3_orchestration.exit_eval.v6.types import GateResult
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import eval_x1a
from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
    _build_l2_exit_receipts,
)


def test_integrated_r4_l2_receipts_resolve_x1a_from_pipeline_defaults() -> None:
    """Brown & Brown-style path: same app uses pipeline_defaults.exit_eval_wire (no run ids)."""
    r = _build_l2_exit_receipts(
        run_id="rid-x1a-wire",
        request_id="req-x1a-wire",
        trace_root="trace-x1a-wire",
        c0_bypass_digest="sha256:c0fixture",
        l2_result={"stage": "sealed_fixture"},
        effective_route_id="R4_SINGLE_ACTION",
        route_contract_id="contract-x1a-wire",
        replay_key="r4:replaykeyfixtureabcd",
        policy_digest="policy_v1_fixture",
        blueprint_digest="blueprint_v1_fixture",
        terminal_class="success",
        app_name="apps_rg",
    )

    gc = r.get("grader_composition") or {}
    assert isinstance(gc.get("roster"), list) and gc["roster"], "roster threaded"
    assert gc.get("threshold_profile"), "threshold_profile threaded"

    pkt = normalize_to_packet(r)
    verdict = eval_x1a(pkt)
    assert verdict.result is GateResult.PASS, verdict.reason_codes
