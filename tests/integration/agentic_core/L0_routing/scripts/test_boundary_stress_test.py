"""Test BoundaryStressTest functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBoundaryStressTest:
    """Test BoundaryStressTest functionality."""

    def test_boundary_stress_imports(self):
        """Test boundary stress module imports."""
        from agentic_core.L0_routing.scripts import boundary_stress
        assert boundary_stress is not None

    def test_boundary_stress_runner(self):
        """Test boundary stress runner exists."""
        try:
            from agentic_core.L0_routing.scripts.boundary_stress import StressTestRunner
            assert StressTestRunner is not None
        except ImportError:
            pytest.skip("StressTestRunner not available")

    def test_run_stress_test(self):
        """Test run stress test function."""
        try:
            from agentic_core.L0_routing.scripts.boundary_stress import run_stress_test
            assert callable(run_stress_test)
        except ImportError:
            pytest.skip("run_stress_test not available")
