"""Test NewDependenciesSmoke functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNewDependenciesSmoke:
    """Test NewDependenciesSmoke functionality."""

    def test_new_dependencies_smoke_imports(self):
        """Test new_dependencies_smoke module imports."""
        from agentic_core import new_dependencies_smoke

        assert new_dependencies_smoke is not None

    def test_new_dependencies_smoke_class(self):
        """Test NewDependenciesSmoke class exists."""
        from agentic_core import NewDependenciesSmoke

        assert NewDependenciesSmoke is not None

    def test_new_dependencies_smoke_callable(self):
        """Test new_dependencies_smoke functions are callable."""
        from agentic_core import validate_new_dependencies_smoke

        assert callable(validate_new_dependencies_smoke)
