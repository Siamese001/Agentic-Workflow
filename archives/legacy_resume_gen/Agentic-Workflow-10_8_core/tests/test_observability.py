"""Grouped observability and self-correction tests."""
import pytest

from runtime.observability.utils import CostTracker
from l3_orchestration import BulletOrchestrator
from l3_orchestration import DraftOrchestrator
from l3_orchestration import GraphOrchestrator
from l3_orchestration import QAOrchestrator
from l3_orchestration import RAGOrchestrator


def test_cost_tracker_records_spans_and_cost():
    tracker = CostTracker()

    tracker.start_span("planning")
    tracker.end_span("planning")

    assert "planning" in tracker.spans


def test_cost_tracker_snapshot_is_deterministic_copy():
    tracker = CostTracker()
    tracker.start_span("execution")

    snapshot_a = tracker.snapshot()
    snapshot_b = tracker.snapshot()

    assert snapshot_a == snapshot_b
    assert snapshot_a["spans"][0]["name"] == "execution"


@pytest.mark.parametrize(
    "orchestrator_cls,payload,state_expectation",
    [
        (
            GraphOrchestrator,
            {"messages": [{"role": "user", "content": "hi"}]},
            lambda result: result.state.get("self_correction", {}).get("surface")
            == "strategy_replan",
        ),
        (
            RAGOrchestrator,
            {"objective": "collect"},
            lambda result: result.execution_patch["last_retrieval"]["status"]
            == "completed",
        ),
        (
            DraftOrchestrator,
            {"objective": "compose", "tone": "warm"},
            lambda result: result.state.get("draft", {}).get("tone") == "warm",
        ),
        (
            BulletOrchestrator,
            {"objective": "share highlights", "deliverables": ["alpha"]},
            lambda result: bool(result.state.get("messages")),
        ),
        (
            QAOrchestrator,
            {"messages": [{"role": "assistant", "content": "draft"}]},
            lambda result: result.state.get("safety_gateway", {}).get("status")
            == "allowed",
        ),
    ],
)

def test_orchestrators_attach_telemetry_without_behavior_drift(
    orchestrator_cls, payload, state_expectation
):
    orchestrator = orchestrator_cls()
    result = orchestrator.orchestrate(payload)

    spans = result.state.get("telemetry", {}).get("spans", {})

    assert spans["planning"] == {
        "start": 0,
        "end": 1,
        "tokens": 0,
        "cost": 0.0,
    }
    assert spans["execution"] == {
        "start": 0,
        "end": 1,
        "tokens": 0,
        "cost": 0.0,
    }
    assert result.plan["routing"]["latency_target"] == 2.0
    assert state_expectation(result)
import importlib

import telemetry_schema


def test_metric_event_instantiation():
    tags = {"source": "unit-test", "env": "dev"}
    event = telemetry_schema.MetricEvent(name="requests", value=10.5, tags=tags)

    assert event.name == "requests"
    assert event.value == 10.5
    assert event.tags == tags


def test_span_event_fields():
    tags = {"operation": "fetch", "status": "ok"}
    span = telemetry_schema.SpanEvent(
        name="http_request",
        start_time_ms=1000,
        end_time_ms=1500,
        tags=tags,
    )

    assert span.name == "http_request"
    assert span.start_time_ms == 1000
    assert span.end_time_ms == 1500
    assert span.tags == tags


def test_trace_context_spans_deterministic():
    span = telemetry_schema.SpanEvent(
        name="child_span",
        start_time_ms=2000,
        end_time_ms=3000,
        tags={"detail": "child"},
    )
    spans = {"span-1": span}

    context = telemetry_schema.TraceContext(trace_id="trace-123", spans=spans)

    assert context.trace_id == "trace-123"
    assert context.spans == spans
    assert list(context.spans.keys()) == ["span-1"]


