"""Chroma collections must not use DefaultEmbeddingFunction (MiniLM) on apps_rg paths."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from apps_rg.runtime.chroma_precomputed_collection import (
    ForbidChromaDefaultEmbeddingFunction,
    collection_uses_chroma_default_ef,
    get_precomputed_embeddings_collection,
    get_precomputed_embeddings_collection_for_query,
)
from apps_rg.runtime.embedding_settings import apply_apps_rg_embedding_env_guards


@pytest.fixture(autouse=True)
def _forbid_default_ef_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_FORBID_CHROMA_DEFAULT_EF", "1")
    monkeypatch.setenv("CHROMA_DISABLE_DEFAULT_EMBEDDING", "1")


def test_forbid_ef_raises_on_call() -> None:
    ef = ForbidChromaDefaultEmbeddingFunction()
    with pytest.raises(RuntimeError, match="DefaultEmbeddingFunction"):
        ef(["hello"])


def test_collection_does_not_use_chroma_default_ef(tmp_path: Path) -> None:
    apply_apps_rg_embedding_env_guards()
    chromadb = pytest.importorskip("chromadb")
    chroma_dir = tmp_path / "guard"
    client = chromadb.PersistentClient(path=str(chroma_dir))
    col = get_precomputed_embeddings_collection(client, "fact_vectors_test")
    assert collection_uses_chroma_default_ef(col) is False
    ef = getattr(col, "_embedding_function", None) or getattr(col, "embedding_function", None)
    assert isinstance(ef, ForbidChromaDefaultEmbeddingFunction)
    del client


def test_query_open_legacy_default_ef_collection_without_conflict(tmp_path: Path) -> None:
    """Query path uses get_collection only — no EF re-bind on legacy MiniLM collections."""
    chromadb = pytest.importorskip("chromadb")
    client = chromadb.PersistentClient(path=str(tmp_path / "legacy"))
    legacy = client.get_or_create_collection(name="fact_vectors_legacy", metadata={"hnsw:space": "cosine"})
    assert collection_uses_chroma_default_ef(legacy) is True
    opened = get_precomputed_embeddings_collection_for_query(client, "fact_vectors_legacy")
    assert opened.name == "fact_vectors_legacy"


def test_bare_get_or_create_uses_default_ef_without_guard(tmp_path: Path) -> None:
    """Document contrast: unguarded Chroma attach MiniLM default."""
    chromadb = pytest.importorskip("chromadb")
    os.environ.pop("APPS_RG_FORBID_CHROMA_DEFAULT_EF", None)
    client = chromadb.PersistentClient(path=str(tmp_path / "bare"))
    col = client.get_or_create_collection(
        name="unguarded_test",
        metadata={"hnsw:space": "cosine"},
    )
    assert collection_uses_chroma_default_ef(col) is True
