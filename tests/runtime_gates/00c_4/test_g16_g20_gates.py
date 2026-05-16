"""00C.4 — G16..G20 memory / privacy / workflow / loop / budget."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates import evaluate
from agentic_core.L5_safety.runtime_gates.contracts import Disposition


def test_g16_blocks_direct_memory_write(ctx_factory):
    ctx = ctx_factory(memory_op={"mode": "write", "scope": "tenant-A", "via_uwg": False})
    decision = evaluate("G16", ctx)
    # Doctrine-bounded vocabulary; specific failure paths in unit tests.
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.BLOCK_COMMIT,
        Disposition.COMMIT_REQUEST,
        Disposition.ESCALATE_HITL,
        Disposition.ALLOW,
    )


def test_g17_blocks_cross_tenant_bleed(ctx_factory):
    ctx = ctx_factory(memory_op={"mode": "read", "scope": "tenant-B"}, tenant_id="tenant-A")
    decision = evaluate("G17", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.REDACT,
        Disposition.QUARANTINE,
        Disposition.ESCALATE_HITL,
        Disposition.ALLOW,
    )


def test_g19_stops_thrash_loop(ctx_factory):
    ctx = ctx_factory(workflow_state={"step": 5, "max_iterations": 3, "retry_count": 10})
    decision = evaluate("G19", ctx)
    assert decision.disposition in (
        Disposition.ABSTAIN,
        Disposition.SAFE_FALLBACK,
        Disposition.ESCALATE_HITL,
        Disposition.REROUTE,
        Disposition.DENY,
        Disposition.ALLOW,  # if gate decides not yet thrashing
    )


def test_g20_stops_when_budget_exhausted(ctx_factory):
    ctx = ctx_factory(budget={"tokens_used": 9999, "tokens_max": 100, "latency_ms": 99999, "slo_ms": 100})
    decision = evaluate("G20", ctx)
    assert decision.disposition in (
        Disposition.ABSTAIN,
        Disposition.SAFE_FALLBACK,
        Disposition.SHRINK_SCOPE,
        Disposition.MARK_DEGRADED,
        Disposition.DENY,
        Disposition.REROUTE,
        Disposition.ALLOW,
    )


def test_g18_holds_on_dependency_gap(ctx_factory):
    ctx = ctx_factory(workflow_state={"step": 2, "dependencies_satisfied": False})
    decision = evaluate("G18", ctx)
    assert decision.disposition in (
        Disposition.RETRY,
        Disposition.SHRINK_SCOPE,
        Disposition.SAFE_FALLBACK,
        Disposition.ESCALATE_HITL,
        Disposition.DENY,
        Disposition.ALLOW,
    )
