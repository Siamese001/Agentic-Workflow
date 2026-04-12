"""Test ExecutionStatusAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecutionStatusAdg:
    """Test ExecutionStatusAdg functionality."""

    def test_execution_status_adg_imports(self):
        """Test execution_status_adg module imports."""
        from agentic_core import execution_status_adg

        assert execution_status_adg is not None

    def test_execution_status_adg_class(self):
        """Test ExecutionStatusAdg class exists."""
        from agentic_core import ExecutionStatusAdg

        assert ExecutionStatusAdg is not None

    def test_execution_status_adg_callable(self):
        """Test execution_status_adg functions are callable."""
        from agentic_core import validate_execution_status_adg

        assert callable(validate_execution_status_adg)
