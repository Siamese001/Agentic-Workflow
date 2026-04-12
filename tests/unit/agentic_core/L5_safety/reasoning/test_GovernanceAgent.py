"""Test Governanceagent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGovernanceagent:
    """Test Governanceagent functionality."""

    def test_GovernanceAgent_imports(self):
        """Test GovernanceAgent module imports."""
        from agentic_core import GovernanceAgent

        assert GovernanceAgent is not None

    def test_GovernanceAgent_class(self):
        """Test Governanceagent class exists."""
        from agentic_core import Governanceagent

        assert Governanceagent is not None

    def test_GovernanceAgent_callable(self):
        """Test GovernanceAgent functions are callable."""
        from agentic_core import validate_GovernanceAgent

        assert callable(validate_GovernanceAgent)
