"""Test BoundaryEndToEnd functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBoundaryEndToEnd:
    """Test BoundaryEndToEnd functionality."""

    def test_boundary_e2e_imports(self):
        """Test boundary e2e module imports."""
        from agentic_core.L2_execution.enforcement import boundary_e2e

        assert boundary_e2e is not None

    def test_boundary_e2e_checker(self):
        """Test boundary e2e checker exists."""
        from agentic_core.L2_execution.enforcement.boundary_e2e import BoundaryE2EChecker

        assert BoundaryE2EChecker is not None

    def test_boundary_e2e_validate(self):
        """Test boundary e2e validate function."""
        from agentic_core.L2_execution.enforcement.boundary_e2e import validate_boundary_e2e

        assert callable(validate_boundary_e2e)