def test_module_has_no_side_effects():
    reloaded = importlib.reload(telemetry_schema)
    exported = {
        name
        for name in dir(reloaded)
        if not name.startswith("__")
    }
    expected = {"Any", "Dict", "MetricEvent", "SpanEvent", "TraceContext", "dataclass"}
    assert exported == expected
import pytest

from runtime.observability.utils import PolicyAutoTunerStub
from l3_orchestration import GraphOrchestrator
from runtime.observability.utils import PredictiveCache


def test_predictive_cache_set_get_deterministic():
    cache = PredictiveCache()
    cache.set("alpha", {"value": 1})

    assert cache.get("alpha") == {"value": 1}
    assert cache.get("missing") is None


def test_predictive_cache_snapshot_is_copy():
    cache = PredictiveCache()
    cache.set("beta", {"count": 2})

    snapshot = cache.snapshot()
    snapshot["beta"] = {"count": 3}
    snapshot["gamma"] = {"count": 4}

    assert cache.get("beta") == {"count": 2}
    assert "gamma" not in cache.cache


def test_policy_auto_tuner_stub_suggests_deterministically():
    tuner = PolicyAutoTunerStub()
    suggestion = tuner.suggest_config(state={}, metrics={})

    assert suggestion == {
        "temperature": 0.3,
        "max_tokens": 500,
        "routing_adjustment": "none",
    }


def test_graph_orchestrator_exposes_predictive_cache_and_tuning_metadata():
    orchestrator = GraphOrchestrator()
    result = orchestrator.orchestrate()
    final_state = result.state

    assert final_state.get("predictive_cache") == {"snapshot": {}}
    assert final_state.get("tuning", {}).get("suggestion") == {
        "temperature": 0.3,
        "max_tokens": 500,
    }
import time

import pytest

from runtime.observability.utils import CostTracker
from runtime.observability.utils import compute_optimization_hint
from runtime.observability.utils import TELEMETRY_EVENTS, get_events
from l3_orchestration import GraphOrchestrator


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
import pytest

from l3_orchestration import BulletOrchestrator
from l3_orchestration import DraftOrchestrator
from l3_orchestration import GraphOrchestrator
from l3_orchestration import QAOrchestrator
from l3_orchestration import RAGOrchestrator
from self_correction import SelfCorrectionSurface


def test_qa_orchestrator_sets_arbitration_metadata():
    orchestrator = QAOrchestrator()

    result = orchestrator.orchestrate()

    sc = result.state.get("self_correction", {})
    assert sc.get("surface") == SelfCorrectionSurface.QA_RECHECK.value
    assert sc.get("decision", {}).get("action") in {
        "accept",
        "retry",
        "replan",
        "escalate",
    }


@pytest.mark.parametrize(
    "orchestrator_cls, expected_surface",
    [
        (RAGOrchestrator, SelfCorrectionSurface.RAG_RETRY.value),
        (DraftOrchestrator, SelfCorrectionSurface.DRAFT_RETRY.value),
        (BulletOrchestrator, SelfCorrectionSurface.STRATEGY_REPLAN.value),
        (GraphOrchestrator, SelfCorrectionSurface.STRATEGY_REPLAN.value),
    ],
)
def test_orchestrators_expose_self_correction_surface(orchestrator_cls, expected_surface):
    orchestrator = orchestrator_cls()

    result = orchestrator.orchestrate()

    sc = result.state.get("self_correction", {})
    assert sc.get("surface") == expected_surface
    assert result.execution_patch is not None
    assert result.safety_patch is not None
import pytest

from self_correction import SelfCorrectionSurface, should_retry


def test_should_retry_qa_pending():
    state = {}
    last_result = {
        "qa_report": {
            "findings": [
                {"status": "pending", "detail": "needs review"},
                {"status": "pass", "detail": "ok"},
            ]
        }
    }

    assert should_retry(SelfCorrectionSurface.QA_RECHECK, state, last_result) is True


