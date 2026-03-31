"""Test ADG accelerator wiring functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.adg.accelerators.orchestrator import (
    run_fast_test,
    run_hardening_p0,
    run_hardening_p1,
    run_incremental_update,
    run_testing,
)


@pytest.mark.unit
class TestAcceleratorWiring:
    """Test ADG accelerator wiring functionality."""

    def test_run_testing_accelerator(self):
        """Test that run_testing invokes the correct subprocess command."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_testing(["--help"])
            assert result == 0
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert "tools.adg_test_accelerator" in cmd

    def test_run_hardening_p0_with_layer(self):
        """Test P0 hardening with layer parameter."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_hardening_p0(layer="L3", dim="evidence", apply=False)
            assert result == 0
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert "tools/p0_batch_wirer.py" in cmd
            assert "--layer" in cmd
            assert "L3" in cmd

    def test_run_hardening_p0_with_apply(self):
        """Test P0 hardening with apply flag."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_hardening_p0(layer="L0", dim="governance", apply=True)
            assert result == 0
            cmd = mock_run.call_args[0][0]
            assert "--apply" in cmd

    def test_run_hardening_p1(self):
        """Test P1 hardening accelerator invocation."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_hardening_p1(apply=False)
            assert result == 0
            cmd = mock_run.call_args[0][0]
            assert "tools/p1_batch_wire.py" in cmd

    def test_run_incremental_update(self):
        """Test incremental update accelerator."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_incremental_update(["file1.py", "file2.py"])
            assert result == 0
            cmd = mock_run.call_args[0][0]
            assert "tools/adg_incremental_update.py" in cmd
            assert "file1.py" in cmd

    def test_run_fast_test(self):
        """Test fast test accelerator."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_fast_test(adg=True, dry_run=True)
            assert result == 0
            cmd = mock_run.call_args[0][0]
            assert "tools/fast_test.py" in cmd
            assert "--adg" in cmd
            assert "--dry-run" in cmd

    def test_run_hardening_p0_returns_error_code(self):
        """Test that P0 hardening returns error code on failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = run_hardening_p0(layer="L3", dim="trace", apply=False)
            assert result == 1


class TestAcceleratorConstants:
    """Test accelerator constants and configuration."""

    def test_dimension_config_structure(self):
        """Test that DIMENSION_CONFIG has required dimensions."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG

        required_dims = ["evidence", "governance", "trace", "runtime"]
        for dim in required_dims:
            assert dim in DIMENSION_CONFIG
            config = DIMENSION_CONFIG[dim]
            assert "check_edges" in config
            assert "emit_func" in config
            assert "import_line" in config
            assert "call_lines" in config

    def test_layer_dirs_mapping(self):
        """Test LAYER_DIRS maps all layers."""
        from tools.p0_batch_wirer import LAYER_DIRS, LAYER_SEGMENTS

        layers = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
        for layer in layers:
            assert layer in LAYER_DIRS
            assert layer in LAYER_SEGMENTS
            assert LAYER_DIRS[layer].startswith("agentic_core/")

    def test_p1_symbols_defined(self):
        """Test P1_SYMBOLS contains required orchestration symbols."""
        from tools.p1_batch_wire import P1_SYMBOLS

        required = [
            "_emit_routes_to_agent",
            "_emit_dispatches_execution_plan",
            "_emit_validates_agent_capability",
            "_emit_checks_agent_registry",
        ]
        for sym in required:
            assert sym in P1_SYMBOLS


class TestAcceleratorProxies:
    """Test accelerator proxy imports."""

    def test_testing_proxy_exports(self):
        """Test testing accelerator proxy exports required symbols."""
        from tools.adg.accelerators.testing import adg_test_accelerator

        assert hasattr(adg_test_accelerator, "ADGIndex")
        assert hasattr(adg_test_accelerator, "main")

    def test_test_selector_proxy_exports(self):
        """Test test selector proxy exports required symbols."""
        from tools.adg.accelerators.testing import adg_test_selector

        assert hasattr(adg_test_selector, "ADGTestSelector")
        assert hasattr(adg_test_selector, "TestImpactAnalyzer")
        assert hasattr(adg_test_selector, "select_tests_for_changes")

    def test_p0_proxy_exports(self):
        """Test P0 batch wirer proxy exports required symbols."""
        from tools.adg.accelerators.hardening import p0_batch_wirer

        assert hasattr(p0_batch_wirer, "DIMENSION_CONFIG")
        assert hasattr(p0_batch_wirer, "main")

    def test_p1_proxy_exports(self):
        """Test P1 batch wire proxy exports required symbols."""
        from tools.adg.accelerators.hardening import p1_batch_wire

        assert hasattr(p1_batch_wire, "P1_SYMBOLS")
        assert hasattr(p1_batch_wire, "should_process_file")
        assert hasattr(p1_batch_wire, "main")
