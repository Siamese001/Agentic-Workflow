"""Unit tests for tools.ingestion.late_chunking_helper (Wave C).

Covers:
    * is_enabled_from_env_or_flag: CLI flag, env values, precedence
    * _resolve_source_path: key ordering, missing file handling
    * _locate_chunk_span: found, not found, empty content
    * apply_late_chunking: happy path (input-order preservation), missing
      file fallback, relocation-miss fallback, embedder-error fallback,
      None return when embedder module unavailable
    * SovereignChromaClient.add_documents: new embeddings param shape check
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.ingestion import late_chunking_helper as helper
from tools.ingestion.late_chunking_helper import (
    _locate_chunk_span,
    _resolve_source_path,
    apply_late_chunking,
    is_enabled_from_env_or_flag,
)


# ---------------------------------------------------------------------------
# is_enabled_from_env_or_flag
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "env_val,expected",
    [
        ("1", True),
        ("true", True),
        ("True", True),
        ("yes", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("", False),
        ("no", False),
    ],
)
def test_env_flag_parses_truthy_values(env_val, expected, monkeypatch):
    monkeypatch.setenv("LATE_CHUNKING", env_val)
    assert is_enabled_from_env_or_flag(False) is expected


def test_cli_flag_overrides_env_false(monkeypatch):
    monkeypatch.setenv("LATE_CHUNKING", "false")
    assert is_enabled_from_env_or_flag(True) is True


def test_cli_flag_false_and_env_unset_returns_false(monkeypatch):
    monkeypatch.delenv("LATE_CHUNKING", raising=False)
    assert is_enabled_from_env_or_flag(False) is False


# ---------------------------------------------------------------------------
# _resolve_source_path
# ---------------------------------------------------------------------------


def test_resolve_source_path_prefers_file_path_key(tmp_path):
    real = tmp_path / "real.py"
    real.write_text("x", encoding="utf-8")
    metadata = {"file_path": str(real), "source_path": "/ghost/missing.py"}
    assert _resolve_source_path(metadata) == real


def test_resolve_source_path_falls_through_to_source_path(tmp_path):
    real = tmp_path / "doc.md"
    real.write_text("x", encoding="utf-8")
    metadata = {"source_path": str(real)}
    assert _resolve_source_path(metadata) == real


def test_resolve_source_path_falls_through_to_doc_id(tmp_path):
    real = tmp_path / "legacy.md"
    real.write_text("x", encoding="utf-8")
    metadata = {"doc_id": str(real)}
    assert _resolve_source_path(metadata) == real


def test_resolve_source_path_returns_none_when_no_key_exists():
    assert _resolve_source_path({}) is None
    assert _resolve_source_path({"file_path": "/nope/missing.py"}) is None


# ---------------------------------------------------------------------------
# _locate_chunk_span
# ---------------------------------------------------------------------------


def test_locate_chunk_span_finds_substring():
    doc = "prefix CHUNK_BODY suffix"
    assert _locate_chunk_span(doc, "CHUNK_BODY") == (7, 17)


def test_locate_chunk_span_returns_none_when_missing():
    assert _locate_chunk_span("doc text", "not present") is None


def test_locate_chunk_span_returns_none_for_empty_content():
    assert _locate_chunk_span("doc text", "") is None


# ---------------------------------------------------------------------------
# apply_late_chunking
# ---------------------------------------------------------------------------


def _make_chunk(chunk_id: str, content: str, file_path: str) -> dict:
    return {
        "id": chunk_id,
        "content": content,
        "metadata": {"file_path": file_path},
    }


def test_apply_late_chunking_returns_none_when_module_unavailable(monkeypatch):
    """ImportError on lazy-load => None => caller delegates to default path."""
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def _blocked_import(name, *args, **kwargs):
        if name == "agentic_core.knowledge.retrieval.late_chunking":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _blocked_import)
    result = apply_late_chunking([_make_chunk("c1", "hello", "/ghost")])
    assert result is None


def test_apply_late_chunking_happy_path_preserves_input_order(tmp_path):
    """Two chunks across one file: output vectors come back in input order,
    each vector produced by the mocked embedder."""
    doc_file = tmp_path / "doc.py"
    doc_file.write_text("alpha beta gamma delta epsilon", encoding="utf-8")

    chunks = [
        _make_chunk("c_alpha", "alpha beta", str(doc_file)),
        _make_chunk("c_gamma", "gamma delta", str(doc_file)),
    ]

    fake_embedder_cls = MagicMock()
    fake_embedder = MagicMock()
    fake_embedder_cls.return_value = fake_embedder
    # Return embeddings keyed by chunk_id so the helper can stitch by id.
    fake_embedder.embed_chunks_from_doc.return_value = {
        "c_alpha": [0.1] * 1024,
        "c_gamma": [0.2] * 1024,
    }

    with patch(
        "agentic_core.knowledge.retrieval.late_chunking.LateChunkingEmbedder",
        fake_embedder_cls,
    ):
        result = apply_late_chunking(chunks)

    assert result is not None
    assert len(result) == 2
    assert result[0] == [0.1] * 1024  # c_alpha comes first — input order preserved
    assert result[1] == [0.2] * 1024  # c_gamma second


def test_apply_late_chunking_falls_back_when_chunk_cannot_be_relocated(tmp_path, monkeypatch):
    """Chunk content not found in file -> fallback to bge_embed_query.
    Verifies mixed-mode behavior (some chunks late-chunked, others fell back)."""
    doc_file = tmp_path / "doc.py"
    doc_file.write_text("found_text", encoding="utf-8")

    chunks = [
        _make_chunk("c_found", "found_text", str(doc_file)),
        _make_chunk("c_missing", "not_in_file", str(doc_file)),
    ]

    fake_embedder_cls = MagicMock()
    fake_embedder = MagicMock()
    fake_embedder_cls.return_value = fake_embedder
    fake_embedder.embed_chunks_from_doc.return_value = {"c_found": [0.5] * 1024}

    fallback_vec = [0.9] * 1024
    fallback_calls: list[str] = []

    def _fake_bge_query(text: str) -> list[float]:
        fallback_calls.append(text)
        return fallback_vec

    import agentic_core.embeddings.bge_runtime as bge_rt

    monkeypatch.setattr(bge_rt, "bge_embed_query", _fake_bge_query)

    with patch(
        "agentic_core.knowledge.retrieval.late_chunking.LateChunkingEmbedder",
        fake_embedder_cls,
    ):
        result = apply_late_chunking(chunks)

    assert result is not None
    assert len(result) == 2
    assert result[0] == [0.5] * 1024  # late-chunked
    assert result[1] == fallback_vec  # fallback for unlocatable chunk
    assert fallback_calls == ["not_in_file"]


def test_apply_late_chunking_fallback_on_missing_file(tmp_path, monkeypatch):
    """file_path doesn't exist -> bge_embed_query fallback for that chunk."""
    chunks = [_make_chunk("c1", "some body", "/absolutely/not/a/real/path.py")]

    fallback_vec = [0.7] * 1024
    import agentic_core.embeddings.bge_runtime as bge_rt

    monkeypatch.setattr(bge_rt, "bge_embed_query", lambda t: fallback_vec)

    # Still need the LateChunkingEmbedder import to succeed so the helper
    # doesn't return None up front.
    fake_embedder_cls = MagicMock(return_value=MagicMock())
    with patch(
        "agentic_core.knowledge.retrieval.late_chunking.LateChunkingEmbedder",
        fake_embedder_cls,
    ):
        result = apply_late_chunking(chunks)

    assert result == [fallback_vec]


