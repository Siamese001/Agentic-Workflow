"""Test AddCoverageUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAddCoverageUtil:
    """Test AddCoverageUtil functionality."""

    def test_add_coverage_util_imports(self):
        """Test add_coverage_util module imports."""
        from agentic_core import add_coverage_util

        assert add_coverage_util is not None

    def test_add_coverage_util_class(self):
        """Test AddCoverageUtil class exists."""
        from agentic_core import AddCoverageUtil

        assert AddCoverageUtil is not None

    def test_add_coverage_util_callable(self):
        """Test add_coverage_util functions are callable."""
        from agentic_core import validate_add_coverage_util

        assert callable(validate_add_coverage_util)
