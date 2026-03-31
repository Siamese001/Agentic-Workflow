"""Test AdgExceptionHardeningE2E functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgExceptionHardeningE2E:
    """Test AdgExceptionHardeningE2E functionality."""

    def test_exception_hardening_imports(self):
        """Test exception hardening module imports."""
        from tests import exception_hardening
        assert exception_hardening is not None

    def test_exception_hardening_runner(self):
        """Test exception hardening runner exists."""
        from tests.exception_hardening import E2EHardeningRunner
        assert E2EHardeningRunner is not None

    def test_run_exception_tests(self):
        """Test run exception tests function."""
        from tests.exception_hardening import run_exception_tests
        assert callable(run_exception_tests)
