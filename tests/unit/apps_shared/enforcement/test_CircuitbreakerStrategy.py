"""Test Circuitbreakerstrategy functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCircuitbreakerstrategy:
    """Test Circuitbreakerstrategy functionality."""

    def test_CircuitbreakerStrategy_imports(self):
        """Test CircuitbreakerStrategy module imports."""
        from agentic_core import CircuitbreakerStrategy

        assert CircuitbreakerStrategy is not None

    def test_CircuitbreakerStrategy_class(self):
        """Test Circuitbreakerstrategy class exists."""
        from agentic_core import Circuitbreakerstrategy

        assert Circuitbreakerstrategy is not None

    def test_CircuitbreakerStrategy_callable(self):
        """Test CircuitbreakerStrategy functions are callable."""
        from agentic_core import validate_CircuitbreakerStrategy

        assert callable(validate_CircuitbreakerStrategy)
