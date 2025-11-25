"""ChromaDB Vector Store - Infrastructure Layer

This module provides ChromaDB integration for vector storage and retrieval.

Layer: Infrastructure/Meta
Responsibilities:
- Chroma client initialization
- Collection management
- Hybrid search
- Semantic cache operations

Non-responsibilities:
- Prompt knowledge
- Agent logic
- Workflow plans
- Business logic
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Sequence


class ChromaNotConfiguredError(RuntimeError):
    """Raised when Chroma usage is requested but not configured/enabled."""


class ChromaClientError(RuntimeError):
    """Raised when the underlying Chroma client cannot be created or used."""


@dataclass
class ChromaConfig:
    """Configuration for connecting to a ChromaDB instance."""

    collection_name: str
    persist_directory: Optional[str] = None
    require_collection: bool = True


def _import_chromadb():
    """Import the chromadb package using provider isolation."""
    from providers.chromadb_client import ChromaClient
    return ChromaClient


def init_chroma_client(cfg: ChromaConfig):
    """Initialise a Chroma client and return (client, collection)."""

    if not cfg.collection_name:
        raise ChromaNotConfiguredError("ChromaConfig.collection_name must be set")

    chromadb = _import_chromadb()

    try:
        client = chromadb.Client(
            chromadb.config.Settings(
                is_persistent=bool(cfg.persist_directory),
                persist_directory=cfg.persist_directory,
            )
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        raise ChromaClientError(f"Failed to create Chroma client: {exc}") from exc

    try:
        try:
            collection = client.get_collection(cfg.collection_name)
        except Exception:
            if cfg.require_collection:
                raise
            collection = client.create_collection(cfg.collection_name)
    except Exception as exc:  # pragma: no cover - environment dependent
        raise ChromaClientError(
            f"Failed to access Chroma collection {cfg.collection_name!r}: {exc}"
        ) from exc

    return client, collection


def chroma_hybrid_search(
    collection,
    query_texts: Sequence[str],
    *,
    n_results: int = 20,
    where: Optional[Dict[str, Any]] = None,
    where_document: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run a hybrid (dense + lexical) search over a Chroma collection.

    This is a thin wrapper around ``collection.query``. It returns the
    raw Chroma response so that higher layers can adapt it into Evidence
    objects or other structures.
    """

    try:
        return collection.query(
            query_texts=list(query_texts),
            n_results=n_results,
            where=where,
            where_document=where_document,
        )
    except Exception as exc:  # pragma: no cover - network/dependency dependent
        raise ChromaClientError(f"Chroma query failed: {exc}") from exc


def chroma_semantic_cache_lookup(
    collection,
    query_texts: Sequence[str],
    *,
    n_results: int = 1,
    where: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Look up cached results from a Chroma collection.

    This is a thin wrapper around ``collection.query`` for semantic cache lookups.
    Returns the raw Chroma response.
    """

    try:
        return collection.query(
            query_texts=list(query_texts),
            n_results=n_results,
            where=where,
        )
    except Exception as exc:  # pragma: no cover - network/dependency dependent
        raise ChromaClientError(f"Chroma cache lookup failed: {exc}") from exc


def chroma_semantic_cache_upsert(
    collection,
    ids: Sequence[str],
    documents: Sequence[str],
    metadatas: Optional[Sequence[Dict[str, Any]]] = None,
) -> None:
    """Upsert documents into a Chroma collection for semantic caching.

    The caller is responsible for providing stable IDs and any metadata
    required to later filter or interpret cached entries.
    """

    if len(ids) != len(documents):
        raise ValueError("ids and documents must have the same length")

    try:
        collection.upsert(
            ids=list(ids),
            documents=list(documents),
            metadatas=list(metadatas) if metadatas is not None else None,
        )
    except Exception as exc:  # pragma: no cover - network/dependency dependent
        raise ChromaClientError(f"Chroma upsert failed: {exc}") from exc



