"""Test HealingOrchestratorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealingOrchestratorAdg:
    """Test HealingOrchestratorAdg functionality."""

    def test_healing_orchestrator_adg_imports(self):
        """Test healing_orchestrator_adg module imports."""
        from agentic_core import healing_orchestrator_adg

        assert healing_orchestrator_adg is not None

    def test_healing_orchestrator_adg_class(self):
        """Test HealingOrchestratorAdg class exists."""
        from agentic_core import HealingOrchestratorAdg

        assert HealingOrchestratorAdg is not None

    def test_healing_orchestrator_adg_callable(self):
        """Test healing_orchestrator_adg functions are callable."""
        from agentic_core import validate_healing_orchestrator_adg

        assert callable(validate_healing_orchestrator_adg)
