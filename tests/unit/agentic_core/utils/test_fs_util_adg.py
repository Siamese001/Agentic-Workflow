"""ADG-driven tests for agentic_core/utils/fs_util.py — fan_in=5.

Tests cover get_python_files_fast, calculate_file_hash, get_canonical_path,
and remove_duplicate_suffix_path — all pure file-system utilities.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.utils.fs_util import (
    calculate_file_hash,
    get_canonical_path,
    get_python_files_fast,
    remove_duplicate_suffix_path,
)


class TestGetPythonFilesFast:
    def test_yields_py_files(self, tmp_path):
        (tmp_path / "a.py").write_text("x = 1")
        (tmp_path / "b.py").write_text("y = 2")
        (tmp_path / "c.txt").write_text("text")
        files = list(get_python_files_fast(tmp_path))
        names = {f.name for f in files}
        assert "a.py" in names
        assert "b.py" in names
        assert "c.txt" not in names

    def test_excludes_pycache(self, tmp_path):
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "cached.py").write_text("# cached")
        (tmp_path / "real.py").write_text("# real")
        files = list(get_python_files_fast(tmp_path))
        names = {f.name for f in files}
        assert "real.py" in names
        assert "cached.py" not in names

    def test_custom_exclude_dirs(self, tmp_path):
        excluded = tmp_path / "vendor"
        excluded.mkdir()
        (excluded / "vendor_mod.py").write_text("# vendor")
        (tmp_path / "app.py").write_text("# app")
        files = list(get_python_files_fast(tmp_path, exclude_dirs=["vendor"]))
        names = {f.name for f in files}
        assert "app.py" in names
        assert "vendor_mod.py" not in names

    def test_empty_directory_yields_nothing(self, tmp_path):
        files = list(get_python_files_fast(tmp_path))
        assert files == []

    def test_returns_generator(self, tmp_path):
        import types
        result = get_python_files_fast(tmp_path)
        assert isinstance(result, types.GeneratorType)


class TestCalculateFileHash:
    def test_sha256_hash_correct(self, tmp_path):
        f = tmp_path / "test.py"
        content = b"x = 1\n"
        f.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()
        assert calculate_file_hash(f) == expected

    def test_missing_file_returns_empty_string(self, tmp_path):
        missing = tmp_path / "nonexistent.py"
        assert calculate_file_hash(missing) == ""

    def test_custom_algorithm_md5(self, tmp_path):
        f = tmp_path / "x.py"
        content = b"hello"
        f.write_bytes(content)
        expected = hashlib.md5(content).hexdigest()
        assert calculate_file_hash(f, algorithm="md5") == expected

    def test_empty_file_has_known_hash(self, tmp_path):
        f = tmp_path / "empty.py"
        f.write_bytes(b"")
        result = calculate_file_hash(f)
        assert result == hashlib.sha256(b"").hexdigest()


class TestGetCanonicalPath:
    def test_resolves_to_absolute(self, tmp_path):
        f = tmp_path / "subdir" / "module.py"
        f.parent.mkdir()
        f.touch()
        result = get_canonical_path(f)
        assert result.is_absolute()

    def test_returns_path_object(self, tmp_path):
        f = tmp_path / "a" / "b.py"
        f.parent.mkdir(parents=True)
        f.touch()
        result = get_canonical_path(f)
        assert isinstance(result, Path)


class TestRemoveDuplicateSuffixPath:
    def test_removes_duplicate_suffix(self, tmp_path):
        path = tmp_path / "FooAgentAgent.py"
        canonical, matched = remove_duplicate_suffix_path(path, ["Agent"])
        assert canonical.name == "FooAgent.py"
        assert matched == "Agent"

    def test_no_matching_suffix_returns_original(self, tmp_path):
        path = tmp_path / "FooBar.py"
        canonical, matched = remove_duplicate_suffix_path(path, ["Agent"])
        assert canonical.name == "FooBar.py"
        assert matched is None

    def test_multiple_suffixes_first_match_wins(self, tmp_path):
        path = tmp_path / "BarValidatorValidator.py"
        canonical, matched = remove_duplicate_suffix_path(path, ["Agent", "Validator"])
        assert canonical.name == "BarValidator.py"
        assert matched == "Validator"

    def test_returns_tuple(self, tmp_path):
        path = tmp_path / "X.py"
        result = remove_duplicate_suffix_path(path, ["Agent"])
        assert isinstance(result, tuple)
        assert len(result) == 2
