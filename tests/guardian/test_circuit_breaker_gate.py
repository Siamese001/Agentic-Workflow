"""Test CircuitBreakerGate functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCircuitBreakerGate:
    """Test CircuitBreakerGate functionality."""

    def test_circuit_breaker_gate_imports(self):
        """Test circuit_breaker_gate module imports."""
        from agentic_core import circuit_breaker_gate
        assert circuit_breaker_gate is not None

    def test_circuit_breaker_gate_class(self):
        """Test CircuitBreakerGate class exists."""
        from agentic_core import CircuitBreakerGate
        assert CircuitBreakerGate is not None

    def test_circuit_breaker_gate_callable(self):
        """Test circuit_breaker_gate functions are callable."""
        from agentic_core import validate_circuit_breaker_gate
        assert callable(validate_circuit_breaker_gate)
