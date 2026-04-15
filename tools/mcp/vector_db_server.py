#!/usr/bin/env python3
"""
Vector DB MCP Server - ChromaDB-backed vector storage and semantic search.

Uses shared mcp_bootstrap for standardized startup (repo-root, logging, FastMCP,
env safety) and mcp_deferred_loader for lazy embedding model loading.
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import queue
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from tools.mcp.mcp_bootstrap import REPO_ROOT, create_mcp_server, run_server
from tools.mcp.mcp_deferred_loader import DeferredLoader

try:
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    print(f"Vector DB libraries not found: {e}", file=sys.stderr)
    print("Install with: pip install chromadb sentence-transformers numpy", file=sys.stderr)
    sys.exit(1)

logger = logging.getLogger(__name__)

_raw_chroma_path = os.environ.get("VECTOR_DB_CHROMA_PATH", "")
CHROMA_PATH: Path = Path(_raw_chroma_path) if _raw_chroma_path else REPO_ROOT / "data" / "cache" / "chromadb"
DEFAULT_EMBEDDING_MODEL: str = os.environ.get("VECTOR_DB_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
ALLOW_MODEL_DOWNLOAD: bool = os.environ.get("VECTOR_DB_ALLOW_MODEL_DOWNLOAD", "0").strip() == "1"
MODEL_LOAD_TIMEOUT: float = float(os.environ.get("VECTOR_DB_MODEL_LOAD_TIMEOUT", "120"))
CHROMA_INIT_TIMEOUT: float = float(os.environ.get("VECTOR_DB_CHROMA_INIT_TIMEOUT", "30"))
EMBEDDING_ENCODE_TIMEOUT: float = float(os.environ.get("VECTOR_DB_ENCODE_TIMEOUT", "20"))
EMBEDDING_QUEUE_WAIT_TIMEOUT: float = float(os.environ.get("VECTOR_DB_ENCODE_QUEUE_WAIT_TIMEOUT", "10"))
QUERY_COLLECTION_TIMEOUT: float = float(os.environ.get("VECTOR_DB_QUERY_COLLECTION_TIMEOUT", "20"))
SEARCH_PER_COLLECTION_TIMEOUT: float = float(os.environ.get("VECTOR_DB_SEARCH_PER_COLLECTION_TIMEOUT", "15"))
SEARCH_GLOBAL_TIMEOUT: float = float(os.environ.get("VECTOR_DB_SEARCH_GLOBAL_TIMEOUT", "60"))
PREWARM_QUERY_TEXT: str = os.environ.get("VECTOR_DB_PREWARM_QUERY_TEXT", "warmup")


def _parse_float_env(name: str, default: float, min_val: float = 0.0) -> float:
    raw = os.environ.get(name, "")
    if not raw:
        return default
    try:
        val = float(raw)
    except ValueError:
        logger.error("Invalid value for %s=%r — must be a number; using default %.1f", name, raw, default)
        return default
    if val < min_val:
        logger.error(
            "Invalid value for %s=%s — must be >= %.1f; using default %.1f", name, raw, min_val, default
        )
        return default
    return val


def _parse_int_env(name: str, default: int, min_val: int = 1) -> int:
    raw = os.environ.get(name, "")
    if not raw:
        return default
    try:
        val = int(raw)
    except ValueError:
        logger.error("Invalid value for %s=%r — must be an integer; using default %d", name, raw, default)
        return default
    if val < min_val:
        logger.error("Invalid value for %s=%d — must be >= %d; using default %d", name, val, min_val, default)
        return default
    return val


MAX_RESULTS: int = _parse_int_env("VECTOR_DB_MAX_QUERY_RESULTS", 100)
MAX_EMBEDDING_BATCH_SIZE: int = _parse_int_env("VECTOR_DB_MAX_BATCH", 32)
MAX_SEARCH_RESULTS: int = _parse_int_env("VECTOR_DB_MAX_SEARCH_RESULTS", 20)
QUERY_EMBED_BATCH_WINDOW_MS: float = _parse_float_env("VECTOR_DB_QUERY_BATCH_WINDOW_MS", 15.0, min_val=0.0)
QUERY_EMBED_MAX_BATCH: int = _parse_int_env("VECTOR_DB_QUERY_EMBED_MAX_BATCH", 8)

_KNOWN_MODEL_DIMS: dict[str, int] = {
    "BAAI/bge-m3": 1024,
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "text-embedding-ada-002": 1536,
}

mcp = create_mcp_server(
    "vector-db",
    "ChromaDB-backed vector storage and semantic search. "
    "Provides embeddings, similarity queries, and collection management.",
)

_COUNT_CACHE: dict[str, tuple[int, float]] = {}
_COUNT_CACHE_TTL: float = 60.0
_COLLECTION_LOCKS: dict[str, threading.Lock] = {}
_COLLECTION_LOCKS_GUARD = threading.Lock()
_PREWARM_STATE: dict[str, Any] = {"phase": "idle", "total": 0, "done": 0, "current": "", "last_error": ""}


@dataclass
class _QueryEmbeddingRequest:
    text: str
    event: threading.Event = field(default_factory=threading.Event)
    result: Any | None = None
    error: BaseException | None = None


class QueryEmbeddingBatcher:
    """Micro-batch single-query embedding requests to avoid serialized pileups."""

    def __init__(
        self,
        *,
        batch_window_ms: float,
        max_batch_size: int,
        encode_timeout_s: float,
        queue_wait_timeout_s: float,
    ) -> None:
        self.batch_window_ms = max(batch_window_ms, 0.0)
        self.max_batch_size = max(1, max_batch_size)
        self.encode_timeout_s = encode_timeout_s
        self.queue_wait_timeout_s = queue_wait_timeout_s
        self._pending: list[_QueryEmbeddingRequest] = []
        self._pending_lock = threading.Lock()
        self._drain_active = False

    def encode_one(self, text: str, *, op_name: str) -> Any:
        request = _QueryEmbeddingRequest(text=text)
        self._enqueue(request)

        total_wait = self.queue_wait_timeout_s + self.encode_timeout_s + (self.batch_window_ms / 1000.0) + 1.0
        if not request.event.wait(timeout=max(total_wait, 0.1)):
            raise TimeoutError(f"{op_name} timed out after {total_wait:.1f}s waiting for batched embedding")

        if request.error is not None:
            raise request.error

        return request.result

    def _enqueue(self, request: _QueryEmbeddingRequest) -> None:
        should_start_worker = False
        with self._pending_lock:
            self._pending.append(request)
            if not self._drain_active:
                self._drain_active = True
                should_start_worker = True

        if should_start_worker:
            threading.Thread(
                target=self._drain_loop,
                daemon=True,
                name="query-embedding-batcher",
            ).start()

    def _drain_loop(self) -> None:
        if self.batch_window_ms > 0:
            time.sleep(self.batch_window_ms / 1000.0)

        while True:
            with self._pending_lock:
                if not self._pending:
                    self._drain_active = False
                    return
                batch = self._pending[: self.max_batch_size]
                del self._pending[: self.max_batch_size]

            texts = [request.text for request in batch]
            try:
                embeddings = _encode_with_guard(
                    f"encode:query_batch:{len(texts)}",
                    texts,
                )
                if len(embeddings) != len(batch):
                    raise RuntimeError(
                        f"batched encode length mismatch: expected {len(batch)} got {len(embeddings)}"
                    )
            except BaseException as exc:  # guardian: allow-broad-except -- batch boundary
                for request in batch:
                    request.error = exc
                    request.event.set()
                continue

            for index, request in enumerate(batch):
                request.result = embeddings[index : index + 1]
                request.event.set()


def _get_named_lock(name: str) -> threading.Lock:
    with _COLLECTION_LOCKS_GUARD:
        lock = _COLLECTION_LOCKS.get(name)
        if lock is None:
            lock = threading.Lock()
            _COLLECTION_LOCKS[name] = lock
        return lock


def _set_prewarm_state(**updates: Any) -> None:
    _PREWARM_STATE.update(updates)


def _register_client_close(client: Any) -> None:
    close_fn = getattr(client, "close", None)
    if not callable(close_fn):
        return

    def _close_client() -> None:
        try:
            close_fn()
        except Exception:
            logger.exception("CHROMA_CLOSE_FAIL")

    atexit.register(_close_client)


def _release_lock_when_worker_finishes(lock: threading.Lock, worker: threading.Thread, op_name: str) -> None:
    def _releaser() -> None:
        worker.join()
        lock.release()
        logger.info("SINGLE_FLIGHT_RELEASED: %s finished after timeout", op_name)

    threading.Thread(
        target=_releaser,
        daemon=True,
        name=f"{op_name}-release",
    ).start()


def _run_single_flight_with_timeout(
    *,
    lock: threading.Lock,
    fn: Any,
    op_name: str,
    call_timeout_s: float,
    acquire_timeout_s: float | None = None,
) -> Any:
    effective_acquire_timeout = call_timeout_s if acquire_timeout_s is None else acquire_timeout_s
    acquired = lock.acquire(timeout=max(effective_acquire_timeout, 0.0))
    if not acquired:
        raise TimeoutError(
            f"{op_name} could not start after waiting {effective_acquire_timeout:.1f}s for the prior call"
        )

    result_q: queue.Queue[tuple[bool, object]] = queue.Queue(maxsize=1)

    def _worker() -> None:
        try:
            result_q.put((True, fn()))
        except BaseException as exc:  # guardian: allow-broad-except -- worker boundary
            result_q.put((False, exc))

    worker = threading.Thread(target=_worker, daemon=True, name=f"{op_name}-worker")
    worker.start()

    try:
        ok, payload = result_q.get(timeout=call_timeout_s)
    except queue.Empty as exc:
        logger.warning(
            "SINGLE_FLIGHT_TIMEOUT: %s — no result after %.1fs; quarantining subsequent calls until worker exits",
            op_name,
            call_timeout_s,
        )
        _release_lock_when_worker_finishes(lock, worker, op_name)
        raise TimeoutError(f"{op_name} timed out after {call_timeout_s:.1f}s") from exc

    lock.release()
    if ok:
        return payload
    raise payload  # type: ignore[misc]


def _init_chroma() -> chromadb.PersistentClient:
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    logger.info("CHROMA_INIT_START: path=%s — loading HNSW indexes from disk...", CHROMA_PATH)
    t0 = time.monotonic()
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False),
    )
    elapsed = time.monotonic() - t0
    logger.info("CHROMA_INIT_DONE: ready in %.1fs", elapsed)
    _check_embedding_alignment(client, DEFAULT_EMBEDDING_MODEL)
    _register_client_close(client)
    return client


def _load_embedding_model():
    _old_tqdm_disable = os.environ.get("TQDM_DISABLE")
    os.environ["TQDM_DISABLE"] = "1"
    try:
        from sentence_transformers import SentenceTransformer
    finally:
        if _old_tqdm_disable is None:
            os.environ.pop("TQDM_DISABLE", None)
        else:
            os.environ["TQDM_DISABLE"] = _old_tqdm_disable

    if not ALLOW_MODEL_DOWNLOAD:
        os.environ["HF_HUB_OFFLINE"] = "1"

    t0 = time.monotonic()
    try:
        model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL, local_files_only=True)
        logger.info(
            "MODEL_LOAD_CACHE: model=%r loaded in %.2fs", DEFAULT_EMBEDDING_MODEL, time.monotonic() - t0
        )
        return model
    except (OSError, ValueError):
        if not ALLOW_MODEL_DOWNLOAD:
            raise RuntimeError(
                f"model {DEFAULT_EMBEDDING_MODEL!r} not in local cache; "
                "set VECTOR_DB_ALLOW_MODEL_DOWNLOAD=1 to allow online download"
            )
        logger.warning("MODEL_LOAD_ONLINE: downloading %r from HuggingFace", DEFAULT_EMBEDDING_MODEL)
        model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)
        logger.info("MODEL_LOAD_ONLINE: complete in %.2fs", time.monotonic() - t0)
        return model


_embedding_loader = DeferredLoader(
    "embedding-model",
    _load_embedding_model,
    timeout=MODEL_LOAD_TIMEOUT,
)


def _check_embedding_alignment(client: chromadb.PersistentClient, model_name: str) -> None:
    configured_dim = _KNOWN_MODEL_DIMS.get(model_name)
    if configured_dim is None:
        return
    try:
        collections = client.list_collections()
    except (RuntimeError, ValueError):
        return
    for col in collections:
        corpus_dim = (col.metadata or {}).get("embedding_dim")
        if corpus_dim is None:
            continue
        try:
            corpus_dim_int = int(corpus_dim)
        except (TypeError, ValueError):
            continue
        if corpus_dim_int != configured_dim:
            corpus_model = (col.metadata or {}).get("embedding_model", "<unknown>")
            logger.error(
                "EMBEDDING_MISMATCH: configured model=%r (dim=%d) != corpus collection=%r "
                "(embedding_dim=%d, embedding_model=%r). "
                "Fix: set VECTOR_DB_EMBEDDING_MODEL to %r in mcp_config.json.",
                model_name,
                configured_dim,
                col.name,
                corpus_dim_int,
                corpus_model,
                corpus_model,
            )
            return
    logger.info("EMBEDDING_ALIGNMENT_OK: model=%r dim=%d", model_name, configured_dim)


_chroma_loader = DeferredLoader(
    "chromadb-client",
    _init_chroma,
    timeout=CHROMA_INIT_TIMEOUT,
)


def _get_chroma() -> chromadb.PersistentClient | None:
    return _chroma_loader.get()  # type: ignore[return-value]


def _require_chroma() -> chromadb.PersistentClient:
    if not _chroma_loader.is_loaded():
        _chroma_loader.get(wait_timeout=0)
        raise RuntimeError(
            "ChromaDB is still initializing (HNSW indexes loading from disk). "
            f"Retry in a few seconds. Timeout: {CHROMA_INIT_TIMEOUT:.0f}s. "
            "Check server stderr for CHROMA_INIT_DONE to confirm readiness."
        )
    return _chroma_loader.require()  # type: ignore[return-value]


def _require_model_ready():
    if not _embedding_loader.is_loaded():
        _embedding_loader.get(wait_timeout=0)
        raise RuntimeError(
            "Embedding model is still initializing. Retry in a few seconds. "
            f"Timeout: {MODEL_LOAD_TIMEOUT:.0f}s. "
            "Check server stderr for PREWARM_PHASE_2_DONE to confirm readiness."
        )
    return _embedding_loader.require()


def _encode_with_guard(op_name: str, *args: Any, **kwargs: Any) -> Any:
    def _encode(model: Any) -> Any:
        return model.encode(*args, **kwargs)

    return _embedding_loader.call_serialized(
        _encode,
        wait_timeout=0,
        call_timeout=EMBEDDING_ENCODE_TIMEOUT,
        queue_wait_timeout=EMBEDDING_QUEUE_WAIT_TIMEOUT,
        op_name=op_name,
    )


_query_embedding_batcher = QueryEmbeddingBatcher(
    batch_window_ms=QUERY_EMBED_BATCH_WINDOW_MS,
    max_batch_size=min(QUERY_EMBED_MAX_BATCH, MAX_EMBEDDING_BATCH_SIZE),
    encode_timeout_s=EMBEDDING_ENCODE_TIMEOUT,
    queue_wait_timeout_s=EMBEDDING_QUEUE_WAIT_TIMEOUT,
)


def _encode_query_text(query_text: str, *, op_name: str) -> Any:
    return _query_embedding_batcher.encode_one(query_text, op_name=op_name)


def _query_collection_with_timeout(
    collection: Any,
    *,
    query_embeddings: list[list[float]],
    n_results: int,
    where: dict | None,
    include: list[str],
    collection_name: str,
    timeout_s: float | None = None,
    op_name: str = "query_collection",
) -> Any:
    lock = _get_named_lock(f"query:{collection_name}")
    effective_timeout = QUERY_COLLECTION_TIMEOUT if timeout_s is None else timeout_s
    return _run_single_flight_with_timeout(
        lock=lock,
        fn=lambda: collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where if where else None,
            include=include,
        ),
        op_name=f"{op_name}:{collection_name}",
        call_timeout_s=effective_timeout,
        acquire_timeout_s=effective_timeout,
    )


def _get_cached_count(collection_name: str, collection: Any) -> int | None:
    now = time.time()
    cached = _COUNT_CACHE.get(collection_name)
    if cached is not None:
        count, fetched_at = cached
        if now - fetched_at < _COUNT_CACHE_TTL:
            return count

    try:
        count = _run_single_flight_with_timeout(
            lock=_get_named_lock(f"count:{collection_name}"),
            fn=collection.count,
            op_name=f"count:{collection_name}",
            call_timeout_s=2.0,
            acquire_timeout_s=2.0,
        )
        _COUNT_CACHE[collection_name] = (count, now)
        return count
    except TimeoutError:
        logger.warning("COUNT_TIMEOUT: collection=%r", collection_name)
        return None
    except (RuntimeError, ValueError, OSError) as exc:
        logger.warning("COUNT_ERROR: collection=%r error=%s", collection_name, exc)
        return None


def _prewarm_hnsw_indexes(client: chromadb.PersistentClient, model: Any) -> None:
    """Force first-query HNSW initialization for all non-empty collections."""
    try:
        warm_embedding = model.encode([PREWARM_QUERY_TEXT]).tolist()
        model_dim = len(warm_embedding[0]) if warm_embedding and warm_embedding[0] else None
    except Exception as exc:  # guardian: allow-broad-except -- warmup must not crash server
        logger.warning("PREWARM_HNSW_EMBED_FAIL: %s", exc)
        warm_embedding = None
        model_dim = None

    try:
        collections = client.list_collections()
    except (RuntimeError, ValueError) as exc:
        logger.error("PREWARM_HNSW_FAIL: unable to list collections: %s", exc)
        _set_prewarm_state(phase="warmup_failed", last_error=str(exc))
        return

    candidates: list[tuple[int, str, Any, int | None]] = []
    for col_meta in collections:
        collection_name = col_meta.name
        try:
            collection = client.get_collection(collection_name)
            doc_count = collection.count()
        except (RuntimeError, ValueError, chromadb.errors.ChromaError) as exc:
            logger.warning("PREWARM_HNSW_SKIP: collection=%r count/get failed: %s", collection_name, exc)
            continue

        if doc_count <= 0:
            logger.info("PREWARM_HNSW_SKIP: collection=%r empty", collection_name)
            continue

        metadata = col_meta.metadata or {}
        embedding_dim = metadata.get("embedding_dim")
        try:
            dim = int(embedding_dim) if embedding_dim is not None else None
        except (TypeError, ValueError):
            dim = None
        if dim is None:
            dim = model_dim

        candidates.append((doc_count, collection_name, collection, dim))

    candidates.sort(key=lambda item: item[0], reverse=True)
    _set_prewarm_state(phase="warming_hnsw", total=len(candidates), done=0, current="", last_error="")

    for index, (doc_count, collection_name, collection, dim) in enumerate(candidates, start=1):
        _set_prewarm_state(current=collection_name)
        if warm_embedding is not None and model_dim is not None and dim == model_dim:
            query_embeddings = warm_embedding
        elif dim is not None:
            query_embeddings = [[0.0] * dim]
        else:
            logger.warning("PREWARM_HNSW_SKIP: collection=%r missing embedding dimension", collection_name)
            _set_prewarm_state(done=index)
            continue

        t0 = time.monotonic()
        try:
            collection.query(
                query_embeddings=query_embeddings,
                n_results=1,
                include=["distances"],
            )
            logger.info(
                "PREWARM_HNSW_DONE: collection=%r docs=%d dim=%s elapsed=%.2fs",
                collection_name,
                doc_count,
                dim,
                time.monotonic() - t0,
            )
        except (RuntimeError, ValueError, chromadb.errors.ChromaError) as exc:
            logger.warning("PREWARM_HNSW_FAIL: collection=%r error=%s", collection_name, exc)
            _set_prewarm_state(last_error=f"{collection_name}: {exc}")
        finally:
            _set_prewarm_state(done=index)

    _set_prewarm_state(phase="ready", current="")


@mcp.tool()
def create_collection(name: str, metadata: dict[str, str] | None = None) -> str:
    client = _require_chroma()
    try:
        client.get_collection(name)
        return f"Collection '{name}' already exists"
    except chromadb.errors.NotFoundError:
        pass
    collection = client.create_collection(name=name, metadata=metadata)
    result = f"Collection '{name}' created successfully\nID: {collection.id}\n"
    if metadata:
        result += f"Metadata: {json.dumps(metadata, indent=2)}\n"
    return result


@mcp.tool()
def list_collections() -> str:
    client = _require_chroma()
    collections = client.list_collections()
    result = f"Vector Collections ({len(collections)} total):\n\n"
    for collection in collections:
        result += f"📁 {collection.name}\n"
        result += f"   ID: {collection.id}\n"
        if collection.metadata:
            result += f"   Metadata: {json.dumps(collection.metadata, indent=6)}\n"
        result += "   Count: use get_collection_info or vector_stats\n\n"
    return result


@mcp.tool()
def delete_collection(name: str) -> str:
    client = _require_chroma()
    client.delete_collection(name)
    return f"Collection '{name}' deleted successfully"


@mcp.tool()
def add_documents(
    collection_name: str,
    documents: list[str],
    metadatas: list[dict] | None = None,
    ids: list[str] | None = None,
) -> str:
    client = _require_chroma()
    _require_model_ready()

    if len(documents) > MAX_EMBEDDING_BATCH_SIZE:
        return f"Too many documents (max {MAX_EMBEDDING_BATCH_SIZE})"

    collection = client.get_collection(collection_name)

    t0 = time.time()
    embeddings = _encode_with_guard(
        f"encode:add_documents:{collection_name}",
        documents,
    )
    embedding_time = time.time() - t0

    if not ids:
        ids = [str(uuid4()) for _ in range(len(documents))]

    t1 = time.time()
    collection.upsert(
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas if metadatas else None,
        ids=ids,
    )
    add_time = time.time() - t1

    return (
        f"Added {len(documents)} documents to '{collection_name}'\n"
        f"Embedding time: {embedding_time:.2f}s\n"
        f"Add time: {add_time:.2f}s\n"
        f"Total time: {embedding_time + add_time:.2f}s\n"
    )


@mcp.tool()
def query_collection(
    collection_name: str,
    query_text: str,
    n_results: int = 10,
    where: dict | None = None,
    include: list[str] | None = None,
) -> str:
    client = _require_chroma()
    _require_model_ready()

    if not query_text.strip():
        return "Error: EMPTY_QUERY — query_text must be non-empty"

    n_results = min(n_results, MAX_RESULTS)
    if include is None:
        include = ["metadatas", "documents", "distances"]

    collection = client.get_collection(collection_name)

    t0 = time.time()
    query_embedding = _encode_query_text(
        query_text,
        op_name=f"encode:query_collection:{collection_name}",
    )
    embedding_time = time.time() - t0

    t1 = time.time()
    results = _query_collection_with_timeout(
        collection,
        query_embeddings=query_embedding.tolist(),
        n_results=n_results,
        where=where,
        include=include,
        collection_name=collection_name,
        timeout_s=QUERY_COLLECTION_TIMEOUT,
        op_name="query_collection",
    )
    query_time = time.time() - t1

    result_text = f"Query Results for '{collection_name}'\n"
    result_text += f'Query: "{query_text}"\n'
    result_text += f"Embedding time: {embedding_time:.3f}s\n"
    result_text += f"Query time: {query_time:.3f}s\n"
    result_text += f"Results: {n_results}\n\n"

    if results and "documents" in results and results["documents"]:
        documents = results["documents"][0]
        distances = results.get("distances", [[]])[0]
        metadatas_list = results.get("metadatas", [[]])[0]
        for i, doc in enumerate(documents):
            result_text += f"Result {i + 1}:\n"
            result_text += f"  Document: {doc[:200]}{'...' if len(doc) > 200 else ''}\n"
            if i < len(distances):
                result_text += f"  Distance: {distances[i]:.4f}\n"
            if i < len(metadatas_list) and metadatas_list[i]:
                result_text += f"  Metadata: {json.dumps(metadatas_list[i], indent=4)}\n"
            result_text += "\n"

    return result_text


@mcp.tool()
def get_collection_info(name: str) -> str:
    client = _require_chroma()
    collection = client.get_collection(name)

    info = f"Collection Info: '{name}'\n"
    info += f"ID: {collection.id}\n"

    try:
        count = collection.count()
        info += f"Document count: {count}\n"
    except (RuntimeError, ValueError, OSError):
        info += "Document count: Unknown\n"

    if collection.metadata:
        info += f"Metadata:\n{json.dumps(collection.metadata, indent=2)}\n"

    try:
        sample = collection.get(limit=5, include=["metadatas", "documents"])
        sample_documents = sample.get("documents") or []
    except (RuntimeError, ValueError, OSError):
        sample_documents = []

    if sample_documents:
        info += "\nSample documents:\n"
        for i, doc in enumerate(sample_documents):
            info += f"{i + 1}. {doc[:100]}{'...' if len(doc) > 100 else ''}\n"

    return info


@mcp.tool()
def embed_text(texts: list[str], batch_size: int = 32) -> str:
    _require_model_ready()
    batch_size = min(batch_size, MAX_EMBEDDING_BATCH_SIZE)

    if len(texts) > MAX_EMBEDDING_BATCH_SIZE:
        return f"Too many texts (max {MAX_EMBEDDING_BATCH_SIZE})"

    t0 = time.time()
    embeddings = _encode_with_guard(
        "encode:embed_text",
        texts,
        batch_size=batch_size,
    )
    processing_time = time.time() - t0

    safe_time = max(processing_time, 1e-9)
    result = "Embedding Results\n"
    result += f"Texts processed: {len(texts)}\n"
    result += f"Processing time: {processing_time:.2f}s\n"
    result += f"Embedding dimension: {embeddings.shape[1]}\n"
    result += f"Texts per second: {len(texts) / safe_time:.1f}\n\n"

    result += "Sample embeddings (first 5 dimensions):\n"
    for i, (text, embedding) in enumerate(zip(texts, embeddings)):
        result += f'\n{i + 1}. "{text[:50]}{"..." if len(text) > 50 else ""}"\n'
        result += f"   [{', '.join(f'{x:.4f}' for x in embedding[:5])}, ...]\n"

    return result


@mcp.tool()
def semantic_search(
    query: str,
    collections: list[str] | None = None,
    n_results: int = 5,
) -> str:
    client = _require_chroma()
    _require_model_ready()

    if not query.strip():
        return "Error: EMPTY_QUERY — query must be non-empty"

    n_results = min(n_results, MAX_SEARCH_RESULTS)

    if not collections:
        all_cols = client.list_collections()
        collections = [col.name for col in all_cols]

    query_embedding = _encode_query_text(
        query,
        op_name="encode:semantic_search",
    )

    merged: list[dict] = []
    collection_errors: dict[str, str] = {}
    total_time = 0.0
    global_deadline = time.monotonic() + SEARCH_GLOBAL_TIMEOUT

    for cn in collections:
        remaining = global_deadline - time.monotonic()
        if remaining <= 0:
            collection_errors[cn] = f"GLOBAL_TIMEOUT (>{SEARCH_GLOBAL_TIMEOUT:.1f}s)"
            continue
        timeout_s = min(SEARCH_PER_COLLECTION_TIMEOUT, remaining)
        try:
            col = client.get_collection(cn)
            t0 = time.time()
            res = _query_collection_with_timeout(
                col,
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=None,
                include=["metadatas", "documents", "distances"],
                collection_name=cn,
                timeout_s=timeout_s,
                op_name="semantic_search",
            )
            elapsed = time.time() - t0
            docs = res.get("documents", [[]])[0] if res.get("documents") else []
            dists = res.get("distances", [[]])[0] if res.get("distances") else []
            metas = res.get("metadatas", [[]])[0] if res.get("metadatas") else []
            for doc, dist, meta in zip(docs, dists, metas or [None] * len(docs)):
                merged.append({"collection": cn, "distance": dist, "document": doc, "metadata": meta})
            total_time += elapsed
        except TimeoutError:
            collection_errors[cn] = f"QUERY_TIMEOUT (>{timeout_s:.1f}s — HNSW index may still be cold)"
        except (RuntimeError, ValueError, chromadb.errors.ChromaError) as col_err:
            collection_errors[cn] = str(col_err)

    merged.sort(key=lambda r: (r["distance"], r["collection"], r["document"]))

    result_text = "Semantic Search Results\n"
    result_text += f'Query: "{query}"\n'
    result_text += f"Collections searched: {len(collections)}\n"
    result_text += f"Total results: {len(merged)}\n"
    result_text += f"Total search time: {total_time:.3f}s\n"
    if collection_errors:
        result_text += f"Collection errors: {len(collection_errors)}\n"
        for cname, cerr in collection_errors.items():
            result_text += f"  {cname}: {cerr}\n"
    result_text += "\n"

    for rank, hit in enumerate(merged, start=1):
        result_text += (
            f"{rank}. [{hit['collection']}] "
            f"(dist: {hit['distance']:.4f}) "
            f"{hit['document'][:100]}{'...' if len(hit['document']) > 100 else ''}\n"
        )

    return result_text


@mcp.tool()
def vector_stats() -> str:
    client = _require_chroma()
    cols = client.list_collections()

    model_loaded = _embedding_loader.is_loaded()
    model = _embedding_loader.get(wait_timeout=0) if model_loaded else None
    embedding_dimension: int | None = None
    if model_loaded:
        try:
            embedding_dimension = model.get_sentence_embedding_dimension()
        except (AttributeError, RuntimeError):
            pass

    stats = "Vector Database Statistics\n"
    stats += f"ChromaDB path: {CHROMA_PATH}\n"
    stats += f"Total collections: {len(cols)}\n"
    stats += f"Embedding model: {DEFAULT_EMBEDDING_MODEL}\n"
    stats += f"Model loaded: {model_loaded}\n"
    stats += f"Embedding dimension: {embedding_dimension}\n"
    stats += f"Encode timeout: {EMBEDDING_ENCODE_TIMEOUT:.0f}s\n"
    stats += f"Encode queue wait timeout: {EMBEDDING_QUEUE_WAIT_TIMEOUT:.0f}s\n"
    stats += f"Query batch window: {QUERY_EMBED_BATCH_WINDOW_MS:.0f}ms\n"
    stats += f"Query batch max size: {min(QUERY_EMBED_MAX_BATCH, MAX_EMBEDDING_BATCH_SIZE)}\n"
    stats += f"Per-collection query timeout: {QUERY_COLLECTION_TIMEOUT:.0f}s\n"
    stats += f"Per-collection semantic search timeout: {SEARCH_PER_COLLECTION_TIMEOUT:.0f}s\n"

    stats += "\nCollection Details:\n"
    total_documents = 0
    for col in cols:
        count = _get_cached_count(col.name, col)
        if count is not None:
            total_documents += count
            count_str = str(count)
        else:
            count_str = "N/A (timeout)"
        stats += f"  📁 {col.name}: {count_str} documents"
        if col.metadata:
            stats += f" ({json.dumps(col.metadata)})"
        stats += "\n"

    stats += f"\nTotal documents across all collections: {total_documents}\n"

    try:
        disk_bytes = sum(f.stat().st_size for f in CHROMA_PATH.rglob("*") if f.is_file())
        disk_mb = disk_bytes / (1024 * 1024)
        stats += f"Disk bytes: {disk_bytes}\n"
        stats += f"Disk usage: {disk_mb:.3f} MB\n"
    except (OSError, PermissionError):
        pass

    return stats


@mcp.tool()
def readiness() -> str:
    chroma_loaded = _chroma_loader.is_loaded()
    chroma_loading = _chroma_loader.is_loading()
    model_loaded = _embedding_loader.is_loaded()
    model_loading = _embedding_loader.is_loading()

    status = "Vector DB Readiness\n"
    status += f"Chroma ready: {chroma_loaded}\n"
    status += f"Chroma loading: {chroma_loading}\n"
    status += f"Embedding model ready: {model_loaded}\n"
    status += f"Embedding model loading: {model_loading}\n"
    status += f"Chroma timeout: {CHROMA_INIT_TIMEOUT:.0f}s\n"
    status += f"Model timeout: {MODEL_LOAD_TIMEOUT:.0f}s\n"
    status += f"Encode timeout: {EMBEDDING_ENCODE_TIMEOUT:.0f}s\n"
    status += f"Query batch window: {QUERY_EMBED_BATCH_WINDOW_MS:.0f}ms\n"
    status += f"Query batch max size: {min(QUERY_EMBED_MAX_BATCH, MAX_EMBEDDING_BATCH_SIZE)}\n"
    status += f"Query timeout: {QUERY_COLLECTION_TIMEOUT:.0f}s\n"
    status += f"Prewarm phase: {_PREWARM_STATE['phase']}\n"
    status += f"Prewarm progress: {_PREWARM_STATE['done']}/{_PREWARM_STATE['total']}\n"
    status += f"Prewarm current: {_PREWARM_STATE['current']}\n"
    status += f"Prewarm last error: {_PREWARM_STATE['last_error']}\n"
    if chroma_loaded and model_loaded and _PREWARM_STATE["phase"] == "ready":
        status += "Ready for full semantic operations\n"
    else:
        status += "Warmup still in progress\n"
    return status


def _prewarm() -> None:
    client = None
    _set_prewarm_state(phase="starting", total=0, done=0, current="", last_error="")

    try:
        logger.info("PREWARM_PHASE_1: initializing ChromaDB client...")
        client = _get_chroma()
        if client is not None:
            cols = client.list_collections()
            logger.info("PREWARM_PHASE_1_DONE: ChromaDB ready, %d collections", len(cols))
            _set_prewarm_state(phase="chroma_ready")
        else:
            logger.error("PREWARM_PHASE_1_FAIL: ChromaDB client returned None")
            _set_prewarm_state(phase="chroma_failed", last_error="client returned None")
    except (OSError, RuntimeError, ValueError) as e:
        logger.error("PREWARM_PHASE_1_FAIL: %s", e)
        _set_prewarm_state(phase="chroma_failed", last_error=str(e))

    try:
        logger.info("PREWARM_PHASE_2: loading embedding model...")
        model = _embedding_loader.get()
        if model is None:
            logger.error("PREWARM_PHASE_2_FAIL: embedding model returned None")
            _set_prewarm_state(phase="model_failed", last_error="model returned None")
            return
        logger.info("PREWARM_PHASE_2_DONE: embedding model ready")
        _set_prewarm_state(phase="model_ready")
        if client is not None:
            logger.info("PREWARM_PHASE_3: warming HNSW indexes for all collections...")
            _prewarm_hnsw_indexes(client, model)
            logger.info("PREWARM_PHASE_3_DONE: HNSW warmup complete")
    except (RuntimeError, OSError, ImportError) as e:
        logger.error("PREWARM_PHASE_2_FAIL: %s", e)
        _set_prewarm_state(phase="model_failed", last_error=str(e))


if __name__ == "__main__":
    _prewarm_thread = threading.Thread(target=_prewarm, daemon=True, name="prewarm")
    _prewarm_thread.start()
    logger.info("Background prewarm started (ChromaDB + embedding model + prioritized HNSW warmup)")
    run_server(mcp)
