#!/usr/bin/env python3
"""
Vector DB MCP Server - ChromaDB-backed vector storage and semantic search.

Uses shared mcp_bootstrap for standardized startup (repo-root, logging, FastMCP,
env safety) and mcp_deferred_loader for lazy embedding model loading.
"""

from __future__ import annotations

import json
import logging
import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

# ── Shared MCP bootstrap (repo-root, logging→stderr, env safety, FastMCP) ─
# Must be the first project import — sets sys.path, TOKENIZERS_PARALLELISM, etc.
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

# ── Env-var configuration — all values frozen at startup ───────────────────
_raw_chroma_path = os.environ.get("VECTOR_DB_CHROMA_PATH", "")
CHROMA_PATH: Path = Path(_raw_chroma_path) if _raw_chroma_path else REPO_ROOT / "data" / "cache" / "chromadb"
DEFAULT_EMBEDDING_MODEL: str = os.environ.get("VECTOR_DB_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
ALLOW_MODEL_DOWNLOAD: bool = os.environ.get("VECTOR_DB_ALLOW_MODEL_DOWNLOAD", "0").strip() == "1"
MODEL_LOAD_TIMEOUT: float = float(os.environ.get("VECTOR_DB_MODEL_LOAD_TIMEOUT", "120"))
CHROMA_INIT_TIMEOUT: float = float(os.environ.get("VECTOR_DB_CHROMA_INIT_TIMEOUT", "30"))


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

_KNOWN_MODEL_DIMS: dict[str, int] = {
    "BAAI/bge-m3": 1024,
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "text-embedding-ada-002": 1536,
}

# ── FastMCP server instance — via shared bootstrap ────────────────────────
mcp = create_mcp_server(
    "vector-db",
    "ChromaDB-backed vector storage and semantic search. "
    "Provides embeddings, similarity queries, and collection management.",
)

# ── Module-level singletons — lazy-initialized via DeferredLoader ──────────
_COUNT_CACHE: dict[str, tuple[int, float]] = {}
_COUNT_CACHE_TTL: float = 60.0


def _init_chroma() -> chromadb.PersistentClient:
    """Factory for DeferredLoader — creates ChromaDB PersistentClient.

    Runs inside a daemon thread so it never blocks the MCP stdio
    transport. DeferredLoader enforces CHROMA_INIT_TIMEOUT (default 30s).
    """
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
    return client


def _load_embedding_model():
    """Factory for DeferredLoader — loads SentenceTransformer from cache."""
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


# ── Deferred ChromaDB loader — CHROMA_INIT_TIMEOUT bounds the wait ─────────
# Declared after _init_chroma/_check_embedding_alignment are defined.
# DeferredLoader runs _init_chroma in a daemon thread so PersistentClient
# HNSW cold-start never blocks the MCP stdio transport thread.
def _check_embedding_alignment(client: chromadb.PersistentClient, model_name: str) -> None:
    """Fail-fast: configured embedding model dim must match corpus."""
    configured_dim = _KNOWN_MODEL_DIMS.get(model_name)
    if configured_dim is None:
        return
    try:
        collections = client.list_collections()
    except (RuntimeError, ValueError):
        return
    for col in collections:  # progress_bar: bounded collection list
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


# _chroma_loader instantiated HERE — after both _init_chroma and
# _check_embedding_alignment are fully defined (the factory calls the latter).
_chroma_loader = DeferredLoader(
    "chromadb-client",
    _init_chroma,
    timeout=CHROMA_INIT_TIMEOUT,
)


def _get_chroma() -> chromadb.PersistentClient | None:
    """Get ChromaDB client — None if not yet loaded or load failed."""
    return _chroma_loader.get()  # type: ignore[return-value]


def _call_with_timeout(fn: Any, timeout_s: float, op_name: str) -> Any:
    """Run a callable in a daemon thread and return or time out without blocking shutdown."""
    result_q: queue.Queue[tuple[bool, object]] = queue.Queue(maxsize=1)

    def _worker() -> None:
        try:
            result_q.put((True, fn()))
        except BaseException as exc:  # guardian: allow-broad-except -- daemon thread boundary
            result_q.put((False, exc))

    worker = threading.Thread(target=_worker, daemon=True, name=f"{op_name}-timeout-guard")
    worker.start()

    try:
        ok, payload = result_q.get(timeout=timeout_s)
    except queue.Empty as exc:
        raise TimeoutError(f"{op_name} timed out after {timeout_s:.1f}s") from exc

    if ok:
        return payload
    raise payload  # type: ignore[misc]


def _require_chroma() -> chromadb.PersistentClient:
    """Get ChromaDB or raise — fails fast if still loading during prewarm."""
    if not _chroma_loader.is_loaded():
        _chroma_loader.get(wait_timeout=0)
        raise RuntimeError(
            "ChromaDB is still initializing (HNSW indexes loading from disk). "
            f"Retry in a few seconds. Timeout: {CHROMA_INIT_TIMEOUT:.0f}s. "
            "Check server stderr for CHROMA_INIT_DONE to confirm readiness."
        )
    return _chroma_loader.require()  # type: ignore[return-value]


def _require_model_ready():
    """Fail fast while the embedding model is still warming instead of blocking MCP calls."""
    if not _embedding_loader.is_loaded():
        _embedding_loader.get(wait_timeout=0)
        raise RuntimeError(
            "Embedding model is still initializing. Retry in a few seconds. "
            f"Timeout: {MODEL_LOAD_TIMEOUT:.0f}s. "
            "Check server stderr for PREWARM_PHASE_2_DONE to confirm readiness."
        )
    return _embedding_loader.require()


def _get_cached_count(collection_name: str, collection: Any) -> int | None:
    """Return cached document count or fetch with a 2s timeout."""
    now = time.time()
    cached = _COUNT_CACHE.get(collection_name)
    if cached is not None:
        count, fetched_at = cached
        if now - fetched_at < _COUNT_CACHE_TTL:
            return count
    try:
        count = _call_with_timeout(collection.count, 2.0, f"count:{collection_name}")
        _COUNT_CACHE[collection_name] = (count, now)
        return count
    except TimeoutError:
        logger.warning("COUNT_TIMEOUT: collection=%r", collection_name)
        return None
    except (RuntimeError, ValueError, OSError) as exc:
        logger.warning("COUNT_ERROR: collection=%r error=%s", collection_name, exc)
        return None


# ── Tool implementations ───────────────────────────────────────────────────


@mcp.tool()
def create_collection(name: str, metadata: dict[str, str] | None = None) -> str:
    """Create a new vector collection"""
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
    """List all vector collections"""
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
    """Delete a vector collection"""
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
    """Add documents to a collection with embeddings"""
    client = _require_chroma()
    model = _require_model_ready()

    if len(documents) > MAX_EMBEDDING_BATCH_SIZE:
        return f"Too many documents (max {MAX_EMBEDDING_BATCH_SIZE})"

    collection = client.get_collection(collection_name)

    t0 = time.time()
    embeddings = model.encode(documents)
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
    """Query a collection for similar documents"""
    client = _require_chroma()
    model = _require_model_ready()

    if not query_text.strip():
        return "Error: EMPTY_QUERY — query_text must be non-empty"

    n_results = min(n_results, MAX_RESULTS)
    if include is None:
        include = ["metadatas", "documents", "distances"]

    collection = client.get_collection(collection_name)

    t0 = time.time()
    query_embedding = model.encode([query_text])
    embedding_time = time.time() - t0

    t1 = time.time()
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=n_results,
        where=where if where else None,
        include=include,
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
        for i, doc in enumerate(documents):  # progress_bar: bounded by n_results (max 100)
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
    """Get detailed information about a collection"""
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
    """Generate embeddings for text"""
    model = _require_model_ready()
    batch_size = min(batch_size, MAX_EMBEDDING_BATCH_SIZE)

    if len(texts) > MAX_EMBEDDING_BATCH_SIZE:
        return f"Too many texts (max {MAX_EMBEDDING_BATCH_SIZE})"

    t0 = time.time()
    embeddings = model.encode(texts, batch_size=batch_size)
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
    """Perform semantic search across all collections"""
    client = _require_chroma()
    model = _require_model_ready()

    if not query.strip():
        return "Error: EMPTY_QUERY — query must be non-empty"

    n_results = min(n_results, MAX_SEARCH_RESULTS)

    if not collections:
        all_cols = client.list_collections()
        collections = [col.name for col in all_cols]

    query_embedding = model.encode([query])

    merged: list[dict] = []
    collection_errors: dict[str, str] = {}
    total_time = 0.0
    per_collection_timeout = 5.0
    global_deadline = time.monotonic() + 30.0

    def _query_one(col_name: str) -> tuple[str, list[dict], float]:
        col = client.get_collection(col_name)
        t0 = time.time()
        res = col.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            include=["metadatas", "documents", "distances"],
        )
        elapsed = time.time() - t0
        docs = res.get("documents", [[]])[0] if res.get("documents") else []
        dists = res.get("distances", [[]])[0] if res.get("distances") else []
        metas = res.get("metadatas", [[]])[0] if res.get("metadatas") else []
        hits = []
        for doc, dist, meta in zip(docs, dists, metas or [None] * len(docs)):
            hits.append({"collection": col_name, "distance": dist, "document": doc, "metadata": meta})
        return col_name, hits, elapsed

    for cn in collections:  # progress_bar: bounded collection list with per-item timeout
        remaining = global_deadline - time.monotonic()
        if remaining <= 0:
            collection_errors[cn] = "GLOBAL_TIMEOUT (>30s)"
            continue
        timeout_s = min(per_collection_timeout, remaining)
        try:
            _, hits, elapsed = _call_with_timeout(
                lambda collection_name=cn: _query_one(collection_name),
                timeout_s,
                f"semantic_search:{cn}",
            )
            merged.extend(hits)
            total_time += elapsed
        except TimeoutError:
            collection_errors[cn] = f"QUERY_TIMEOUT (>{timeout_s:.1f}s — HNSW index may be cold)"
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
    """Get vector database statistics"""
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

    stats += "\nCollection Details:\n"
    total_documents = 0
    for col in cols:  # progress_bar: bounded collection list
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
    """Report ChromaDB and embedding-model warmup state without triggering heavy work."""
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
    if chroma_loaded and model_loaded:
        status += "Ready for full semantic operations\n"
    else:
        status += "Warmup still in progress\n"
    return status


