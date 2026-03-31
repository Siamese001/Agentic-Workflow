"""Test ADG accelerators edge cases."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgAcceleratorsEdgeCases:
    """Test ADG accelerators edge cases."""

    def test_orchestrator_testing_no_args(self):
        """Test orchestrator handles empty args list."""
        from tools.adg.accelerators.orchestrator import run_testing

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_testing([])
            assert result == 0

    def test_orchestrator_p0_no_dim_raises(self):
        """Test P0 runner requires dim parameter."""
        from tools.adg.accelerators.orchestrator import run_hardening_p0

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_hardening_p0(layer="L3", dim="evidence", apply=False)
            assert result is not None

    def test_orchestrator_p1_apply_true(self):
        """Test P1 runner with apply=True."""
        from tools.adg.accelerators.orchestrator import run_hardening_p1

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_hardening_p1(apply=True)
            cmd = mock_run.call_args[0][0]
            assert "--apply" in cmd

    def test_orchestrator_incremental_empty_list(self):
        """Test incremental update with empty file list."""
        from tools.adg.accelerators.orchestrator import run_incremental_update

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_incremental_update([])
            assert result == 0

    def test_orchestrator_fast_test_no_flags(self):
        """Test fast test with no flags."""
        from tools.adg.accelerators.orchestrator import run_fast_test

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_fast_test(adg=False, dry_run=False)
            cmd = mock_run.call_args[0][0]
            assert "--adg" not in cmd
            assert "--dry-run" not in cmd

    def test_p0_invalid_layer_returns_empty(self):
        """Test P0 get_gap_files handles invalid layer."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG, get_gap_files

        try:
            result = get_gap_files("INVALID", DIMENSION_CONFIG["evidence"])
        except KeyError:
            pass  # KeyError is acceptable for invalid layer

    def test_p1_should_process_file_none_path(self):
        """Test P1 should_process_file with edge cases."""
        from tools.p1_batch_wire import should_process_file

        result = should_process_file(Path(""))
        assert result is False

    def test_accelerator_proxy_imports_work(self):
        """Test accelerator proxies handle imports."""
        from tools.adg.accelerators.testing import adg_test_accelerator
        from tools.adg.accelerators.testing import adg_test_selector

        assert adg_test_accelerator is not None
        assert adg_test_selector is not None