def test_should_retry_qa_no_pending():
    state = {}
    last_result = {
        "qa_report": {
            "findings": [
                {"status": "pass", "detail": "good"},
                {"status": "pass", "detail": "ok"},
            ]
        }
    }

    assert should_retry(SelfCorrectionSurface.QA_RECHECK, state, last_result) is False


def test_should_retry_other_surfaces_false():
    state = {}
    last_result = {}
    for surface in (
        SelfCorrectionSurface.RAG_RETRY,
        SelfCorrectionSurface.DRAFT_RETRY,
        SelfCorrectionSurface.STRATEGY_REPLAN,
    ):
        assert should_retry(surface, state, last_result) is False
import pytest

from self_correction import ArbitrationEngine
from self_correction import CORRECTION_JOURNAL
from self_correction import evaluate_correction
from l3_orchestration import BulletOrchestrator
from l3_orchestration import DraftOrchestrator
from l3_orchestration import GraphOrchestrator
from l3_orchestration import QAOrchestrator
from l3_orchestration import RAGOrchestrator
from self_correction import SelfCorrectionSurface, all_surfaces


def test_all_surfaces_export():
    surfaces = all_surfaces()
    expected = ["RAG_RETRY", "DRAFT_RETRY", "QA_RECHECK", "STRATEGY_REPLAN"]
    for key in expected:
        assert key in sorted(surfaces.keys())


def test_supervisor_qa_pending():
    surface = SelfCorrectionSurface.QA_RECHECK
    state = {"qa_report": {"findings": [{"status": "pending"}]}}
    recommendation = evaluate_correction(surface, state, state)
    assert recommendation["needs_retry"] is True


def test_supervisor_no_messages_replan():
    surface = SelfCorrectionSurface.STRATEGY_REPLAN
    recommendation = evaluate_correction(surface, {}, {})
    assert recommendation["needs_replan"] is True


def test_arbitration_surface_hints():
    engine = ArbitrationEngine()

    blocked = engine.evaluate({}, {}, {"safety_gateway": {"status": "blocked"}})
    assert blocked["surface_hint"] == "strategy_replan"

    pending = engine.evaluate({}, {"findings": [{"status": "pending"}]}, {})
    assert pending["surface_hint"] == "qa_recheck"

    replan = engine.evaluate({}, {}, {})
    assert replan["surface_hint"] == "strategy_replan"

    accept = engine.evaluate({"messages": [{}]}, {}, {})
    assert accept["surface_hint"] == "qa_recheck"


@pytest.mark.parametrize(
    "orchestrator_cls, expected_surface",
    [
        (QAOrchestrator, SelfCorrectionSurface.QA_RECHECK.value),
        (RAGOrchestrator, SelfCorrectionSurface.RAG_RETRY.value),
        (DraftOrchestrator, SelfCorrectionSurface.DRAFT_RETRY.value),
        (BulletOrchestrator, SelfCorrectionSurface.STRATEGY_REPLAN.value),
        (GraphOrchestrator, SelfCorrectionSurface.STRATEGY_REPLAN.value),
    ],
)
def test_orchestrators_emit_self_correction(orchestrator_cls, expected_surface):
    orchestrator = orchestrator_cls()
    result = orchestrator.orchestrate()

    sc = result.state.get("self_correction", {})
    assert sc.get("surface") == expected_surface
    assert isinstance(sc.get("recommendation"), dict)


@pytest.mark.parametrize(
    "orchestrator_cls",
    [QAOrchestrator, RAGOrchestrator, DraftOrchestrator, BulletOrchestrator, GraphOrchestrator],
)
def test_correction_journal_records_events(orchestrator_cls):
    CORRECTION_JOURNAL.clear()
    orchestrator = orchestrator_cls()

    initial_len = len(CORRECTION_JOURNAL)
    orchestrator.orchestrate()
    assert len(CORRECTION_JOURNAL) == initial_len + 1
