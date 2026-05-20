"""R4 SINGLE_ACTION Exit §5.0 receipt wiring vs validate_required_receipts."""
from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6.preflight import (
    bind_run_identity,
    normalize_to_packet,
    validate_required_receipts,
)
from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
    _build_l2_exit_receipts,
)


def _sample_receipts(*, terminal_class: str = "success") -> dict:
    """Shape aligned with integrated_r4 L2-complete handoff (no live run ids)."""
    return _build_l2_exit_receipts(
        run_id="rid-test",
        request_id="req-test",
        trace_root="trace-test",
        c0_bypass_digest="sha256:c0fixture",
        l2_result={"stage": "sealed_fixture"},
        effective_route_id="R4_SINGLE_ACTION",
        route_contract_id="contract-test",
        replay_key="r4:replaykeyfixture0123",
        policy_digest="policy_v1_fixture",
        blueprint_digest="blueprint_v1_fixture",
        terminal_class=terminal_class,
        app_name="apps_rg",
    )


def test_build_l2_exit_receipts_satisfies_exit_v6_preflight() -> None:
    r = _sample_receipts()
    vf = validate_required_receipts(r)
    bi = bind_run_identity(r)
    missing = {(f.field, f.reason_code) for f in (*vf, *bi)}
    assert vf == [], f"unexpected preflight misses: {vf}"
    assert bi == [], f"unexpected identity misses: {bi}"
    rc = r.get("route_contract", {})
    assert rc.get("route_id") == r["route_id"]
    assert r["terminal_class"] == "success"
    pkt = normalize_to_packet(r)
    assert pkt.l5_certification_refs, "profile must define spine_exit_packet_carrier_refs"
    assert "test:valid:w6" not in pkt.l5_certification_refs, (
        "integrated R4 must not use harness test tokens as runtime L5 carriers"
    )
    assert pkt.l5_certification_refs[0].startswith("apps_rg::spine:r4:l5_packet_carrier")


def test_build_l2_exit_receipts_failure_terminal_class_still_preflight_clean() -> None:
    """L2 fault receipts use terminal_class=failure — still non-action; §5.0 holds."""
    r = _sample_receipts(terminal_class="failure")
    r["l2_fault"] = "L2_EXECUTION_ERROR:RuntimeError:test"
    assert validate_required_receipts(r) == []
