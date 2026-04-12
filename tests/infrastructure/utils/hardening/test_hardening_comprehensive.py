"""Test HardeningComprehensive functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHardeningComprehensive:
    """Test HardeningComprehensive functionality."""

    def test_hardening_comprehensive_imports(self):
        """Test hardening comprehensive module imports."""
        from ops_scripts.ci import hardening_comprehensive

        assert hardening_comprehensive is not None

    def test_hardening_comprehensive_checker(self):
        """Test hardening comprehensive checker exists."""
        from ops_scripts.ci.hardening_comprehensive import ComprehensiveHardeningChecker

        assert ComprehensiveHardeningChecker is not None

    def test_hardening_comprehensive_validate(self):
        """Test hardening comprehensive validate function."""
        from ops_scripts.ci.hardening_comprehensive import validate_comprehensive_hardening

        assert callable(validate_comprehensive_hardening)
