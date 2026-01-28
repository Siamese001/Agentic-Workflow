# TESTS DEPTH VIOLATION — 2026-01-18 05:21:41
# tests\mixins\test_rate_limit_mixin.py was depth 3, MUST be 2.

import unittest
import asyncio
import time
from agentic_core.utils.core_extensions.rate_limit_mixin import RateLimitMixin, RateLimitExceeded

class RateLimitedAgent(RateLimitMixin):
    """Mock agent for testing throttling logic."""
    def __init__(self):
        # Configure a strict limit: 2 actions per 1 second
        self._rate_limits = {"test_op": {"rate": 2, "per": 1, "burst": 2}}
        super().__init__()

class TestRateLimitMixin(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent = RateLimitedAgent()

    async def test_tc1_allow_within_limit(self):
        """TC1: Should allow operations that stay within the 2/1s limit."""
        # First two should pass immediately (using burst)
        self.assertTrue(await self.agent.check_rate_limit("test_op"))
        self.assertTrue(await self.agent.check_rate_limit("test_op"))

    async def test_tc2_raise_when_exceeded(self):
        """TC2: Should raise RateLimitExceeded on the 3rd attempt within 1s."""
        await self.agent.check_rate_limit("test_op")
        await self.agent.check_rate_limit("test_op")
        
        with self.assertRaises(RateLimitExceeded) as cm:
            await self.agent.check_rate_limit("test_op")
        
        self.assertEqual(cm.exception.key, "test_op")
        self.assertGreater(cm.exception.wait_time, 0)

    async def test_tc3_refill_mechanism(self):
        """TC3: Should allow another operation after the refill period."""
        await self.agent.check_rate_limit("test_op")
        await self.agent.check_rate_limit("test_op")
        
        # Wait for refill (0.5s should refill 1 token at 2/1s rate)
        await asyncio.sleep(0.6)
        self.assertTrue(await self.agent.check_rate_limit("test_op"))

    async def test_tc4_decorator_enforcement(self):
        """TC4: Should enforce limits when using the @rate_limit decorator."""
        class DecoratedAgent(RateLimitedAgent):
            @RateLimitMixin.rate_limit("test_op")
            async def perform_action(self):
                return "success"

        agent = DecoratedAgent()
        await agent.perform_action()
        await agent.perform_action()
        
        with self.assertRaises(RateLimitExceeded):
            await agent.perform_action()

if __name__ == "__main__":
    unittest.main()
