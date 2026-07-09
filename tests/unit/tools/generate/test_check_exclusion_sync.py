#!/usr/bin/env python3
"""Tests for check_exclusion_sync.py.

Tests cover:
- Loading excluded paths from YAML
- Loading pre-commit excludes from .pre-commit-config.yaml
- Pattern normalization
- Pattern comparison
- Main function CLI interface
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

import check_exclusion_sync


class TestLoadExcludedPaths:
    """Test loading excluded paths from YAML config."""

    def test_load_excluded_paths_success(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful loading of excluded paths."""
        yaml_content = """
version: "1.0.0"

build_cache_dirs:
  - "__pycache__"

precommit_excludes:
  - "artifacts/test.json"
  - "pytestdebug.log"

file_patterns:
  - "*.pyc"
"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        logging.info("C3 write receipt: tests/unit/tools/generate/test_check_exclusion_sync.py write side effect recorded")
        yaml_path = config_dir / "excluded_paths.yaml"
        yaml_path.write_text(yaml_content)

        monkeypatch.setattr(check_exclusion_sync, "_REPO_ROOT", tmp_path)
        data = check_exclusion_sync.load_excluded_paths()

        assert data["precommit_excludes"] == ["artifacts/test.json", "pytestdebug.log"]
        assert data["file_patterns"] == ["*.pyc"]

    def test_load_excluded_paths_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error handling when config file is missing."""
        monkeypatch.setattr(check_exclusion_sync, "_REPO_ROOT", tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            check_exclusion_sync.load_excluded_paths()
        assert exc_info.value.code == 1


class TestLoadPrecommitExcludes:
    """Test loading pre-commit excludes from .pre-commit-config.yaml."""

    def test_load_precommit_excludes_success(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful loading of pre-commit excludes."""
        precommit_content = """# Test config
exclude: |
  (?x)^(
    artifacts/test.json|
    pytestdebug.log|
    temp_[^/]*/.*
  )
"""
        precommit_path = tmp_path / ".pre-commit-config.yaml"
        precommit_path.write_text(precommit_content)

        monkeypatch.setattr(check_exclusion_sync, "_REPO_ROOT", tmp_path)
        patterns = check_exclusion_sync.load_precommit_excludes()

        assert "artifacts/test.json" in patterns
        assert "pytestdebug.log" in patterns
        assert "temp_[^/]*/.*" in patterns
        assert len(patterns) == 3

    def test_load_precommit_excludes_with_nested_parens(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading with nested parentheses in patterns."""
        precommit_content = """# Test config
exclude: |
  (?x)^(
    guardian_.*.(txt|json)|
    artifacts/test.json
  )
"""
        precommit_path = tmp_path / ".pre-commit-config.yaml"
        precommit_path.write_text(precommit_content)

        monkeypatch.setattr(check_exclusion_sync, "_REPO_ROOT", tmp_path)
        patterns = check_exclusion_sync.load_precommit_excludes()

        assert "guardian_.*.(txt|json)" in patterns
        assert "artifacts/test.json" in patterns

    def test_load_precommit_excludes_missing_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error handling when config file is missing."""
        monkeypatch.setattr(check_exclusion_sync, "_REPO_ROOT", tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            check_exclusion_sync.load_precommit_excludes()
        assert exc_info.value.code == 1

    def test_load_precommit_excludes_invalid_format(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error handling when exclude section is malformed."""
        precommit_content = """# Test config
exclude: invalid
"""
        precommit_path = tmp_path / ".pre-commit-config.yaml"
        precommit_path.write_text(precommit_content)

        monkeypatch.setattr(check_exclusion_sync, "_REPO_ROOT", tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            check_exclusion_sync.load_precommit_excludes()
        assert exc_info.value.code == 1

    def test_load_precommit_excludes_no_regex_block(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error when exclude: | is present but (?x)^( is missing (line-61 branch)."""
        precommit_content = """# Test config
exclude: |
  some_text_without_regex_pattern
"""
        precommit_path = tmp_path / ".pre-commit-config.yaml"
        precommit_path.write_text(precommit_content)

        monkeypatch.setattr(check_exclusion_sync, "_REPO_ROOT", tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            check_exclusion_sync.load_precommit_excludes()
        assert exc_info.value.code == 1

    def test_load_precommit_excludes_unclosed_parens(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error when (?x)^( regex block has no matching closing ) (line-83 branch)."""
        precommit_content = """# Test config
exclude: |
  (?x)^(
    pattern_one|
    pattern_two
"""
        precommit_path = tmp_path / ".pre-commit-config.yaml"
        precommit_path.write_text(precommit_content)

        monkeypatch.setattr(check_exclusion_sync, "_REPO_ROOT", tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            check_exclusion_sync.load_precommit_excludes()
        assert exc_info.value.code == 1


class TestNormalizePattern:
    """Test pattern normalization for comparison."""

    def test_normalize_pattern_basic(self) -> None:
        """Test basic pattern normalization."""
        assert check_exclusion_sync.normalize_pattern(r"\.pyc") == ".pyc"
        assert check_exclusion_sync.normalize_pattern(".*") == "*"
        assert check_exclusion_sync.normalize_pattern("^test$") == "test"

    def test_normalize_pattern_regex_special_chars(self) -> None:
        """Test normalization of regex special characters."""
        assert check_exclusion_sync.normalize_pattern(r"\.") == "."
        assert check_exclusion_sync.normalize_pattern(r"[a-z]") == "a-z"
        assert check_exclusion_sync.normalize_pattern(r"/.*") == "/*"

    def test_normalize_pattern_anchored(self) -> None:
        """Test removal of anchors."""
        assert check_exclusion_sync.normalize_pattern("^test") == "test"
        assert check_exclusion_sync.normalize_pattern("test$") == "test"

    def test_normalize_pattern_whitespace(self) -> None:
        """Test whitespace stripping."""
        assert check_exclusion_sync.normalize_pattern("  test  ") == "test"


class TestComparePatterns:
    """Test pattern comparison between YAML and pre-commit config."""

    def test_compare_patterns_in_sync(self) -> None:
        """Test comparison when patterns are in sync."""
        yaml_data = {"precommit_excludes": ["test.json", "pytestdebug.log"]}
        precommit_patterns = ["test.json", "pytestdebug.log"]

        result = check_exclusion_sync.compare_patterns(yaml_data, precommit_patterns)

        assert result["in_yaml_not_precommit"] == []
        assert result["in_precommit_not_yaml"] == []
        assert result["total_yaml"] == 2
        assert result["total_precommit"] == 2
        assert result["common_count"] == 2

    def test_compare_patterns_yaml_extra(self) -> None:
        """Test comparison when YAML has extra patterns."""
        yaml_data = {"precommit_excludes": ["test.json", "pytestdebug.log", "extra.json"]}
        precommit_patterns = ["test.json", "pytestdebug.log"]

        result = check_exclusion_sync.compare_patterns(yaml_data, precommit_patterns)

        assert len(result["in_yaml_not_precommit"]) == 1
        assert "extra" in result["in_yaml_not_precommit"][0]
        assert result["in_precommit_not_yaml"] == []
        assert result["common_count"] == 2

    def test_compare_patterns_precommit_extra(self) -> None:
        """Test comparison when pre-commit has extra patterns."""
        yaml_data = {"precommit_excludes": ["test.json"]}
        precommit_patterns = ["test.json", "extra.json"]

        result = check_exclusion_sync.compare_patterns(yaml_data, precommit_patterns)

        assert result["in_yaml_not_precommit"] == []
        assert len(result["in_precommit_not_yaml"]) == 1
        assert "extra" in result["in_precommit_not_yaml"][0]
        assert result["common_count"] == 1

    def test_compare_patterns_with_normalization(self) -> None:
        """Test that patterns are normalized before comparison."""
        yaml_data: dict[str, list[str]] = {"precommit_excludes": [r"test.json"]}
        precommit_patterns: list[str] = ["test.json"]

        result = check_exclusion_sync.compare_patterns(yaml_data, precommit_patterns)

        assert result["in_yaml_not_precommit"] == []
        assert result["in_precommit_not_yaml"] == []
        assert result["common_count"] == 1

    def test_compare_patterns_empty(self) -> None:
        """Test comparison with empty pattern sets."""
        yaml_data: dict[str, list[str]] = {"precommit_excludes": []}
        precommit_patterns: list[str] = []

        result = check_exclusion_sync.compare_patterns(yaml_data, precommit_patterns)

        assert result["total_yaml"] == 0
        assert result["total_precommit"] == 0
        assert result["common_count"] == 0

    def test_compare_patterns_missing_precommit_excludes_key(self) -> None:
        """YAML dict with no 'precommit_excludes' key — get() default path returns zero YAML patterns."""
        result = check_exclusion_sync.compare_patterns({}, ["test.json"])
        assert result["total_yaml"] == 0
        assert result["in_yaml_not_precommit"] == []
        assert len(result["in_precommit_not_yaml"]) == 1


class TestMain:
    """Test main function and CLI interface."""

    def test_main_in_sync(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main when patterns are in sync."""
        yaml_data: dict[str, list[str]] = {"precommit_excludes": ["test.json"]}
        precommit_patterns: list[str] = ["test.json"]

        with patch.object(check_exclusion_sync, "load_excluded_paths", return_value=yaml_data):
            with patch.object(
                check_exclusion_sync, "load_precommit_excludes", return_value=precommit_patterns
            ):
                result = check_exclusion_sync.main([])
                assert result == 0
                captured = capsys.readouterr()
                assert "in sync" in captured.out

    def test_main_out_of_sync(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main when patterns are out of sync."""
        yaml_data: dict[str, list[str]] = {"precommit_excludes": ["test.json", "extra.json"]}
        precommit_patterns: list[str] = ["test.json"]

        with patch.object(check_exclusion_sync, "load_excluded_paths", return_value=yaml_data):
            with patch.object(
                check_exclusion_sync, "load_precommit_excludes", return_value=precommit_patterns
            ):
                result = check_exclusion_sync.main([])
                assert result == 1
                captured = capsys.readouterr()
                assert "out of sync" in captured.out

    def test_main_fix_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main with --fix flag (currently no-op)."""
        yaml_data: dict[str, list[str]] = {"precommit_excludes": ["test.json"]}
        precommit_patterns: list[str] = ["test.json"]

        with patch.object(check_exclusion_sync, "load_excluded_paths", return_value=yaml_data):
            with patch.object(
                check_exclusion_sync, "load_precommit_excludes", return_value=precommit_patterns
            ):
                result = check_exclusion_sync.main(["--fix"])
                assert result == 0

    def test_main_output_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that main output includes expected sections."""
        yaml_data: dict[str, list[str]] = {"precommit_excludes": ["test.json", "extra.json"]}
        precommit_patterns: list[str] = ["test.json"]

        with patch.object(check_exclusion_sync, "load_excluded_paths", return_value=yaml_data):
            with patch.object(
                check_exclusion_sync, "load_precommit_excludes", return_value=precommit_patterns
            ):
                check_exclusion_sync.main([])
                captured = capsys.readouterr()
                assert "YAML precommit_excludes" in captured.out
                assert "Pre-commit patterns" in captured.out
                assert "Common patterns" in captured.out
