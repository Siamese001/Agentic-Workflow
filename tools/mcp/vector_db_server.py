#!/usr/bin/env python3
"""
Thin MCP adapter for the vector retrieval service.

This file keeps only transport-facing concerns:
- MCP tool registration
- argument normalization
- error translation
- backward-compatible async test harness methods

All real retrieval/runtime behavior lives in tools.retrieval.vector_service.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

from tools.mcp.mcp_bootstrap import REPO_ROOT, create_mcp_server, guard_single_instance, run_server
from tools.retrieval.vector_config import (
    BACKGROUND_PREWARM_ENABLED,
    validate_startup_config as _validate_startup_config,
)
# MCP-6 (2026-04-22): async facade moved to tools/retrieval/vector_db_async_facade.
# Re-exported here with the original name for callers still using the old path.
from tools.retrieval.vector_db_async_facade import (
    ToolResultEnvelope,
    VectorDBMCPServer,
    _TextContent,
    _error,
    _ok,
    _translate_error,
)
from tools.retrieval.vector_service import get_vector_service
from tools.retrieval.vector_store import check_embedding_alignment as _check_embedding_alignment

logger = logging.getLogger("vector_db_server")
validate_startup = _validate_startup_config  # alias for readability
validate_startup(logger)

mcp = create_mcp_server(
    "vector-db",
    "Thin MCP adapter for vector retrieval. Delegates all retrieval logic to tools.retrieval.vector_service.",
)


# Re-exported module-level helpers for tests and diagnostics.
# (VectorDBMCPServer, ToolResultEnvelope, _TextContent, _ok, _error,
# _translate_error are now imported from tools.retrieval.vector_db_async_facade
# above and re-exported at module level for wire-compatibility with the
# pre-2026-04-22 import path `tools.mcp.vector_db_server.VectorDBMCPServer`.)


@mcp.tool()
def create_collection(name: str, metadata: dict[str, Any] | None = None) -> str:
    return get_vector_service().format_create_collection(name, metadata)


@mcp.tool()
def list_collections() -> str:
    return get_vector_service().format_list_collections()


@mcp.tool()
def delete_collection(name: str) -> str:
    return get_vector_service().format_delete_collection(name)


@mcp.tool()
def add_documents(
    collection_name: str,
    documents: list[str],
    metadatas: list[dict[str, Any]] | None = None,
    ids: list[str] | None = None,
) -> str:
    return get_vector_service().format_add_documents(collection_name, documents, metadatas, ids)


@mcp.tool()
def query_collection(
    collection_name: str,
    query_text: str,
    n_results: int = 10,
    where: dict[str, Any] | None = None,
    include: list[str] | None = None,
) -> str:
    return get_vector_service().format_query_collection(
        collection_name,
        query_text,
        n_results=n_results,
        where=where,
        include=include,
    )


@mcp.tool()
def get_collection_info(name: str) -> str:
    return get_vector_service().format_get_collection_info(name)


@mcp.tool()
def embed_text(texts: list[str], batch_size: int = 32, return_vectors: bool = False) -> str:
    return get_vector_service().format_embed_text(
        texts,
        batch_size=batch_size,
        return_vectors=return_vectors,
    )


@mcp.tool()
def semantic_search(query: str, collections: list[str] | None = None, n_results: int = 5) -> str:
    return get_vector_service().format_semantic_search(
        query,
        collections=collections,
        n_results=n_results,
    )


@mcp.tool()
def vector_stats() -> str:
    return get_vector_service().format_vector_stats()


@mcp.tool()
def readiness() -> str:
    return get_vector_service().format_readiness()


def _start_background_prewarm() -> None:
    """Fire off ChromaDB client + embedding model loading on a daemon thread.

    Without prewarm the first MCP query pays the full cold-load cost (~15-30s
    for BAAI/bge-m3), which produces the appearance of a stall and interacts
    badly with client-side cancellations. Prewarm makes first-query latency
    deterministic.

    Opt out with VECTOR_DB_ENABLE_STARTUP_PREWARM=0 (useful for tests).
    """
    if not BACKGROUND_PREWARM_ENABLED:
        logger.info("PREWARM_SKIPPED: VECTOR_DB_ENABLE_STARTUP_PREWARM=0")
        return

    def _prewarm() -> None:
        t0 = time.monotonic()
        service = get_vector_service()
        try:
            service.store.ensure_client()
            t_chroma = time.monotonic() - t0
            logger.info("PREWARM_CHROMA_READY: %.2fs", t_chroma)
        except (RuntimeError, OSError) as exc:
            logger.warning("PREWARM_CHROMA_FAILED: %s", exc)

        t1 = time.monotonic()
        try:
            service.embedder.ensure_ready()
            t_model = time.monotonic() - t1
            logger.info(
                "PREWARM_MODEL_READY: %.2fs (cumulative %.2fs)",
                t_model,
                time.monotonic() - t0,
            )
        except (RuntimeError, OSError) as exc:
            logger.warning("PREWARM_MODEL_FAILED: %s", exc)

    threading.Thread(
        target=_prewarm,
        daemon=True,
        name="vector-db-prewarm",
    ).start()


if __name__ == "__main__":
    # Use shared guard from mcp_bootstrap (was private _kill_zombie_siblings
    # here pre-2026-04-22 MCP standardization). Same semantics.
    guard_single_instance("vector_db_server.py", skip_env="VECTOR_DB_SKIP_ZOMBIE_KILL")
    _start_background_prewarm()
    run_server(mcp)
