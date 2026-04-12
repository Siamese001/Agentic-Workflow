"""Test BoundaryTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBoundaryTypesAdg:
    """Test BoundaryTypesAdg functionality."""

    def test_boundary_types_adg_imports(self):
        """Test boundary_types_adg module imports."""
        from agentic_core import boundary_types_adg

        assert boundary_types_adg is not None

    def test_boundary_types_adg_class(self):
        """Test BoundaryTypesAdg class exists."""
        from agentic_core import BoundaryTypesAdg

        assert BoundaryTypesAdg is not None

    def test_boundary_types_adg_callable(self):
        """Test boundary_types_adg functions are callable."""
        from agentic_core import validate_boundary_types_adg

        assert callable(validate_boundary_types_adg)
