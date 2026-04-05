"""Test HardeningRigorous functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHardeningRigorous:
    """Test HardeningRigorous functionality."""

    def test_hardening_rigorous_imports(self):
        """Test hardening rigorous module imports."""
        from ops_scripts.ci import hardening_rigorous
        assert hardening_rigorous is not None

    def test_hardening_rigorous_checker(self):
        """Test hardening rigorous checker exists."""
        from ops_scripts.ci.hardening_rigorous import RigorousHardeningChecker
        assert RigorousHardeningChecker is not None

    def test_hardening_rigorous_validate(self):
        """Test hardening rigorous validate function."""
        from ops_scripts.ci.hardening_rigorous import validate_rigorous_hardening
        assert callable(validate_rigorous_hardening)
