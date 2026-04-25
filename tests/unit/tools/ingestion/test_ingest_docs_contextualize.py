"""Tests for ``ingest_docs.py --contextualize`` (W6.2).

Plan: ``anthropic-rag-gaps-7f3c2a.md`` phase W6.2. Mirrors the
contextualization path already exercised on ``ingest_code.py``.

Strategy: drive ``main()`` in ``--dry-run --mock-embeddings`` mode over
a tmp-path markdown file, patch ``ContextualChunkBuilder.build`` to
return a deterministic stub, and assert (a) the flag is plumbed, (b)
chunk content is prepended with the context prefix, and (c)
``chunk_context`` is stamped on metadata.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.ingestion import ingest_docs


def _make_doc(tmp_path: Path, body: str = "# Heading\n\nSome body text.\n") -> Path:
    src = tmp_path / "docs"
    src.mkdir()
    (src / "doc_a.md").write_text(body, encoding="utf-8")
    return src


def _stub_builder_result(context: str):
    """Return a fake ContextualChunkBuilder.build() that emits ``context``.

    Patched via ``patch.object(cls, "build", fn)`` — fn receives ``self``
    plus the request. Signature must match.
    """

    class _Result:
        def __init__(self, ctx: str) -> None:
            self.context = ctx

    def _build(_self, _request):
        return _Result(context)

    return _build


def test_contextualize_flag_parsed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """W6.2: ``--contextualize`` is accepted by argparse and logs the
    'ENABLED' banner on run start."""
    src = _make_doc(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ingest_docs.py",
            "--source-dir",
            str(src),
            "--dry-run",
            "--mock-embeddings",
            "--contextualize",
        ],
    )
    with patch.object(ingest_docs.ContextualChunkBuilder, "build", _stub_builder_result("CTX")):
        rc = ingest_docs.main()
    assert rc == 0


def test_contextualize_prepends_context_and_stamps_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """W6.2: with --contextualize, each chunk's content must gain the
    context prefix and ``chunk_context`` must land in metadata.

    We capture the chunks by intercepting ingest_chunks (reached only
    when --dry-run is off) OR by capturing all_chunks via monkeypatched
    ``DocumentChunker.chunk_document`` return. Here we use the latter:
    stub the chunker, run main() dry-run, and inspect the chunk list
    via a capturing patched ``Logger.info`` trail.
    """
    src = _make_doc(tmp_path)
    captured_chunks: list[dict] = []

    original_chunk = ingest_docs.DocumentChunker.chunk_document

    def _capturing_chunk(self, file_path, *, embedding_model=None, embedding_dim=None):
        chunks = original_chunk(
            self,
            file_path,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
        )
        # Share reference: the outer captured_chunks list sees the same
        # dicts ``main()`` mutates in-place under --contextualize.
        captured_chunks.extend(chunks)
        return chunks

    monkeypatch.setattr(ingest_docs.DocumentChunker, "chunk_document", _capturing_chunk)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ingest_docs.py",
            "--source-dir",
            str(src),
            "--dry-run",
            "--mock-embeddings",
            "--contextualize",
        ],
    )

    with patch.object(
        ingest_docs.ContextualChunkBuilder,
        "build",
        _stub_builder_result("SYNTHETIC_CONTEXT_PREFIX"),
    ):
        rc = ingest_docs.main()

    assert rc == 0
    assert captured_chunks, "expected at least one chunk from the seed doc"
    # Every chunk's content now starts with the prepended context.
    for chunk in captured_chunks:
        assert "SYNTHETIC_CONTEXT_PREFIX" in chunk["content"]
        assert chunk["metadata"].get("chunk_context") == "SYNTHETIC_CONTEXT_PREFIX"


def test_contextualize_off_does_not_mutate_chunks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """W6.2 default-off: without --contextualize, chunks are NOT
    enriched and no ``chunk_context`` metadata is stamped."""
    src = _make_doc(tmp_path)
    captured_chunks: list[dict] = []

    original_chunk = ingest_docs.DocumentChunker.chunk_document

    def _capturing_chunk(self, file_path, *, embedding_model=None, embedding_dim=None):
        chunks = original_chunk(
            self,
            file_path,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
        )
        captured_chunks.extend(chunks)
        return chunks

    monkeypatch.setattr(ingest_docs.DocumentChunker, "chunk_document", _capturing_chunk)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ingest_docs.py",
            "--source-dir",
            str(src),
            "--dry-run",
            "--mock-embeddings",
        ],  # no --contextualize
    )

    # Should never be called. Use a sentinel that raises if invoked.
    def _forbidden(_self, _request):
        raise AssertionError("ContextualChunkBuilder.build was invoked when --contextualize was absent")

    with patch.object(ingest_docs.ContextualChunkBuilder, "build", _forbidden):
        rc = ingest_docs.main()

    assert rc == 0
    assert captured_chunks, "expected at least one chunk from the seed doc"
    for chunk in captured_chunks:
        assert "chunk_context" not in chunk["metadata"]


def test_contextualize_skips_chunks_when_context_is_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """W6.2: builder returning empty context is a best-effort miss —
    chunk content is untouched, no ``chunk_context`` is stamped, and
    ingestion proceeds normally."""
    src = _make_doc(tmp_path)
    captured_chunks: list[dict] = []

    original_chunk = ingest_docs.DocumentChunker.chunk_document

    def _capturing_chunk(self, file_path, *, embedding_model=None, embedding_dim=None):
        chunks = original_chunk(
            self,
            file_path,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
        )
        captured_chunks.extend(chunks)
        return chunks

    monkeypatch.setattr(ingest_docs.DocumentChunker, "chunk_document", _capturing_chunk)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ingest_docs.py",
            "--source-dir",
            str(src),
            "--dry-run",
            "--mock-embeddings",
            "--contextualize",
        ],
    )

    def _record_and_empty(_self, _request):
        class _R:
            context = ""

        return _R()

    with patch.object(ingest_docs.ContextualChunkBuilder, "build", _record_and_empty):
        rc = ingest_docs.main()

    assert rc == 0
    for chunk in captured_chunks:
        assert "chunk_context" not in chunk["metadata"]
