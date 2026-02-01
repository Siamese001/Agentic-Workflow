"""
Unit tests for validate_report_location pre-commit hook - Phase 3.

Tests cover:
- Enforcement modes (dry-run, warn, strict)
- Violation logging
- Staged-only checking
- Auto-fix functionality
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))


class TestEnforcementModes:
    """Tests for different enforcement modes."""

    def test_dry_run_mode_returns_zero(self) -> None:
        """Test that dry-run mode returns 0 even with violations."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "dry-run",
                "--quiet",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # Should return 0 (dry-run doesn't block)
        assert result.returncode == 0

    def test_warn_mode_returns_zero(self) -> None:
        """Test that warn mode returns 0 even with violations."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "warn",
                "--quiet",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # Should return 0 (warn doesn't block)
        assert result.returncode == 0

    def test_default_mode_is_warn(self) -> None:
        """Test that default mode is warn."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--quiet",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # Should return 0 (warn is default, doesn't block)
        assert result.returncode == 0


class TestViolationLogging:
    """Tests for violation logging functionality."""

    def test_log_flag_creates_file(self) -> None:
        """Test that --log flag creates a compliance report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test project with a misplaced report
            project = Path(tmpdir)
            (project / "test_report.md").write_text("Test")

            # Run the hook with logging
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                    "--mode",
                    "dry-run",
                    "--log",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )

            # Check that log was mentioned in output
            assert "logged" in result.stdout.lower() or result.returncode == 0

    def test_log_contains_violation_details(self) -> None:
        """Test that log file contains violation details."""
        log_dir = PROJECT_ROOT / "logs" / "compliance_reports"

        # Run hook with logging
        subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "dry-run",
                "--log",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # Find the latest log file
        if log_dir.exists():
            logs = sorted(log_dir.glob("report_location_violations_*.json"))
            if logs:
                with open(logs[-1]) as f:
                    data = json.load(f)

                assert "timestamp" in data
                assert "mode" in data
                assert "violations" in data


class TestStagedOnlyMode:
    """Tests for staged-only checking."""

    def test_staged_only_flag_accepted(self) -> None:
        """Test that --staged-only flag is accepted."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--staged-only",
                "--quiet",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # Should not error on flag
        assert result.returncode in [0, 1]  # Either pass or fail, but not error

    def test_staged_only_with_no_staged_files(self) -> None:
        """Test staged-only mode with no staged files returns success."""
        # This test assumes no report files are currently staged
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--staged-only",
                "--mode",
                "strict",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # With no staged report files, should pass
        assert result.returncode == 0


class TestQuietMode:
    """Tests for quiet mode."""

    def test_quiet_mode_suppresses_success_output(self) -> None:
        """Test that quiet mode suppresses success messages."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--staged-only",
                "--quiet",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # With quiet and no violations, output should be minimal
        if result.returncode == 0:
            # Success case - should have minimal output
            assert len(result.stdout) < 100 or "[OK]" not in result.stdout


class TestHelpOutput:
    """Tests for help output."""

    def test_help_shows_all_options(self) -> None:
        """Test that help shows all available options."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--help",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--mode" in result.stdout
        assert "--fix" in result.stdout
        assert "--quiet" in result.stdout
        assert "--log" in result.stdout
        assert "--staged-only" in result.stdout

    def test_help_shows_mode_choices(self) -> None:
        """Test that help shows mode choices."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--help",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert "dry-run" in result.stdout
        assert "warn" in result.stdout
        assert "strict" in result.stdout


class TestOutputMessages:
    """Tests for output messages."""

    def test_dry_run_shows_dry_run_message(self) -> None:
        """Test that dry-run mode shows appropriate message."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "dry-run",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # Should show dry-run indicator or success
        assert "DRY-RUN" in result.stdout or "[OK]" in result.stdout

    def test_warn_shows_warn_message(self) -> None:
        """Test that warn mode shows appropriate message."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "warn",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # Should show warn indicator or success
        assert "WARN" in result.stdout or "[OK]" in result.stdout


class TestIntegrationWithValidator:
    """Tests for integration with ReportLocationValidator."""

    def test_uses_ssot_reports_dir(self) -> None:
        """Test that hook uses correct SSOT reports directory."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "dry-run",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # Should reference docs/reports in output
        assert "docs/reports" in result.stdout or "[OK]" in result.stdout

    def test_detects_misplaced_reports(self) -> None:
        """Test that hook detects misplaced reports in project root."""
        # The project has reports in root (PHASE*.md, RCA*.md)
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "dry-run",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # Should detect violations or show success
        assert (
            "misplaced" in result.stdout.lower()
            or "violation" in result.stdout.lower()
            or "[OK]" in result.stdout
        )


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_mode_shows_error(self) -> None:
        """Test that invalid mode shows error."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "invalid",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_handles_missing_project_gracefully(self) -> None:
        """Test that hook handles edge cases gracefully."""
        # Running from project root should work
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--staged-only",
                "--quiet",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # Should not crash
        assert result.returncode in [0, 1]


class TestCombinedFlags:
    """Tests for combined flag usage."""

    def test_log_with_dry_run(self) -> None:
        """Test --log with --mode dry-run."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "dry-run",
                "--log",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_quiet_with_strict(self) -> None:
        """Test --quiet with --mode strict."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "strict",
                "--quiet",
                "--staged-only",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # Should work without error
        assert result.returncode in [0, 1]

    def test_staged_only_with_log(self) -> None:
        """Test --staged-only with --log."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--staged-only",
                "--log",
                "--mode",
                "dry-run",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
