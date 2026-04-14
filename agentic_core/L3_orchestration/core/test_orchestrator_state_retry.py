"""Test OrchestratorStateRetry functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestOrchestratorStateRetry:
    """Test OrchestratorStateRetry functionality."""

    def test_orchestrator_state_retry_imports(self):
        """Test orchestrator_state_retry module imports."""
        from agentic_core import orchestrator_state_retry

        assert orchestrator_state_retry is not None

    def test_orchestrator_state_retry_class(self):
        """Test OrchestratorStateRetry class exists."""
        from agentic_core import OrchestratorStateRetry

        assert OrchestratorStateRetry is not None

    def test_orchestrator_state_retry_callable(self):
        """Test orchestrator_state_retry functions are callable."""
        from agentic_core import validate_orchestrator_state_retry

        assert callable(validate_orchestrator_state_retry)
