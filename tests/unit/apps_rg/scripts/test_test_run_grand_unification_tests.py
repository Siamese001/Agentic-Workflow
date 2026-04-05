"""Test RunGrandUnificationTests functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunGrandUnificationTests:
    """Test RunGrandUnificationTests functionality."""

    def test_run_grand_unification_tests_imports(self):
        """Test run_grand_unification_tests module imports."""
        from agentic_core import run_grand_unification_tests
        assert run_grand_unification_tests is not None

    def test_run_grand_unification_tests_class(self):
        """Test RunGrandUnificationTests class exists."""
        from agentic_core import RunGrandUnificationTests
        assert RunGrandUnificationTests is not None

    def test_run_grand_unification_tests_callable(self):
        """Test run_grand_unification_tests functions are callable."""
        from agentic_core import validate_run_grand_unification_tests
        assert callable(validate_run_grand_unification_tests)
