from meta.metacognition.hypothesis import generate_initial_hypotheses
from meta.metacognition.models import Hypothesis


class DummyRAG:
    def __init__(self, evidence_count: int) -> None:
        self.evidence = [object() for _ in range(evidence_count)]


class DummyAgentCard:
    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id


def test_generate_initial_hypotheses_with_evidence():
    rag = DummyRAG(evidence_count=3)
    agent = DummyAgentCard("planner_1")

    hs = generate_initial_hypotheses("task", rag, agent)
    assert len(hs) >= 1
    assert all(isinstance(h, Hypothesis) for h in hs)
    assert {h.agent_id for h in hs} == {"planner_1"}


def test_generate_initial_hypotheses_without_evidence():
    rag = DummyRAG(evidence_count=0)
    agent = DummyAgentCard("planner_1")

    hs = generate_initial_hypotheses("task", rag, agent)
    assert len(hs) == 1
    assert hs[0].confidence <= 0.3






