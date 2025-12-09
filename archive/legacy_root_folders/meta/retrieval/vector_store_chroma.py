from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from infra.storage.vector_store_chroma import (
    chroma_hybrid_search as _core_chroma_hybrid_search,
    chroma_semantic_cache_lookup as _core_chroma_semantic_cache_lookup,
    chroma_semantic_cache_upsert as _core_chroma_semantic_cache_upsert,
)


def chroma_hybrid_search(collection, query_texts: Sequence[str], n_results: int) -> Dict[str, Any]:
    """META wrapper for Chroma hybrid search.

    Delegates to the core vector_store_chroma implementation.
    """

    return _core_chroma_hybrid_search(collection, query_texts=query_texts, n_results=n_results)


def chroma_semantic_cache_lookup(collection, query_texts: Sequence[str], n_results: int) -> Dict[str, Any]:
    """META wrapper for Chroma-based semantic cache lookup."""

    return _core_chroma_semantic_cache_lookup(collection, query_texts=query_texts, n_results=n_results)


def chroma_semantic_cache_upsert(
    collection,
    ids: Sequence[str],
    documents: Sequence[str],
    metadatas: Optional[Sequence[Dict[str, Any]]] = None,
) -> None:
    """META wrapper for Chroma-based semantic cache upsert."""

    _core_chroma_semantic_cache_upsert(
        collection,
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )




