# TESTS DEPTH VIOLATION — 2026-01-18 05:21:41
# tests\mixins\test_state_validation_mixin.py was depth 3, MUST be 2.

import unittest

from agentic_core.utils.core_extensions.state_validation_mixin import (
    StateValidationError,
    StateValidationMixin,
)


class ValidatedAgent(StateValidationMixin):
    def __init__(self):
        self.status = "idle"
        self.counter = 0
        super().__init__()

    def is_idle(self) -> bool:
        return self.status == "idle"

    def is_busy(self, result) -> bool:
        return self.status == "busy"


class TestStateValidationMixin(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent = ValidatedAgent()

    async def test_tc5_precondition_success(self):
        """TC5: Should allow execution if pre-condition (is_idle) is met."""

        @StateValidationMixin.validate_state(pre=lambda s: s.is_idle())
        async def work(agent):
            agent.status = "busy"
            return "done"

        result = await work(self.agent)
        self.assertEqual(result, "done")
        self.assertEqual(self.agent.status, "busy")

    async def test_tc6_precondition_failure(self):
        """TC6: Should block execution if pre-condition is not met."""
        self.agent.status = "error"

        @StateValidationMixin.validate_state(pre=lambda s: s.is_idle())
        async def work(agent):
            return "should not run"

        with self.assertRaises(StateValidationError):
            await work(self.agent)

    async def test_tc7_idempotency_cache(self):
        """TC7: Should return cached result and not re-execute if idempotent=True."""
        self.execution_count = 0

        @StateValidationMixin.validate_state(idempotent=True)
        async def increment(agent, val):
            self.execution_count += 1
            return f"Result {val}"

        # First call
        res1 = await increment(self.agent, 10)
        # Second call with same args
        res2 = await increment(self.agent, 10)
        # Third call with different args
        res3 = await increment(self.agent, 20)

        self.assertEqual(res1, res2)
        self.assertNotEqual(res1, res3)
        self.assertEqual(self.execution_count, 2)  # Incremented only twice

    async def test_tc8_postcondition_validation(self):
        """TC8: Should raise error if post-condition fails after execution."""

        @StateValidationMixin.validate_state(post=lambda s, r: r == "correct")
        async def bad_work(agent):
            return "wrong"

        with self.assertRaises(StateValidationError):
            await bad_work(self.agent)


if __name__ == "__main__":
    unittest.main()
