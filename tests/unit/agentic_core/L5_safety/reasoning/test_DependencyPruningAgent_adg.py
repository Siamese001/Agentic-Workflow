"""Test DependencypruningagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDependencypruningagentAdg:
    """Test DependencypruningagentAdg functionality."""

    def test_DependencyPruningAgent_adg_imports(self):
        """Test DependencyPruningAgent_adg module imports."""
        from agentic_core import DependencyPruningAgent_adg

        assert DependencyPruningAgent_adg is not None

    def test_DependencyPruningAgent_adg_class(self):
        """Test DependencypruningagentAdg class exists."""
        from agentic_core import DependencypruningagentAdg

        assert DependencypruningagentAdg is not None

    def test_DependencyPruningAgent_adg_callable(self):
        """Test DependencyPruningAgent_adg functions are callable."""
        from agentic_core import validate_DependencyPruningAgent_adg

        assert callable(validate_DependencyPruningAgent_adg)