# ── Background prewarm — init ChromaDB + load model BEFORE mcp.run() ──────
# This runs in a daemon thread so it doesn't block the MCP handshake.
# ChromaDB PersistentClient init loads HNSW indexes from disk (can take
# seconds with large collections). Without prewarm, the first tool call
# (e.g. list_collections) blocks the stdio transport and appears to hang.
def _prewarm() -> None:
    """Init ChromaDB + load embedding model in background — never blocks stdio."""
    # Phase 1: ChromaDB client (fast, ~1-3s — but blocks HNSW cold-start)
    try:
        logger.info("PREWARM_PHASE_1: initializing ChromaDB client...")
        client = _get_chroma()
        if client is not None:
            cols = client.list_collections()
            logger.info("PREWARM_PHASE_1_DONE: ChromaDB ready, %d collections", len(cols))
        else:
            logger.error("PREWARM_PHASE_1_FAIL: ChromaDB client returned None")
    except (OSError, RuntimeError, ValueError) as e:
        logger.error("PREWARM_PHASE_1_FAIL: %s", e)

    # Phase 2: Embedding model (slow, ~12-15s)
    try:
        logger.info("PREWARM_PHASE_2: loading embedding model...")
        _embedding_loader.get()
        logger.info("PREWARM_PHASE_2_DONE: embedding model ready")
    except (RuntimeError, OSError, ImportError) as e:
        logger.error("PREWARM_PHASE_2_FAIL: %s", e)


# ── Entry point — via shared bootstrap ─────────────────────────────────────
if __name__ == "__main__":
    # Start prewarm as daemon thread — runs alongside mcp.run()
    _prewarm_thread = threading.Thread(target=_prewarm, daemon=True, name="prewarm")
    _prewarm_thread.start()
    logger.info("Background prewarm started (ChromaDB + embedding model)")
    run_server(mcp)
