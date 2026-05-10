"""Retrieval service for vector database operations.

This module is the real runtime. It owns:
- embedding lifecycle
- vector-store lifecycle
- request validation
- collection operations
- search orchestration
- metrics / readiness / stats

It intentionally does NOT speak MCP. The MCP adapter imports this service.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any
from uuid import uuid4

from .embedder import EmbeddingRuntime
from .formatters import (
    format_collection_info,
    format_collection_listing,
    format_embed_text,
    format_query_collection,
    format_readiness,
    format_semantic_search,
    format_vector_stats,
)
from .vector_config import (
    BACKGROUND_PREWARM_ENABLED,
    CHROMA_INIT_TIMEOUT,
    CHROMA_PATH,
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_ENCODE_TIMEOUT,
    EMBEDDING_QUEUE_WAIT_TIMEOUT,
    MAX_EMBEDDING_BATCH_SIZE,
    MAX_RESULTS,
    MAX_SEARCH_RESULTS,
    MODEL_LOAD_TIMEOUT,
    QUERY_COLLECTION_TIMEOUT,
    SEARCH_PER_COLLECTION_TIMEOUT,
    SEARCH_GLOBAL_TIMEOUT,
    validate_startup_config,
)
from .vector_errors import (
    VectorConflictError,
    VectorNotFoundError,
    VectorServiceError,
    VectorUnavailableError,
    VectorValidationError,
)
from .vector_schemas import (
    CollectionInfoReport,
    CollectionStat,
    CollectionSummary,
    EmbedTextReport,
    EmbeddingPreview,
    OperationReport,
    QueryCollectionReport,
    QueryHit,
    ReadinessReport,
    SemanticSearchReport,
    VectorStatsReport,
)
from .vector_store import ChromaVectorStore, check_embedding_alignment

logger = logging.getLogger("vector_service")
validate_startup_config(logger)


def _coerce_positive_int(value: Any, *, default: int, max_value: int) -> int:
    try:
        coerced = int(value)
    except (TypeError, ValueError):
        return default
    if coerced < 1:
        return default
    return min(coerced, max_value)


class VectorRetrievalService:
    """Service boundary for all vector retrieval operations."""

    def __init__(
        self,
        *,
        store: ChromaVectorStore | None = None,
        embedder: EmbeddingRuntime | None = None,
    ) -> None:
        self.store = store or ChromaVectorStore()
        self.embedder = embedder or EmbeddingRuntime()
        self._lock = threading.RLock()

    @property
    def chroma_client(self) -> Any | None:
        return self.store.client_override

    @chroma_client.setter
    def chroma_client(self, value: Any | None) -> None:
        self.store.client_override = value

    @property
    def embedding_model(self) -> Any | None:
        return self.embedder.model_override

    @embedding_model.setter
    def embedding_model(self, value: Any | None) -> None:
        self.embedder.model_override = value

    def ensure_embedding_model(self) -> bool:
        self.embedder.ensure_ready()
        return True

    def create_collection(self, name: str, metadata: dict[str, Any] | None = None) -> OperationReport:
        if not name or not str(name).strip():
            raise VectorValidationError("Collection name must be non-empty")
        try:
            collection = self.store.create_collection(str(name), metadata)
        except VectorConflictError:
            raise
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            raise VectorServiceError(str(exc)) from exc
        message = f"Collection '{name}' created successfully\nID: {collection.id}\n"
        if metadata:
            message += f"Metadata: {metadata}\n"
        return OperationReport(message=message)

    def list_collections(self) -> list[CollectionSummary]:
        try:
            collections = self.store.list_collections()
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            raise VectorServiceError(str(exc)) from exc
        summaries: list[CollectionSummary] = []
        for collection in collections:
            summaries.append(
                CollectionSummary(
                    name=getattr(collection, "name", "<unknown>"),
                    id=getattr(collection, "id", "<unknown>"),
                    metadata=getattr(collection, "metadata", None),
                    count=None,
                    count_error=None,
                )
            )
        return summaries

    def delete_collection(self, name: str) -> OperationReport:
        if not name or not str(name).strip():
            raise VectorValidationError("Collection name must be non-empty")
        try:
            self.store.delete_collection(str(name))
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            raise VectorServiceError(str(exc)) from exc
        return OperationReport(message=f"Collection '{name}' deleted successfully")

    def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> OperationReport:
        if len(documents) > MAX_EMBEDDING_BATCH_SIZE:
            raise VectorValidationError(f"Too many documents (max {MAX_EMBEDDING_BATCH_SIZE})")
        if not documents:
            raise VectorValidationError("documents must be non-empty")

        try:
            collection = self.store.get_collection(collection_name)
        except VectorNotFoundError:
            self.store.create_collection(collection_name)
            collection = self.store.get_collection(collection_name)

        t0 = time.time()
        embeddings = self.embedder.encode(documents, batch_size=min(len(documents), MAX_EMBEDDING_BATCH_SIZE))
        embedding_time = time.time() - t0

        if ids is None:
            ids = [str(uuid4()) for _ in range(len(documents))]

        t1 = time.time()
        collection.upsert(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas if metadatas else None,
            ids=ids,
        )
        add_time = time.time() - t1

        return OperationReport(
            message=(
                f"Added {len(documents)} documents to '{collection_name}'\n"
                f"Embedding time: {embedding_time:.2f}s\n"
                f"Add time: {add_time:.2f}s\n"
                f"Total time: {embedding_time + add_time:.2f}s\n"
            )
        )

    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        *,
        n_results: int = 10,
        where: dict[str, Any] | None = None,
        include: list[str] | None = None,
    ) -> QueryCollectionReport:
        # progress_bar: N/A — single-query call, function body is long due to
        # phased timing/logging (embed → chroma query → response assembly) not
        # due to iteration. Bounded by n_results (typ. 10). §16 exempt.
        if not query_text or not query_text.strip():
            raise VectorValidationError("EMPTY_QUERY — query_text must be non-empty")

        requested = _coerce_positive_int(n_results, default=10, max_value=MAX_RESULTS)
        includes = include if include is not None else ["metadatas", "documents", "distances"]

        req_id = uuid4().hex[:8]
        t_start = time.monotonic()

        # Phase 1: model readiness (cold vs warm)
        model_was_loaded = self.embedder.is_loaded()
        ready_start = time.monotonic()
        query_embedding = self.embedder.encode([query_text])
        embed_total_s = time.monotonic() - ready_start
        embedding_time = embed_total_s

        # Phase 2: Chroma query
        chroma_start = time.monotonic()
        results = self.store.query_collection(
            collection_name,
            query_embeddings=query_embedding.tolist(),
            n_results=requested,
            where=where,
            include=includes,
        )
        chroma_s = time.monotonic() - chroma_start
        query_time = chroma_s

        # Phase 3: response assembly
        build_start = time.monotonic()
        documents = results.get("documents", [[]])[0] if results.get("documents") else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

        hits: list[QueryHit] = []
        for idx, doc in enumerate(documents):
            dist = distances[idx] if idx < len(distances) else None
            meta = metadatas[idx] if idx < len(metadatas) else None
            hits.append(
                QueryHit(
                    collection=collection_name,
                    document=doc,
                    distance=float(dist) if dist is not None else None,
                    metadata=meta,
                )
            )
        build_s = time.monotonic() - build_start
        total_s = time.monotonic() - t_start

        logger.info(
            "QUERY_PHASE req=%s collection=%s model_warm=%s embed_s=%.3f chroma_s=%.3f build_s=%.3f total_s=%.3f hits=%d",
            req_id,
            collection_name,
            model_was_loaded,
            embed_total_s,
            chroma_s,
            build_s,
            total_s,
            len(hits),
        )

        return QueryCollectionReport(
            collection_name=collection_name,
            query_text=query_text,
            embedding_time_s=embedding_time,
            query_time_s=query_time,
            requested_results=requested,
            hits=hits,
        )

    def get_collection_info(self, name: str) -> CollectionInfoReport:
        collection = self.store.get_collection(name)

        try:
            count = int(collection.count())
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError):
            count = None

        sample_documents: list[str] = []
        sample_error: str | None = None
        try:
            sample = collection.get(limit=5, include=["metadatas", "documents"])
            sample_documents = list(sample.get("documents") or [])
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            sample_error = str(exc)

        return CollectionInfoReport(
            name=name,
            id=getattr(collection, "id", "<unknown>"),
            document_count=count,
            metadata=getattr(collection, "metadata", None),
            sample_documents=sample_documents,
            sample_error=sample_error,
        )

    def embed_text(
        self, texts: list[str], *, batch_size: int = 32, return_vectors: bool = False
    ) -> EmbedTextReport:
        if len(texts) > MAX_EMBEDDING_BATCH_SIZE:
            raise VectorValidationError(f"Too many texts (max {MAX_EMBEDDING_BATCH_SIZE})")
        if not texts:
            raise VectorValidationError("texts must be non-empty")

        effective_batch = min(batch_size, MAX_EMBEDDING_BATCH_SIZE)
        t0 = time.time()
        embeddings = self.embedder.encode(texts, batch_size=effective_batch)
        processing_time = time.time() - t0
        safe_time = max(processing_time, 1e-9)

        previews: list[EmbeddingPreview] = []
        for text, vector in zip(texts, embeddings):
            as_list = [float(x) for x in vector.tolist()]
            previews.append(
                EmbeddingPreview(
                    text=text,
                    preview=as_list[:5],
                    full_vector=as_list if return_vectors else None,
                )
            )

        dimension = None
        if len(embeddings) > 0:
            try:
                dimension = int(embeddings.shape[1])
            except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError):
                dimension = len(previews[0].full_vector or previews[0].preview)

        return EmbedTextReport(
            texts_processed=len(texts),
            processing_time_s=processing_time,
            embedding_dimension=dimension,
            texts_per_second=len(texts) / safe_time,
            return_vectors=return_vectors,
            previews=previews,
        )

    def semantic_search(
        self,
        query: str,
        *,
        collections: list[str] | None = None,
        n_results: int = 5,
    ) -> SemanticSearchReport:
        if not query or not query.strip():
            raise VectorValidationError("EMPTY_QUERY — query must be non-empty")

        requested = _coerce_positive_int(n_results, default=5, max_value=MAX_SEARCH_RESULTS)

        if not collections:
            collections = [summary.name for summary in self.list_collections()]

        if not collections:
            return SemanticSearchReport(
                query=query,
                collections=[],
                total_search_time_s=0.0,
                hits=[],
                collection_errors={},
            )

        query_embedding = self.embedder.encode([query])

        merged: list[QueryHit] = []
        collection_errors: dict[str, str] = {}
        total_time = 0.0
        global_deadline = time.monotonic() + SEARCH_GLOBAL_TIMEOUT

        for collection_name in collections:
            if time.monotonic() >= global_deadline:
                collection_errors[collection_name] = f"GLOBAL_TIMEOUT (>{SEARCH_GLOBAL_TIMEOUT:.1f}s)"
                continue
            t0 = time.time()
            try:
                results = self.store.query_collection(
                    collection_name,
                    query_embeddings=query_embedding.tolist(),
                    n_results=requested,
                    where=None,
                    include=["metadatas", "documents", "distances"],
                )
            except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
                collection_errors[collection_name] = str(exc)
                continue
            elapsed = time.time() - t0
            total_time += elapsed
            documents = results.get("documents", [[]])[0] if results.get("documents") else []
            distances = results.get("distances", [[]])[0] if results.get("distances") else []
            metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

            for idx, doc in enumerate(documents):
                dist = distances[idx] if idx < len(distances) else None
                meta = metadatas[idx] if idx < len(metadatas) else None
                merged.append(
                    QueryHit(
                        collection=collection_name,
                        document=doc,
                        distance=float(dist) if dist is not None else None,
                        metadata=meta,
                    )
                )

        merged.sort(
            key=lambda hit: (
                hit.distance if hit.distance is not None else float("inf"),
                hit.collection,
                hit.document,
            )
        )

        return SemanticSearchReport(
            query=query,
            collections=collections,
            total_search_time_s=total_time,
            hits=merged,
            collection_errors=collection_errors,
        )

    def vector_stats(self) -> VectorStatsReport:
        collections_raw = self.store.list_collections()
        collection_stats: list[CollectionStat] = []
        total_documents = 0
        for collection in collections_raw:
            count: int | None = None
            count_error: str | None = None
            try:
                count = self.store.get_cached_count(getattr(collection, "name", "<unknown>"), collection)
                if count is not None:
                    total_documents += count
            except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
                count_error = str(exc)
            collection_stats.append(
                CollectionStat(
                    name=getattr(collection, "name", "<unknown>"),
                    count=count,
                    metadata=getattr(collection, "metadata", None),
                    count_error=count_error,
                )
            )

        return VectorStatsReport(
            chroma_path=str(CHROMA_PATH),
            total_collections=len(collections_raw),
            embedding_model=DEFAULT_EMBEDDING_MODEL,
            model_loaded=self.embedder.is_loaded(),
            embedding_dimension=self.embedder.get_dimension(),
            encode_timeout_s=EMBEDDING_ENCODE_TIMEOUT,
            encode_queue_wait_timeout_s=EMBEDDING_QUEUE_WAIT_TIMEOUT,
            query_timeout_s=QUERY_COLLECTION_TIMEOUT,
            search_per_collection_timeout_s=SEARCH_PER_COLLECTION_TIMEOUT,
            background_prewarm_enabled=BACKGROUND_PREWARM_ENABLED,
            collections=collection_stats,
            total_documents=total_documents,
            disk_bytes=self.store.disk_usage_bytes(),
        )

    def readiness(self) -> ReadinessReport:
        return ReadinessReport(
            chroma_ready=self.store.is_loaded(),
            chroma_loading=self.store.is_loading(),
            embedding_model_ready=self.embedder.is_loaded(),
            embedding_model_loading=self.embedder.is_loading(),
            chroma_timeout_s=CHROMA_INIT_TIMEOUT,
            model_timeout_s=MODEL_LOAD_TIMEOUT,
            encode_timeout_s=EMBEDDING_ENCODE_TIMEOUT,
            query_timeout_s=QUERY_COLLECTION_TIMEOUT,
            background_prewarm_enabled=BACKGROUND_PREWARM_ENABLED,
        )

    # Convenience helpers for the adapter layer
    def format_create_collection(self, name: str, metadata: dict[str, Any] | None = None) -> str:
        return self.create_collection(name, metadata).message

    def format_list_collections(self) -> str:
        return format_collection_listing(self.list_collections())

    def format_delete_collection(self, name: str) -> str:
        return self.delete_collection(name).message

    def format_add_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> str:
        return self.add_documents(collection_name, documents, metadatas, ids).message

    def format_query_collection(
        self,
        collection_name: str,
        query_text: str,
        *,
        n_results: int = 10,
        where: dict[str, Any] | None = None,
        include: list[str] | None = None,
    ) -> str:
        return format_query_collection(
            self.query_collection(
                collection_name,
                query_text,
                n_results=n_results,
                where=where,
                include=include,
            )
        )

    def format_get_collection_info(self, name: str) -> str:
        return format_collection_info(self.get_collection_info(name))

    def format_embed_text(
        self, texts: list[str], *, batch_size: int = 32, return_vectors: bool = False
    ) -> str:
        return format_embed_text(self.embed_text(texts, batch_size=batch_size, return_vectors=return_vectors))

    def format_semantic_search(
        self,
        query: str,
        *,
        collections: list[str] | None = None,
        n_results: int = 5,
    ) -> str:
        return format_semantic_search(
            self.semantic_search(query, collections=collections, n_results=n_results)
        )

    def format_vector_stats(self) -> str:
        return format_vector_stats(self.vector_stats())

    def format_readiness(self) -> str:
        return format_readiness(self.readiness())


_service_singleton: VectorRetrievalService | None = None
_service_lock = threading.Lock()


def get_vector_service() -> VectorRetrievalService:
    """Return the singleton retrieval service used by the MCP adapter."""
    global _service_singleton
    if _service_singleton is not None:
        return _service_singleton
    with _service_lock:
        if _service_singleton is None:
            _service_singleton = VectorRetrievalService()
    return _service_singleton


__all__ = [
    "VectorRetrievalService",
    "get_vector_service",
    "check_embedding_alignment",
]
