"""Test CI gap enforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCiGapEnforcement:
    """Test CI gap enforcement functionality."""

    def test_ci_gap_enforcement_imports(self):
        """Test CI gap enforcement module imports."""
        from ops_scripts.ci import _adg_ci_gates
        assert _adg_ci_gates is not None

    def test_ci_gap_check_function(self):
        """Test CI gap check function exists."""
        from ops_scripts.ci._adg_ci_gates import check_gaps
        assert callable(check_gaps)

    def test_ci_gap_enforcement_workflow(self):
        """Test CI gap enforcement workflow exists."""
        from ops_scripts.ci._adg_ci_gates import enforce_gap_policy
        assert callable(enforce_gap_policy)
