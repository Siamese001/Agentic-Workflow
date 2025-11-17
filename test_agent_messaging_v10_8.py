from agent_messaging import AgentMessage, route_to_specialist
from agent_topology import AgentRole, LINEAR_PIPELINE


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
