"""Shared fixtures for runtime-gate proof tests (00C doctrine).

Each fixture below produces a fully-populated ``GateContext`` for one of the
spec layers so individual tests can mutate just the slice they care about
without re-deriving every envelope field.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates.otel_spans import get_recorder
from agentic_core.L5_safety.runtime_gates.types import GateContext


def _base_ctx(**overrides) -> GateContext:
    """Fully-populated baseline context — every doctrine envelope field set."""
    base: dict[str, object] = {
        "request_id": "req-doctrine-001",
        "session_id": "sess-doctrine-001",
        "run_id": "run-doctrine-001",
        "trace_root": "trace-doctrine-001",
        "trace_id": "trace-id-001",
        "tenant_id": "tenant-A",
        "policy_hash": "pol-deadbeef",
        "compliance_hash": "comp-deadbeef",
        "blueprint_hash": "blue-deadbeef",
        "replay_key": "rk-deadbeef",
        "evaluated_packet_ref": "packet:doctrine:001",
        "intent": {"objective": "answer", "raw_text": "what is x?", "payload_bytes": 100},
        "caller_scope_baseline": {"region": "us-east-1"},
        "risk_tier": "low",
        "reversible": True,
        "impact_class": "read",
        "route_contract": {
            "route_id": "R3_GROUNDED_READ",
            "confidence": 0.92,
            "freshness_class": "live",
            "cache_policy": "no_cache",
            "execution_form": "single_step",
            "cost_tier": "standard",
            "fallback_chain": ["R5_FALLBACK"],
            "slo": {"p95_ms": 2000},
            "tenant_scope": "tenant-A",
            "hmac_sig": "sig-x",
            "reason_codes": ["evidence_required"],
        },
        "retrieval_plan": {"sources": ["docs"], "k": 5, "max_graph_hops": 1},
        "evidence": {
            "support_score": 0.85,
            "cited_spans": ["doc1:1-3"],
            "source_ids": ["doc1"],
            "contradiction_flags": [],
            "freshness": "fresh",
        },
        "prompt_packet": {
            "slot_order": ["S0", "D0", "I0", "E0", "C0", "M0", "U0", "H0"],
            "manifest_hash": "ph-1",
            "hmac": "ph-sig",
            "budget_report": {"tokens": 1500},
            "schema_bound": True,
        },
        "tool_call": {
            "tool_id": "approved_search",
            "args": {"q": "x"},
            "approved_models": ["approved_search"],
        },
        "memory_op": {"mode": "read", "scope": "tenant-A"},
        "workflow_state": {
            "step": 1,
            "max_iterations": 5,
            "retry_count": 0,
            "branches": [],
            "dependencies_satisfied": True,
        },
        "budget": {
            "tokens_used": 100,
            "tokens_max": 5000,
            "latency_ms": 100,
            "slo_ms": 2000,
        },
        "output": {
            "schema_valid": True,
            "groundedness": 0.9,
            "citations_ok": True,
            "leakage_flags": [],
        },
        "baseline": {"tokens_p95": 2000, "latency_p95": 1500},
        "observed": {"tokens": 1500, "latency_ms": 1100},
        "hitl": {"required": False},
        "trace_artifacts": {
            "trace_root": "trace-doctrine-001",
            "route_contract": True,
            "tool_invocations": True,
            "evidence_contract": True,
            "step_outputs": True,
            "exit_disposition": True,
            "audit_bundle": "ok",
        },
        "learning_signal": {"runtime_only": False, "future_run": True},
    }
    base.update(overrides)
    return GateContext(**base)


@pytest.fixture
def base_ctx() -> GateContext:
    """Doctrine-compliant fully-populated baseline context."""
    return _base_ctx()


@pytest.fixture
def ctx_factory():
    """Factory for ad-hoc context overrides."""
    return _base_ctx


@pytest.fixture(autouse=True)
def _reset_recorder():
    """Ensure each test starts with a clean OTEL span recorder."""
    rec = get_recorder()
    rec.reset()
    yield
    rec.reset()
