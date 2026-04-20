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
from dataclasses import dataclass
from typing import Any

from tools.mcp.mcp_bootstrap import REPO_ROOT, create_mcp_server, run_server
from tools.retrieval.vector_config import (
    ALLOW_MODEL_DOWNLOAD,
    BACKGROUND_PREWARM_ENABLED,
    CHROMA_PATH,
    DEFAULT_EMBEDDING_MODEL,
    MAX_EMBEDDING_BATCH_SIZE,
    MAX_RESULTS,
    MAX_SEARCH_RESULTS,
    validate_startup_config as _validate_startup_config,
)
from tools.retrieval.vector_errors import (
    VectorConflictError,
    VectorNotFoundError,
    VectorServiceError,
    VectorUnavailableError,
    VectorValidationError,
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


@dataclass
class _TextContent:
    text: str


@dataclass
class ToolResultEnvelope:
    isError: bool
    content: list[_TextContent]


def _ok(text: str) -> ToolResultEnvelope:
    return ToolResultEnvelope(isError=False, content=[_TextContent(text=text)])


def _error(text: str) -> ToolResultEnvelope:
    return ToolResultEnvelope(isError=True, content=[_TextContent(text=text)])


def _translate_error(exc: BaseException) -> str:
    if isinstance(exc, VectorValidationError):
        return str(exc)
    if isinstance(exc, VectorConflictError):
        return str(exc)
    if isinstance(exc, VectorNotFoundError):
        return str(exc)
    if isinstance(exc, VectorUnavailableError):
        return str(exc)
    if isinstance(exc, VectorServiceError):
        return str(exc)
    return f"{exc.__class__.__name__}: {exc}"


class VectorDBMCPServer:
    """Backward-compatible async façade used by tests and non-MCP call sites."""

    def __init__(self, *, service: Any | None = None) -> None:
        self.service = service or get_vector_service()

    @property
    def chroma_client(self) -> Any | None:
        return self.service.chroma_client

    @chroma_client.setter
    def chroma_client(self, value: Any | None) -> None:
        self.service.chroma_client = value

    @property
    def embedding_model(self) -> Any | None:
        return self.service.embedding_model

    @embedding_model.setter
    def embedding_model(self, value: Any | None) -> None:
        self.service.embedding_model = value

    async def _ensure_embedding_model(self) -> bool:
        return self.service.ensure_embedding_model()

    async def _create_collection(self, args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(
                self.service.format_create_collection(
                    args["name"],
                    args.get("metadata"),
                )
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _list_collections(self, _args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(self.service.format_list_collections())
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _delete_collection(self, args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(self.service.format_delete_collection(args["name"]))
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _add_documents(self, args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(
                self.service.format_add_documents(
                    args["collection_name"],
                    args["documents"],
                    args.get("metadatas"),
                    args.get("ids"),
                )
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _query_collection(self, args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(
                self.service.format_query_collection(
                    args["collection_name"],
                    args["query_text"],
                    n_results=args.get("n_results", 10),
                    where=args.get("where"),
                    include=args.get("include"),
                )
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _get_collection_info(self, args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(self.service.format_get_collection_info(args["name"]))
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _embed_text(self, args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(
                self.service.format_embed_text(
                    args["texts"],
                    batch_size=args.get("batch_size", 32),
                    return_vectors=bool(args.get("return_vectors", False)),
                )
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _semantic_search(self, args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(
                self.service.format_semantic_search(
                    args["query"],
                    collections=args.get("collections"),
                    n_results=args.get("n_results", 5),
                )
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _vector_stats(self, _args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(self.service.format_vector_stats())
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _readiness(self, _args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(self.service.format_readiness())
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))


# Re-exported module-level helpers for tests and diagnostics
_validate_startup_config = _validate_startup_config
_check_embedding_alignment = _check_embedding_alignment


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
    _start_background_prewarm()
    run_server(mcp)