def test_apply_late_chunking_fallback_when_embedder_raises(tmp_path, monkeypatch):
    """Embedder raising RuntimeError during embed_chunks_from_doc -> all that
    file's chunks fall back, helper does not crash."""
    doc_file = tmp_path / "doc.py"
    doc_file.write_text("content", encoding="utf-8")

    chunks = [_make_chunk("c1", "content", str(doc_file))]

    fake_embedder_cls = MagicMock()
    fake_embedder = MagicMock()
    fake_embedder_cls.return_value = fake_embedder
    fake_embedder.embed_chunks_from_doc.side_effect = RuntimeError("CUDA OOM")

    fallback_vec = [0.3] * 1024
    import agentic_core.embeddings.bge_runtime as bge_rt

    monkeypatch.setattr(bge_rt, "bge_embed_query", lambda t: fallback_vec)

    with patch(
        "agentic_core.knowledge.retrieval.late_chunking.LateChunkingEmbedder",
        fake_embedder_cls,
    ):
        result = apply_late_chunking(chunks)

    assert result == [fallback_vec]


# ---------------------------------------------------------------------------
# SovereignChromaClient.add_documents — new embeddings param
# ---------------------------------------------------------------------------


def test_chroma_client_rejects_mismatched_embeddings_length():
    """Precomputed embeddings whose length != documents length must raise
    before any Chroma call happens, so silent shape mismatches never leak
    into the index."""
    pytest.importorskip("chromadb")
    from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

    client = SovereignChromaClient.__new__(SovereignChromaClient)
    # Bypass __init__ (which would try to instantiate a real ChromaDB client)
    # by patching just the dispatch path; we only exercise the length check.
    with pytest.raises(ValueError, match="embeddings length"):
        client.add_documents(
            collection_name="any",
            documents=["a", "b", "c"],
            metadatas=[{}, {}, {}],
            embeddings=[[0.1], [0.2]],  # length 2 != 3 documents
        )


def test_chroma_client_uses_precomputed_embeddings_when_provided(monkeypatch):
    """Happy path: precomputed embeddings skip the internal embed_texts
    call, collection.add receives the caller's vectors verbatim."""
    pytest.importorskip("chromadb")
    from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

    client = SovereignChromaClient.__new__(SovereignChromaClient)

    embed_texts_calls: list[list[str]] = []
    client.embed_texts = lambda texts: embed_texts_calls.append(list(texts)) or [[0.0]]

    fake_collection = MagicMock()
    client.get_collection = lambda _name: fake_collection

    # Internal sanitize helper is unused in the branch we're testing but
    # must be wired so add_documents doesn't crash on None.
    client._sanitize_metadata = lambda m: m

    precomputed = [[1.0, 2.0], [3.0, 4.0]]
    client.add_documents(
        collection_name="any",
        documents=["doc1", "doc2"],
        metadatas=[
            {"metadata_version": "v1"},  # skip coercion path
            {"metadata_version": "v1"},
        ],
        embeddings=precomputed,
    )

    # The embedder MUST NOT have been called when embeddings are provided.
    assert embed_texts_calls == []
    # Collection.add receives the caller's vectors unchanged.
    kwargs = fake_collection.add.call_args.kwargs
    assert kwargs["embeddings"] == precomputed
