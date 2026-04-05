"""Test HardeningPerformance functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHardeningPerformance:
    """Test HardeningPerformance functionality."""

    def test_hardening_performance_imports(self):
        """Test hardening performance module imports."""
        from ops_scripts.ci import hardening_performance
        assert hardening_performance is not None

    def test_hardening_performance_checker(self):
        """Test hardening performance checker exists."""
        from ops_scripts.ci.hardening_performance import PerformanceHardeningChecker
        assert PerformanceHardeningChecker is not None

    def test_hardening_performance_validate(self):
        """Test hardening performance validate function."""
        from ops_scripts.ci.hardening_performance import validate_performance_hardening
        assert callable(validate_performance_hardening)
