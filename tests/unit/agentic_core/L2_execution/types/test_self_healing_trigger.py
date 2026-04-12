"""Test SelfHealingTrigger functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSelfHealingTrigger:
    """Test SelfHealingTrigger functionality."""

    def test_self_healing_trigger_imports(self):
        """Test self_healing_trigger module imports."""
        from agentic_core import self_healing_trigger

        assert self_healing_trigger is not None

    def test_self_healing_trigger_class(self):
        """Test SelfHealingTrigger class exists."""
        from agentic_core import SelfHealingTrigger

        assert SelfHealingTrigger is not None

    def test_self_healing_trigger_callable(self):
        """Test self_healing_trigger functions are callable."""
        from agentic_core import validate_self_healing_trigger

        assert callable(validate_self_healing_trigger)
