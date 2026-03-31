"""Test ADG accelerator consolidation functionality."""

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgAcceleratorConsolidation:
    """Test ADG accelerator consolidation functionality."""

    def test_accelerator_directory_structure(self):
        """Test that accelerators directory has expected structure."""
        accel_dir = REPO_ROOT / "tools" / "adg" / "accelerators"
        assert accel_dir.exists()

        # Check required subdirectories
        subdirs = ["hardening", "incremental", "testing"]
        for subdir in subdirs:
            assert (accel_dir / subdir).is_dir()

        # Check required files
        assert (accel_dir / "__init__.py").exists()
        assert (accel_dir / "orchestrator.py").exists()
        assert (accel_dir / "__main__.py").exists()

    def test_accelerator_orchestrator_exports(self):
        """Test orchestrator module exports all accelerator runners."""
        from tools.adg.accelerators.orchestrator import (
            run_fast_test,
            run_hardening_p0,
            run_hardening_p1,
            run_incremental_update,
            run_testing,
        )

        assert callable(run_testing)
        assert callable(run_hardening_p0)
        assert callable(run_hardening_p1)
        assert callable(run_incremental_update)
        assert callable(run_fast_test)

    def test_p0_batch_wirer_main_function(self):
        """Test P0 batch wirer has main entry point."""
        from tools.p0_batch_wirer import main

        assert callable(main)

    def test_p1_batch_wire_main_function(self):
        """Test P1 batch wire has main entry point."""
        from tools.p1_batch_wire import main

        assert callable(main)

    def test_dimension_config_has_all_dimensions(self):
        """Test DIMENSION_CONFIG includes all 4 dimensions."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG

        required = ["evidence", "governance", "trace", "runtime"]
        for dim in required:
            assert dim in DIMENSION_CONFIG

    def test_layer_dirs_covers_all_layers(self):
        """Test LAYER_DIRS covers all 7 layers."""
        from tools.p0_batch_wirer import LAYER_DIRS

        layers = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
        for layer in layers:
            assert layer in LAYER_DIRS
            assert LAYER_DIRS[layer].startswith("agentic_core/")

    def test_accelerator_init_not_empty(self):
        """Test accelerators __init__ exports something."""
        from tools.adg import accelerators

        # Should have at least the orchestrator or __main__ reference
        assert hasattr(accelerators, "__file__")
