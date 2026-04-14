"""Test ExecutionOrchestrator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecutionOrchestrator:
    """Test ExecutionOrchestrator functionality."""

    def test_execution_orchestrator_imports(self):
        """Test execution_orchestrator module imports."""
        from agentic_core import execution_orchestrator

        assert execution_orchestrator is not None

    def test_execution_orchestrator_class(self):
        """Test ExecutionOrchestrator class exists."""
        from agentic_core import ExecutionOrchestrator

        assert ExecutionOrchestrator is not None

    def test_execution_orchestrator_callable(self):
        """Test execution_orchestrator functions are callable."""
        from agentic_core import validate_execution_orchestrator

        assert callable(validate_execution_orchestrator)
