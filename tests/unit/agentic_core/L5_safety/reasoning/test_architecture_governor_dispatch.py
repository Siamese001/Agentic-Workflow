"""Test ArchitectureGovernorDispatch functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestArchitectureGovernorDispatch:
    """Test ArchitectureGovernorDispatch functionality."""

    def test_architecture_governor_dispatch_imports(self):
        """Test architecture_governor_dispatch module imports."""
        from agentic_core import architecture_governor_dispatch

        assert architecture_governor_dispatch is not None

    def test_architecture_governor_dispatch_class(self):
        """Test ArchitectureGovernorDispatch class exists."""
        from agentic_core import ArchitectureGovernorDispatch

        assert ArchitectureGovernorDispatch is not None

    def test_architecture_governor_dispatch_callable(self):
        """Test architecture_governor_dispatch functions are callable."""
        from agentic_core import validate_architecture_governor_dispatch

        assert callable(validate_architecture_governor_dispatch)
