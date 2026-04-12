#!/usr/bin/env python3
"""
Vector DB MCP Server - ChromaDB-backed vector storage and semantic search
Provides vector operations for semantic search, embeddings, and similarity queries
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from tqdm import tqdm

import anyio

# Vector database imports
try:
    import chromadb
    import numpy as np
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"Vector DB libraries not found: {e}", file=sys.stderr)
    print("Install with: pip install chromadb sentence-transformers numpy", file=sys.stderr)
    sys.exit(1)

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.lowlevel.server import NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        TextContent,
        Tool,
    )
except ImportError:
    print("MCP SDK not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging - use stderr to avoid interfering with MCP protocol on stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Env-var configuration — all values frozen at startup, no dynamic reload
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.parent

_raw_chroma_path = os.environ.get("VECTOR_DB_CHROMA_PATH", "")
CHROMA_PATH: Path = Path(_raw_chroma_path) if _raw_chroma_path else REPO_ROOT / "data" / "cache" / "chromadb"

DEFAULT_EMBEDDING_MODEL: str = os.environ.get("VECTOR_DB_EMBEDDING_MODEL", "all-MiniLM-L6-v2")


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

# Known model → output dimension map. Extend when new models are indexed into the corpus.
_KNOWN_MODEL_DIMS: dict[str, int] = {
    "BAAI/bge-m3": 1024,
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "text-embedding-ada-002": 1536,
}


def _check_embedding_alignment(chroma_client: "chromadb.PersistentClient", model_name: str) -> None:
    """Fail-fast startup check: configured embedding model dimension must match corpus.

    Reads each collection's ``embedding_dim`` metadata field and compares it to
    the dimension expected for *model_name*.  Emits a loud ERROR tagged
    EMBEDDING_MISMATCH if they differ.  Fail-open on infrastructure errors so
    startup is never blocked by a listing failure.
    """
    configured_dim = _KNOWN_MODEL_DIMS.get(model_name)
    if configured_dim is None:
        logger.warning(
            "EMBEDDING_DIM_UNKNOWN: cannot validate alignment for model %r "
            "\u2014 add it to _KNOWN_MODEL_DIMS to enable the check.",
            model_name,
        )
        return
    try:
        collections = chroma_client.list_collections()
    except Exception:  # guardian: allow-broad-exception -- ChromaDB list_collections raises heterogeneous internal errors with no shared catchable base; fail-open to avoid blocking startup
        return
    for col in tqdm(collections, desc="Checking embedding dims", unit="collection", leave=False):
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
                "EMBEDDING_MISMATCH: configured model=%r (dim=%d) ≠ corpus collection=%r "
                "(embedding_dim=%d, embedding_model=%r). "
                "All semantic_search / query_collection calls will return empty results "
                "or raise InvalidDimensionException. "
                "Fix: set VECTOR_DB_EMBEDDING_MODEL to %r in mcp_config.json.",
                model_name,
                configured_dim,
                col.name,
                corpus_dim_int,
                corpus_model,
                corpus_model,
            )
            return  # one loud error is enough
    logger.info(
        "EMBEDDING_ALIGNMENT_OK: model=%r dim=%d is consistent with corpus.",
        model_name,
        configured_dim,
    )


_COUNT_CACHE_TTL: float = 60.0  # seconds — collection counts are cached this long in vector_stats


def _validate_startup_config() -> None:
    """Log resolved config and warn on obvious misconfigurations at startup."""
    if not CHROMA_PATH.exists():
        logger.warning(
            "STARTUP_WARN: CHROMA_PATH does not exist: %s — will be created on first write.", CHROMA_PATH
        )
    else:
        logger.info("STARTUP: CHROMA_PATH resolved to %s", CHROMA_PATH)

    if DEFAULT_EMBEDDING_MODEL not in _KNOWN_MODEL_DIMS:
        logger.warning(
            "STARTUP_WARN: VECTOR_DB_EMBEDDING_MODEL=%r is not in _KNOWN_MODEL_DIMS; "
            "embedding dimension parity check is disabled. "
            "Add it to _KNOWN_MODEL_DIMS to enable the check.",
            DEFAULT_EMBEDDING_MODEL,
        )
    else:
        logger.info(
            "STARTUP: VECTOR_DB_EMBEDDING_MODEL=%r expected_dim=%d",
            DEFAULT_EMBEDDING_MODEL,
            _KNOWN_MODEL_DIMS[DEFAULT_EMBEDDING_MODEL],
        )


_log_level_name: str = os.environ.get("VECTOR_DB_LOG_LEVEL", "INFO").upper()
_log_level: int = getattr(logging, _log_level_name, logging.INFO)
if not isinstance(_log_level, int):
    logger.error("Invalid VECTOR_DB_LOG_LEVEL=%r; defaulting to INFO", _log_level_name)
    _log_level = logging.INFO
logger.setLevel(_log_level)


class VectorDBMCPServer:
    def __init__(self):
        self.server = Server("vector-db")
        self.chroma_client = None
        self.embedding_model = None
        self._embedding_model_loading = False
        self._model_lock = asyncio.Lock()
        self._count_cache: dict[str, tuple[int, float]] = {}  # name -> (count, fetched_at)
        self._setup_handlers()
        # Fast initialization - defer heavy loading
        self._initialize_chroma_only()

    def _initialize_chroma_only(self):
        """Initialize only ChromaDB for fast startup"""
        _validate_startup_config()
        try:
            CHROMA_PATH.mkdir(parents=True, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=str(CHROMA_PATH),
                settings=Settings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB initialized at: {CHROMA_PATH}")
            _check_embedding_alignment(self.chroma_client, DEFAULT_EMBEDDING_MODEL)
        except Exception as e:  # guardian: allow-broad-exception -- chromadb.PersistentClient raises heterogeneous errors from SQLite/HNSW/hnswlib with no shared catchable base
            logger.error(f"Failed to initialize ChromaDB: {e}")

    def _get_cached_count(self, collection_name: str, collection: Any) -> int | None:
        """Return cached document count or fetch with a 2 s timeout.

        Returns None when the count cannot be obtained within the timeout or
        an error occurs.  Caches successful results for _COUNT_CACHE_TTL seconds
        so repeated calls to vector_stats never re-block on a slow segment.
        """
        import concurrent.futures as _cf

        now = time.time()
        cached = self._count_cache.get(collection_name)
        if cached is not None:
            count, fetched_at = cached
            if now - fetched_at < _COUNT_CACHE_TTL:
                return count

        try:
            with _cf.ThreadPoolExecutor(max_workers=1) as _ex:
                count = _ex.submit(collection.count).result(timeout=2.0)
            self._count_cache[collection_name] = (count, now)
            return count
        except _cf.TimeoutError:
            logger.warning(
                "COUNT_TIMEOUT: collection=%r count() did not complete within 2 s; "
                "returning None. Use get_collection_info for an explicit count.",
                collection_name,
            )
            return None
        except Exception as exc:  # guardian: allow-broad-exception -- ChromaDB count() raises heterogeneous internal errors with no shared catchable base
            logger.warning("COUNT_ERROR: collection=%r error=%s", collection_name, exc)
            return None

    async def _ensure_embedding_model(self):
        """Load embedding model on first use, non-blocking via thread executor.

        SentenceTransformer.__init__ is CPU-bound and holds the GIL.  Running it
        in an executor releases the asyncio event loop so the MCP handshake and
        other coroutines (including the prewarm background task) can proceed.
        """
        async with self._model_lock:
            if self.embedding_model is None:
                try:
                    logger.info("Loading embedding model in thread executor...")
                    loop = asyncio.get_event_loop()
                    self.embedding_model = await loop.run_in_executor(
                        None, lambda: SentenceTransformer(DEFAULT_EMBEDDING_MODEL)
                    )
                    logger.info(f"Embedding model loaded: {DEFAULT_EMBEDDING_MODEL}")
                except Exception as e:  # guardian: allow-broad-exception -- SentenceTransformer raises heterogeneous errors from torch/transformers/safetensors with no shared base
                    logger.error(f"Failed to load embedding model: {e}")
        return self.embedding_model is not None

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available vector database tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="create_collection",
                        description="Create a new vector collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                                "metadata": {
                                    "type": "object",
                                    "description": "Collection metadata",
                                    "additionalProperties": {"type": "string"},
                                },
                            },
                            "required": ["name"],
                        },
                    ),
                    Tool(
                        name="list_collections",
                        description="List all vector collections",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                    Tool(
                        name="delete_collection",
                        description="Delete a vector collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                            },
                            "required": ["name"],
                        },
                    ),
                    Tool(
                        name="add_documents",
                        description="Add documents to a collection with embeddings",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "collection_name": {
                                    "type": "string",
                                    "description": "Target collection",
                                },
                                "documents": {
                                    "type": "array",
                                    "description": "Documents to add",
                                    "items": {"type": "string"},
                                },
                                "metadatas": {
                                    "type": "array",
                                    "description": "Metadata for each document",
                                    "items": {"type": "object"},
                                },
                                "ids": {
                                    "type": "array",
                                    "description": "Unique IDs for each document",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["collection_name", "documents"],
                        },
                    ),
                    Tool(
                        name="query_collection",
                        description="Query a collection for similar documents",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "collection_name": {
                                    "type": "string",
                                    "description": "Collection to query",
                                },
                                "query_text": {
                                    "type": "string",
                                    "description": "Query text",
                                },
                                "n_results": {
                                    "type": "integer",
                                    "description": "Number of results to return",
                                    "default": 10,
                                    "maximum": 100,
                                },
                                "where": {
                                    "type": "object",
                                    "description": "Filter conditions",
                                },
                                "include": {
                                    "type": "array",
                                    "description": "What to include in results",
                                    "items": {
                                        "type": "string",
                                        "enum": ["metadatas", "documents", "distances"],
                                    },
                                    "default": ["metadatas", "documents", "distances"],
                                },
                            },
                            "required": ["collection_name", "query_text"],
                        },
                    ),
                    Tool(
                        name="get_collection_info",
                        description="Get detailed information about a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                            },
                            "required": ["name"],
                        },
                    ),
                    Tool(
                        name="embed_text",
                        description="Generate embeddings for text",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "texts": {
                                    "type": "array",
                                    "description": "Texts to embed",
                                    "items": {"type": "string"},
                                },
                                "batch_size": {
                                    "type": "integer",
                                    "description": "Batch size for processing",
                                    "default": 32,
                                    "maximum": 32,
                                },
                            },
                            "required": ["texts"],
                        },
                    ),
                    Tool(
                        name="semantic_search",
                        description="Perform semantic search across all collections",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query",
                                },
                                "collections": {
                                    "type": "array",
                                    "description": "Collections to search (empty = all)",
                                    "items": {"type": "string"},
                                },
                                "n_results": {
                                    "type": "integer",
                                    "description": "Results per collection",
                                    "default": 5,
                                    "maximum": 20,
                                },
                            },
                            "required": ["query"],
                        },
                    ),
                    Tool(
                        name="vector_stats",
                        description="Get vector database statistics",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                ],
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "create_collection":
                    return await self._create_collection(arguments)
                elif name == "list_collections":
                    return await self._list_collections(arguments)
                elif name == "delete_collection":
                    return await self._delete_collection(arguments)
                elif name == "add_documents":
                    return await self._add_documents(arguments)
                elif name == "query_collection":
                    return await self._query_collection(arguments)
                elif name == "get_collection_info":
                    return await self._get_collection_info(arguments)
                elif name == "embed_text":
                    return await self._embed_text(arguments)
                elif name == "semantic_search":
                    return await self._semantic_search(arguments)
                elif name == "vector_stats":
                    return await self._vector_stats(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )

    async def _create_collection(self, args: dict[str, Any]) -> CallToolResult:
        """Create a new vector collection"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        name = args["name"]
        metadata = args.get("metadata") or None

        try:
            # Check if collection already exists
            try:
                self.chroma_client.get_collection(name)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Collection '{name}' already exists",
                        )
                    ],
                    isError=True,
                )
            except chromadb.errors.NotFoundError:
                pass  # Collection doesn't exist, which is good

            # Create collection
            collection = self.chroma_client.create_collection(
                name=name,
                metadata=metadata,
            )

            result = f"✅ Collection '{name}' created successfully\n"
            result += f"ID: {collection.id}\n"
            if metadata:
                result += f"Metadata: {json.dumps(metadata, indent=2)}\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to create collection: {str(e)}")],
                isError=True,
            )

    async def _list_collections(self, args: dict[str, Any]) -> CallToolResult:
        """List all vector collections"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        try:
            collections = self.chroma_client.list_collections()

            result = f"Vector Collections ({len(collections)} total):\n\n"

            for collection in collections:
                result += f"📁 {collection.name}\n"
                result += f"   ID: {collection.id}\n"
                if collection.metadata:
                    result += f"   Metadata: {json.dumps(collection.metadata, indent=6)}\n"
                result += "   Count: use get_collection_info or vector_stats\n"
                result += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to list collections: {str(e)}")],
                isError=True,
            )

    async def _delete_collection(self, args: dict[str, Any]) -> CallToolResult:
        """Delete a vector collection"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        name = args["name"]

        try:
            self.chroma_client.delete_collection(name)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ Collection '{name}' deleted successfully",
                    )
                ],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to delete collection: {str(e)}")],
                isError=True,
            )

    async def _add_documents(self, args: dict[str, Any]) -> CallToolResult:
        """Add documents to a collection with embeddings"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        # Lazy load embedding model
        if not await self._ensure_embedding_model():
            return CallToolResult(
                content=[TextContent(type="text", text="Failed to load embedding model")],
                isError=True,
            )

        collection_name = args["collection_name"]
        documents = args["documents"]
        metadatas = args.get("metadatas", [])
        ids = args.get("ids", [])

        if len(documents) > MAX_EMBEDDING_BATCH_SIZE:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Too many documents (max {MAX_EMBEDDING_BATCH_SIZE})",
                    )
                ],
                isError=True,
            )

        try:
            # Get collection
            collection = self.chroma_client.get_collection(collection_name)

            # Generate embeddings
            start_time = time.time()
            embeddings = self.embedding_model.encode(documents)
            embedding_time = time.time() - start_time

            # Generate IDs if not provided
            if not ids:
                ids = [str(uuid4()) for _ in range(len(documents))]

            # Add documents (upsert: duplicate IDs overwrite per contract)
            start_time = time.time()
            collection.upsert(
                documents=documents,
                embeddings=embeddings.tolist(),
                metadatas=metadatas if metadatas else None,
                ids=ids,
            )
            add_time = time.time() - start_time

            result = f"✅ Added {len(documents)} documents to '{collection_name}'\n"
            result += f"Embedding time: {embedding_time:.2f}s\n"
            result += f"Add time: {add_time:.2f}s\n"
            result += f"Total time: {embedding_time + add_time:.2f}s\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to add documents: {str(e)}")],
                isError=True,
            )

    async def _query_collection(self, args: dict[str, Any]) -> CallToolResult:
        """Query a collection for similar documents"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        # Lazy load embedding model
        if not await self._ensure_embedding_model():
            return CallToolResult(
                content=[TextContent(type="text", text="Failed to load embedding model")],
                isError=True,
            )

        collection_name = args["collection_name"]
        query_text = args["query_text"]
        if not query_text.strip():
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Error: EMPTY_QUERY — query_text must be a non-empty, non-whitespace string",
                    )
                ],
                isError=True,
            )
        n_results = min(args.get("n_results", 10), MAX_RESULTS)
        where = args.get("where", {})
        include = args.get("include", ["metadatas", "documents", "distances"])

        try:
            # Get collection
            collection = self.chroma_client.get_collection(collection_name)

            # Generate query embedding
            start_time = time.time()
            query_embedding = self.embedding_model.encode([query_text])
            embedding_time = time.time() - start_time

            # Query collection
            start_time = time.time()
            results = collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=where if where else None,
                include=include,
            )
            query_time = time.time() - start_time

            # Format results
            result_text = f"Query Results for '{collection_name}'\n"
            result_text += f'Query: "{query_text}"\n'
            result_text += f"Embedding time: {embedding_time:.3f}s\n"
            result_text += f"Query time: {query_time:.3f}s\n"
            result_text += f"Results: {n_results}\n\n"

            if results and "documents" in results and results["documents"]:
                documents = results["documents"][0]
                distances = results.get("distances", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]

                for i, doc in enumerate(documents):
                    result_text += f"Result {i + 1}:\n"
                    result_text += f"  Document: {doc[:200]}{'...' if len(doc) > 200 else ''}\n"
                    if i < len(distances):
                        result_text += f"  Distance: {distances[i]:.4f}\n"
                    if i < len(metadatas) and metadatas[i]:
                        result_text += f"  Metadata: {json.dumps(metadatas[i], indent=4)}\n"
                    result_text += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to query collection: {str(e)}")],
                isError=True,
            )

    async def _get_collection_info(self, args: dict[str, Any]) -> CallToolResult:
        """Get detailed information about a collection"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        name = args["name"]

        try:
            collection = self.chroma_client.get_collection(name)

            # Get basic info
            info = f"Collection Info: '{name}'\n"
            info += f"ID: {collection.id}\n"

            # Get count
            try:
                count = collection.count()
                info += f"Document count: {count}\n"
            except Exception:
                info += "Document count: Unknown\n"

            # Get metadata
            if collection.metadata:
                info += f"Metadata:\n{json.dumps(collection.metadata, indent=2)}\n"

            # Get sample of data — structured error field, never silent
            sample_documents: list = []
            sample_error: str | None = None
            try:
                sample = collection.get(limit=5, include=["metadatas", "documents"])
                sample_documents = sample.get("documents") or []
            except Exception as fetch_err:  # guardian: allow-broad-exception -- ChromaDB get() raises heterogeneous internal errors with no shared catchable base type
                sample_error = str(fetch_err)

            if sample_documents:
                info += "\nSample documents:\n"
                for i, doc in enumerate(sample_documents):
                    info += f"{i + 1}. {doc[:100]}{'...' if len(doc) > 100 else ''}\n"
            info += f"sample_error: {sample_error}\n"

            return CallToolResult(
                content=[TextContent(type="text", text=info)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get collection info: {str(e)}")],
                isError=True,
            )

    async def _embed_text(self, args: dict[str, Any]) -> CallToolResult:
        """Generate embeddings for text"""
        # Lazy load embedding model
        if not await self._ensure_embedding_model():
            return CallToolResult(
                content=[TextContent(type="text", text="Failed to load embedding model")],
                isError=True,
            )

        texts = args["texts"]
        batch_size = min(args.get("batch_size", 32), MAX_EMBEDDING_BATCH_SIZE)
        return_vectors: bool = bool(args.get("return_vectors", False))

        if len(texts) > MAX_EMBEDDING_BATCH_SIZE:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Too many texts (max {MAX_EMBEDDING_BATCH_SIZE})",
                    )
                ],
                isError=True,
            )

        try:
            start_time = time.time()
            embeddings = self.embedding_model.encode(texts, batch_size=batch_size)
            processing_time = time.time() - start_time

            safe_time = max(processing_time, 1e-9)  # guard against sub-timer-resolution runs
            result = "Embedding Results\n"
            result += f"Texts processed: {len(texts)}\n"
            result += f"Processing time: {processing_time:.2f}s\n"
            result += f"Embedding dimension: {embeddings.shape[1]}\n"
            result += f"Texts per second: {len(texts) / safe_time:.1f}\n"
            result += f"return_vectors: {return_vectors}\n\n"

            # Previews always present (first 5 dimensions)
            result += "Sample embeddings (first 5 dimensions):\n"
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                result += f'\n{i + 1}. "{text[:50]}{"..." if len(text) > 50 else ""}"\n'
                result += f"   [{', '.join(f'{x:.4f}' for x in embedding[:5])}, ...]\n"

            # Full vectors only when explicitly requested
            if return_vectors:
                result += "\nFull vectors:\n"
                for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                    result += f'\n{i + 1}. "{text[:50]}{"..." if len(text) > 50 else ""}"\n'
                    result += f"   {json.dumps(embedding.tolist())}\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to generate embeddings: {str(e)}")],
                isError=True,
            )

    async def _semantic_search(self, args: dict[str, Any]) -> CallToolResult:
        """Perform semantic search across all collections"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        # Lazy load embedding model
        if not await self._ensure_embedding_model():
            return CallToolResult(
                content=[TextContent(type="text", text="Failed to load embedding model")],
                isError=True,
            )

        query = args["query"]
        if not query.strip():
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Error: EMPTY_QUERY — query must be a non-empty, non-whitespace string",
                    )
                ],
                isError=True,
            )
        collections = args.get("collections", [])
        n_results: int = min(int(args.get("n_results", 5)), MAX_SEARCH_RESULTS)

        try:
            # Get all collections if none specified
            if not collections:
                all_collections = self.chroma_client.list_collections()
                collections = [col.name for col in all_collections]

            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])

            merged: list[dict] = []
            collection_errors: dict[str, str] = {}
            total_time = 0.0

            for collection_name in tqdm(collections, desc="search-collections", leave=False, disable=True):
                try:
                    collection = self.chroma_client.get_collection(collection_name)
                    start_time = time.time()
                    search_results = collection.query(
                        query_embeddings=query_embedding.tolist(),
                        n_results=n_results,
                        include=["metadatas", "documents", "distances"],
                    )
                    total_time += time.time() - start_time

                    docs = search_results.get("documents", [[]])[0] if search_results.get("documents") else []
                    dists = (
                        search_results.get("distances", [[]])[0] if search_results.get("distances") else []
                    )
                    metas = (
                        search_results.get("metadatas", [[]])[0] if search_results.get("metadatas") else []
                    )

                    for doc, dist, meta in zip(docs, dists, metas or [None] * len(docs)):
                        merged.append(
                            {
                                "collection": collection_name,
                                "distance": dist,
                                "document": doc,
                                "metadata": meta,
                            }
                        )

                except Exception as col_err:  # guardian: allow-broad-exception -- ChromaDB raises heterogeneous errors per collection; non-fatal to preserve cross-collection results
                    collection_errors[collection_name] = str(col_err)

            # Sort merged results by distance ascending; secondary keys break ties deterministically
            merged.sort(key=lambda r: (r["distance"], r["collection"], r["document"]))

            result_text = "Semantic Search Results\n"
            result_text += f'Query: "{query}"\n'
            result_text += f"Collections searched: {len(collections)}\n"
            result_text += f"Total results: {len(merged)}\n"
            result_text += f"Total search time: {total_time:.3f}s\n"
            if collection_errors:
                result_text += f"Collection errors: {len(collection_errors)}\n"
                for cname, cerr in collection_errors.items():
                    result_text += f"  ❌ {cname}: {cerr}\n"
            result_text += "\n"

            for rank, hit in enumerate(merged, start=1):
                result_text += (
                    f"{rank}. [{hit['collection']}] "
                    f"(dist: {hit['distance']:.4f}) "
                    f"{hit['document'][:100]}{'...' if len(hit['document']) > 100 else ''}\n"
                )

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to perform semantic search: {str(e)}")],
                isError=True,
            )

    async def _vector_stats(self, args: dict[str, Any]) -> CallToolResult:
        """Get vector database statistics"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        try:
            collections = self.chroma_client.list_collections()

            model_loaded = self.embedding_model is not None
            embedding_dimension: int | None = None
            if model_loaded:
                try:
                    embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
                except Exception:  # guardian: allow-broad-exception -- sentence-transformers raises heterogeneous errors across model types with no shared base
                    pass

            stats = "Vector Database Statistics\n"
            stats += f"ChromaDB path: {CHROMA_PATH}\n"
            stats += f"Total collections: {len(collections)}\n"
            stats += f"Embedding model: {DEFAULT_EMBEDDING_MODEL}\n"
            stats += f"Model loaded: {model_loaded}\n"
            stats += f"Embedding dimension: {embedding_dimension}\n"

            stats += "\nCollection Details:\n"

            total_documents = 0
            for collection in tqdm(
                collections, desc="Collection stats", unit="col", leave=False, disable=True
            ):
                count = self._get_cached_count(collection.name, collection)
                if count is not None:
                    total_documents += count
                    count_str = str(count)
                else:
                    count_str = "N/A (timeout — retry or call get_collection_info)"
                stats += f"  📁 {collection.name}: {count_str} documents"
                if collection.metadata:
                    stats += f" ({json.dumps(collection.metadata)})"
                stats += "\n"

            stats += f"\nTotal documents across all collections: {total_documents}\n"

            # Disk usage — directory bytes, not partition usage
            try:
                disk_bytes = sum(f.stat().st_size for f in CHROMA_PATH.rglob("*") if f.is_file())
                disk_mb = disk_bytes / (1024 * 1024)
                stats += f"Disk bytes: {disk_bytes}\n"
                stats += f"Disk usage: {disk_mb:.3f} MB\n"
            except Exception:  # guardian: allow-broad-exception -- Path.rglob raises heterogeneous OS errors (PermissionError, OSError) across platforms with no single catch base
                pass

            return CallToolResult(
                content=[TextContent(type="text", text=stats)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get vector stats: {str(e)}")],
                isError=True,
            )


async def main():
    """Main entry point"""
    server_instance = VectorDBMCPServer()

    # Prewarm: start loading the embedding model in the background so the first
    # semantic_search call does not bear the full cold-start latency (~4 s).
    asyncio.create_task(server_instance._ensure_embedding_model())

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="vector-db",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(
                        prompts_changed=False,
                        resources_changed=False,
                        tools_changed=False,
                    ),
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("Vector DB MCP Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
