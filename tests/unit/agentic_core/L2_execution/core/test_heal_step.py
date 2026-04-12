"""Test HealStep functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealStep:
    """Test HealStep functionality."""

    def test_heal_step_imports(self):
        """Test heal_step module imports."""
        from agentic_core import heal_step

        assert heal_step is not None

    def test_heal_step_class(self):
        """Test HealStep class exists."""
        from agentic_core import HealStep

        assert HealStep is not None

    def test_heal_step_callable(self):
        """Test heal_step functions are callable."""
        from agentic_core import validate_heal_step

        assert callable(validate_heal_step)
