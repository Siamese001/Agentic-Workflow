"""Regression — L6 eval-readiness honestly reflects sealed trace evidence.

Bridges the runtime-span adapter (Phase 4) to the L6 6A ingest + observer
(Phase 7) and asserts:
  * sealed trace evidence  ->  evaluable (READY_FOR_6B), normalized records built,
    no live OTEL backend touched;
  * no trace evidence      ->  honestly NON_EVALUABLE_PACKET.
"""

from __future__ import annotations

from agentic_core.L6_observability.shadow_eval.observer import (
    READINESS_NON_EVAL,
    READINESS_READY,
)
from agentic_core.L6_observability.shadow_eval.pipeline import (
    L6PipelineState,
    run_6a,
    run_observer,
)
from agentic_core.runtime.exhaust.shadow_raw_exhaust_adapter import (
    build_l6_shadow_raw_exhaust,
)


def _spans():
    return [
        {
            "name": "runtime.trace_root", "layer": "L0_routing", "kind": "trace_root",
            "trace_id": "trace-abc", "span_id": "root", "parent_span_id": "",
            "status": "ok", "duration_ms": 0.0, "attributes": {"prompt_hash": "ph-1"},
        },
        {
            "name": "L2.step.seal", "layer": "L2_execution", "kind": "seal",
            "trace_id": "trace-abc", "span_id": "l2", "parent_span_id": "root",
            "status": "ok", "duration_ms": 1.0, "attributes": {},
        },
        {
            "name": "exit.disposition", "layer": "L5_safety", "kind": "exit",
            "trace_id": "trace-abc", "span_id": "exit", "parent_span_id": "l2",
            "status": "ok", "duration_ms": 0.0, "attributes": {},
        },
    ]


def _raw_exhaust(spans):
    return build_l6_shadow_raw_exhaust(
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-abc" if spans else "",
        completed_at="2026-06-14T00:00:00Z",
        runtime_boundary_crossed=True,
        exit_disposition_ref="exit-disp-digest-1",
        spans=spans,
        policy_hash="policy-1",
        replay_key="replay-1",
        route_contract_ref="route-contract-1",
    )


def test_sealed_trace_evidence_is_evaluable():
    state = L6PipelineState()
    run_6a(state, _raw_exhaust(_spans()))
    readiness = run_observer(state)

    assert readiness.readiness_decision == READINESS_READY
    assert readiness.readiness_decision != READINESS_NON_EVAL
    assert state.ingest is not None
    assert len(state.ingest.normalized) == 3  # normalized evidence from bridged spans


def test_no_trace_evidence_is_non_evaluable():
    state = L6PipelineState()
    run_6a(state, _raw_exhaust([]))  # no spans -> no events -> no normalized records
    readiness = run_observer(state)

    assert readiness.readiness_decision == READINESS_NON_EVAL
