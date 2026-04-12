"""Test ComplexityVisitorUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestComplexityVisitorUtil:
    """Test ComplexityVisitorUtil functionality."""

    def test_complexity_visitor_util_imports(self):
        """Test complexity_visitor_util module imports."""
        from agentic_core import complexity_visitor_util

        assert complexity_visitor_util is not None

    def test_complexity_visitor_util_class(self):
        """Test ComplexityVisitorUtil class exists."""
        from agentic_core import ComplexityVisitorUtil

        assert ComplexityVisitorUtil is not None

    def test_complexity_visitor_util_callable(self):
        """Test complexity_visitor_util functions are callable."""
        from agentic_core import validate_complexity_visitor_util

        assert callable(validate_complexity_visitor_util)
