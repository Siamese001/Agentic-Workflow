"""Grouped multi-agent tests."""
from multi_agent import AgentMessage, route_to_specialist
from multi_agent import AgentRole, LINEAR_PIPELINE


def test_agent_message_stores_fields():
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.RETRIEVER,
        content={"query": "example"},
        metadata={"priority": "high"},
    )

    assert message.sender == AgentRole.PLANNER
    assert message.recipient == AgentRole.RETRIEVER
    assert message.content == {"query": "example"}
    assert message.metadata == {"priority": "high"}


def test_route_to_specialist_finds_recipient():
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.DRAFTER,
        content={},
        metadata={},
    )

    node = route_to_specialist(LINEAR_PIPELINE, message)
    assert node is not None
    assert node.role == AgentRole.DRAFTER


def test_route_to_specialist_returns_none_when_missing():
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.BULLET,
        content={},
        metadata={},
    )

    assert route_to_specialist(LINEAR_PIPELINE, message) is None


def test_route_to_specialist_is_deterministic():
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.QA,
        content={},
        metadata={},
    )

    first_result = route_to_specialist(LINEAR_PIPELINE, message)
    second_result = route_to_specialist(LINEAR_PIPELINE, message)

    assert first_result == second_result
from multi_agent import (
    AgentGraph,
    AgentNode,
    AgentRole,
    COUNCIL_OF_QA,
    LINEAR_PIPELINE,
)


def test_agent_role_member_count():
    assert len(AgentRole) == 6


def test_agent_graph_is_deterministic():
    node = AgentNode(AgentRole.PLANNER, {"example": True})
    graph_one = AgentGraph(nodes=[node], edges=[(AgentRole.PLANNER, AgentRole.PLANNER)])
    graph_two = AgentGraph(
        nodes=[AgentNode(AgentRole.PLANNER, {"example": True})],
        edges=[(AgentRole.PLANNER, AgentRole.PLANNER)],
    )

    assert graph_one == graph_two


def test_linear_pipeline_roles_order():
    expected_roles = [
        AgentRole.PLANNER,
        AgentRole.RETRIEVER,
        AgentRole.DRAFTER,
        AgentRole.QA,
        AgentRole.SAFETY,
    ]
    assert [node.role for node in LINEAR_PIPELINE.nodes] == expected_roles

    assert LINEAR_PIPELINE.edges == [
        (AgentRole.PLANNER, AgentRole.RETRIEVER),
        (AgentRole.RETRIEVER, AgentRole.DRAFTER),
        (AgentRole.DRAFTER, AgentRole.QA),
        (AgentRole.QA, AgentRole.SAFETY),
    ]


def test_council_of_qa_contains_three_nodes():
    assert len(COUNCIL_OF_QA.nodes) == 3
    assert all(node.role == AgentRole.QA for node in COUNCIL_OF_QA.nodes)
    assert [node.config.get("id") for node in COUNCIL_OF_QA.nodes] == [1, 2, 3]
from multi_agent import AgentMessage
from multi_agent import AgentGraph, AgentNode, AgentRole
from l4_state import StateAdapter
from multi_agent import MultiAgentOrchestrator


def _build_graph():
    return AgentGraph(
        nodes=[
            AgentNode(AgentRole.PLANNER, {}),
            AgentNode(AgentRole.RETRIEVER, {}),
            AgentNode(AgentRole.DRAFTER, {}),
        ],
        edges=[(AgentRole.PLANNER, AgentRole.RETRIEVER)],
    )


def test_dispatch_records_last_message_metadata():
    adapter = StateAdapter()
    orchestrator = MultiAgentOrchestrator(_build_graph(), adapter)
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.RETRIEVER,
        content={"query": "docs"},
        metadata={"trace_id": "123"},
    )

    state = orchestrator.dispatch(message, adapter.state)

    last_message = state["multi_agent"]["last_message"]

    assert last_message["sender"] == AgentRole.PLANNER.value
    assert last_message["recipient"] == AgentRole.RETRIEVER.value
    assert last_message["content"] == {"query": "docs"}


def test_dispatch_sets_routed_to_role_value():
    adapter = StateAdapter()
    orchestrator = MultiAgentOrchestrator(_build_graph(), adapter)
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.RETRIEVER,
        content={},
        metadata={},
    )

    state = orchestrator.dispatch(message, adapter.state)

    assert state["multi_agent"]["routed_to"] == AgentRole.RETRIEVER.value
    assert state["multi_agent"]["delegation"] == {
        "from": AgentRole.PLANNER.value,
        "to": AgentRole.RETRIEVER.value,
        "allowed": True,
    }


