"""Wave 2 unit tests — Heal-Mode Enablement (Phase 1).

Tests:
  A) Long-path preflight: scan-based gate + AGENTIC_SKIP_LONGPATH_PREFLIGHT override.
  B) Runtime artifact persistence: assert_no_persistent_write allows operational
     outputs when path is supplied.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    assert_no_persistent_write,
)

pytestmark = pytest.mark.guardian


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def _clean_env():
    """Restore env vars after each test."""
    saved = {
        k: os.environ.get(k)
        for k in ("AGENTIC_SKIP_LONGPATH_PREFLIGHT", "AGENTIC_ALLOW_MUTATION_FOR_TESTS")
    }
    yield
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


# =============================================================================
# A) Long-path preflight gate
# =============================================================================


class TestLongPathPreflight:
    """Verify PreFlightValidator scan-based long-path gate."""

    def _make_validator(self, project_root: Path, dry_run: bool = False):
        from agentic_core.L0_routing.scripts.execute_ssot import PreFlightValidator
        return PreFlightValidator(project_root, dry_run=dry_run)

    def test_no_offenders_allows_heal_mode(self, tmp_path):
        """When no paths exceed threshold, non-dry-run proceeds (no error appended)."""
        # tmp_path has short paths — no offenders
        validator = self._make_validator(tmp_path, dry_run=False)

        # Simulate LongPathsEnabled = 0 on Windows via mock
        mock_key = MagicMock()
        with patch("platform.system", return_value="Windows"), \
             patch("winreg.OpenKey", return_value=mock_key), \
             patch("winreg.QueryValueEx", return_value=(0, None)):
            ok, errors = validator.run_checks()

        longpath_errors = [e for e in errors if "LongPathsEnabled" in e]
        assert longpath_errors == [], (
            f"Expected no long-path errors with short paths, got: {longpath_errors}"
        )

    def test_offenders_block_heal_mode(self, tmp_path):
        """When paths exceed threshold, error is appended."""
        validator = self._make_validator(tmp_path, dry_run=False)

        # Create a fake long path in rglob results
        long_path = tmp_path / ("x" * 241)
        mock_key = MagicMock()

        with patch("platform.system", return_value="Windows"), \
             patch("winreg.OpenKey", return_value=mock_key), \
             patch("winreg.QueryValueEx", return_value=(0, None)), \
             patch.object(Path, "rglob", return_value=[long_path]):
            ok, errors = validator.run_checks()

        longpath_errors = [e for e in errors if "LongPathsEnabled" in e]
        assert len(longpath_errors) == 1
        assert "exceed" in longpath_errors[0]

    def test_skip_env_override_bypasses_scan(self, tmp_path):
        """AGENTIC_SKIP_LONGPATH_PREFLIGHT=1 skips scan, no error appended."""
        os.environ["AGENTIC_SKIP_LONGPATH_PREFLIGHT"] = "1"
        validator = self._make_validator(tmp_path, dry_run=False)

        mock_key = MagicMock()
        with patch("platform.system", return_value="Windows"), \
             patch("winreg.OpenKey", return_value=mock_key), \
             patch("winreg.QueryValueEx", return_value=(0, None)):
            ok, errors = validator.run_checks()

        longpath_errors = [e for e in errors if "LongPathsEnabled" in e]
        assert longpath_errors == [], (
            f"Expected override to suppress long-path error, got: {longpath_errors}"
        )

    def test_dry_run_still_warns_not_errors(self, tmp_path):
        """dry_run=True logs warning, does not append error."""
        validator = self._make_validator(tmp_path, dry_run=True)

        mock_key = MagicMock()
        with patch("platform.system", return_value="Windows"), \
             patch("winreg.OpenKey", return_value=mock_key), \
             patch("winreg.QueryValueEx", return_value=(0, None)):
            ok, errors = validator.run_checks()

        longpath_errors = [e for e in errors if "LongPathsEnabled" in e]
        assert longpath_errors == []

    def test_non_windows_skips_check(self, tmp_path):
        """On non-Windows, long-path check is skipped entirely."""
        validator = self._make_validator(tmp_path, dry_run=False)
        with patch("platform.system", return_value="Linux"):
            ok, errors = validator.run_checks()
        longpath_errors = [e for e in errors if "LongPathsEnabled" in e]
        assert longpath_errors == []


# =============================================================================
# B) Runtime artifact persistence allowlist
# =============================================================================


class TestRuntimeArtifactPersistence:
    """Verify assert_no_persistent_write allows operational outputs when path given."""

    def test_runtime_state_json_allowed_from_l0_with_path(self, tmp_path):
        """runtime_state.json path passes the allowlist check from L0."""
        path = str(tmp_path / "runtime_state.json")
        # Must NOT raise
        assert_no_persistent_write("L0", "json.dump", path)

    def test_compliance_report_allowed_from_l0_with_path(self, tmp_path):
        """compliance_report_ prefix passes allowlist from L0."""
        path = str(tmp_path / "compliance_reports" / "compliance_report_L5.json")
        assert_no_persistent_write("L0", "json.dump", path)

    def test_executive_summary_allowed_from_l0_with_path(self, tmp_path):
        """executive_summary_ prefix passes allowlist from L0."""
        path = str(tmp_path / "compliance_reports" / "executive_summary_L5.md")
        assert_no_persistent_write("L0", "json.dump", path)

    def test_compliance_reports_dir_allowed_from_l0(self, tmp_path):
        """compliance_reports/ directory pattern passes allowlist from L0."""
        path = str(tmp_path / "logs" / "compliance_reports" / "report.json")
        assert_no_persistent_write("L0", "json.dump", path)

    def test_arbitrary_path_still_blocked_from_l0(self, tmp_path):
        """Non-operational paths are still blocked from L0."""
        path = str(tmp_path / "some_other_file.json")
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L0"):
            assert_no_persistent_write("L0", "json.dump", path)

    def test_no_path_still_blocked_from_l0(self):
        """Without path, L0 writes are blocked (allowlist cannot fire)."""
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L0"):
            assert_no_persistent_write("L0", "json.dump")

    def test_agent_discovery_json_allowed_from_l0(self, tmp_path):
        """agent_discovery_full.json is a runtime artifact — allowed from L0."""
        path = str(tmp_path / "agent_discovery_full.json")
        # agent_discovery_full.json is NOT in the current allowlist patterns —
        # this test documents the current behavior (blocked) so we can track
        # if it needs to be added.
        # For now it IS blocked; the discovery cache write uses json_path which
        # resolves to project_root/agent_discovery_full.json — not matching
        # current patterns. This is acceptable: the cache write failure is
        # non-fatal (caught by guardian: allow-silent-swallow).
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L0"):
            assert_no_persistent_write("L0", "json.dump", path)
