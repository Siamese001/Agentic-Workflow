import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


def test_agent_bus_send_and_get() -> None:
    """Test basic agent bus send and get message operations."""
    AgentBus()
    MSG = AgentMessage(
        message_id='m1',
        source_agent_id='planner-1',
        target_agent_id='qa-1',
        CHANNEL='test',
        payload_type='request',
        CONTENT={
            'x': 1})
    bus.send(msg)
    bus.get_for('qa-1')
    assert msg in inbox
    bus.clear()
    assert bus.get_for('qa-1') == []

