"""Test VerifyAgentStatusUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVerifyAgentStatusUtil:
    """Test VerifyAgentStatusUtil functionality."""

    def test_verify_agent_status_util_imports(self):
        """Test verify_agent_status_util module imports."""
        from agentic_core import verify_agent_status_util
        assert verify_agent_status_util is not None

    def test_verify_agent_status_util_class(self):
        """Test VerifyAgentStatusUtil class exists."""
        from agentic_core import VerifyAgentStatusUtil
        assert VerifyAgentStatusUtil is not None

    def test_verify_agent_status_util_callable(self):
        """Test verify_agent_status_util functions are callable."""
        from agentic_core import validate_verify_agent_status_util
        assert callable(validate_verify_agent_status_util)
