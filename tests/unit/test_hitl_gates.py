"""Test HitlGates functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHitlGates:
    """Test HitlGates functionality."""

    def test_hitl_gates_imports(self):
        """Test hitl_gates module imports."""
        from agentic_core import hitl_gates
        assert hitl_gates is not None

    def test_hitl_gates_class(self):
        """Test HitlGates class exists."""
        from agentic_core import HitlGates
        assert HitlGates is not None

    def test_hitl_gates_callable(self):
        """Test hitl_gates functions are callable."""
        from agentic_core import validate_hitl_gates
        assert callable(validate_hitl_gates)
