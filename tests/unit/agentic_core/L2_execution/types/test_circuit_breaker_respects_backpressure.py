"""Smoke tests for circuit_breaker_respects_backpressure exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestCircuitBreakerRespectsBackpressure:
    """Smoke tests for circuit_breaker_respects_backpressure exports."""

    def test_circuit_breaker_respects_backpressure_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "circuit_breaker_respects_backpressure")
        assert module is not None

    def test_circuit_breaker_respects_backpressure_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "CircuitBreakerRespectsBackpressure")
        assert klass is not None

    def test_circuit_breaker_respects_backpressure_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_circuit_breaker_respects_backpressure")
        assert callable(validator)
