"""Test RunGrandUnificationTestsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunGrandUnificationTestsAdg:
    """Test RunGrandUnificationTestsAdg functionality."""

    def test_run_grand_unification_tests_adg_imports(self):
        """Test run_grand_unification_tests_adg module imports."""
        from agentic_core import run_grand_unification_tests_adg
        assert run_grand_unification_tests_adg is not None

    def test_run_grand_unification_tests_adg_class(self):
        """Test RunGrandUnificationTestsAdg class exists."""
        from agentic_core import RunGrandUnificationTestsAdg
        assert RunGrandUnificationTestsAdg is not None

    def test_run_grand_unification_tests_adg_callable(self):
        """Test run_grand_unification_tests_adg functions are callable."""
        from agentic_core import validate_run_grand_unification_tests_adg
        assert callable(validate_run_grand_unification_tests_adg)
