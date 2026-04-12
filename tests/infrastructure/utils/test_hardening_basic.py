"""Test HardeningBasic functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHardeningBasic:
    """Test HardeningBasic functionality."""

    def test_hardening_basic_imports(self):
        """Test hardening basic module imports."""
        from ops_scripts.ci import hardening_basic

        assert hardening_basic is not None

    def test_hardening_basic_checker(self):
        """Test hardening basic checker exists."""
        from ops_scripts.ci.hardening_basic import BasicHardeningChecker

        assert BasicHardeningChecker is not None

    def test_hardening_basic_validate(self):
        """Test hardening basic validate function."""
        from ops_scripts.ci.hardening_basic import validate_basic_hardening

        assert callable(validate_basic_hardening)
