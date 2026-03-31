"""Test InjectionRegressionGate functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInjectionRegressionGate:
    """Test InjectionRegressionGate functionality."""

    def test_injection_regression_gate_imports(self):
        """Test injection_regression_gate module imports."""
        from agentic_core import injection_regression_gate
        assert injection_regression_gate is not None

    def test_injection_regression_gate_class(self):
        """Test InjectionRegressionGate class exists."""
        from agentic_core import InjectionRegressionGate
        assert InjectionRegressionGate is not None

    def test_injection_regression_gate_callable(self):
        """Test injection_regression_gate functions are callable."""
        from agentic_core import validate_injection_regression_gate
        assert callable(validate_injection_regression_gate)
