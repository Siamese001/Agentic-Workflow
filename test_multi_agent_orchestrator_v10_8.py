from agent_messaging import AgentMessage
from agent_topology import AgentGraph, AgentNode, AgentRole
from l4_state_adapter import StateAdapter
from multi_agent_orchestrator import MultiAgentOrchestrator


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
