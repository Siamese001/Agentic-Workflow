"""Test HealingOrchestrationTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealingOrchestrationTypes:
    """Test HealingOrchestrationTypes functionality."""

    def test_healing_orchestration_types_imports(self):
        """Test healing_orchestration_types module imports."""
        from agentic_core import healing_orchestration_types

        assert healing_orchestration_types is not None

    def test_healing_orchestration_types_class(self):
        """Test HealingOrchestrationTypes class exists."""
        from agentic_core import HealingOrchestrationTypes

        assert HealingOrchestrationTypes is not None

    def test_healing_orchestration_types_callable(self):
        """Test healing_orchestration_types functions are callable."""
        from agentic_core import validate_healing_orchestration_types

        assert callable(validate_healing_orchestration_types)
