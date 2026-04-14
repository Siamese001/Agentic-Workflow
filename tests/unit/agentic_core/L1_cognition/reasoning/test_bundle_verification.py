"""Tests for packaging-verification helpers."""

from __future__ import annotations

from pathlib import Path

from scripts.verify_source_tree import (
    find_forbidden_paths,
    is_forbidden_path,
    missing_required_files,
    verify_tree,
)


def test_is_forbidden_path_detects_cache_and_compiled_artifacts(tmp_path: Path):
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()
    pyc_file = tmp_path / "module.pyc"
    pyc_file.write_text("x")
    assert is_forbidden_path(cache_dir)
    assert is_forbidden_path(pyc_file)


def test_find_forbidden_paths_detects_cache_and_pyc(tmp_path: Path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "module.pyc").write_text("x")
    found = find_forbidden_paths(tmp_path)
    names = {path.name for path in found}
    assert "__pycache__" in names
    assert "module.pyc" in names


def test_missing_required_files_reports_absent_metadata(tmp_path: Path):
    missing = missing_required_files(tmp_path)
    assert "README.md" in missing
    assert "pyproject.toml" in missing


def test_verify_tree_passes_when_required_files_exist(tmp_path: Path):
    for name in ("README.md", "pyproject.toml", "Makefile", "MANIFEST.in"):
        (tmp_path / name).write_text("ok")
    forbidden, missing = verify_tree(tmp_path)
    assert forbidden == []
    assert missing == []
