"""Test RunNamingLawCheckUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunNamingLawCheckUtilAdg:
    """Test RunNamingLawCheckUtilAdg functionality."""

    def test_run_naming_law_check_util_adg_imports(self):
        """Test run_naming_law_check_util_adg module imports."""
        from agentic_core import run_naming_law_check_util_adg

        assert run_naming_law_check_util_adg is not None

    def test_run_naming_law_check_util_adg_class(self):
        """Test RunNamingLawCheckUtilAdg class exists."""
        from agentic_core import RunNamingLawCheckUtilAdg

        assert RunNamingLawCheckUtilAdg is not None

    def test_run_naming_law_check_util_adg_callable(self):
        """Test run_naming_law_check_util_adg functions are callable."""
        from agentic_core import validate_run_naming_law_check_util_adg

        assert callable(validate_run_naming_law_check_util_adg)
