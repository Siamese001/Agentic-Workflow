"""Test HealerGate functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealerGate:
    """Test HealerGate functionality."""

    def test_healer_gate_imports(self):
        """Test healer_gate module imports."""
        from agentic_core import healer_gate
        assert healer_gate is not None

    def test_healer_gate_class(self):
        """Test HealerGate class exists."""
        from agentic_core import HealerGate
        assert HealerGate is not None

    def test_healer_gate_callable(self):
        """Test healer_gate functions are callable."""
        from agentic_core import validate_healer_gate
        assert callable(validate_healer_gate)
