"""Chroma collections for apps_rg — precomputed BGE vectors only (no Chroma default EF).

Chroma's ``DefaultEmbeddingFunction`` delegates to ONNX MiniLM (384d), which duplicates
and conflicts with explicit BAAI/bge-m3 (1024d) via ``embed_text`` / ``load_bge_sentence_transformer``.
All apps_rg writes and queries must pass ``embeddings=`` / ``query_embeddings=``; never ``query_texts``.
"""

from __future__ import annotations

import os
from typing import Any

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

FORBID_CHROMA_DEFAULT_EF_ENV = "APPS_RG_FORBID_CHROMA_DEFAULT_EF"
CHROMA_DISABLE_DEFAULT_EMBEDDING_ENV = "CHROMA_DISABLE_DEFAULT_EMBEDDING"

_FORBIDDEN_EF_MESSAGE = (
    "Chroma DefaultEmbeddingFunction (ONNX MiniLM) is forbidden for apps_rg; "
    "use explicit BGE-M3 embeddings via apps_rg.runtime.embedding_settings.load_bge_sentence_transformer "
    "and pass embeddings= / query_embeddings= only."
)


class ForbidChromaDefaultEmbeddingFunction(EmbeddingFunction[Documents]):
    """Placeholder EF so Chroma does not attach DefaultEmbeddingFunction (MiniLM)."""

    def __init__(self) -> None:
        pass

    def __call__(self, input: Documents) -> Embeddings:
        raise RuntimeError(_FORBIDDEN_EF_MESSAGE)

    @staticmethod
    def name() -> str:
        return "apps_rg_forbid_chroma_default_ef"

    def get_config(self) -> dict[str, Any]:
        return {"provider": "apps_rg", "forbidden": True}

    @staticmethod
    def build_from_config(config: dict[str, Any]) -> "ForbidChromaDefaultEmbeddingFunction":
        ForbidChromaDefaultEmbeddingFunction.validate_config(config)
        return ForbidChromaDefaultEmbeddingFunction()

    @staticmethod
    def validate_config(config: dict[str, Any]) -> None:
        return


def chroma_default_ef_forbidden() -> bool:
    if os.environ.get(FORBID_CHROMA_DEFAULT_EF_ENV, "").strip().lower() in (
        "0",
        "false",
        "no",
    ):
        return False
    if os.environ.get(CHROMA_DISABLE_DEFAULT_EMBEDDING_ENV, "").strip().lower() in (
        "0",
        "false",
        "no",
    ):
        return False
    return True


def assert_chroma_default_ef_forbidden() -> None:
    if not chroma_default_ef_forbidden():
        raise RuntimeError(
            f"{FORBID_CHROMA_DEFAULT_EF_ENV} or {CHROMA_DISABLE_DEFAULT_EMBEDDING_ENV} "
            "must be set for apps_rg Chroma access"
        )


def persistent_chroma_client(path: str) -> Any:
    """Create an apps_rg Chroma client through the sanctioned Chroma boundary."""
    import chromadb
    from chromadb.config import Settings

    return chromadb.PersistentClient(
        path=path,
        settings=Settings(anonymized_telemetry=False),
    )


def _collection_embedding_function() -> ForbidChromaDefaultEmbeddingFunction | None:
    if not chroma_default_ef_forbidden():
        return None
    return ForbidChromaDefaultEmbeddingFunction()


# Canonical BAAI/bge-m3 dimensionality. Stored apps_rg vectors must match this; a 384-dim
# Chroma DefaultEmbeddingFunction (MiniLM) collection would silently return zero/garbage hits.
EXPECTED_BGE_DIMENSION = 1024


def assert_collection_embedding_parity(
    collection: Any, *, expected_dim: int = EXPECTED_BGE_DIMENSION
) -> None:
    """Fail loud when a collection's STORED vectors do not match the canonical BGE-M3 dimension (G9).

    A stale embedding alias or a collection accidentally built with Chroma's DefaultEmbeddingFunction
    (384-dim MiniLM) silently returns zero/garbage hits against 1024-dim BGE queries (plan
    apps-rg-e2e-gap-remediation-7e2d9c). We peek one stored vector and compare dimensions. An empty
    collection — or a Chroma version whose ``peek`` omits embeddings — is left to the emptiness gates
    (G2/G6); parity is only assertable when stored vectors exist.
    """
    try:
        peek = collection.peek(limit=1)
    except Exception:  # guardian: allow-broad-exception -- peek API varies by Chroma version; parity is a best-effort diagnostic, never a crash
        return
    embeddings = peek.get("embeddings") if isinstance(peek, dict) else None
    # peek() may return embeddings as a numpy array — never apply truthiness to an array
    # (``if not embeddings`` raises "truth value of an array is ambiguous"). Use len() instead.
    try:
        n_rows = len(embeddings) if embeddings is not None else 0
    except TypeError:
        n_rows = 0
    if n_rows == 0:
        return
    first = embeddings[0]
    try:
        stored_dim = len(first) if first is not None else 0
    except TypeError:
        stored_dim = 0
    if stored_dim and stored_dim != int(expected_dim):
        raise RuntimeError(
            f"C0.2 embedding parity violation: fact_vectors stores {stored_dim}-dim vectors but "
            f"apps_rg queries with {expected_dim}-dim BGE-M3. A stale embedding alias or a "
            f"DefaultEmbeddingFunction-built collection causes silent zero/garbage retrieval. "
            f"Rebuild with: python -m apps_rg bootstrap fact-vectors --strict."
        )


def get_precomputed_embeddings_collection_for_query(client: Any, name: str) -> Any:
    """Open an existing collection for query-only paths (explicit ``query_embeddings`` only).

    Does not attach a new embedding function — avoids EF conflict on legacy collections
    that were created with Chroma ``DefaultEmbeddingFunction``.
    """
    assert_chroma_default_ef_forbidden()
    return client.get_collection(name)


def get_precomputed_embeddings_collection(
    client: Any,
    name: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> Any:
    """Open or create a Chroma collection for **write** paths (upsert/ingest)."""
    assert_chroma_default_ef_forbidden()
    meta = dict(metadata or {})
    meta.setdefault("hnsw:space", "cosine")
    meta.setdefault("apps_rg_embedding_provider", "bge_local_explicit")
    meta.setdefault("chroma_default_ef_forbidden", "true")
    ef = _collection_embedding_function()
    if ef is not None:
        return client.get_or_create_collection(
            name=name,
            metadata=meta,
            embedding_function=ef,
        )
    return client.get_or_create_collection(name=name, metadata=meta)


def collection_uses_chroma_default_ef(collection: Any) -> bool:
    ef = getattr(collection, "_embedding_function", None) or getattr(
        collection, "embedding_function", None
    )
    if ef is None:
        return False
    return type(ef).__name__ == "DefaultEmbeddingFunction"


__all__ = [
    "CHROMA_DISABLE_DEFAULT_EMBEDDING_ENV",
    "FORBID_CHROMA_DEFAULT_EF_ENV",
    "ForbidChromaDefaultEmbeddingFunction",
    "assert_chroma_default_ef_forbidden",
    "chroma_default_ef_forbidden",
    "collection_uses_chroma_default_ef",
    "get_precomputed_embeddings_collection",
    "get_precomputed_embeddings_collection_for_query",
    "persistent_chroma_client",
]
