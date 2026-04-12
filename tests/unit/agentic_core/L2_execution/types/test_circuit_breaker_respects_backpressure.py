"""Test CircuitBreakerRespectsBackpressure functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCircuitBreakerRespectsBackpressure:
    """Test CircuitBreakerRespectsBackpressure functionality."""

    def test_circuit_breaker_respects_backpressure_imports(self):
        """Test circuit_breaker_respects_backpressure module imports."""
        from agentic_core import circuit_breaker_respects_backpressure

        assert circuit_breaker_respects_backpressure is not None

    def test_circuit_breaker_respects_backpressure_class(self):
        """Test CircuitBreakerRespectsBackpressure class exists."""
        from agentic_core import CircuitBreakerRespectsBackpressure

        assert CircuitBreakerRespectsBackpressure is not None

    def test_circuit_breaker_respects_backpressure_callable(self):
        """Test circuit_breaker_respects_backpressure functions are callable."""
        from agentic_core import validate_circuit_breaker_respects_backpressure

        assert callable(validate_circuit_breaker_respects_backpressure)
