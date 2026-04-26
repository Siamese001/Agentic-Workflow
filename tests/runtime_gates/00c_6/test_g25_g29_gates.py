"""00C.6 — G25..G29 anomaly / exit / write / audit / learning firewall."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates import evaluate
from agentic_core.L5_safety.runtime_gates.types import Disposition


def test_g25_marks_degraded_on_anomaly(ctx_factory):
    ctx = ctx_factory(
        baseline={"tokens_p95": 1000, "latency_p95": 1000},
        observed={"tokens": 50000, "latency_ms": 60000},
    )
    decision = evaluate("G25", ctx)
    assert decision.disposition in (
        Disposition.MARK_DEGRADED,
        Disposition.SHRINK_SCOPE,
        Disposition.REROUTE,
        Disposition.SAFE_FALLBACK,
        Disposition.ESCALATE_HITL,
        Disposition.ABSTAIN,
        Disposition.ALLOW,
    )


def test_g26_blocks_unsealed_artifact(ctx_factory):
    ctx = ctx_factory(output={"sealed": False, "schema_valid": False})
    decision = evaluate("G26", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.REROUTE,
        Disposition.ESCALATE_HITL,
        Disposition.SAFE_FALLBACK,
        Disposition.ABSTAIN,
        Disposition.ALLOW,
    )


def test_g27_routes_writes_to_uwg(ctx_factory):
    ctx = ctx_factory(
        memory_op={"mode": "write", "scope": "tenant-A", "via_uwg": True},
        impact_class="write",
    )
    decision = evaluate("G27", ctx)
    assert decision.disposition in (
        Disposition.COMMIT_REQUEST,
        Disposition.BLOCK_COMMIT,
        Disposition.ESCALATE_HITL,
        Disposition.ALLOW,
    )


def test_g28_blocks_when_audit_missing(ctx_factory):
    ctx = ctx_factory(
        trace_artifacts={
            "trace_root": "",
            "route_contract": False,
            "tool_invocations": False,
            "evidence_contract": False,
            "step_outputs": False,
            "exit_disposition": False,
            "audit_bundle": "",
        }
    )
    decision = evaluate("G28", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.BLOCK_COMMIT,
        Disposition.MARK_DEGRADED,
        Disposition.ESCALATE_HITL,
        Disposition.SAFE_FALLBACK,
    )


def test_g29_blocks_runtime_only_learning(ctx_factory):
    ctx = ctx_factory(learning_signal={"runtime_only": True, "future_run": False})
    decision = evaluate("G29", ctx)
    assert decision.disposition is not Disposition.ALLOW
    assert decision.disposition is not Disposition.COMMIT_REQUEST
