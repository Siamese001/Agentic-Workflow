# TESTS DEPTH VIOLATION — 2026-01-18 05:21:41
# tests\mixins\test_context_propagation_mixin.py was depth 3, MUST be 2.

import asyncio
import unittest

from agentic_core.utils.core_extensions.context_propagation_mixin import ContextPropagationMixin


class TraceableAgent(ContextPropagationMixin):
    @ContextPropagationMixin.trace_context
    async def sub_task(self):
        return self.get_context()

    @ContextPropagationMixin.trace_context
    async def main_task(self):
        ctx_main = self.get_context()
        ctx_sub = await self.sub_task()
        return ctx_main, ctx_sub


class TestContextPropagationMixin(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent = TraceableAgent()

    async def test_tc21_trace_propagation(self):
        """TC21: Trace ID should remain consistent across nested async calls."""
        ctx_main, ctx_sub = await self.agent.main_task()

        self.assertIsNotNone(ctx_main["trace_id"])
        self.assertEqual(ctx_main["trace_id"], ctx_sub["trace_id"])
        # Span IDs should be different for nested calls
        self.assertNotEqual(ctx_main["span_id"], ctx_sub["span_id"])

    async def test_tc22_async_isolation(self):
        """TC22: Concurrent tasks should have isolated trace contexts."""

        async def run_and_get_trace():
            await asyncio.sleep(0.01)
            ctx, _ = await self.agent.main_task()
            return ctx["trace_id"]

        traces = await asyncio.gather(run_and_get_trace(), run_and_get_trace())
        self.assertNotEqual(
            traces[0], traces[1], "Trace IDs must be isolated across concurrent tasks"
        )


if __name__ == "__main__":
    unittest.main()
