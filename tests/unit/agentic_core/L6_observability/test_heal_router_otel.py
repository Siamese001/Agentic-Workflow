"""Wave F2.3 tests: `heal_router.v1` unified OTEL emitter (Phase M1)."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.healers.confidence_scorer import HealTier
from agentic_core.L2_execution.healers.healing_router import RoutingDecision
from agentic_core.L6_observability.heal_router_otel import (
    DISPATCH_ATTRIBUTES,
    REQUIRED_ATTRIBUTES,
    SPAN_NAME_ROUTE,
    HealRouterTelemetryEmitter,
    RoutingSpanRecord,
    get_default_emitter,
)

pytestmark = pytest.mark.unit


def _decision(
    tier: HealTier = HealTier.LOW,
    gate_applied: str = "NO_OVERRIDE",
    gemini_subtier: str = "FLASH",
    cost_demoted: bool = False,
    target_model: str = "gemini-2.0-flash-001",
) -> RoutingDecision:
    return RoutingDecision(
        tier=tier,
        target_model=target_model,
        timeout_seconds=30,
        max_tokens=1024,
        requires_sandbox=False,
        reasoning="test",
        gate_applied=gate_applied,
        gemini_subtier=gemini_subtier,
        cost_demoted=cost_demoted,
    )


# ==========================================================================
# Span attribute schema contracts
# ==========================================================================


def test_span_name_is_stable_wire_format():
    assert SPAN_NAME_ROUTE == "heal_router.v1.route"


def test_required_attributes_match_adr_025():
    # ADR-025 §2 — contract for every span in heal_router.v1 family
    expected = {
        "routing.trace_id",
        "routing.tier",
        "routing.gate_applied",
        "routing.gemini_subtier",
        "routing.cost_demoted",
        "routing.target_model",
        "routing.app_name",
        "routing.confidence_score",
    }
    assert REQUIRED_ATTRIBUTES == frozenset(expected)


def test_dispatch_attributes_match_adr_025():
    expected = {
        "routing.cost_usd",
        "routing.tokens_in",
        "routing.tokens_out",
        "routing.latency_ms",
        "routing.error_code",
        "routing.dry_plan",
    }
    assert DISPATCH_ATTRIBUTES == frozenset(expected)


# ==========================================================================
# emit_route_span — core behavior
# ==========================================================================


def test_emit_route_span_generates_trace_id_when_not_provided():
    emitter = HealRouterTelemetryEmitter()
    record = emitter.emit_route_span(decision=_decision())
    assert record.routing_trace_id
    assert len(record.routing_trace_id) == 36  # uuid4 canonical length


def test_emit_route_span_accepts_caller_supplied_trace_id():
    emitter = HealRouterTelemetryEmitter()
    supplied = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    record = emitter.emit_route_span(routing_trace_id=supplied, decision=_decision())
    assert record.routing_trace_id == supplied


def test_emit_route_span_captures_decision_fields():
    emitter = HealRouterTelemetryEmitter()
    decision = _decision(
        tier=HealTier.LOW,
        gate_applied="GATE_1_RETRY_OVERRIDE",
        gemini_subtier="PRO",
        cost_demoted=True,
        target_model="gemini-2.5-pro-preview-06-05",
    )
    record = emitter.emit_route_span(
        decision=decision,
        confidence_score=0.42,
        app_name="apps_lic",
        cost_budget_remaining_usd=15.50,
    )
    assert record.tier == "LOW"
    assert record.gate_applied == "GATE_1_RETRY_OVERRIDE"
    assert record.gemini_subtier == "PRO"
    assert record.cost_demoted is True
    assert record.target_model == "gemini-2.5-pro-preview-06-05"
    assert record.app_name == "apps_lic"
    assert record.confidence_score == 0.42
    assert record.cost_budget_remaining_usd == 15.50


def test_emit_route_span_default_app_name():
    emitter = HealRouterTelemetryEmitter()
    record = emitter.emit_route_span(decision=_decision())
    assert record.app_name == "healing_router"


def test_emit_route_span_dry_plan_flag():
    emitter = HealRouterTelemetryEmitter()
    record = emitter.emit_route_span(
        decision=_decision(),
        dry_plan=True,
        error_code="gemini_gateway_not_provisioned",
    )
    assert record.dry_plan is True
    assert record.error_code == "gemini_gateway_not_provisioned"


# ==========================================================================
# to_span_attributes — OTEL attribute projection
# ==========================================================================


def test_to_span_attributes_contains_required_keys():
    emitter = HealRouterTelemetryEmitter()
    record = emitter.emit_route_span(decision=_decision(), confidence_score=0.5)
    attrs = record.to_span_attributes()
    # All required attributes present
    for key in REQUIRED_ATTRIBUTES:
        assert key in attrs, f"missing required attribute {key}"


def test_to_span_attributes_omits_optional_when_none():
    emitter = HealRouterTelemetryEmitter()
    record = emitter.emit_route_span(decision=_decision())
    attrs = record.to_span_attributes()
    # cost_usd was not provided → must not appear
    assert "routing.cost_usd" not in attrs
    assert "routing.latency_ms" not in attrs
    assert "routing.error_code" not in attrs
    assert "routing.dry_plan" not in attrs  # False is omitted by contract


def test_to_span_attributes_includes_dispatch_fields_when_set():
    emitter = HealRouterTelemetryEmitter()
    record = emitter.emit_route_span(
        decision=_decision(),
        latency_ms=42,
        outcome_success=True,
    )
    attrs = record.to_span_attributes()
    assert attrs["routing.latency_ms"] == 42
    assert attrs["routing.outcome_success"] is True


def test_to_span_attributes_propagates_extra_attributes():
    emitter = HealRouterTelemetryEmitter()
    record = emitter.emit_route_span(
        decision=_decision(),
        extra_attributes={"custom.app_version": "1.2.3"},
    )
    attrs = record.to_span_attributes()
    assert attrs["custom.app_version"] == "1.2.3"


# ==========================================================================
# Ring buffer + recent() + clear()
# ==========================================================================


def test_ring_captures_emitted_records():
    emitter = HealRouterTelemetryEmitter()
    assert len(emitter) == 0
    emitter.emit_route_span(decision=_decision())
    emitter.emit_route_span(decision=_decision())
    assert len(emitter) == 2


def test_recent_returns_copy_of_ring():
    emitter = HealRouterTelemetryEmitter()
    emitter.emit_route_span(decision=_decision(target_model="m1"))
    emitter.emit_route_span(decision=_decision(target_model="m2"))
    recent = emitter.recent(limit=10)
    assert len(recent) == 2
    assert recent[-1].target_model == "m2"
    # Mutating the copy does not affect the ring
    recent.clear()
    assert len(emitter) == 2


def test_recent_respects_limit():
    emitter = HealRouterTelemetryEmitter()
    for _ in range(5):
        emitter.emit_route_span(decision=_decision())
    assert len(emitter.recent(limit=3)) == 3


def test_clear_empties_ring():
    emitter = HealRouterTelemetryEmitter()
    emitter.emit_route_span(decision=_decision())
    emitter.emit_route_span(decision=_decision())
    emitter.clear()
    assert len(emitter) == 0


def test_ring_eviction_at_max_size():
    emitter = HealRouterTelemetryEmitter()
    # Override for test speed
    emitter._MAX_RING_SIZE = 3
    for _ in range(5):
        emitter.emit_route_span(decision=_decision())
    assert len(emitter) == 3  # oldest 2 evicted


# ==========================================================================
# Default emitter singleton
# ==========================================================================


def test_default_emitter_is_singleton():
    a = get_default_emitter()
    b = get_default_emitter()
    assert a is b


def test_default_emitter_is_usable():
    emitter = get_default_emitter()
    emitter.clear()
    record = emitter.emit_route_span(decision=_decision())
    assert isinstance(record, RoutingSpanRecord)
    assert len(emitter) >= 1
    emitter.clear()
