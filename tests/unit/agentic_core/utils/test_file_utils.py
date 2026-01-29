#!/usr/bin/env python3
"""
Test Suite: Safe File Operations Utilities

Tests for agentic_core/utils/file_utils.py

All tests must pass 100% before proceeding to Phase 2.2.
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

try:
    from agentic_core.utils.file_utils import (
        safe_read_file,
        safe_write_file,
        safe_read_json,
        safe_write_json,
        safe_read_lines,
        file_exists,
        ensure_directory,
    )
except ImportError:
    # Fallback to archived location for legacy tests
    from archives.location_violations.file_utils import (
        safe_read_file,
        safe_write_file,
        safe_read_json,
        safe_write_json,
        safe_read_lines,
        file_exists,
        ensure_directory,
    )


class TestSafeReadFile:
    """Tests for safe_read_file function."""

    def test_read_existing_file(self, tmp_path):
        """Test reading an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!", encoding="utf-8")

        content = safe_read_file(test_file)
        assert content == "Hello, World!"

    def test_read_missing_file(self, tmp_path):
        """Test Case 2: Read Missing - should return None, NO crash."""
        missing_file = tmp_path / "nonexistent.txt"

        content = safe_read_file(missing_file)
        assert content is None

    def test_read_missing_file_with_default(self, tmp_path):
        """Test reading missing file with custom default."""
        missing_file = tmp_path / "nonexistent.txt"

        content = safe_read_file(missing_file, default="default value")
        assert content == "default value"

    def test_read_utf8_content(self, tmp_path):
        """Test reading UTF-8 encoded content."""
        test_file = tmp_path / "unicode.txt"
        test_file.write_text("Hello 世界 🌍", encoding="utf-8")

        content = safe_read_file(test_file)
        assert content == "Hello 世界 🌍"

    def test_read_with_encoding_errors(self, tmp_path):
        """Test reading file with encoding errors (replace mode)."""
        test_file = tmp_path / "binary.txt"
        # Write some bytes that aren't valid UTF-8
        test_file.write_bytes(b"Hello \xff\xfe World")

        content = safe_read_file(test_file, errors="replace")
        assert content is not None
        assert "Hello" in content
        assert "World" in content


class TestSafeWriteFile:
    """Tests for safe_write_file function."""

    def test_write_new_file(self, tmp_path):
        """Test writing to a new file."""
        test_file = tmp_path / "output.txt"

        success = safe_write_file(test_file, "Test content")

        assert success is True
        assert test_file.exists()
        assert test_file.read_text() == "Test content"

    def test_atomic_write(self, tmp_path):
        """Test Case 1: Atomic Write - file should exist after write."""
        test_file = tmp_path / "atomic.txt"
        large_content = "x" * 10000  # Large content

        success = safe_write_file(test_file, large_content, atomic=True)

        assert success is True
        assert test_file.exists()
        assert test_file.read_text() == large_content
        # Temp file should not exist after successful write
        tmp_file = test_file.with_suffix(".txt.tmp")
        assert not tmp_file.exists()

    def test_non_atomic_write(self, tmp_path):
        """Test non-atomic write."""
        test_file = tmp_path / "direct.txt"

        success = safe_write_file(test_file, "Direct write", atomic=False)

        assert success is True
        assert test_file.read_text() == "Direct write"

    def test_create_parent_directories(self, tmp_path):
        """Test that parent directories are created."""
        nested_file = tmp_path / "a" / "b" / "c" / "file.txt"

        success = safe_write_file(nested_file, "Nested content", create_dirs=True)

        assert success is True
        assert nested_file.exists()
        assert nested_file.read_text() == "Nested content"

    def test_overwrite_existing_file(self, tmp_path):
        """Test overwriting an existing file."""
        test_file = tmp_path / "existing.txt"
        test_file.write_text("Original content")

        success = safe_write_file(test_file, "New content")

        assert success is True
        assert test_file.read_text() == "New content"


