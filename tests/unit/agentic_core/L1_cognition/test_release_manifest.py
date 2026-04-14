"""Tests for release manifest generation helpers."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build_release_manifest import (
    build_manifest,
    is_ignored_release_path,
    iter_release_files,
    sha256_file,
    write_manifest,
)


def test_iter_release_files_skips_ignored_paths(tmp_path: Path):
    (tmp_path / "keep.py").write_text("print(1)")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "skip.pyc").write_text("x")
    files = iter_release_files(tmp_path)
    assert [path.name for path in files] == ["keep.py"]


def test_is_ignored_release_path_detects_generated_and_cache_files(tmp_path: Path):
    manifest = tmp_path / "RELEASE_MANIFEST.json"
    manifest.write_text("{}")
    pyc = tmp_path / "module.pyc"
    pyc.write_text("x")
    assert is_ignored_release_path(tmp_path, manifest)
    assert is_ignored_release_path(tmp_path, pyc)


def test_sha256_file_returns_hex_digest(tmp_path: Path):
    target = tmp_path / "data.txt"
    target.write_text("abc")
    digest = sha256_file(target)
    assert len(digest) == 64
    assert all(ch in "0123456789abcdef" for ch in digest)


def test_write_manifest_creates_json_file(tmp_path: Path):
    (tmp_path / "README.md").write_text("readme")
    path = write_manifest(tmp_path)
    payload = json.loads(path.read_text())
    assert payload["file_count"] == 1
    assert payload["files"][0]["path"] == "README.md"


def test_build_manifest_tracks_size_bytes(tmp_path: Path):
    target = tmp_path / "hello.txt"
    target.write_text("hello")
    manifest = build_manifest(tmp_path)
    assert manifest["files"][0]["size_bytes"] == 5
    assert manifest["total_size_bytes"] == 5
    assert len(manifest["manifest_sha256"]) == 64
