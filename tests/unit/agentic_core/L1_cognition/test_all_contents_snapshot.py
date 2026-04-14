"""Tests for deterministic all_contents snapshot generation."""

from __future__ import annotations

from pathlib import Path

from scripts.build_all_contents import build_all_contents_text, iter_snapshot_files, write_all_contents


def test_iter_snapshot_files_skips_generated_outputs(tmp_path: Path):
    keep = tmp_path / "README.md"
    keep.write_text("readme")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "bundle.zip").write_text("x")
    (tmp_path / "all_contents.txt").write_text("old")

    files = iter_snapshot_files(tmp_path)
    assert files == [keep]


def test_build_all_contents_text_uses_relative_headers(tmp_path: Path):
    target = tmp_path / "pkg" / "module.py"
    target.parent.mkdir()
    target.write_text('print("ok")\n')

    snapshot = build_all_contents_text(tmp_path)
    assert "###FILE:pkg/module.py" in snapshot
    assert "/mnt/data" not in snapshot


def test_write_all_contents_creates_snapshot_file(tmp_path: Path):
    target = tmp_path / "README.md"
    target.write_text("hello\n")

    output = write_all_contents(tmp_path)
    payload = output.read_text()
    assert output.name == "all_contents.txt"
    assert "###FILE:README.md" in payload
    assert "hello" in payload
