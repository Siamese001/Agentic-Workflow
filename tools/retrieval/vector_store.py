"""Vector-store adapter for ChromaDB."""

from __future__ import annotations

import atexit
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from tools.mcp.mcp_deferred_loader import DeferredLoader

from .vector_config import (
    CHROMA_INIT_TIMEOUT,
    CHROMA_PATH,
    COUNT_CACHE_TTL,
    DEFAULT_EMBEDDING_MODEL,
    KNOWN_MODEL_DIMS,
    QUERY_COLLECTION_TIMEOUT,
)
from .vector_errors import VectorConflictError, VectorNotFoundError, VectorUnavailableError

logger = logging.getLogger("vector_service")

try:
    import chromadb
    from chromadb.config import Settings
except ImportError as exc:
    chromadb = None  # type: ignore[assignment]
    Settings = None  # type: ignore[assignment]
    _CHROMA_IMPORT_ERROR = exc
else:
    _CHROMA_IMPORT_ERROR = None


def _is_not_found_error(exc: BaseException) -> bool:
    name = exc.__class__.__name__.lower()
    text = str(exc).lower()
    return "notfound" in name or "not found" in text or "does not exist" in text


def check_embedding_alignment(client: Any, model_name: str) -> None:
    """Log an error when configured embedding dimension mismatches stored corpus."""
    configured_dim = KNOWN_MODEL_DIMS.get(model_name)
    if configured_dim is None:
        return

    try:
        collections = client.list_collections()
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError):
        return

    for col in collections:
        metadata = getattr(col, "metadata", {}) or {}
        corpus_dim = metadata.get("embedding_dim")
        if corpus_dim is None:
            continue
        try:
            corpus_dim_int = int(corpus_dim)
        except (TypeError, ValueError):
            continue
        if corpus_dim_int != configured_dim:
            corpus_model = metadata.get("embedding_model", "<unknown>")
            logger.error(
                "EMBEDDING_MISMATCH: configured model=%r (dim=%d) != corpus collection=%r "
                "(embedding_dim=%d, embedding_model=%r). Fix: set VECTOR_DB_EMBEDDING_MODEL to %r.",
                model_name,
                configured_dim,
                getattr(col, "name", "<unknown>"),
                corpus_dim_int,
                corpus_model,
                corpus_model,
            )
            return

    logger.info("EMBEDDING_ALIGNMENT_OK: model=%r dim=%d", model_name, configured_dim)


class ChromaVectorStore:
    """Owns ChromaDB client lifecycle and store-level operations."""

    def __init__(
        self,
        *,
        chroma_path: Path = CHROMA_PATH,
        init_timeout: float = CHROMA_INIT_TIMEOUT,
        query_lock_timeout: float = QUERY_COLLECTION_TIMEOUT,
        count_cache_ttl: float = COUNT_CACHE_TTL,
        client_override: Any | None = None,
    ) -> None:
        self.chroma_path = chroma_path
        self.init_timeout = init_timeout
        self.query_lock_timeout = query_lock_timeout
        self.count_cache_ttl = count_cache_ttl
        self._client_override = client_override
        self._loader = DeferredLoader("chromadb-client", self._create_client, timeout=self.init_timeout)
        self._query_locks: dict[str, threading.Lock] = {}
        self._query_locks_guard = threading.Lock()
        self._count_cache: dict[str, tuple[int, float]] = {}

    @property
    def client_override(self) -> Any | None:
        return self._client_override

    @client_override.setter
    def client_override(self, value: Any | None) -> None:
        self._client_override = value

    def is_loaded(self) -> bool:
        return self._client_override is not None or self._loader.is_loaded()

    def is_loading(self) -> bool:
        if self._client_override is not None:
            return False
        return self._loader.is_loading()

    def ensure_client(self) -> Any:
        if self._client_override is not None:
            return self._client_override
        client = self._loader.get(wait_timeout=self.init_timeout)
        if client is None:
            if self._loader.is_loading():
                raise VectorUnavailableError(
                    "ChromaDB is still initializing. Retry shortly and check stderr for DEFERRED_LOAD logs."
                )
            raise VectorUnavailableError("ChromaDB client is unavailable.")
        return client

    def list_collections(self) -> list[Any]:
        client = self.ensure_client()
        return list(client.list_collections())

    def get_collection(self, name: str) -> Any:
        client = self.ensure_client()
        try:
            return client.get_collection(name)
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            if _is_not_found_error(exc):
                raise VectorNotFoundError(f"Collection {name!r} not found") from exc
            raise

    def create_collection(self, name: str, metadata: dict[str, Any] | None = None) -> Any:
        client = self.ensure_client()
        try:
            client.get_collection(name)
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            if not _is_not_found_error(exc):
                raise
        else:
            raise VectorConflictError(f"Collection {name!r} already exists")
        return client.create_collection(name=name, metadata=metadata)

    def delete_collection(self, name: str) -> None:
        client = self.ensure_client()
        client.delete_collection(name)

    def query_collection(
        self,
        collection_name: str,
        *,
        query_embeddings: list[list[float]],
        n_results: int,
        where: dict[str, Any] | None = None,
        include: list[str] | None = None,
    ) -> Any:
        collection = self.get_collection(collection_name)
        lock = self._get_named_lock(f"query:{collection_name}")
        acquired = lock.acquire(timeout=max(self.query_lock_timeout, 0.0))
        if not acquired:
            raise VectorUnavailableError(
                f"query:{collection_name} busy — could not start after waiting {self.query_lock_timeout:.1f}s"
            )
        try:
            return collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where if where else None,
                include=include,
            )
        finally:
            lock.release()

    def get_cached_count(self, collection_name: str, collection: Any) -> int | None:
        now = time.time()
        cached = self._count_cache.get(collection_name)
        if cached is not None:
            count, fetched_at = cached
            if now - fetched_at < self.count_cache_ttl:
                return count
        try:
            count = int(collection.count())
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError):
            return None
        self._count_cache[collection_name] = (count, now)
        return count

    def disk_usage_bytes(self) -> int | None:
        try:
            return sum(p.stat().st_size for p in self.chroma_path.rglob("*") if p.is_file())
        except (OSError, PermissionError):
            return None

    def _get_named_lock(self, name: str) -> threading.Lock:
        with self._query_locks_guard:
            lock = self._query_locks.get(name)
            if lock is None:
                lock = threading.Lock()
                self._query_locks[name] = lock
            return lock

    def _create_client(self) -> Any:
        if chromadb is None or Settings is None:
            raise RuntimeError(
                f"Vector DB libraries not found: {_CHROMA_IMPORT_ERROR}. "
                "Install with: pip install chromadb sentence-transformers numpy"
            )

        self.chroma_path.mkdir(parents=True, exist_ok=True)
        logger.info("CHROMA_INIT_START: path=%s", self.chroma_path)
        t0 = time.monotonic()
        client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(anonymized_telemetry=False),
        )
        logger.info("CHROMA_INIT_DONE: ready in %.1fs", time.monotonic() - t0)
        check_embedding_alignment(client, DEFAULT_EMBEDDING_MODEL)
        self._register_client_close(client)
        return client

    @staticmethod
    def _register_client_close(client: Any) -> None:
        close_fn = getattr(client, "close", None)
        if not callable(close_fn):
            return

        def _close_client() -> None:
            try:
                close_fn()
            except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError):
                logger.exception("CHROMA_CLOSE_FAIL")

        atexit.register(_close_client)
