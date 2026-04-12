"""Test CoverageMapper functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCoverageMapper:
    """Test CoverageMapper functionality."""

    def test_coverage_mapper_imports(self):
        """Test coverage_mapper module imports."""
        from agentic_core import coverage_mapper

        assert coverage_mapper is not None

    def test_coverage_mapper_class(self):
        """Test CoverageMapper class exists."""
        from agentic_core import CoverageMapper

        assert CoverageMapper is not None

    def test_coverage_mapper_callable(self):
        """Test coverage_mapper functions are callable."""
        from agentic_core import validate_coverage_mapper

        assert callable(validate_coverage_mapper)