def test_dispatch_scopes_metadata_under_multi_agent_only():
    adapter = StateAdapter()
    orchestrator = MultiAgentOrchestrator(_build_graph(), adapter)
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.RETRIEVER,
        content={},
        metadata={},
    )
    initial_state = adapter.state

    state = orchestrator.dispatch(message, initial_state)

    assert "multi_agent" in state
    assert set(state.keys()) == set(initial_state.keys()) | {"multi_agent"}


def test_dispatch_does_not_mutate_existing_keys():
    adapter = StateAdapter()
    orchestrator = MultiAgentOrchestrator(_build_graph(), adapter)
    message = AgentMessage(
        sender=AgentRole.PLANNER,
        recipient=AgentRole.RETRIEVER,
        content={},
        metadata={},
    )
    initial_state = adapter.state

    state = orchestrator.dispatch(message, initial_state)

    for key in initial_state:
        if key == "metadata":
            continue
        assert state[key] == initial_state[key]
import pytest

from multi_agent import AgentMessage, route_to_specialist
from multi_agent import (
    AgentGraph,
    AgentNode,
    AgentRole,
    COUNCIL_OF_QA,
    LINEAR_PIPELINE,
    summarize_graph,
)
from multi_agent import deterministic_vote
from multi_agent import can_delegate, delegation_metadata
from l3_orchestration import GraphOrchestrator
from l4_state import StateAdapter
from multi_agent import MultiAgentOrchestrator


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

    assert multi_agent["last_message"] == {
        "content": {"result": "ok"},
        "sender": AgentRole.QA.value,
        "recipient": AgentRole.QA.value,
    }
    assert multi_agent["sender"] == AgentRole.QA.value
    assert multi_agent["recipient"] == AgentRole.QA.value
    assert multi_agent["routed_to"] == AgentRole.QA.value
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


def test_graph_orchestrator_runs_multi_agent_block():
    orchestrator = GraphOrchestrator()

    result = orchestrator.orchestrate({"objective": "ship", "audience": "ops"})

    multi_agent = result.state.get("multi_agent")

    assert multi_agent is not None
    assert multi_agent["delegation"] == {
        "from": AgentRole.PLANNER.value,
        "to": AgentRole.QA.value,
        "allowed": True,
    }
    assert multi_agent["graph_summary"] == summarize_graph(COUNCIL_OF_QA)
    assert multi_agent["council_vote"] == {
        "id": 1,
        "score": 0.7,
        "rationale": "baseline",
    }
import pytest

from self_correction import ArbitrationEngine


def test_arbitration_escalate_on_safety_blocked():
    engine = ArbitrationEngine()
    state = {"messages": ["msg"]}
    qa_report = {"findings": []}
    safety_patch = {"safety_gateway": {"status": "blocked"}}

    result = engine.evaluate(state, qa_report, safety_patch)

    assert result["action"] == "escalate"


def test_arbitration_retry_on_pending_qa():
    engine = ArbitrationEngine()
    state = {"messages": ["msg"]}
    qa_report = {"findings": [{"status": "pending"}]}
    safety_patch = {"safety_gateway": {"status": "allowed"}}

    result = engine.evaluate(state, qa_report, safety_patch)

    assert result["action"] == "retry"


def test_arbitration_replan_on_empty_messages():
    engine = ArbitrationEngine()
    state = {"messages": []}
    qa_report = {"findings": []}
    safety_patch = {"safety_gateway": {"status": "allowed"}}

    result = engine.evaluate(state, qa_report, safety_patch)

    assert result["action"] == "replan"


def test_arbitration_accept_default():
    engine = ArbitrationEngine()
    state = {"messages": ["msg"]}
    qa_report = {"findings": []}
    safety_patch = {"safety_gateway": {"status": "allowed"}}

    result = engine.evaluate(state, qa_report, safety_patch)

    assert result["action"] == "accept"
from copy import deepcopy

from hil_interface import apply_hil_feedback


def test_apply_hil_feedback_does_not_mutate():
    original_state = {"a": 1, "nested": {"b": 2}}
    snapshot = deepcopy(original_state)

    updated = apply_hil_feedback(original_state, {"comment": "looks good"})

    assert original_state == snapshot
    assert updated is not original_state


def test_apply_hil_feedback_deterministic():
    state = {"foo": "bar"}
    feedback = {"note": "check"}

    first = apply_hil_feedback(state, feedback)
    second = apply_hil_feedback(state, feedback)

    assert first == second
    assert first["hil_feedback"] == feedback


def test_apply_hil_feedback_sets_key():
    state = {}
    feedback = {"decision": "approve"}

    updated = apply_hil_feedback(state, feedback)

    assert "hil_feedback" in updated
    assert updated["hil_feedback"] == feedback
