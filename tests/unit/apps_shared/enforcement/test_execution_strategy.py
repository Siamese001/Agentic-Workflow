"""Test ExecutionStrategy functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecutionStrategy:
    """Test ExecutionStrategy functionality."""

    def test_execution_strategy_imports(self):
        """Test execution_strategy module imports."""
        from agentic_core import execution_strategy

        assert execution_strategy is not None

    def test_execution_strategy_class(self):
        """Test ExecutionStrategy class exists."""
        from agentic_core import ExecutionStrategy

        assert ExecutionStrategy is not None

    def test_execution_strategy_callable(self):
        """Test execution_strategy functions are callable."""
        from agentic_core import validate_execution_strategy

        assert callable(validate_execution_strategy)
