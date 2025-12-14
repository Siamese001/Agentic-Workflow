import logging

# from archives.legacy_root_folders.orchestration.agent_bus import AgentBus  # DEPRECATED: Archiv...
# from archives.legacy_root_folders.core.models.models import AgentMessage  # DEPRECATED: Archive...

def test_agent_bus_send_and_get() -> None:
    """Test basic agent bus send and get message operations."""
    bus = AgentBus()

    msg = AgentMessage(
        message_id="m1",
        source_agent_id="planner-1",
        target_agent_id="qa-1",
        channel="test",
        payload_type="request",
        content={"x": 1},
    )

    bus.send(msg)

    inbox = bus.get_for("qa-1")
    assert msg in inbox

    bus.clear()
    assert bus.get_for("qa-1") == []
