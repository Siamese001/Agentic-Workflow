"""Test ExecutionStrategyAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecutionStrategyAdg:
    """Test ExecutionStrategyAdg functionality."""

    def test_execution_strategy_adg_imports(self):
        """Test execution_strategy_adg module imports."""
        from agentic_core import execution_strategy_adg

        assert execution_strategy_adg is not None

    def test_execution_strategy_adg_class(self):
        """Test ExecutionStrategyAdg class exists."""
        from agentic_core import ExecutionStrategyAdg

        assert ExecutionStrategyAdg is not None

    def test_execution_strategy_adg_callable(self):
        """Test execution_strategy_adg functions are callable."""
        from agentic_core import validate_execution_strategy_adg

        assert callable(validate_execution_strategy_adg)
