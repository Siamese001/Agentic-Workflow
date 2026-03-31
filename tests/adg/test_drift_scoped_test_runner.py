"""Test drift scoped test runner functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDriftScopedTestRunner:
    """Test drift scoped test runner functionality."""

    def test_drift_scoped_runner_imports(self):
        """Test drift scoped runner module imports."""
        from tools.adg import drift_lifecycle
        assert drift_lifecycle is not None

    def test_scoped_runner_class(self):
        """Test scoped runner class exists."""
        from tools.adg.drift_lifecycle import ScopedTestRunner
        assert ScopedTestRunner is not None

    def test_scoped_runner_run_function(self):
        """Test scoped runner run function."""
        from tools.adg.drift_lifecycle import run_scoped_tests
        assert callable(run_scoped_tests)
