"""Test BoundaryVerifierAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBoundaryVerifierAdg:
    """Test BoundaryVerifierAdg functionality."""

    def test_boundary_verifier_adg_imports(self):
        """Test boundary_verifier_adg module imports."""
        from agentic_core import boundary_verifier_adg

        assert boundary_verifier_adg is not None

    def test_boundary_verifier_adg_class(self):
        """Test BoundaryVerifierAdg class exists."""
        from agentic_core import BoundaryVerifierAdg

        assert BoundaryVerifierAdg is not None

    def test_boundary_verifier_adg_callable(self):
        """Test boundary_verifier_adg functions are callable."""
        from agentic_core import validate_boundary_verifier_adg

        assert callable(validate_boundary_verifier_adg)
