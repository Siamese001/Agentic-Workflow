"""Test HealContextTraceId functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealContextTraceId:
    """Test HealContextTraceId functionality."""

    def test_heal_context_imports(self):
        """Test heal context module imports."""
        from agentic_core.L0_routing.scripts import heal_context_trace
        assert heal_context_trace is not None

    def test_heal_context_handler(self):
        """Test heal context handler exists."""
        from agentic_core.L0_routing.scripts.heal_context_trace import ContextTraceHandler
        assert ContextTraceHandler is not None

    def test_heal_context_function(self):
        """Test heal context function."""
        from agentic_core.L0_routing.scripts.heal_context_trace import heal_context
        assert callable(heal_context)
