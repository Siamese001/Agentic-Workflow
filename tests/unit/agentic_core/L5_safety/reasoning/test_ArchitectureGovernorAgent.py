"""Test Architecturegovernoragent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestArchitecturegovernoragent:
    """Test Architecturegovernoragent functionality."""

    def test_ArchitectureGovernorAgent_imports(self):
        """Test ArchitectureGovernorAgent module imports."""
        from agentic_core import ArchitectureGovernorAgent

        assert ArchitectureGovernorAgent is not None

    def test_ArchitectureGovernorAgent_class(self):
        """Test Architecturegovernoragent class exists."""
        from agentic_core import Architecturegovernoragent

        assert Architecturegovernoragent is not None

    def test_ArchitectureGovernorAgent_callable(self):
        """Test ArchitectureGovernorAgent functions are callable."""
        from agentic_core import validate_ArchitectureGovernorAgent

        assert callable(validate_ArchitectureGovernorAgent)
