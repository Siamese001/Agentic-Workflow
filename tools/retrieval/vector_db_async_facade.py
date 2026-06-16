"""Async facade for ``VectorService`` — test harness and non-MCP call sites.

Why this module exists
----------------------
Prior to 2026-04-22 this class lived inside ``tools/mcp/vector_db_server.py``
as ``VectorDBMCPServer`` (~115 lines, half the transport file). It was
documented as "backward-compatible async façade used by tests and non-MCP
call sites" — which means it wasn't transport code. Having it in the MCP
entry file mixed two concerns:

1. MCP transport registration (``@mcp.tool()`` decorators).
2. Test-facing async wrappers returning envelope objects.

The transport file should only handle (1). This module owns (2).

Wire-compatibility
------------------
The class name and all method signatures are preserved. Callers who were
importing ``from tools.mcp.vector_db_server import VectorDBMCPServer``
should update their imports to this module. A thin re-export shim in
``vector_db_server.py`` preserves the old import path for one deprecation
cycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.retrieval.vector_errors import (
    VectorConflictError,
    VectorNotFoundError,
    VectorServiceError,
    VectorUnavailableError,
    VectorValidationError,
)
from tools.retrieval.vector_service import get_vector_service


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

    async def _health_snapshot(self, _args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(self.service.format_health_snapshot())
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))

    async def _readiness(self, _args: dict[str, Any]) -> ToolResultEnvelope:
        try:
            return _ok(self.service.format_readiness())
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            return _error(_translate_error(exc))


__all__ = [
    "VectorDBMCPServer",
    "ToolResultEnvelope",
    "_TextContent",
    "_ok",
    "_error",
    "_translate_error",
]
