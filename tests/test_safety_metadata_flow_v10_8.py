import pytest

from l1_drafting_reasoner import DraftingReasoner
from l1_rag_reasoner import RAGReasoner
from l1_strategy_reasoner import StrategyReasoner
from l3_bullet_orchestrator import BulletOrchestrator
from l3_draft_orchestrator import DraftOrchestrator
from l3_graph_orchestrator import GraphOrchestrator
from l3_qa_orchestrator import QAOrchestrator
from l3_rag_orchestrator import RAGOrchestrator


class DummyExecutor:
    def execute(self, plan, state):
        return {}


class FakeSafetyGateway:
    def __init__(self):
        self.received_payloads = []

    def evaluate(self, payload):
        self.received_payloads.append(payload)
        return {"safety_gateway": {"status": "allowed"}}


@pytest.mark.parametrize(
    "reasoner_cls",
    [StrategyReasoner, RAGReasoner, DraftingReasoner],
)
def test_metadata_added_in_l1_strategy(reasoner_cls):
    state = {"objective": "test-objective", "audience": "expert"}
    plan = reasoner_cls().plan(state)

    metadata = plan.get("safety_metadata")
    assert metadata
    assert metadata["objective"] == "test-objective"
    assert metadata["sensitivity"] == "low"
    assert metadata["audience"] == "expert"
    assert metadata["tags"] == ["planning"]


def _assert_payload_contains_metadata(gateway, expected_objective=None, expected_audience=None):
    assert gateway.received_payloads
    payload = gateway.received_payloads[-1]
    assert payload.get("context_tags") == ["l3_orchestrator"]
    intent = payload.get("intent", {})
    assert intent.get("safety_metadata")
    if expected_objective is not None:
        assert intent.get("objective") == expected_objective
        assert intent["safety_metadata"]["objective"] == expected_objective
    if expected_audience is not None:
        assert intent["safety_metadata"]["audience"] == expected_audience
    return intent


def test_metadata_attached_in_all_l3_orchestrators():
    gateway = FakeSafetyGateway()
    executors = DummyExecutor()
    orchestrators = [
        BulletOrchestrator(safety_gateway=gateway, executor=executors),
        DraftOrchestrator(safety_gateway=gateway, executor=executors),
        GraphOrchestrator(safety_gateway=gateway, executor=executors),
        QAOrchestrator(safety_gateway=gateway, executor=executors),
        RAGOrchestrator(safety_gateway=gateway, executor=executors),
    ]

    for orchestrator in orchestrators:
        gateway.received_payloads.clear()
        orchestrator.orchestrate({"objective": "metadata-check", "audience": "review"})
        _assert_payload_contains_metadata(
            gateway, expected_objective="metadata-check", expected_audience="review"
        )


def test_safety_gateway_receives_metadata():
    gateway = FakeSafetyGateway()
    orchestrator = GraphOrchestrator(safety_gateway=gateway, executor=DummyExecutor())

    orchestrator.orchestrate({"objective": "propagate", "audience": "ops"})
    intent = _assert_payload_contains_metadata(
        gateway, expected_objective="propagate", expected_audience="ops"
    )

    metadata = intent["safety_metadata"]
    assert metadata["objective"] == "propagate"
    assert metadata["audience"] == "ops"
