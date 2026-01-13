import unittest
import json
from unittest.mock import MagicMock
from agentic_core.utils.core_extensions.event_emission_mixin import EventEmissionMixin, SovereignEvent

class RedisObservableAgent(EventEmissionMixin):
    def __init__(self):
        self.redis_client = MagicMock()  # Mock Redis for testing
        super().__init__()

class TestRedisEventDispatch(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.agent = RedisObservableAgent()

    def test_tc25_dispatch_to_redis_stream(self):
        """TC25: verify _dispatch_to_observability calls xadd with correct payload."""
        event = SovereignEvent(event_type="test.dispatch", source_agent="TestAgent")

        self.agent._dispatch_to_observability(event)

        # Verify Redis xadd call
        self.agent.redis_client.xadd.assert_called_once()
        call_args = self.agent.redis_client.xadd.call_args

        self.assertEqual(call_args[0][0], "sovereign_event_stream")
        payload = json.loads(call_args[0][1]["event"])
        self.assertEqual(payload["event_type"], "test.dispatch")

    def test_tc26_graceful_failure_no_redis(self):
        """TC26: verify agent logic continues even if Redis is unavailable."""
        self.agent.redis_client = None
        event = SovereignEvent(event_type="test.fail", source_agent="TestAgent")

        # Should not raise exception
        self.agent._dispatch_to_observability(event)

if __name__ == "__main__":
    unittest.main()
