import pytest

from cost_tracker import CostTracker
from l1_strategy_reasoner import StrategyReasoner
from l3_qa_orchestrator import QAOrchestrator
from meta_profile import META_PROFILE
from routing_policy import RoutingCriteria, decide_route


@pytest.fixture(autouse=True)
def reset_meta_profile():
    META_PROFILE.routing_bias.clear()
    META_PROFILE.planning_bias.clear()
    yield
    META_PROFILE.routing_bias.clear()
    META_PROFILE.planning_bias.clear()


def test_meta_profile_updates_after_orchestrator(monkeypatch):
    def fake_snapshot(self):
        return {
            "spans": [
                {"name": "execution", "duration_ms": 1.0},
                {"name": "planning", "duration_ms": 2.0},
            ]
        }

    monkeypatch.setattr(CostTracker, "snapshot", fake_snapshot)

    orchestrator = QAOrchestrator()
    orchestrator.orchestrate({})

    assert META_PROFILE.routing_bias.get("prefer_fast") is True
    assert META_PROFILE.planning_bias.get("conservative") is True


def test_routing_prefers_fast_under_bias():
    META_PROFILE.routing_bias["prefer_fast"] = True
    decision = decide_route(RoutingCriteria(task_type="analysis", complexity="high"))
    assert decision.endpoint == "fast"


def test_strategy_reasoner_conservative_plan():
    META_PROFILE.planning_bias["conservative"] = True
    reasoner = StrategyReasoner()
    plan = reasoner.plan({"objective": "test", "deliverables": ["a", "b", "c"]})

    assert len(plan["deliverables"]) <= 2
    assert len(plan["steps"]) <= 2
