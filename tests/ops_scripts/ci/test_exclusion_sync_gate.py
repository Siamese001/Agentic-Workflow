#!/usr/bin/env python3
"""Tests for exclusion_sync_gate.py.

Tests cover:
- Loading YAML exclusions
- Loading SSOT exclusions
- Loading .gitignore entries
- Sync checking between all three sources
- Main function CLI interface
- Edge cases and error handling
"""
from __future__ import annotations

# Import the module under test
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ops_scripts" / "ci"))

import exclusion_sync_gate


class TestLoadYamlExclusions:
    """Test loading exclusions from YAML config."""

    def test_load_yaml_exclusions_success(self, tmp_path: Path) -> None:
        """Test successful loading of YAML exclusions."""
        yaml_content = """
version: "1.0.0"

build_cache_dirs:
  - "__pycache__"
  - ".pytest_cache"

version_control_dirs:
  - ".git"

virtual_env_dirs:
  - ".venv"

coverage_dirs:
  - "htmlcov"

archive_dirs:
  - "archives"

ide_dirs:
  - ".idea"

vendor_dirs:
  - "google"

data_dirs:
  - "data"

special_dirs:
  - "_compat"
"""
        yaml_path = tmp_path / "excluded_paths.yaml"
        yaml_path.write_text(yaml_content)

        # Mock the config path calculation
        with patch.object(exclusion_sync_gate.Path, "__file__", str(yaml_path)):
            # Patch the path calculation to return our test file
            original_path = exclusion_sync_gate.Path
            def mock_path_calc(*args, **kwargs):
                if args and isinstance(args[0], str):
                    return original_path(args[0])
                return yaml_path
            with patch.object(exclusion_sync_gate, "Path", side_effect=mock_path_calc):
                dirs = exclusion_sync_gate.load_yaml_exclusions()

        assert "__pycache__" in dirs
        assert ".git" in dirs
        assert ".venv" in dirs
        assert "archives" in dirs
        assert len(dirs) == 10

    def test_load_yaml_exclusions_missing_file(self, tmp_path: Path) -> None:
        """Test error handling when config file is missing."""
        non_existent_path = tmp_path / "non_existent.yaml"

        with patch.object(exclusion_sync_gate.Path, "__new__", return_value=non_existent_path):
            with pytest.raises(SystemExit) as exc_info:
                exclusion_sync_gate.load_yaml_exclusions()
            assert exc_info.value.code == 2

    def test_load_yaml_exclusions_missing_yaml_import(self) -> None:
        """Test error handling when PyYAML is not installed."""
        with patch.dict(sys.modules, {"yaml": None}):
            with pytest.raises(SystemExit) as exc_info:
                exclusion_sync_gate.load_yaml_exclusions()
            assert exc_info.value.code == 2


class TestLoadSsotExclusions:
    """Test loading SSOT exclusions from ssot.py."""

    def test_load_ssot_exclusions_success(self) -> None:
        """Test successful loading of SSOT exclusions."""
        # Mock the import
        mock_ssot = MagicMock()
        mock_ssot.SOVEREIGN_EXCLUDED_FOLDERS = ["__pycache__", ".git", ".venv", "archives"]

        with patch.dict("sys.modules", {"agentic_core.L5_safety.config.structure_blueprint.ssot": mock_ssot}):
            dirs = exclusion_sync_gate.load_ssot_exclusions()

        assert "__pycache__" in dirs
        assert ".git" in dirs
        assert ".venv" in dirs
        assert "archives" in dirs

    def test_load_ssot_exclusions_import_error(self) -> None:
        """Test error handling when import fails."""
        with patch.dict("sys.modules", {"agentic_core.L5_safety.config.structure_blueprint.ssot": None}):
            with pytest.raises(SystemExit) as exc_info:
                exclusion_sync_gate.load_ssot_exclusions()
            assert exc_info.value.code == 2


class TestLoadGitignoreEntries:
    """Test loading directory entries from .gitignore."""

    def test_load_gitignore_entries_success(self, tmp_path: Path) -> None:
        """Test successful loading of .gitignore entries."""
        gitignore_content = """# Generated from config/excluded_paths.yaml
/__pycache__/
/.git/
/.venv/
*.pyc
*.log
"""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text(gitignore_content)

        with patch.object(exclusion_sync_gate.Path, "__new__", return_value=gitignore_path):
            entries = exclusion_sync_gate.load_gitignore_entries()

        assert "__pycache__" in entries
        assert ".git" in entries
        assert ".venv" in entries
        # File patterns should not be included
        assert "*.pyc" not in entries
        assert "*.log" not in entries

    def test_load_gitignore_entries_missing_file(self, tmp_path: Path) -> None:
        """Test error handling when .gitignore is missing."""
        non_existent_path = tmp_path / "non_existent.gitignore"

        with patch.object(exclusion_sync_gate.Path, "__new__", return_value=non_existent_path):
            with pytest.raises(SystemExit) as exc_info:
                exclusion_sync_gate.load_gitignore_entries()
            assert exc_info.value.code == 2

    def test_load_gitignore_entries_filters_patterns(self, tmp_path: Path) -> None:
        """Test that file patterns are filtered out."""
        gitignore_content = """# Comments
/__pycache__/
*.pyc
*.log
test/
"""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text(gitignore_content)

        with patch.object(exclusion_sync_gate.Path, "__new__", return_value=gitignore_path):
            entries = exclusion_sync_gate.load_gitignore_entries()

        assert "__pycache__" in entries
        assert "test" in entries
        assert "*.pyc" not in entries
        assert "*.log" not in entries


