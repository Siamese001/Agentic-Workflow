"""Test ADG accelerator medium/low priority functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgAcceleratorMediumLow:
    """Test ADG accelerator medium/low priority functionality."""

    def test_accelerator_readmes_exist(self):
        """Test that all accelerator subdirs have README documentation."""
        accel_dir = REPO_ROOT / "tools" / "adg" / "accelerators"

        subdirs = ["hardening", "incremental", "testing"]
        for subdir in subdirs:
            readme = accel_dir / subdir / "README.md"
            assert readme.exists(), f"Missing README in {subdir}"

    def test_incremental_update_script_exists(self):
        """Test incremental update accelerator script exists."""
        script = REPO_ROOT / "tools" / "adg_incremental_update.py"
        assert script.exists()

    def test_fast_test_script_exists(self):
        """Test fast test accelerator script exists."""
        script = REPO_ROOT / "tools" / "fast_test.py"
        assert script.exists()

    def test_p0_batch_wirer_layer_dirs_valid(self):
        """Test P0 layer directories point to valid paths."""
        from tools.p0_batch_wirer import LAYER_DIRS

        for layer, dir_path in LAYER_DIRS.items():
            full_path = REPO_ROOT / dir_path.replace("/", "\\")
            assert full_path.exists(), f"Layer {layer} path {dir_path} does not exist"

    def test_p1_excluded_dirs_is_set(self):
        """Test P1 EXCLUDED_DIRS is a set."""
        from tools.p1_batch_wire import EXCLUDED_DIRS

        assert isinstance(EXCLUDED_DIRS, set)
        assert "__pycache__" in EXCLUDED_DIRS
        assert ".git" in EXCLUDED_DIRS

    def test_p1_root_is_path(self):
        """Test P1 ROOT is a Path object."""
        from tools.p1_batch_wire import ROOT

        assert isinstance(ROOT, Path)

    def test_p0_layer_segments_has_all_layers(self):
        """Test LAYER_SEGMENTS covers all 7 layers."""
        from tools.p0_batch_wirer import LAYER_SEGMENTS

        expected = {
            "L0": "L0_ROUTING",
            "L1": "L1_COGNITION",
            "L2": "L2_EXECUTION",
            "L3": "L3_ORCHESTRATION",
            "L4": "L4_STATE",
            "L5": "L5_SAFETY",
            "L6": "L6_OBSERVABILITY",
        }

        for layer, segment in expected.items():
            assert LAYER_SEGMENTS.get(layer) == segment

    def test_p0_dimension_config_runtime_has_state_edges(self):
        """Test runtime dimension includes state edges."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG

        runtime = DIMENSION_CONFIG["runtime"]
        edges = runtime["check_edges"]

        assert "snapshots_state" in edges
        assert "writes_through" in edges
