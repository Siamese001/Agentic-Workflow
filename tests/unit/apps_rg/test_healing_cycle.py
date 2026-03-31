"""Test HealingCycle functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealingCycle:
    """Test HealingCycle functionality."""

    def test_healing_cycle_imports(self):
        """Test healing_cycle module imports."""
        from agentic_core import healing_cycle
        assert healing_cycle is not None

    def test_healing_cycle_class(self):
        """Test HealingCycle class exists."""
        from agentic_core import HealingCycle
        assert HealingCycle is not None

    def test_healing_cycle_callable(self):
        """Test healing_cycle functions are callable."""
        from agentic_core import validate_healing_cycle
        assert callable(validate_healing_cycle)