class TestMain:
    """Test main function and CLI interface."""

    def test_main_all_in_sync(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main when all sources are in sync."""
        yaml_dirs = {"__pycache__", ".git", ".venv"}
        ssot_dirs = {"__pycache__", ".git", ".venv"}
        gitignore_dirs = {"__pycache__", ".git", ".venv"}

        with patch.object(exclusion_sync_gate, "load_yaml_exclusions", return_value=yaml_dirs):
            with patch.object(exclusion_sync_gate, "load_ssot_exclusions", return_value=ssot_dirs):
                with patch.object(exclusion_sync_gate, "load_gitignore_entries", return_value=gitignore_dirs):
                    result = exclusion_sync_gate.main()
                    assert result == 0
                    captured = capsys.readouterr()
                    assert "ALL SOURCES IN SYNC" in captured.out

    def test_main_yaml_vs_ssot_mismatch(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main when YAML and ssot.py are out of sync."""
        yaml_dirs = {"__pycache__", ".git", ".venv", "extra_dir"}
        ssot_dirs = {"__pycache__", ".git", ".venv"}
        gitignore_dirs = {"__pycache__", ".git", ".venv"}

        with patch.object(exclusion_sync_gate, "load_yaml_exclusions", return_value=yaml_dirs):
            with patch.object(exclusion_sync_gate, "load_ssot_exclusions", return_value=ssot_dirs):
                with patch.object(exclusion_sync_gate, "load_gitignore_entries", return_value=gitignore_dirs):
                    result = exclusion_sync_gate.main()
                    assert result == 1
                    captured = capsys.readouterr()
                    assert "SYNC ISSUES DETECTED" in captured.out
                    assert "extra_dir" in captured.out

    def test_main_yaml_vs_gitignore_mismatch(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main when YAML and .gitignore are out of sync."""
        yaml_dirs = {"__pycache__", ".git", ".venv", "extra_dir"}
        ssot_dirs = {"__pycache__", ".git", ".venv", "extra_dir"}
        gitignore_dirs = {"__pycache__", ".git", ".venv"}

        with patch.object(exclusion_sync_gate, "load_yaml_exclusions", return_value=yaml_dirs):
            with patch.object(exclusion_sync_gate, "load_ssot_exclusions", return_value=ssot_dirs):
                with patch.object(exclusion_sync_gate, "load_gitignore_entries", return_value=gitignore_dirs):
                    result = exclusion_sync_gate.main()
                    assert result == 1
                    captured = capsys.readouterr()
                    assert "SYNC ISSUES DETECTED" in captured.out
                    assert "extra_dir" in captured.out

    def test_main_ssot_extra_entries(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main when ssot.py has extra entries (legacy/intentional)."""
        yaml_dirs = {"__pycache__", ".git", ".venv"}
        ssot_dirs = {"__pycache__", ".git", ".venv", "legacy_dir"}
        gitignore_dirs = {"__pycache__", ".git", ".venv"}

        with patch.object(exclusion_sync_gate, "load_yaml_exclusions", return_value=yaml_dirs):
            with patch.object(exclusion_sync_gate, "load_ssot_exclusions", return_value=ssot_dirs):
                with patch.object(exclusion_sync_gate, "load_gitignore_entries", return_value=gitignore_dirs):
                    result = exclusion_sync_gate.main()
                    # Should fail because YAML vs gitignore is also mismatched
                    assert result == 1
                    captured = capsys.readouterr()
                    assert "legacy/intentional" in captured.out

    def test_main_output_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that main output includes expected sections."""
        yaml_dirs = {"__pycache__", ".git"}
        ssot_dirs = {"__pycache__", ".git"}
        gitignore_dirs = {"__pycache__", ".git"}

        with patch.object(exclusion_sync_gate, "load_yaml_exclusions", return_value=yaml_dirs):
            with patch.object(exclusion_sync_gate, "load_ssot_exclusions", return_value=ssot_dirs):
                with patch.object(exclusion_sync_gate, "load_gitignore_entries", return_value=gitignore_dirs):
                    exclusion_sync_gate.main()
                    captured = capsys.readouterr()
                    assert "Exclusion Synchronization Gate" in captured.out
                    assert "YAML config:" in captured.out
                    assert "ssot.py:" in captured.out
                    assert ".gitignore:" in captured.out

    def test_main_remediation_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that remediation messages are provided."""
        yaml_dirs = {"__pycache__", ".git", ".venv", "extra_dir"}
        ssot_dirs = {"__pycache__", ".git", ".venv"}
        gitignore_dirs = {"__pycache__", ".git", ".venv"}

        with patch.object(exclusion_sync_gate, "load_yaml_exclusions", return_value=yaml_dirs):
            with patch.object(exclusion_sync_gate, "load_ssot_exclusions", return_value=ssot_dirs):
                with patch.object(exclusion_sync_gate, "load_gitignore_entries", return_value=gitignore_dirs):
                    exclusion_sync_gate.main()
                    captured = capsys.readouterr()
                    assert "REMEDIATION:" in captured.out
                    assert "SOVEREIGN_EXCLUDED_FOLDERS" in captured.out
                    assert "generate_gitignore.py" in captured.out
