"""Test ExecutionGatewayBugfixes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecutionGatewayBugfixes:
    """Test ExecutionGatewayBugfixes functionality."""

    def test_execution_gateway_bugfixes_imports(self):
        """Test execution_gateway_bugfixes module imports."""
        from agentic_core import execution_gateway_bugfixes
        assert execution_gateway_bugfixes is not None

    def test_execution_gateway_bugfixes_class(self):
        """Test ExecutionGatewayBugfixes class exists."""
        from agentic_core import ExecutionGatewayBugfixes
        assert ExecutionGatewayBugfixes is not None

    def test_execution_gateway_bugfixes_callable(self):
        """Test execution_gateway_bugfixes functions are callable."""
        from agentic_core import validate_execution_gateway_bugfixes
        assert callable(validate_execution_gateway_bugfixes)
