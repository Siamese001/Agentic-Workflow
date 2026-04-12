"""Test ForceAnnexationUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestForceAnnexationUtilAdg:
    """Test ForceAnnexationUtilAdg functionality."""

    def test_force_annexation_util_adg_imports(self):
        """Test force_annexation_util_adg module imports."""
        from agentic_core import force_annexation_util_adg

        assert force_annexation_util_adg is not None

    def test_force_annexation_util_adg_class(self):
        """Test ForceAnnexationUtilAdg class exists."""
        from agentic_core import ForceAnnexationUtilAdg

        assert ForceAnnexationUtilAdg is not None

    def test_force_annexation_util_adg_callable(self):
        """Test force_annexation_util_adg functions are callable."""
        from agentic_core import validate_force_annexation_util_adg

        assert callable(validate_force_annexation_util_adg)
