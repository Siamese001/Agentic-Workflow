import time

import pytest

from cost_tracker import CostTracker
from optimization_hints import compute_optimization_hint
from telemetry_store import TELEMETRY_EVENTS, get_events
from l3_graph_orchestrator import GraphOrchestrator


@pytest.fixture(autouse=True)
def clear_telemetry_events():
    TELEMETRY_EVENTS.clear()
    yield
    TELEMETRY_EVENTS.clear()


def test_cost_tracker_spans():
    tracker = CostTracker()
    tracker.start_span("planning")
    time.sleep(0.001)
    tracker.end_span("planning")
    spans = tracker.snapshot()
    assert "spans" in spans
    assert spans["spans"][0]["name"] == "planning"
    assert spans["spans"][0]["duration_ms"] > 0


def test_optimization_hint_logic():
    spans = [
        {"name": "planning", "duration_ms": 20},
        {"name": "execution", "duration_ms": 10},
    ]
    assert compute_optimization_hint(spans)["suggestion"] == "reroute_fast"
    spans_reverse = [
        {"name": "planning", "duration_ms": 5},
        {"name": "execution", "duration_ms": 10},
    ]
    assert compute_optimization_hint(spans_reverse)["suggestion"] == "normal"


def test_telemetry_store_events():
    orchestrator = GraphOrchestrator()
    orchestrator.orchestrate()
    events = get_events()
    assert events, "Expected telemetry events to be recorded"
    assert events[-1]["name"] == "orchestrator_cycle"
    payload = events[-1]["payload"]
    assert "spans" in payload
    assert "optimization" in payload


def test_predictive_cache_written():
    orchestrator = GraphOrchestrator()
    result = orchestrator.orchestrate()
    predictive_cache = result.state.get("predictive_cache", {})
    assert predictive_cache.get("next_hint") is not None
