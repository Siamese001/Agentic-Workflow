#!/usr/bin/env python3
"""Tests for generate_gitignore.py.

Tests cover:
- Loading exclusions from YAML config
- Generating .gitignore content
- Generating pre-commit exclude section
- Sync checking
- Edge cases and error handling
"""

from __future__ import annotations

import logging

# Import the module under test
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "tools" / "generate"))

import generate_gitignore


class TestLoadExclusions:
    """Test loading exclusions from YAML config."""

    def test_load_exclusions_success(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful loading of exclusions from YAML."""
        # Create a minimal YAML config
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

precommit_excludes:
  - "artifacts/adg_ci_lane_gate_result.json"
  - "pytestdebug.log"

file_patterns:
  - "*.pyc"
  - "*.log"
"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        logging.info("C3 write receipt: tests/unit/tools/generate/test_generate_gitignore.py write side effect recorded")
        yaml_path = config_dir / "excluded_paths.yaml"
        yaml_path.write_text(yaml_content)

        monkeypatch.setattr(generate_gitignore, "_REPO_ROOT", tmp_path)
        dirs, patterns, precommit = generate_gitignore.load_exclusions()

        assert "__pycache__" in dirs
        assert ".git" in dirs
        assert "*.pyc" in patterns
        assert "artifacts/adg_ci_lane_gate_result.json" in precommit
        assert len(precommit) == 2

    def test_load_exclusions_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error handling when config file is missing."""
        monkeypatch.setattr(generate_gitignore, "_REPO_ROOT", tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            generate_gitignore.load_exclusions()
        assert exc_info.value.code == 1

    def test_load_exclusions_missing_yaml_import(self) -> None:
        """Test error handling when PyYAML is not installed."""
        with patch.dict(sys.modules, {"yaml": None}):
            with pytest.raises(SystemExit) as exc_info:
                generate_gitignore.load_exclusions()
            assert exc_info.value.code == 1


class TestGenerateGitignoreContent:
    """Test generation of .gitignore content."""

    def test_generate_gitignore_content_basic(self) -> None:
        """Test basic .gitignore content generation."""
        dirs = {"__pycache__", ".git", ".venv"}
        patterns = {"*.pyc", "*.log"}

        content = generate_gitignore.generate_gitignore_content(dirs, patterns)

        assert "# Generated from config/excluded_paths.yaml" in content
        assert "__pycache__/" in content or "/__pycache__/" in content
        assert "*.pyc" in content
        assert "*.log" in content

    def test_generate_gitignore_content_categorization(self) -> None:
        """Test that directories are correctly categorized."""
        dirs = {"__pycache__", ".git", ".venv", "htmlcov", "archives", ".idea", "google", "data", "_compat"}
        patterns = {"*.pyc"}

        content = generate_gitignore.generate_gitignore_content(dirs, patterns)

        # Check that categories are present
        assert "Build & Cache" in content
        assert "Version Control" in content
        assert "Virtual Environments" in content

    def test_generate_gitignore_content_empty(self) -> None:
        """Test generation with empty inputs."""
        content = generate_gitignore.generate_gitignore_content(set(), set())
        assert "# Generated from config/excluded_paths.yaml" in content

    def test_file_patterns_no_directory_only_slash_on_dot_globs(self) -> None:
        """Dot-prefixed file_patterns must not become directory-only rules."""
        content = generate_gitignore.generate_gitignore_content(
            set(),
            {".coverage.*", "Thumbs.db", "*.log"},
        )
        assert ".coverage.*" in content
        assert ".coverage.*/" not in content
        assert "Thumbs.db" in content
        assert "Thumbs.db/" not in content
        assert "*.log" in content


class TestGeneratePrecommitExclude:
    """Test generation of pre-commit exclude section."""

    def test_generate_precommit_exclude_basic(self) -> None:
        """Test basic pre-commit exclude generation."""
        patterns = {
            "artifacts/adg_ci_lane_gate_result.json",
            "pytestdebug.log",
            "temp_[^/]*/.*",
        }

        content = generate_gitignore.generate_precommit_exclude(patterns)

        assert "# Generated from config/excluded_paths.yaml" in content
        assert "exclude: |" in content
        assert "(?x)^(" in content
        assert "artifacts/adg_ci_lane_gate_result.json" in content
        assert "pytestdebug.log" in content
        # Last content line must NOT end with | (line-190 strip)
        content_lines = [
            ln.rstrip()
            for ln in content.split("\n")
            if ln.strip()
            and not ln.strip().startswith("#")
            and ln.strip() not in ("exclude: |", "(?x)^(", ")")
        ]
        assert content_lines, "Expected at least one pattern line"
        assert not content_lines[-1].endswith("|"), f"Last pattern must not end with |: {content_lines[-1]!r}"

    def test_generate_precommit_exclude_sorted(self) -> None:
        """Test that patterns are sorted for consistency."""
        patterns = {"z_pattern", "a_pattern", "m_pattern"}

        content = generate_gitignore.generate_precommit_exclude(patterns)

        # Check that patterns appear in sorted order
        lines = content.split("\n")
        pattern_lines = [
            line.strip()
            for line in lines
            if line.strip()
            and not line.strip().startswith("#")
            and line.strip() not in ("exclude: |", "(?x)^(", ")")
        ]

        # Find the indices of each pattern
        indices = {}
        for pattern in patterns:
            for i, line in enumerate(pattern_lines):
                if pattern in line:
                    indices[pattern] = i
                    break

        # Verify order
        assert indices["a_pattern"] < indices["m_pattern"] < indices["z_pattern"]

    def test_generate_precommit_exclude_empty(self) -> None:
        """Test generation with empty patterns."""
        content = generate_gitignore.generate_precommit_exclude(set())
        assert "# Generated from config/excluded_paths.yaml" in content
        assert "exclude: |" in content

    def test_generate_precommit_exclude_single_pattern(self) -> None:
        """Single-pattern set: the sole pattern line must NOT end with |."""
        content = generate_gitignore.generate_precommit_exclude({"only_pattern"})
        pattern_lines = [
            ln.rstrip()
            for ln in content.split("\n")
            if ln.strip()
            and not ln.strip().startswith("#")
            and ln.strip() not in ("exclude: |", "(?x)^(", ")")
        ]
        assert len(pattern_lines) == 1
        assert not pattern_lines[0].endswith("|"), f"Single pattern must not end with |: {pattern_lines[0]!r}"
        assert "only_pattern" in pattern_lines[0]


class TestCheckSync:
    """Test .gitignore sync checking."""

    def test_check_sync_in_sync(self, tmp_path: Path) -> None:
        """Test check when .gitignore is in sync."""
        # Create a .gitignore file
        gitignore_content = """# Generated from config/excluded_paths.yaml
# Do not edit manually - run: python tools/generate_gitignore.py --write
# Last generated: 2026-04-06T00:00:00

/test_dir/
*.pyc
"""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text(gitignore_content)

        # Mock the functions to return matching content
        with patch.object(
            generate_gitignore, "load_exclusions", return_value=({"test_dir"}, {"*.pyc"}, set())
        ):
            with patch.object(generate_gitignore, "read_current_gitignore", return_value=gitignore_content):
                with patch.object(
                    generate_gitignore, "generate_gitignore_content", return_value=gitignore_content
                ):
                    result = generate_gitignore.check_sync()
                    assert result is True

    def test_check_sync_out_of_sync(self, tmp_path: Path) -> None:
        """Test check when .gitignore is out of sync."""
        gitignore_content = """# Generated from config/excluded_paths.yaml
# Do not edit manually - run: python tools/generate_gitignore.py --write
# Last generated: 2026-04-06T00:00:00

/test_dir/
*.pyc
"""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text(gitignore_content)

        # Mock to return different content
        different_content = gitignore_content + "*.log\n"

        with patch.object(
            generate_gitignore, "load_exclusions", return_value=({"test_dir"}, {"*.pyc"}, set())
        ):
            with patch.object(generate_gitignore, "read_current_gitignore", return_value=gitignore_content):
                with patch.object(
                    generate_gitignore, "generate_gitignore_content", return_value=different_content
                ):
                    result = generate_gitignore.check_sync()
                    assert result is False

    def test_check_sync_missing_gitignore(self) -> None:
        """Test check when .gitignore does not exist."""
        with patch.object(generate_gitignore, "load_exclusions", return_value=(set(), set(), set())):
            with patch.object(generate_gitignore, "generate_gitignore_content", return_value="# Generated\n"):
                with patch.object(generate_gitignore, "read_current_gitignore", return_value=None):
                    result = generate_gitignore.check_sync()
                    assert result is False

    def test_check_sync_non_generated_gitignore(self) -> None:
        """Test check when current .gitignore was not generated (else branch in line-224)."""
        hand_written = "/hand_written/\n*.pyc\n"
        generated_content = "# Generated from config/excluded_paths.yaml\n# header\n# ts\n\n/other/\n"

        with patch.object(generate_gitignore, "load_exclusions", return_value=({"other"}, set(), set())):
            with patch.object(
                generate_gitignore, "generate_gitignore_content", return_value=generated_content
            ):
                with patch.object(generate_gitignore, "read_current_gitignore", return_value=hand_written):
                    result = generate_gitignore.check_sync()
                    assert result is False


class TestWriteGitignore:
    """Test .gitignore writing."""

    def test_write_gitignore(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test writing .gitignore file."""
        content = "# Test content\n/test_dir/\n"
        monkeypatch.setattr(generate_gitignore, "_REPO_ROOT", tmp_path)
        generate_gitignore.write_gitignore(content)
        gitignore_path = tmp_path / ".gitignore"
        assert gitignore_path.exists()
        assert gitignore_path.read_text() == content


class TestReadCurrentGitignore:
    """Test reading current .gitignore."""

    def test_read_existing_gitignore(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test reading an existing .gitignore."""
        content = "# Test content\n/test_dir/\n"
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text(content)
        monkeypatch.setattr(generate_gitignore, "_REPO_ROOT", tmp_path)
        result = generate_gitignore.read_current_gitignore()
        assert result == content

    def test_read_missing_gitignore(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test reading a non-existent .gitignore."""
        monkeypatch.setattr(generate_gitignore, "_REPO_ROOT", tmp_path)
        result = generate_gitignore.read_current_gitignore()
        assert result is None


class TestMain:
    """Test main function and CLI interface."""

    def test_main_default(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main with no arguments (prints to stdout)."""
        with patch.object(generate_gitignore, "load_exclusions", return_value=(set(), set(), set())):
            with patch.object(generate_gitignore, "generate_gitignore_content", return_value="# Test"):
                result = generate_gitignore.main([])
                assert result == 0
                captured = capsys.readouterr()
                assert "# Test" in captured.out

    def test_main_check_sync_pass(self) -> None:
        """Test main with --check when in sync."""
        with patch.object(generate_gitignore, "check_sync", return_value=True):
            result = generate_gitignore.main(["--check"])
            assert result == 0

    def test_main_check_sync_fail(self) -> None:
        """Test main with --check when out of sync."""
        with patch.object(generate_gitignore, "check_sync", return_value=False):
            result = generate_gitignore.main(["--check"])
            assert result == 1

    def test_main_write(self) -> None:
        """Test main with --write."""
        with patch.object(generate_gitignore, "load_exclusions", return_value=(set(), set(), set())):
            with patch.object(generate_gitignore, "generate_gitignore_content", return_value="# Test"):
                with patch.object(generate_gitignore, "write_gitignore"):
                    result = generate_gitignore.main(["--write"])
                    assert result == 0

    def test_main_write_precommit(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main with --write-precommit."""
        with patch.object(
            generate_gitignore, "load_exclusions", return_value=(set(), set(), {"test_pattern"})
        ):
            with patch.object(
                generate_gitignore, "generate_precommit_exclude", return_value="exclude: |\n  test"
            ):
                result = generate_gitignore.main(["--write-precommit"])
                assert result == 0
                captured = capsys.readouterr()
                assert "exclude: |" in captured.out
