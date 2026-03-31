"""Test ADG hardening comprehensive functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgHardeningComprehensive:
    """Test ADG hardening comprehensive functionality."""

    def test_hardening_layer_coverage(self):
        """Test hardening covers all layers."""
        from tools.p0_batch_wirer import LAYER_DIRS
        layers = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
        for layer in layers:
            assert layer in LAYER_DIRS

    def test_hardening_dimensions_complete(self):
        """Test hardening dimensions are complete."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG
        dims = ["evidence", "governance", "trace", "runtime"]
        for dim in dims:
            assert dim in DIMENSION_CONFIG

    def test_hardening_orchestrator_exists(self):
        """Test hardening orchestrator exists."""
        from tools.adg.accelerators.orchestrator import run_hardening_p0
        assert callable(run_hardening_p0)
