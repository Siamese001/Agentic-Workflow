# TESTS DEPTH VIOLATION — 2026-01-18 05:21:41
# tests\mixins\test_batch_operation_mixin.py was depth 3, MUST be 2.

import unittest
import asyncio
import time
from agentic_core.utils.core_extensions.batch_operation_mixin import BatchOperationMixin


class BatchAgent(BatchOperationMixin):
    async def fast_task(self, x):
        return x * 2

    async def slow_task(self, delay=0.1):
        await asyncio.sleep(delay)
        return "slow_done"

    async def failing_task(self):
        raise ValueError("Simulated failure")


class TestBatchOperationMixin(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent = BatchAgent()

    async def test_tc17_successful_batch(self):
        """TC17: Should execute a simple batch of tasks and return ordered results."""
        tasks = [self.agent.fast_task(i) for i in range(5)]
        results = await self.agent.batch_execute(tasks)
        self.assertEqual(results, [0, 2, 4, 6, 8])

    async def test_tc18_concurrency_limiting(self):
        """TC18: Verify that max_workers limits parallel execution."""
        # Run 4 tasks that take 0.1s each, but only allow 2 workers.
        # Total time should be ~0.2s, not 0.1s.
        tasks = [self.agent.slow_task(0.1) for _ in range(4)]

        start = time.time()
        await self.agent.batch_execute(tasks, max_workers=2)
        duration = time.time() - start

        self.assertGreaterEqual(duration, 0.2)
        self.assertLess(duration, 0.3)

    async def test_tc19_partial_failure_handling(self):
        """TC19: Should continue batch execution even if some tasks fail."""
        tasks = [self.agent.fast_task(1), self.agent.failing_task(), self.agent.fast_task(2)]
        results = await self.agent.batch_execute(tasks)

        self.assertEqual(results[0], 2)
        self.assertIsInstance(results[1], ValueError)
        self.assertEqual(results[2], 4)

    async def test_tc20_sequential_mode(self):
        """TC20: Should execute tasks one-by-one when sequential=True."""
        tasks = [self.agent.slow_task(0.05) for _ in range(3)]

        start = time.time()
        results = await self.agent.batch_execute(tasks, sequential=True)
        duration = time.time() - start

        self.assertEqual(len(results), 3)
        self.assertGreaterEqual(duration, 0.15)


if __name__ == "__main__":
    unittest.main()
