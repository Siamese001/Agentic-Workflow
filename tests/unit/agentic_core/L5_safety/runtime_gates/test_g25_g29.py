"""Tests for runtime gates G25-G29 (W5)."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates import (
    DecisionAlias,
    Disposition,
    GateContext,
    all_gates,
    evaluate,
)


# ---- G25 Runtime Anomaly ----


def test_g25_allow_no_baseline() -> None:
    ctx = GateContext()
    d = evaluate("G25", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g25_allow_within_baseline() -> None:
    ctx = GateContext(
        baseline={"tokens": 1000, "cost_usd": 0.10, "tool_count": 5},
        observed={"tokens": 1100, "cost_usd": 0.11, "tool_count": 5},
    )
    d = evaluate("G25", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g25_mark_degraded_severe_anomaly() -> None:
    ctx = GateContext(
        baseline={"tokens": 1000},
        observed={"tokens": 5000},  # 5x = severe
    )
    d = evaluate("G25", ctx)
    assert d.disposition is Disposition.MARK_DEGRADED


def test_g25_escalate_severe_high_risk() -> None:
    ctx = GateContext(
        baseline={"tokens": 1000},
        observed={"tokens": 5000},
        impact_class="write",
    )
    d = evaluate("G25", ctx)
    assert d.disposition is Disposition.ESCALATE_HITL
    assert d.stop_condition_violated


def test_g25_mark_degraded_safety_low_confidence() -> None:
    ctx = GateContext(
        baseline={"tokens": 1000},
        observed={"tokens": 1000, "safety_low_confidence": True},
    )
    d = evaluate("G25", ctx)
    assert d.disposition is Disposition.MARK_DEGRADED


# ---- G26 Exit Disposition ----


def _sealed(**overrides) -> dict:
    base = {
        "sealed": True,
        "sub_results": {
            "policy": "pass",
            "schema": "pass",
            "support": "pass",
            "safety": "pass",
            "sandbox": "pass",
            "mutation_authorization": "pass",
        },
    }
    base.update(overrides)
    return base


def test_g26_allow_clean_exit() -> None:
    ctx = GateContext(output=_sealed())
    d = evaluate("G26", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g26_deny_unsealed() -> None:
    ctx = GateContext(output={"sealed": False})
    d = evaluate("G26", ctx)
    assert d.disposition is Disposition.DENY
    assert d.stop_condition_violated


def test_g26_deny_policy_fail() -> None:
    out = _sealed()
    out["sub_results"]["policy"] = "fail"
    ctx = GateContext(output=out)
    d = evaluate("G26", ctx)
    assert d.disposition is Disposition.DENY


def test_g26_reroute_schema_fail() -> None:
    out = _sealed()
    out["sub_results"]["schema"] = "fail"
    ctx = GateContext(output=out)
    d = evaluate("G26", ctx)
    assert d.disposition is Disposition.REROUTE


def test_g26_commit_request() -> None:
    ctx = GateContext(output=_sealed(requires_commit=True))
    d = evaluate("G26", ctx)
    assert d.disposition is Disposition.COMMIT_REQUEST


def test_g26_escalate_hitl() -> None:
    ctx = GateContext(output=_sealed(requires_hitl=True))
    d = evaluate("G26", ctx)
    assert d.disposition is Disposition.ESCALATE_HITL


# ---- G27 Durable Write Sovereignty ----


def test_g27_allow_no_mutation() -> None:
    ctx = GateContext(memory_op={"is_proposed_mutation": False})
    d = evaluate("G27", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g27_block_l2_direct_write() -> None:
    ctx = GateContext(memory_op={"is_proposed_mutation": True, "caller_layer": "L2"})
    d = evaluate("G27", ctx)
    assert d.disposition is Disposition.BLOCK_COMMIT
    assert d.stop_condition_violated


def test_g27_block_l3_direct_write() -> None:
    ctx = GateContext(memory_op={"is_proposed_mutation": True, "caller_layer": "L3"})
    d = evaluate("G27", ctx)
    assert d.disposition is Disposition.BLOCK_COMMIT


def test_g27_block_invalid_signature() -> None:
    ctx = GateContext(
        memory_op={"is_proposed_mutation": True, "caller_layer": "Exit", "signature_valid": False},
        compliance_hash="c1",
        policy_hash="p1",
    )
    d = evaluate("G27", ctx)
    assert d.disposition is Disposition.BLOCK_COMMIT


def test_g27_commit_request_authorized() -> None:
    ctx = GateContext(
        memory_op={"is_proposed_mutation": True, "caller_layer": "Exit"},
        compliance_hash="c1",
        policy_hash="p1",
    )
    d = evaluate("G27", ctx)
    assert d.disposition is Disposition.COMMIT_REQUEST


def test_g27_escalate_wide_blast() -> None:
    ctx = GateContext(
        memory_op={"is_proposed_mutation": True, "caller_layer": "Exit", "blast_radius_too_wide": True},
        compliance_hash="c1",
        policy_hash="p1",
    )
    d = evaluate("G27", ctx)
    assert d.disposition is Disposition.ESCALATE_HITL


# ---- G28 Audit Trace Completeness ----


def _spans_full() -> dict:
    return {
        "trace_root": "t1",
        "route_contract": "rc1",
        "tool_invocations": ["i1"],
        "evidence_contracts": ["e1"],
        "step_outputs": ["s1"],
        "exit_disposition": "ALLOW",
    }


def test_g28_allow_complete_audit() -> None:
    ctx = GateContext(trace_artifacts={"spans": _spans_full()})
    d = evaluate("G28", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g28_block_audit_required_missing_spans() -> None:
    spans = _spans_full()
    spans.pop("evidence_contracts")
    ctx = GateContext(trace_artifacts={"audit_required": True, "spans": spans})
    d = evaluate("G28", ctx)
    assert d.disposition is Disposition.DENY
    assert d.stop_condition_violated


def test_g28_mark_degraded_partial_no_audit_required() -> None:
    spans = _spans_full()
    spans.pop("evidence_contracts")
    ctx = GateContext(trace_artifacts={"spans": spans})
    d = evaluate("G28", ctx)
    assert d.disposition is Disposition.MARK_DEGRADED


def test_g28_block_commit_missing_receipt() -> None:
    ctx = GateContext(trace_artifacts={"commit_in_run": True, "spans": _spans_full()})
    d = evaluate("G28", ctx)
    assert d.disposition is Disposition.BLOCK_COMMIT


def test_g28_block_commit_hash_mismatch() -> None:
    spans = _spans_full()
    spans["commit_receipts"] = ["r1"]
    ctx = GateContext(
        trace_artifacts={
            "commit_in_run": True,
            "audit_hash_chain_ok": False,
            "spans": spans,
        }
    )
    d = evaluate("G28", ctx)
    assert d.disposition is Disposition.BLOCK_COMMIT


# ---- G29 Learning Firewall ----


def test_g29_archive_sealed_run() -> None:
    ctx = GateContext(learning_signal={"run_status": "sealed"})
    d = evaluate("G29", ctx)
    assert d.disposition is Disposition.ALLOW
    assert d.alias == DecisionAlias.ARCHIVE.value


def test_g29_block_current_run_mutation() -> None:
    ctx = GateContext(learning_signal={"attempts_current_run_mutation": True})
    d = evaluate("G29", ctx)
    assert d.disposition is Disposition.DENY
    assert d.stop_condition_violated


def test_g29_block_l4_direct_write() -> None:
    ctx = GateContext(learning_signal={"attempts_l4_direct_write": True})
    d = evaluate("G29", ctx)
    assert d.disposition is Disposition.BLOCK_COMMIT


def test_g29_deny_unapproved_promotion() -> None:
    ctx = GateContext(learning_signal={"attempts_promotion_without_approval": True})
    d = evaluate("G29", ctx)
    assert d.disposition is Disposition.DENY


def test_g29_block_shadow_eval_bleed() -> None:
    ctx = GateContext(learning_signal={"shadow_eval_bleed": True})
    d = evaluate("G29", ctx)
    assert d.disposition is Disposition.DENY


def test_g29_commit_request_proposed_update() -> None:
    ctx = GateContext(learning_signal={"proposes_update": True})
    d = evaluate("G29", ctx)
    assert d.disposition is Disposition.COMMIT_REQUEST


# ---- Final registry check ----


def test_all_29_gates_registered() -> None:
    gates = all_gates()
    assert len(gates) == 29, f"expected 29 gates, got {len(gates)}: {gates}"
    expected = [f"G{i:02d}" for i in range(1, 30)]
    assert gates == expected
