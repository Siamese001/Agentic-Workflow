"""Test HierarchyAgentDepthViolation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHierarchyAgentDepthViolation:
    """Test HierarchyAgentDepthViolation functionality."""

    def test_hierarchy_agent_depth_violation_imports(self):
        """Test hierarchy_agent_depth_violation module imports."""
        from agentic_core import hierarchy_agent_depth_violation
        assert hierarchy_agent_depth_violation is not None

    def test_hierarchy_agent_depth_violation_class(self):
        """Test HierarchyAgentDepthViolation class exists."""
        from agentic_core import HierarchyAgentDepthViolation
        assert HierarchyAgentDepthViolation is not None

    def test_hierarchy_agent_depth_violation_callable(self):
        """Test hierarchy_agent_depth_violation functions are callable."""
        from agentic_core import validate_hierarchy_agent_depth_violation
        assert callable(validate_hierarchy_agent_depth_violation)
