"""
tests/runtime/test_l0_route_selector_wireup.py

W11 acceptance: validates the L0 route-selector live wire-up.

Target: ``agentic_core.L0_routing.reasoning.v15_route_selector.select_route_v15``

The function is pure (no I/O) so the wire-up is purely about adding the
proof-OTEL emission while keeping the contract output byte-identical.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.reasoning import v15_route_selector as v15
from agentic_core.L0_routing.types.route_contract_v15 import (
    AuthorityScope,
    CapabilityClass,
    FreshnessClassV15,
    SandboxClass,
    SideEffectClass,
    SupportTargetV15,
)
from agentic_core.runtime.prove_requirements.otel_contract import validate_trace
from agentic_core.runtime.prove_requirements.otel_emitter import RuntimeSpanEmitter
from agentic_core.runtime.prove_requirements.replay_engine import replay_digest


@pytest.fixture(scope="module")
def authority() -> AuthorityScope:
    return AuthorityScope(
        tenant_scope="tenant-a",
        acl_scope=("read",),
        region_scope="us-east-1",
        capability_class=CapabilityClass.READ_ONLY,
        side_effect_class=SideEffectClass.PURE,
        sandbox_class=SandboxClass.NO_SANDBOX,
    )


@pytest.fixture(scope="module")
def signals(authority: AuthorityScope) -> v15.RouteSignalsV15:
    return v15.RouteSignalsV15(
        ingress_ok=True,
        authority=authority,
        policy_hash="policy-1",
        blueprint_hash="bp-1",
        snapshot_id="snap-1",
        trace_root="trace-1",
        route_span_id="span-1",
        replay_key="replay-1",
        route_telemetry_event_id="evt-1",
        classifier_confidence=0.80,
        exact_cache_hit=False,
        semantic_cache_hit=False,
        high_risk_action=False,
        low_risk_reversible_action=False,
        action_args_need_grounding=False,
        grounding_required=False,
        support_target=SupportTargetV15.NONE,
        multi_step_required=False,
        cross_step_contract_change=False,
        parallel_safe_shards=False,
        iterative_refinement_needed=False,
        needs_hitl_pause=False,
        freshness_class=FreshnessClassV15.SLOW_CHANGING,
        underspecified=False,
        unsafe=False,
        hitl_pause_points=(),
        workflow_blueprint_id=None,
        base_contract_id="contract-1",
    )


# ---------------------------------------------------------------------------
# Backward-compat
# ---------------------------------------------------------------------------

def test_legacy_select_route_returns_contract(signals: v15.RouteSignalsV15) -> None:
    contract = v15.select_route_v15(signals)
    assert contract is not None


def test_legacy_call_emits_no_proof_span(signals: v15.RouteSignalsV15) -> None:
    e = RuntimeSpanEmitter.for_request(scenario="control_no_event")
    v15.select_route_v15(signals)  # no emitter passed
    assert e.finalize().spans == []


# ---------------------------------------------------------------------------
# Wired path
# ---------------------------------------------------------------------------

def test_wired_emits_route_decision_span(signals: v15.RouteSignalsV15) -> None:
    e = RuntimeSpanEmitter.for_request(scenario="live_l0_route")
    v15.select_route_v15(signals, emitter=e)
    trace = e.finalize()
    names = {s.name for s in trace.spans}
    assert "l0.route_decision" in names


def test_wired_carries_started_reason_code(signals: v15.RouteSignalsV15) -> None:
    e = RuntimeSpanEmitter.for_request()
    v15.select_route_v15(signals, emitter=e)
    span = next(s for s in e.finalize().spans if s.name == "l0.route_decision")
    assert "route_decision_started" in span.reason_codes


def test_wired_status_ok(signals: v15.RouteSignalsV15) -> None:
    e = RuntimeSpanEmitter.for_request()
    v15.select_route_v15(signals, emitter=e)
    span = next(s for s in e.finalize().spans if s.name == "l0.route_decision")
    assert span.status == "OK"


def test_wired_returns_same_contract_as_legacy(signals: v15.RouteSignalsV15) -> None:
    """Critical: the wire-up must not alter the routing decision."""
    legacy = v15.select_route_v15(signals)
    e = RuntimeSpanEmitter.for_request()
    wired = v15.select_route_v15(signals, emitter=e)
    # Same route_id (the most important field) and same reason codes.
    assert legacy.route_id == wired.route_id
    assert legacy.reason_codes == wired.reason_codes


def test_wired_trace_passes_phase5_validator(signals: v15.RouteSignalsV15) -> None:
    e = RuntimeSpanEmitter.for_request(scenario="live_l0_phase5")
    v15.select_route_v15(signals, emitter=e)
    ok, errs = validate_trace(e.finalize().to_dict())
    assert ok, f"L0 trace failed Phase 5: {errs}"


def test_wired_replay_deterministic(signals: v15.RouteSignalsV15) -> None:
    e1 = RuntimeSpanEmitter.for_request(scenario="live_l0_replay")
    v15.select_route_v15(signals, emitter=e1)
    e2 = RuntimeSpanEmitter.for_request(scenario="live_l0_replay")
    v15.select_route_v15(signals, emitter=e2)
    d1 = replay_digest(e1.finalize().to_dict())
    d2 = replay_digest(e2.finalize().to_dict())
    assert d1 == d2
