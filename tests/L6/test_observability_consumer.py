import unittest
from unittest.mock import MagicMock
from agentic_core.L6_observability.sovereign_observability_agent import SovereignObservabilityAgent

class TestObservabilityConsumer(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_redis = MagicMock()
        self.agent = SovereignObservabilityAgent(name="Tester")
        self.agent.redis_client = self.mock_redis

    async def test_tc27_consumer_read_and_ack(self):
        """TC27: verify consumer reads from group and acknowledges messages."""
        mock_payload = {b"event": b'{"event_id": "123", "event_type": "test"}'}
        self.mock_redis.xreadgroup.return_value = [
            (b"sovereign_event_stream", [(b"msg_id_999", mock_payload)])
        ]

        await self.agent.process_stream(count=1)

        self.mock_redis.xreadgroup.assert_called_once()
        self.mock_redis.xack.assert_called_with(
            "sovereign_event_stream", "l6_observability_group", b"msg_id_999"
        )

    def test_tc28_group_setup_resilience(self):
        """TC28: verify setup handles existing group (BUSYGROUP) gracefully."""
        self.mock_redis.xgroup_create.side_effect = Exception("BUSYGROUP Consumer Group name already exists")

        self.agent._setup_consumer_group()
        self.mock_redis.xgroup_create.assert_called()

if __name__ == "__main__":
    unittest.main()
