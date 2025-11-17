import pytest

from agent_messaging import AgentMessage, route_to_specialist
from agent_topology import (
    AgentGraph,
    AgentNode,
    AgentRole,
    COUNCIL_OF_QA,
    LINEAR_PIPELINE,
    summarize_graph,
)
from council_voting import deterministic_vote
from delegation_policy import can_delegate, delegation_metadata
from l4_state_adapter import StateAdapter
from multi_agent_orchestrator import MultiAgentOrchestrator


def _graph_with_different_roles():
    return AgentGraph(
        nodes=[
            AgentNode(AgentRole.PLANNER, {}),
            AgentNode(AgentRole.RETRIEVER, {}),
            AgentNode(AgentRole.DRAFTER, {}),
            AgentNode(AgentRole.QA, {}),
            AgentNode(AgentRole.SAFETY, {}),
        ],
        edges=[
            (AgentRole.PLANNER, AgentRole.RETRIEVER),
            (AgentRole.RETRIEVER, AgentRole.DRAFTER),
            (AgentRole.DRAFTER, AgentRole.QA),
            (AgentRole.QA, AgentRole.SAFETY),
        ],
    )


def test_graph_summary():
    graph = _graph_with_different_roles()

    summary = summarize_graph(graph)

    assert summary["nodes"] == [
        AgentRole.PLANNER.value,
        AgentRole.RETRIEVER.value,
        AgentRole.DRAFTER.value,
        AgentRole.QA.value,
        AgentRole.SAFETY.value,
    ]
    assert summary["edges"] == [
        (AgentRole.PLANNER.value, AgentRole.RETRIEVER.value),
        (AgentRole.RETRIEVER.value, AgentRole.DRAFTER.value),
        (AgentRole.DRAFTER.value, AgentRole.QA.value),
        (AgentRole.QA.value, AgentRole.SAFETY.value),
    ]


def test_message_route_trace():
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.RETRIEVER,
        content={},
        metadata={},
    )

    node = route_to_specialist(LINEAR_PIPELINE, message)

    assert node.role == AgentRole.RETRIEVER
    assert message.metadata["route_trace"] == [AgentRole.PLANNER.value, AgentRole.RETRIEVER.value]


def test_delegation_metadata():
    assert can_delegate(AgentRole.PLANNER, AgentRole.RETRIEVER) is True
    assert can_delegate(AgentRole.PLANNER, AgentRole.SAFETY) is False
    assert can_delegate(AgentRole.RETRIEVER, AgentRole.DRAFTER) is True
    assert can_delegate(AgentRole.DRAFTER, AgentRole.QA) is True
    assert can_delegate(AgentRole.QA, AgentRole.SAFETY) is True
    assert can_delegate(AgentRole.SAFETY, AgentRole.PLANNER) is False

    metadata = delegation_metadata(AgentRole.PLANNER, AgentRole.RETRIEVER)
    assert metadata == {
        "from": AgentRole.PLANNER.value,
        "to": AgentRole.RETRIEVER.value,
        "allowed": True,
    }


def test_council_vote():
    candidates = [
        {"id": 1, "score": 0.7, "rationale": "baseline"},
        {"id": 2, "score": 0.7, "rationale": "alt"},
    ]

    winner = deterministic_vote(candidates)

    assert winner["id"] == 1
    assert winner["score"] == 0.7
    assert winner["rationale"] == "baseline"


def test_multi_agent_orchestrator_metadata():
    adapter = StateAdapter()
    orchestrator = MultiAgentOrchestrator(COUNCIL_OF_QA, adapter)
    message = AgentMessage(
        sender=AgentRole.QA,
        recipient=AgentRole.QA,
        content={"result": "ok"},
        metadata={},
    )

    state = orchestrator.dispatch(message, adapter.state)
    multi_agent = state["multi_agent"]

    assert multi_agent["last_message"] == {"result": "ok"}
    assert multi_agent["sender"] == AgentRole.QA.value
    assert multi_agent["recipient"] == AgentRole.QA.value
    assert multi_agent["delegation"] == {
        "from": AgentRole.QA.value,
        "to": AgentRole.QA.value,
        "allowed": False,
    }
    assert multi_agent["graph_summary"] == summarize_graph(COUNCIL_OF_QA)
    assert multi_agent["council_vote"] == {
        "id": 1,
        "score": 0.7,
        "rationale": "baseline",
    }
