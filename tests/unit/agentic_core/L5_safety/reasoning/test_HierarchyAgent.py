"""Test Hierarchyagent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHierarchyagent:
    """Test Hierarchyagent functionality."""

    def test_HierarchyAgent_imports(self):
        """Test HierarchyAgent module imports."""
        from agentic_core import HierarchyAgent

        assert HierarchyAgent is not None

    def test_HierarchyAgent_class(self):
        """Test Hierarchyagent class exists."""
        from agentic_core import Hierarchyagent

        assert Hierarchyagent is not None

    def test_HierarchyAgent_callable(self):
        """Test HierarchyAgent functions are callable."""
        from agentic_core import validate_HierarchyAgent

        assert callable(validate_HierarchyAgent)
