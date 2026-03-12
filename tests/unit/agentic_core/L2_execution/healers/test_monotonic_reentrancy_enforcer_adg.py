"""ADG-driven tests for L2_execution/healers/monotonic_reentrancy_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.monotonic_reentrancy_enforcer import (
    NonMonotonicRetryViolation,
    MonotonicReentrancyEnforcer,
)


class TestNonMonotonicRetryViolation:
    def test_is_exception(self):
        assert issubclass(NonMonotonicRetryViolation, Exception)


class TestMonotonicReentrancyEnforcer:
    def test_creates(self):
        enforcer = MonotonicReentrancyEnforcer()
        assert enforcer is not None

    def test_first_retry_is_one(self):
        enforcer = MonotonicReentrancyEnforcer()
        count = enforcer.get_and_increment_retry_count("trace-1")
        assert count == 1

    def test_second_retry_is_two(self):
        enforcer = MonotonicReentrancyEnforcer()
        enforcer.get_and_increment_retry_count("trace-1")
        count = enforcer.get_and_increment_retry_count("trace-1")
        assert count == 2

    def test_different_traces_independent(self):
        enforcer = MonotonicReentrancyEnforcer()
        enforcer.get_and_increment_retry_count("trace-a")
        count_b = enforcer.get_and_increment_retry_count("trace-b")
        assert count_b == 1
