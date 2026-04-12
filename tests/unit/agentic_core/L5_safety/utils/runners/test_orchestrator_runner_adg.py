"""Test OrchestratorRunnerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestOrchestratorRunnerAdg:
    """Test OrchestratorRunnerAdg functionality."""

    def test_orchestrator_runner_adg_imports(self):
        """Test orchestrator_runner_adg module imports."""
        from agentic_core import orchestrator_runner_adg

        assert orchestrator_runner_adg is not None

    def test_orchestrator_runner_adg_class(self):
        """Test OrchestratorRunnerAdg class exists."""
        from agentic_core import OrchestratorRunnerAdg

        assert OrchestratorRunnerAdg is not None

    def test_orchestrator_runner_adg_callable(self):
        """Test orchestrator_runner_adg functions are callable."""
        from agentic_core import validate_orchestrator_runner_adg

        assert callable(validate_orchestrator_runner_adg)
