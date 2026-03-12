"""ADG-driven tests for mixins/circuit_breaker_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.circuit_breaker_mixin import (
    CircuitBreakerMixin,
    CircuitState,
    CircuitStats,
)


class TestCircuitState:
    def test_closed_value(self):
        assert CircuitState.CLOSED.value == "closed"

    def test_open_value(self):
        assert CircuitState.OPEN.value == "open"

    def test_half_open_value(self):
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestCircuitStats:
    def test_creates_with_defaults(self):
        stats = CircuitStats()
        assert stats.total_calls == 0
        assert stats.successful_calls == 0
        assert stats.failed_calls == 0

    def test_rejected_calls_default_zero(self):
        stats = CircuitStats()
        assert stats.rejected_calls == 0

    def test_last_failure_time_default_none(self):
        stats = CircuitStats()
        assert stats.last_failure_time is None

    def test_consecutive_failures_default_zero(self):
        stats = CircuitStats()
        assert stats.consecutive_failures == 0


class TestCircuitBreakerMixin:
    def test_importable(self):
        assert callable(CircuitBreakerMixin)

    def test_has_circuit_protected(self):
        assert hasattr(CircuitBreakerMixin, "circuit_protected")

    def test_has_reset_circuit(self):
        assert hasattr(CircuitBreakerMixin, "reset_circuit")
