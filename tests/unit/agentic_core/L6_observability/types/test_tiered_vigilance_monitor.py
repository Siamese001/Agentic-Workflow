"""
§Wave4.1 — TieredVigilanceMonitor integration tests.

1. Unit: tier mapping determinism (order-independent, stable output)
2. Contract: artifact schema (semantic_clock required, sorted signals)
3. Routing: L0 path selection from tier
4. Idempotency: same inputs → byte-identical artifact JSON
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.enforcement.vigilance_routing import (
    route_vigilance_event,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L0_routing.types.routing_artifact_types import RoutePath
from agentic_core.L6_observability.engines.TieredVigilanceEmitter import (
    classify_signals,
    emit_vigilance_event,
)
from agentic_core.L6_observability.types.vigilance_event_types import (
    VigilanceEventArtifact,
    VigilanceSeverity,
    build_deterministic_trace_id,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_tiered_vigilance_monitor")
_emit_applies_guardrail("p0", "test_tiered_vigilance_monitor", "p0_governance")
_emit_reads_policy_state("p0", "test_tiered_vigilance_monitor", "policy_binding")
_emit_snapshots_state("p0", "test_tiered_vigilance_monitor", "state_snapshot")
emit_replay_key("p0", "test_tiered_vigilance_monitor")
emit_determinism_digest("p0", "test_tiered_vigilance_monitor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clock() -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=10, vector_clock=(("L0", 5), ("L6", 5)))


# ===========================================================================
# 1. Unit: tier mapping determinism
# ===========================================================================


class TestTierMappingDeterminism:
    def test_same_signals_different_order_same_tier(self):
        a = classify_signals(["budget_overflow", "guardian_fail", "info_metric"])
        b = classify_signals(["info_metric", "budget_overflow", "guardian_fail"])
        assert a == b

    def test_highest_severity_wins(self):
        assert classify_signals(["info_metric"]) == VigilanceSeverity.LOW
        assert classify_signals(["guardian_fail"]) == VigilanceSeverity.MEDIUM
        assert classify_signals(["budget_overflow"]) == VigilanceSeverity.HIGH
        assert classify_signals(["evacuation_alert"]) == VigilanceSeverity.CRITICAL

    def test_mixed_signals_highest_wins(self):
        tier = classify_signals(["info_metric", "evacuation_alert", "guardian_fail"])
        assert tier == VigilanceSeverity.CRITICAL

    def test_empty_signals_returns_low(self):
        assert classify_signals([]) == VigilanceSeverity.LOW

    def test_unknown_signal_defaults_to_low(self):
        assert classify_signals(["unknown_xyz"]) == VigilanceSeverity.LOW

    def test_signals_sorted_in_artifact(self, clock):
        event = emit_vigilance_event(
            signals=["guardian_fail", "budget_overflow", "info_metric"],
            semantic_clock=clock,
        )
        assert event.signals == ("budget_overflow", "guardian_fail", "info_metric")

    def test_duplicate_signals_deduplicated(self, clock):
        event = emit_vigilance_event(
            signals=["guardian_fail", "guardian_fail", "info_metric"],
            semantic_clock=clock,
        )
        assert event.signals == ("guardian_fail", "info_metric")


# ===========================================================================
# 2. Contract: artifact schema
# ===========================================================================


class TestArtifactSchemaContract:
    def test_semantic_clock_none_raises(self):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            VigilanceEventArtifact(
                event_type="VIGILANCE_DETECTION",
                semantic_clock=None,  # type: ignore[arg-type]
                vigilance_tier=VigilanceSeverity.LOW,
                signals=(),
                trace_id="t1",
            )

    def test_empty_event_type_raises(self):
        clock = SemanticClockSnapshot(tick=1)
        with pytest.raises(ValueError, match="event_type must be non-empty"):
            VigilanceEventArtifact(
                event_type="",
                semantic_clock=clock,
                vigilance_tier=VigilanceSeverity.LOW,
                signals=(),
                trace_id="t1",
            )

    def test_empty_trace_id_raises(self):
        clock = SemanticClockSnapshot(tick=1)
        with pytest.raises(ValueError, match="trace_id must be non-empty"):
            VigilanceEventArtifact(
                event_type="VIGILANCE_DETECTION",
                semantic_clock=clock,
                vigilance_tier=VigilanceSeverity.LOW,
                signals=(),
                trace_id="",
            )

    def test_unsorted_signals_raises(self):
        clock = SemanticClockSnapshot(tick=1)
        with pytest.raises(ValueError, match="signals must be sorted"):
            VigilanceEventArtifact(
                event_type="VIGILANCE_DETECTION",
                semantic_clock=clock,
                vigilance_tier=VigilanceSeverity.LOW,
                signals=("z_signal", "a_signal"),
                trace_id="t1",
            )

    def test_wrong_tier_type_raises(self):
        clock = SemanticClockSnapshot(tick=1)
        with pytest.raises(TypeError, match="VigilanceSeverity"):
            VigilanceEventArtifact(
                event_type="VIGILANCE_DETECTION",
                semantic_clock=clock,
                vigilance_tier="HIGH",  # type: ignore[arg-type]
                signals=(),
                trace_id="t1",
            )

    def test_frozen_immutable(self, clock):
        event = emit_vigilance_event(signals=["info_metric"], semantic_clock=clock)
        with pytest.raises(AttributeError):
            event.vigilance_tier = VigilanceSeverity.HIGH  # type: ignore[misc]

    def test_to_dict_has_all_fields(self, clock):
        event = emit_vigilance_event(
            signals=["guardian_fail"],
            semantic_clock=clock,
            policy_config_hash="abc123",
        )
        d = event.to_dict()
        assert set(d.keys()) == {
            "event_type",
            "semantic_clock",
            "vigilance_tier",
            "signals",
            "trace_id",
            "policy_config_hash",
        }
        assert d["semantic_clock"]["tick"] == 10
        assert d["vigilance_tier"] == "medium"
        assert d["signals"] == ["guardian_fail"]

    def test_semantic_clock_in_to_dict(self, clock):
        event = emit_vigilance_event(signals=["info_metric"], semantic_clock=clock)
        d = event.to_dict()
        sc = d["semantic_clock"]
        assert sc["tick"] == 10
        assert sc["vector_clock"] == {"L0": 5, "L6": 5}


# ===========================================================================
# 3. Routing: L0 path selection from tier
# ===========================================================================


class TestL0RoutingFromTier:
    def test_low_routes_to_standard_validation(self, clock):
        event = emit_vigilance_event(signals=["info_metric"], semantic_clock=clock)
        assert route_vigilance_event(event) == RoutePath.STANDARD_VALIDATION

    def test_medium_routes_to_standard_validation(self, clock):
        event = emit_vigilance_event(signals=["guardian_fail"], semantic_clock=clock)
        assert route_vigilance_event(event) == RoutePath.STANDARD_VALIDATION

    def test_high_routes_to_human_escalation(self, clock):
        event = emit_vigilance_event(signals=["budget_overflow"], semantic_clock=clock)
        assert route_vigilance_event(event) == RoutePath.HUMAN_ESCALATION

    def test_critical_routes_to_human_escalation(self, clock):
        event = emit_vigilance_event(
            signals=["evacuation_alert"],
            semantic_clock=clock,
        )
        assert route_vigilance_event(event) == RoutePath.HUMAN_ESCALATION


# ===========================================================================
# 4. Idempotency: same inputs → byte-identical JSON
# ===========================================================================


class TestIdempotency:
    def test_same_inputs_byte_identical_json(self, clock):
        def _make():
            return emit_vigilance_event(
                signals=["guardian_fail", "budget_overflow", "info_metric"],
                semantic_clock=clock,
                policy_config_hash="policy_abc",
            )

        j1 = json.dumps(_make().to_dict(), sort_keys=True, separators=(",", ":"))
        j2 = json.dumps(_make().to_dict(), sort_keys=True, separators=(",", ":"))
        assert j1 == j2

    def test_trace_id_deterministic_across_calls(self, clock):
        a = emit_vigilance_event(signals=["guardian_fail"], semantic_clock=clock)
        b = emit_vigilance_event(signals=["guardian_fail"], semantic_clock=clock)
        assert a.trace_id == b.trace_id

    def test_different_signal_order_same_json(self, clock):
        a = emit_vigilance_event(
            signals=["info_metric", "budget_overflow"],
            semantic_clock=clock,
        )
        b = emit_vigilance_event(
            signals=["budget_overflow", "info_metric"],
            semantic_clock=clock,
        )
        j1 = json.dumps(a.to_dict(), sort_keys=True, separators=(",", ":"))
        j2 = json.dumps(b.to_dict(), sort_keys=True, separators=(",", ":"))
        assert j1 == j2

    def test_deterministic_trace_id_stable(self):
        id1 = build_deterministic_trace_id(("a", "b"), 5)
        id2 = build_deterministic_trace_id(("a", "b"), 5)
        assert id1 == id2
        assert len(id1) == 16

    def test_different_tick_different_trace_id(self):
        id1 = build_deterministic_trace_id(("a",), 1)
        id2 = build_deterministic_trace_id(("a",), 2)
        assert id1 != id2
