"""Tests for apps_research.integrations.pdf_ingest (plan §P3.1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_research.integrations.pdf_ingest import Chunk, ingest


def test_txt_ingest_produces_chunks(tmp_path: Path):
    words = [f"word{i}" for i in range(1500)]
    f = tmp_path / "sample.txt"
    f.write_text(" ".join(words), encoding="utf-8")
    chunks = ingest(f, chunk_tokens=256, overlap_tokens=25)
    assert len(chunks) >= 3
    for c in chunks:
        assert isinstance(c, Chunk)
        assert c.file_path == str(f)
        assert c.chunk_id.startswith("sample.txt::c")


def test_md_ingest_supported(tmp_path: Path):
    f = tmp_path / "doc.md"
    f.write_text("# Title\n\nOne two three four five six.", encoding="utf-8")
    chunks = ingest(f)
    assert len(chunks) == 1


def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        ingest(tmp_path / "nope.txt")


def test_unsupported_extension_raises(tmp_path: Path):
    f = tmp_path / "doc.docx"
    f.write_bytes(b"fake")
    with pytest.raises(ValueError, match="unsupported"):
        ingest(f)


def test_chunk_id_is_monotonic(tmp_path: Path):
    words = [f"w{i}" for i in range(2000)]
    f = tmp_path / "many.txt"
    f.write_text(" ".join(words), encoding="utf-8")
    chunks = ingest(f, chunk_tokens=256, overlap_tokens=25)
    indices = [c.chunk_index for c in chunks]
    assert indices == sorted(indices)
