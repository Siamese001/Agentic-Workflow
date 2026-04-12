"""Test GravityVisitorUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGravityVisitorUtil:
    """Test GravityVisitorUtil functionality."""

    def test_gravity_visitor_util_imports(self):
        """Test gravity_visitor_util module imports."""
        from agentic_core import gravity_visitor_util

        assert gravity_visitor_util is not None

    def test_gravity_visitor_util_class(self):
        """Test GravityVisitorUtil class exists."""
        from agentic_core import GravityVisitorUtil

        assert GravityVisitorUtil is not None

    def test_gravity_visitor_util_callable(self):
        """Test gravity_visitor_util functions are callable."""
        from agentic_core import validate_gravity_visitor_util

        assert callable(validate_gravity_visitor_util)
