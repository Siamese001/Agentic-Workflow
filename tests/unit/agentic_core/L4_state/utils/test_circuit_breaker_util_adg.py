"""ADG-driven tests for L4_state/utils/circuit_breaker_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.utils.circuit_breaker_util import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitBreakerState,
)


class TestCircuitBreakerState:
    def test_closed_state(self):
        assert CircuitBreakerState.CLOSED.value == "CLOSED"

    def test_open_state(self):
        assert CircuitBreakerState.OPEN.value == "OPEN"

    def test_half_open_state(self):
        assert CircuitBreakerState.HALF_OPEN.value == "HALF_OPEN"


class TestCircuitBreakerOpenError:
    def test_is_exception(self):
        assert issubclass(CircuitBreakerOpenError, Exception)

    def test_has_breaker_name(self):
        err = CircuitBreakerOpenError("circuit is open", "my_breaker")
        assert err.breaker_name == "my_breaker"

    def test_message_in_str(self):
        err = CircuitBreakerOpenError("circuit is open", "my_breaker")
        assert "circuit is open" in str(err)


class TestCircuitBreakerInit:
    def test_creates_with_name(self):
        cb = CircuitBreaker(name="test")
        assert cb.name == "test"

    def test_initial_state_closed(self):
        cb = CircuitBreaker(name="test")
        assert cb.state == CircuitBreakerState.CLOSED

    def test_failure_threshold_default_5(self):
        cb = CircuitBreaker(name="test")
        assert cb.failure_threshold == 5

    def test_reset_after_s_default_30(self):
        cb = CircuitBreaker(name="test")
        assert cb.reset_after_s == 30

    def test_failure_count_starts_zero(self):
        cb = CircuitBreaker(name="test")
        assert cb.failure_count == 0

    def test_success_count_starts_zero(self):
        cb = CircuitBreaker(name="test")
        assert cb.success_count == 0


class TestCircuitBreakerCanExecute:
    def test_can_execute_when_closed(self):
        cb = CircuitBreaker(name="test")
        assert cb.can_execute() is True

    def test_cannot_execute_when_open(self):
        cb = CircuitBreaker(name="test", failure_threshold=1)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.can_execute() is False


class TestCircuitBreakerRecordFailure:
    def test_increments_failure_count(self):
        cb = CircuitBreaker(name="test", failure_threshold=5)
        cb.record_failure()
        assert cb.failure_count == 1

    def test_opens_at_threshold(self):
        cb = CircuitBreaker(name="test", failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_has_record_success(self):
        assert hasattr(CircuitBreaker, "record_success")