class TestSafeReadJson:
    """Tests for safe_read_json function."""

    def test_read_valid_json(self, tmp_path):
        """Test reading valid JSON file."""
        json_file = tmp_path / "config.json"
        json_file.write_text('{"key": "value", "number": 42}')

        data = safe_read_json(json_file)

        assert data == {"key": "value", "number": 42}

    def test_read_json_array(self, tmp_path):
        """Test reading JSON array."""
        json_file = tmp_path / "array.json"
        json_file.write_text('[1, 2, 3, "four"]')

        data = safe_read_json(json_file)

        assert data == [1, 2, 3, "four"]

    def test_read_missing_json(self, tmp_path):
        """Test reading missing JSON file."""
        missing_file = tmp_path / "missing.json"

        data = safe_read_json(missing_file)

        assert data is None

    def test_read_missing_json_with_default(self, tmp_path):
        """Test reading missing JSON with default value."""
        missing_file = tmp_path / "missing.json"

        data = safe_read_json(missing_file, default={})

        assert data == {}

    def test_read_bad_json(self, tmp_path):
        """Test Case 3: Bad JSON - should return default, NO crash."""
        bad_json = tmp_path / "bad.json"
        bad_json.write_text('{"key": "value", invalid}')  # Malformed JSON

        data = safe_read_json(bad_json, default={})

        assert data == {}  # Should return default, not crash

    def test_read_empty_json_file(self, tmp_path):
        """Test reading empty JSON file."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")

        data = safe_read_json(empty_file, default={"default": True})

        assert data == {"default": True}


class TestSafeWriteJson:
    """Tests for safe_write_json function."""

    def test_write_dict(self, tmp_path):
        """Test writing dictionary as JSON."""
        json_file = tmp_path / "output.json"
        data = {"key": "value", "number": 42}

        success = safe_write_json(json_file, data)

        assert success is True
        assert json_file.exists()
        loaded = json.loads(json_file.read_text())
        assert loaded == data

    def test_write_list(self, tmp_path):
        """Test writing list as JSON."""
        json_file = tmp_path / "list.json"
        data = [1, 2, 3, "four"]

        success = safe_write_json(json_file, data)

        assert success is True
        loaded = json.loads(json_file.read_text())
        assert loaded == data

    def test_write_with_indent(self, tmp_path):
        """Test writing JSON with custom indent."""
        json_file = tmp_path / "indented.json"
        data = {"key": "value"}

        success = safe_write_json(json_file, data, indent=4)

        assert success is True
        content = json_file.read_text()
        assert "    " in content  # 4-space indent

    def test_write_unicode(self, tmp_path):
        """Test writing JSON with unicode characters."""
        json_file = tmp_path / "unicode.json"
        data = {"message": "Hello 世界 🌍"}

        success = safe_write_json(json_file, data, ensure_ascii=False)

        assert success is True
        content = json_file.read_text(encoding="utf-8")
        assert "世界" in content
        assert "🌍" in content

    def test_atomic_json_write(self, tmp_path):
        """Test atomic JSON write."""
        json_file = tmp_path / "atomic.json"
        data = {"large": "x" * 10000}

        success = safe_write_json(json_file, data, atomic=True)

        assert success is True
        assert json_file.exists()
        # Temp file should not exist
        tmp_file = json_file.with_suffix(".json.tmp")
        assert not tmp_file.exists()


class TestSafeReadLines:
    """Tests for safe_read_lines function."""

    def test_read_lines(self, tmp_path):
        """Test reading lines from file."""
        test_file = tmp_path / "lines.txt"
        test_file.write_text("line1\nline2\nline3")

        lines = safe_read_lines(test_file)

        assert lines == ["line1", "line2", "line3"]

    def test_read_lines_with_strip(self, tmp_path):
        """Test reading lines with stripping."""
        test_file = tmp_path / "spaces.txt"
        test_file.write_text("  line1  \n  line2  \n  line3  ")

        lines = safe_read_lines(test_file, strip=True)

        assert lines == ["line1", "line2", "line3"]

    def test_read_lines_skip_empty(self, tmp_path):
        """Test reading lines skipping empty."""
        test_file = tmp_path / "empty_lines.txt"
        test_file.write_text("line1\n\nline2\n\nline3")

        lines = safe_read_lines(test_file, skip_empty=True)

        assert lines == ["line1", "line2", "line3"]

    def test_read_lines_missing_file(self, tmp_path):
        """Test reading lines from missing file."""
        missing_file = tmp_path / "missing.txt"

        lines = safe_read_lines(missing_file)

        assert lines == []


class TestFileExists:
    """Tests for file_exists function."""

    def test_existing_file(self, tmp_path):
        """Test checking existing file."""
        test_file = tmp_path / "exists.txt"
        test_file.write_text("content")

        assert file_exists(test_file) is True

    def test_missing_file(self, tmp_path):
        """Test checking missing file."""
        missing_file = tmp_path / "missing.txt"

        assert file_exists(missing_file) is False

    def test_directory(self, tmp_path):
        """Test checking directory."""
        assert file_exists(tmp_path) is True


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_create_new_directory(self, tmp_path):
        """Test creating new directory."""
        new_dir = tmp_path / "new_dir"

        success = ensure_directory(new_dir)

        assert success is True
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_nested_directories(self, tmp_path):
        """Test creating nested directories."""
        nested_dir = tmp_path / "a" / "b" / "c"

        success = ensure_directory(nested_dir)

        assert success is True
        assert nested_dir.exists()

    def test_existing_directory(self, tmp_path):
        """Test with existing directory."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        success = ensure_directory(existing_dir)

        assert success is True
        assert existing_dir.exists()


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "#" * 60)
    print("# File Utils Test Suite")
    print("#" * 60)

    # Run with pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])

    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED (100%)")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(run_all_tests())
