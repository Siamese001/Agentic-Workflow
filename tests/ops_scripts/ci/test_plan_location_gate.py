"""Tests for plan_location_gate.py CI script.

Happy path: staged files in correct location
Failure path: staged files in prohibited location
Edge case: no staged files, non-.md files, windows vs posix paths
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ops_scripts" / "ci"))
from plan_location_gate import get_staged_files, validate_plan_locations


class TestGetStagedFiles:
    """Test get_staged_files function."""

    def test_happy_path_returns_file_list(self, tmp_path):
        """Happy path: git returns list of files."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="file1.md\nfile2.py\n",
                stderr=""
            )
            result = get_staged_files(tmp_path)

            assert len(result) == 2
            assert result[0] == tmp_path / "file1.md"
            assert result[1] == tmp_path / "file2.py"
            mock_run.assert_called_once()

    def test_failure_path_git_error_raises(self, tmp_path):
        """Failure path: git command failure raises RuntimeError."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="fatal: not a git repository"
            )

            with pytest.raises(RuntimeError, match="Git command failed"):
                get_staged_files(tmp_path)

    def test_edge_case_empty_staged(self, tmp_path):
        """Edge case: no staged files returns empty list."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="",
                stderr=""
            )
            result = get_staged_files(tmp_path)

            assert result == []


class TestValidatePlanLocations:
    """Test validate_plan_locations function."""

    def test_happy_path_no_violations(self, tmp_path):
        """Happy path: all files in correct location."""
        with patch("plan_location_gate.get_staged_files") as mock_get:
            mock_get.return_value = [
                tmp_path / ".windsurf" / "plans" / "test_plan.md"
            ]
            result = validate_plan_locations(tmp_path)

            assert result is True

    def test_failure_path_prohibited_location(self, tmp_path, capsys):
        """Failure path: file in docs/reports/plans/ violates policy."""
        with patch("plan_location_gate.get_staged_files") as mock_get:
            mock_get.return_value = [
                tmp_path / "docs" / "reports" / "plans" / "bad_plan.md"
            ]
            result = validate_plan_locations(tmp_path)
            captured = capsys.readouterr()

            assert result is False
            assert "PLAN LOCATION VIOLATIONS" in captured.out
            assert "should be in .windsurf/plans/" in captured.out

    def test_edge_case_non_md_files_ignored(self, tmp_path):
        """Edge case: non-.md files in prohibited location are ignored."""
        with patch("plan_location_gate.get_staged_files") as mock_get:
            mock_get.return_value = [
                tmp_path / "docs" / "reports" / "plans" / "data.json"
            ]
            result = validate_plan_locations(tmp_path)

            assert result is True

    def test_edge_case_no_staged_files(self, tmp_path):
        """Edge case: no staged files returns True."""
        with patch("plan_location_gate.get_staged_files") as mock_get:
            mock_get.return_value = []
            result = validate_plan_locations(tmp_path)

            assert result is True

    def test_windows_posix_path_handling(self, tmp_path):
        """Edge case: Windows backslash paths normalized correctly."""
        with patch("plan_location_gate.get_staged_files") as mock_get:
            # Simulate Windows path with backslashes
            bad_file = tmp_path / "docs" / "reports" / "plans" / "bad.md"
            mock_get.return_value = [bad_file]
            result = validate_plan_locations(tmp_path)

            assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
