"""Behavioral tests for RoutingOutcomeAdapter and build_routing_outcome_package.

Covers:
- Package kind is always 'routing_outcome'
- SUCCESS / SAFE_FAILURE / UNKNOWN outcome derivation
- Payload fields: intent, target_name, confidence, outcome, has_error, timestamp_utc
- influence_class is always C0_INFORMATIONAL
- Adapter.emit() returns True on success
- Adapter.emit() returns False and never raises on MetaLearningBus failure
- Confidence value is rounded to 6 decimal places
- Determinism: same decision → identical package payload
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.engines.agentic_router import RoutingDecision
from agentic_core.L0_routing.engines.routing_outcome_adapter import (
    RoutingOutcomeAdapter,
    build_routing_outcome_package,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _decision(
    *,
    intent: str = "code",
    target_name: str = "code_reviewer",
    confidence: float = 0.85,
    result: object = "ok",
    error: str | None = None,
    trace_id: str = "trace-001",
) -> RoutingDecision:
    return RoutingDecision(
        intent=intent,
        target_name=target_name,
        confidence=confidence,
        result=result,
        error=error,
        metadata={"trace_id": trace_id},
    )


def _mock_bus() -> MagicMock:
    bus = MagicMock()
    bus.enqueue = MagicMock()
    return bus


# ---------------------------------------------------------------------------
# build_routing_outcome_package
# ---------------------------------------------------------------------------


class TestBuildRoutingOutcomePackage:
    def test_kind_is_routing_outcome(self):
        pkg = build_routing_outcome_package(_decision(), timestamp_utc=1000)
        assert pkg.kind == "routing_outcome"

    def test_payload_has_all_required_keys(self):
        pkg = build_routing_outcome_package(_decision(), timestamp_utc=1000)
        required = {
            "intent",
            "target_name",
            "confidence",
            "outcome",
            "has_error",
            "timestamp_utc",
            "influence_class",
        }
        assert required.issubset(set(pkg.payload.keys()))

    def test_outcome_success_when_result_present(self):
        pkg = build_routing_outcome_package(_decision(result="ok", error=None), timestamp_utc=1)
        assert pkg.payload["outcome"] == "SUCCESS"

    def test_outcome_safe_failure_when_error_set(self):
        pkg = build_routing_outcome_package(_decision(result=None, error="boom"), timestamp_utc=1)
        assert pkg.payload["outcome"] == "SAFE_FAILURE"

    def test_outcome_unknown_when_result_none_no_error(self):
        pkg = build_routing_outcome_package(_decision(result=None, error=None), timestamp_utc=1)
        assert pkg.payload["outcome"] == "UNKNOWN"

    def test_has_error_true_when_error_set(self):
        pkg = build_routing_outcome_package(_decision(error="oops"), timestamp_utc=1)
        assert pkg.payload["has_error"] is True

    def test_has_error_false_when_no_error(self):
        pkg = build_routing_outcome_package(_decision(error=None), timestamp_utc=1)
        assert pkg.payload["has_error"] is False

    def test_confidence_in_payload(self):
        pkg = build_routing_outcome_package(_decision(confidence=0.72345678), timestamp_utc=1)
        assert abs(pkg.payload["confidence"] - 0.723457) < 1e-5

    def test_influence_class_is_c0_informational(self):
        pkg = build_routing_outcome_package(_decision(), timestamp_utc=1)
        assert pkg.payload["influence_class"] == "C0_INFORMATIONAL"

    def test_intent_and_target_name_in_payload(self):
        pkg = build_routing_outcome_package(
            _decision(intent="resume", target_name="resume_writer"), timestamp_utc=1
        )
        assert pkg.payload["intent"] == "resume"
        assert pkg.payload["target_name"] == "resume_writer"

    def test_timestamp_utc_in_payload(self):
        pkg = build_routing_outcome_package(_decision(), timestamp_utc=99999)
        assert pkg.payload["timestamp_utc"] == 99999

    def test_deterministic_same_decision_same_payload(self):
        d = _decision(confidence=0.5, trace_id="t42")
        p1 = build_routing_outcome_package(d, timestamp_utc=5)
        p2 = build_routing_outcome_package(d, timestamp_utc=5)
        assert p1.payload == p2.payload

    def test_different_timestamps_produce_different_packages(self):
        d = _decision()
        p1 = build_routing_outcome_package(d, timestamp_utc=1)
        p2 = build_routing_outcome_package(d, timestamp_utc=2)
        assert p1.payload["timestamp_utc"] != p2.payload["timestamp_utc"]


# ---------------------------------------------------------------------------
# RoutingOutcomeAdapter.emit()
# ---------------------------------------------------------------------------


class TestRoutingOutcomeAdapterEmit:
    def test_emit_returns_true_on_success(self):
        bus = _mock_bus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        result = adapter.emit(_decision(), timestamp_utc=1)
        assert result is True

    def test_emit_calls_bus_enqueue_once(self):
        bus = _mock_bus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        adapter.emit(_decision(), timestamp_utc=1)
        bus.enqueue.assert_called_once()

    def test_emit_returns_false_when_bus_raises(self):
        bus = _mock_bus()
        bus.enqueue.side_effect = RuntimeError("bus dead")
        adapter = RoutingOutcomeAdapter(bus=bus)
        result = adapter.emit(_decision(), timestamp_utc=1)
        assert result is False

    def test_emit_does_not_raise_when_bus_raises(self):
        bus = _mock_bus()
        bus.enqueue.side_effect = Exception("unexpected")
        adapter = RoutingOutcomeAdapter(bus=bus)
        try:
            adapter.emit(_decision(), timestamp_utc=1)
        except Exception as exc:
            pytest.fail(f"emit() raised unexpectedly: {exc}")

    def test_emit_passes_correct_package_kind(self):
        captured = []
        bus = _mock_bus()
        bus.enqueue.side_effect = lambda pkg: captured.append(pkg)
        adapter = RoutingOutcomeAdapter(bus=bus)
        adapter.emit(_decision(), timestamp_utc=1)
        assert len(captured) == 1
        assert captured[0].kind == "routing_outcome"

    def test_emit_multiple_decisions_enqueues_each(self):
        bus = _mock_bus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        for i in range(5):
            adapter.emit(_decision(confidence=float(i) / 10), timestamp_utc=i)
        assert bus.enqueue.call_count == 5
