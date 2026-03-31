"""Test ExecutionTraceIntegrity functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecutionTraceIntegrity:
    """Test ExecutionTraceIntegrity functionality."""

    def test_execution_trace_integrity_imports(self):
        """Test execution_trace_integrity module imports."""
        from agentic_core import execution_trace_integrity
        assert execution_trace_integrity is not None

    def test_execution_trace_integrity_class(self):
        """Test ExecutionTraceIntegrity class exists."""
        from agentic_core import ExecutionTraceIntegrity
        assert ExecutionTraceIntegrity is not None

    def test_execution_trace_integrity_callable(self):
        """Test execution_trace_integrity functions are callable."""
        from agentic_core import validate_execution_trace_integrity
        assert callable(validate_execution_trace_integrity)
