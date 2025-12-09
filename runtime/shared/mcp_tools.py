"""
03_runtime/shared/mcp_tools.py
MCP Tool Server for Agentic Workflow

Exposes core SDK capabilities as MCP tools for use by AI agents.
Integrates with: ChromaDB, Qdrant, Redis, Document Processing.

Usage:
    # Start the MCP server
    python -m agentic_workflow.runtime.shared.mcp_tools

    # Or import and extend
    from agentic_workflow.runtime.shared.mcp_tools import mcp_server

    @mcp_server.tool()
    def my_custom_tool(arg: str) -> str:
        return f"Result: {arg}"
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Lazy import to avoid startup cost if not using MCP
_mcp_server = None


def get_mcp_server():
    """Get or create the MCP server singleton."""
    global _mcp_server

    if _mcp_server is not None:
        return _mcp_server

    from fastmcp import FastMCP

    _mcp_server = FastMCP(
        name="agentic-workflow",
        version="1.0.0",
    )

    # Register all tools
    _register_vector_tools(_mcp_server)
    _register_cache_tools(_mcp_server)
    _register_document_tools(_mcp_server)
    _register_llm_tools(_mcp_server)

    logger.info("Initialized MCP server with agentic-workflow tools")
    return _mcp_server


# =============================================================================
# VECTOR STORE TOOLS
# =============================================================================


def _register_vector_tools(mcp):
    """Register vector store tools."""

    @mcp.tool()
    def vector_search(
        query: str,
        collection: str = "default",
        provider: str = "chromadb",
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in a vector store.

        Args:
            query: The search query text
            collection: Name of the collection to search
            provider: Vector store provider (chromadb, qdrant)
            top_k: Number of results to return

        Returns:
            List of matching documents with scores
        """
        from .sdk_registry import get_vector_store

        client = get_vector_store(provider)

        if provider == "chromadb":
            coll = client.get_or_create_collection(collection)
            results = coll.query(query_texts=[query], n_results=top_k)

            documents = []
            for i, doc in enumerate(results.get("documents", [[]])[0]):
                documents.append({
                    "text": doc,
                    "id": results.get("ids", [[]])[0][i] if results.get("ids") else None,
                    "distance": results.get("distances", [[]])[0][i] if results.get("distances") else None,
                    "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                })
            return documents

        elif provider == "qdrant":
            from qdrant_client.models import Distance, VectorParams

            # For Qdrant, we need embeddings - use a simple approach
            # In production, you'd use a proper embedding model
            results = client.scroll(collection_name=collection, limit=top_k)
            return [
                {
                    "id": str(point.id),
                    "payload": point.payload,
                }
                for point in results[0]
            ]

        return []

    @mcp.tool()
    def vector_add(
        documents: List[str],
        collection: str = "default",
        provider: str = "chromadb",
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Add documents to a vector store collection.

        Args:
            documents: List of document texts to add
            collection: Name of the collection
            provider: Vector store provider (chromadb)
            ids: Optional list of document IDs
            metadatas: Optional list of metadata dicts

        Returns:
            Status of the operation
        """
        from .sdk_registry import get_vector_store
        import uuid

        client = get_vector_store(provider)

        if provider == "chromadb":
            coll = client.get_or_create_collection(collection)

            doc_ids = ids or [str(uuid.uuid4()) for _ in documents]

            coll.add(
                documents=documents,
                ids=doc_ids,
                metadatas=metadatas,
            )

            return {
                "status": "success",
                "count": len(documents),
                "collection": collection,
                "ids": doc_ids,
            }

        return {"status": "error", "message": f"Provider {provider} not supported for add"}

    @mcp.tool()
    def vector_list_collections(provider: str = "chromadb") -> List[str]:
        """
        List all collections in the vector store.

        Args:
            provider: Vector store provider

        Returns:
            List of collection names
        """
        from .sdk_registry import get_vector_store

        client = get_vector_store(provider)

        if provider == "chromadb":
            collections = client.list_collections()
            return [c.name for c in collections]
        elif provider == "qdrant":
            collections = client.get_collections()
            return [c.name for c in collections.collections]

        return []


# =============================================================================
# CACHE TOOLS
# =============================================================================


def _register_cache_tools(mcp):
    """Register Redis cache tools."""

    @mcp.tool()
    def cache_get(key: str) -> Optional[str]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value or None if not found
        """
        from .sdk_registry import get_redis_client

        try:
            client = get_redis_client()
            return client.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None

    @mcp.tool()
    def cache_set(key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl_seconds: Optional time-to-live in seconds

        Returns:
            True if successful
        """
        from .sdk_registry import get_redis_client

        try:
            client = get_redis_client()
            if ttl_seconds:
                client.setex(key, ttl_seconds, value)
            else:
                client.set(key, value)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False

    @mcp.tool()
    def cache_delete(key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: The cache key to delete

        Returns:
            True if the key was deleted
        """
        from .sdk_registry import get_redis_client

        try:
            client = get_redis_client()
            return client.delete(key) > 0
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False

    @mcp.tool()
    def cache_keys(pattern: str = "*") -> List[str]:
        """
        List cache keys matching a pattern.

        Args:
            pattern: Glob-style pattern (e.g., "user:*")

        Returns:
            List of matching keys
        """
        from .sdk_registry import get_redis_client

        try:
            client = get_redis_client()
            return list(client.scan_iter(match=pattern, count=100))
        except Exception as e:
            logger.warning(f"Cache keys failed: {e}")
            return []


# =============================================================================
# DOCUMENT PROCESSING TOOLS
# =============================================================================


def _register_document_tools(mcp):
    """Register document processing tools."""

    @mcp.tool()
    def parse_document(file_path: str, strategy: str = "auto") -> List[Dict[str, Any]]:
        """
        Parse a document and extract structured content.

        Args:
            file_path: Path to the document (PDF, DOCX, HTML, etc.)
            strategy: Parsing strategy (auto, fast, hi_res, ocr_only)

        Returns:
            List of extracted elements with text and metadata
        """
        from .sdk_registry import parse_document as _parse
        return _parse(file_path, strategy)

    @mcp.tool()
    def extract_pdf_text(file_path: str) -> str:
        """
        Extract plain text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        from .sdk_registry import extract_pdf_text as _extract
        return _extract(file_path)


# =============================================================================
# LLM TOOLS
# =============================================================================


def _register_llm_tools(mcp):
    """Register LLM-related tools."""

    @mcp.tool()
    def llm_complete(
        prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate a completion using an LLM.

        Args:
            prompt: The prompt text
            model: Model name (supports OpenAI, Anthropic, etc. via LiteLLM)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        import litellm

        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    @mcp.tool()
    def llm_embed(text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Generate embeddings for text.

        Args:
            text: Text to embed
            model: Embedding model name

        Returns:
            Embedding vector
        """
        import litellm

        response = litellm.embedding(model=model, input=[text])
        return response.data[0]["embedding"]

    @mcp.tool()
    def list_available_models() -> List[str]:
        """
        List available LLM models.

        Returns:
            List of model names that can be used
        """
        return [
            # OpenAI
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "o1-preview",
            "o1-mini",
            # Anthropic
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            # Google
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            # Groq
            "groq/llama-3.3-70b-versatile",
            "groq/mixtral-8x7b-32768",
            # Together
            "together/meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "together/mistralai/Mixtral-8x22B-Instruct-v0.1",
            # Fireworks
            "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct",
        ]


# =============================================================================
# RESOURCES
# =============================================================================


def _register_resources(mcp):
    """Register MCP resources."""

    @mcp.resource("config://sdk-registry")
    def get_sdk_registry() -> Dict[str, Any]:
        """Get the SDK registry configuration."""
        from .sdk_registry import SDK_REGISTRY

        return {
            name: {
                "package": entry.package,
                "category": entry.category.value,
                "description": entry.description,
                "mcp_compatible": entry.mcp_compatible,
            }
            for name, entry in SDK_REGISTRY.items()
        }

    @mcp.resource("config://available-sdks")
    def get_available() -> List[str]:
        """Get list of installed SDKs."""
        from .sdk_registry import get_available_sdks
        return get_available_sdks()


# =============================================================================
# SERVER ENTRY POINT
# =============================================================================

# Expose the server for import
mcp_server = get_mcp_server()


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the MCP server."""
    import uvicorn

    server = get_mcp_server()
    uvicorn.run(server.app, host=host, port=port)


if __name__ == "__main__":
    run_server()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "get_mcp_server",
    "mcp_server",
    "run_server",
]
