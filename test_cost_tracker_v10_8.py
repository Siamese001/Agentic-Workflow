import pytest

from cost_tracker import CostTracker
from l3_bullet_orchestrator import BulletOrchestrator
from l3_draft_orchestrator import DraftOrchestrator
from l3_graph_orchestrator import GraphOrchestrator
from l3_qa_orchestrator import QAOrchestrator
from l3_rag_orchestrator import RAGOrchestrator


def test_cost_tracker_records_spans_and_cost():
    tracker = CostTracker()

    tracker.start_span("planning")
    tracker.end_span("planning", tokens=15, cost=0.25)

    assert tracker.spans["planning"] == {
        "start": 0,
        "end": 1,
        "tokens": 15,
        "cost": 0.25,
    }


def test_cost_tracker_snapshot_is_deterministic_copy():
    tracker = CostTracker()
    tracker.start_span("execution")

    snapshot_a = tracker.snapshot()
    snapshot_b = tracker.snapshot()

    assert snapshot_a == {
        "execution": {"start": 0, "end": None, "tokens": 0, "cost": 0.0}
    }
    assert snapshot_b == snapshot_a


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
