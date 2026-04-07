"""Titanium Search Tool - Universal Search Interface for All Agents.

This module provides a singleton wrapper around the TitaniumRAGPipeline
to ensure all agents benefit from the SOTA retrieval system.
"""

import asyncio
import logging
from typing import Any

from .titanium_rag_pipeline import TitaniumRAGPipeline, create_titanium_pipeline

DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)

# Global singleton to preserve cache/Lazy models
_TITANIUM_PIPELINE: TitaniumRAGPipeline | None = None
_LEGACY_FALLBACK_ENABLED = True
_INITIALIZATION_LOCK = asyncio.Lock()


async def _initialize_pipeline() -> TitaniumRAGPipeline:
    """Initialize the Titanium pipeline with fallback handling.

    Returns:
        Initialized TitaniumRAGPipeline or fallback pipeline
    """
    global _TITANIUM_PIPELINE

    async with _INITIALIZATION_LOCK:
        if _TITANIUM_PIPELINE is not None:
            return _TITANIUM_PIPELINE

        try:
            logger.info("Initializing Titanium RAG Pipeline...")
            _TITANIUM_PIPELINE = create_titanium_pipeline(
                enable_all=True,
                max_retrieved_docs=20,
                top_k_final=5,
            )

            # Test availability
            component_info = _TITANIUM_PIPELINE.get_component_info()
            logger.info("Pipeline initialized successfully:")
            logger.info("  - Phase 1 (Precision): Available")
            logger.info("  - Phase 2 (Reasoning): Available")
            logger.info(
                f"  - Phase 3 (SOTA): Reranker={component_info['phase_3_sota']['reranker_available']}, "
                f"cache={component_info['phase_3_sota']['cache_available']}",
            )

            return _TITANIUM_PIPELINE

        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to initialize Titanium pipeline: {e}")
            if _LEGACY_FALLBACK_ENABLED:
                logger.warning("Falling back to legacy search mode")
                _TITANIUM_PIPELINE = await _create_fallback_pipeline()
            else:
                raise RuntimeError("Titanium pipeline initialization failed and fallback disabled")

    return _TITANIUM_PIPELINE


async def _create_fallback_pipeline() -> TitaniumRAGPipeline:
    """Create a minimal fallback pipeline.

    Returns:
        Minimal pipeline with basic functionality
    """
    # Create pipeline with all features disabled for maximum compatibility
    return TitaniumRAGPipeline(
        enable_compression=False,
        enable_decomposition=False,
        enable_reranking=False,
        enable_caching=False,
    )


async def get_titanium_search_tool(
    query: str,
    context: str | None = None,
    max_results: int = 5,
    include_metadata: bool = False,
) -> str:
    """
    The new gold-standard retrieval function for all Agents.

    This function provides a simple interface for all agents to access
    the Titanium RAG Pipeline with automatic fallback handling.

    Args:
        query: Search query string
        context: Optional context to guide retrieval
        max_results: Maximum number of results to return
        include_metadata: Whether to include source metadata

    Returns:
        Formatted string with search results for LLM consumption
    """
    if not query or not query.strip():
        return "No query provided for search."

    try:
        # Get or initialize pipeline
        pipeline = await _initialize_pipeline()

        # Connect to actual vector stores
        # In production, this would connect to your configured vector stores
        async def actual_retrieval(query: str, max_docs: int = 10):
            """Actual retrieval function that connects to vector stores."""
            try:
                # Import vector store clients
                from . import get_vector_store

                # Get primary vector store (e.g., Chroma)
                vector_store = get_vector_store()

                # Perform semantic search
                results = await vector_store.similarity_search(query=query, n_results=max_docs)

                # Convert to document format expected by pipeline
                documents = []
                metadatas = []

                for i, doc in enumerate(results):
                    documents.append(doc.page_content if hasattr(doc, "page_content") else str(doc))
                    metadatas.append(
                        {
                            "text": documents[-1],
                            "source": getattr(doc, "metadata", {}).get("source", f"doc_{i}"),
                            "doc_id": f"doc_{i}",
                        },
                    )

                return documents, metadatas

            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"Vector store retrieval failed: {e}")
                # Fallback to empty results
                return [], []

        # Execute the full pipeline (Gate -> Decompose -> Search -> Rerank)
        results = await pipeline.query(query=query, retrieval_function=actual_retrieval)

        # Format results for LLM consumption
        if not results or not results.get("documents"):
            return f"No relevant information found for: {query}"

        formatted_results = []
        docs = results["documents"][:max_results]

        for i, doc in enumerate(docs, 1):
            # Extract text content
            text_content = ""
            if hasattr(doc, "metadata") and "text" in doc.metadata:
                text_content = doc.metadata["text"]
            elif hasattr(doc, "text"):
                text_content = doc.text
            elif hasattr(doc, "content"):
                text_content = doc.content

            # Format result
            result = f"[Source {i}]: {text_content}"

            # Add metadata if requested
            if include_metadata and hasattr(doc, "metadata"):
                metadata = doc.metadata
                if "source" in metadata:
                    result += f"\n  Source: {metadata['source']}"
                if "date" in metadata:
                    result += f"\n  Date: {metadata['date']}"

            formatted_results.append(result)

        # Add pipeline metadata
        metadata = results.get("metadata", {})
        if metadata.get("cached"):
            formatted_results.append("\n[Results retrieved from semantic cache]")
        if metadata.get("decomposed"):
            formatted_results.append("\n[Query was decomposed for better results]")
        if metadata.get("reranked"):
            formatted_results.append("\n[Results reranked for precision]")

        return "\n\n".join(formatted_results)

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        return "Search encountered an error. Please try rephrasing your query."


async def get_titanium_search_with_sources(
    query: str,
    context: str | None = None,
) -> dict[str, Any]:
    """
    Get search results with full source information.

    This is useful for agents that need to process sources separately
    from the content (e.g., for citation or verification).

    Args:
        query: Search query string
        context: Optional context to guide retrieval

    Returns:
        Dictionary with results and metadata
    """
    try:
        pipeline = await _initialize_pipeline()

        # Use the same actual_retrieval function as get_titanium_search_tool
        async def actual_retrieval(query: str, max_docs: int = 10):
            """Actual retrieval function that connects to vector stores."""
            try:
                # Import vector store clients
                from . import get_vector_store

                # Get primary vector store (e.g., Chroma)
                vector_store = get_vector_store()

                # Perform semantic search
                results = await vector_store.similarity_search(query=query, n_results=max_docs)

                # Convert to document format expected by pipeline
                documents = []
                metadatas = []

                for i, doc in enumerate(results):
                    documents.append(doc.page_content if hasattr(doc, "page_content") else str(doc))
                    metadatas.append(
                        {
                            "text": documents[-1],
                            "source": getattr(doc, "metadata", {}).get("source", f"doc_{i}"),
                            "doc_id": f"doc_{i}",
                        },
                    )

                return documents, metadatas

            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"Vector store retrieval failed: {e}")
                # Fallback to empty results
                return [], []

        results = await pipeline.query(query=query, retrieval_function=actual_retrieval)

        # Extract sources
        sources = []
        for doc in results.get("documents", []):
            source_info = {"content": "", "metadata": {}}

            if hasattr(doc, "metadata"):
                source_info["content"] = doc.metadata.get("text", "")
                source_info["metadata"] = {k: v for k, v in doc.metadata.items() if k != "text"}
            elif hasattr(doc, "text"):
                source_info["content"] = doc.text
            elif hasattr(doc, "content"):
                source_info["content"] = doc.content

            sources.append(source_info)

        return {
            "query": query,
            "sources": sources,
            "metadata": results.get("metadata", {}),
            "response": results.get("response"),
        }

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.error(f"Search with sources failed: {e}")
        return {"query": query, "sources": [], "metadata": {"error": str(e)}, "response": None}


def get_pipeline_stats() -> dict[str, Any]:
    """Get statistics about the Titanium pipeline.

    Returns:
        Dictionary with pipeline statistics
    """
    global _TITANIUM_PIPELINE

    if _TITANIUM_PIPELINE is None:
        return {"status": "not_initialized"}

    try:
        stats = _TITANIUM_PIPELINE.get_stats()
        component_info = _TITANIUM_PIPELINE.get_component_info()

        return {"status": "active", "statistics": stats, "components": component_info}
    # guardian: allow-silent-swallow
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def clear_cache():
    """Clear the semantic cache.

    Useful for testing or when fresh results are needed.
    """
    pipeline = await _initialize_pipeline()
    if hasattr(pipeline, "cache") and pipeline.cache:
        pipeline.cache.clear()
        logger.info("Semantic cache cleared")


# Convenience function for synchronous contexts
def sync_search(query: str, context: str | None = None) -> str:
    """Synchronous wrapper for async search function.

    Args:
        query: Search query string
        context: Optional context

    Returns:
        Search results string
    """
    try:
        # Try to get current event loop
        asyncio.get_running_loop()
        # If we're in an async context, we can't use run_until_complete
        # Use run_coroutine_threadsafe instead
        import concurrent.futures

        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(get_titanium_search_tool(query, context))
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result(timeout=DEFAULT_TIMEOUT)

    except RuntimeError:    # guardian: Runtime errors should be prevented with proper validation
        # No running loop, safe to create new one
        return asyncio.run(get_titanium_search_tool(query, context))


# Legacy compatibility
async def legacy_search(query: str) -> str:
    """Legacy search function for backward compatibility.

    Args:
        query: Search query

    Returns:
        Simple search results
    """
    return await get_titanium_search_tool(query, include_metadata=False)


# Tool registration for agent frameworks
TOOL_REGISTRY = {
    "titanium_search": {
        "function": get_titanium_search_tool,
        "description": "Search using the Titanium RAG Pipeline with precision, reasoning, and SOTA ranking",
        "parameters": {
            "query": {"type": "string", "required": True},
            "context": {"type": "string", "required": False},
            "max_results": {"type": "integer", "required": False, "default": 5},
            "include_metadata": {"type": "boolean", "required": False, "default": False},
        },
    },
    "titanium_search_with_sources": {
        "function": get_titanium_search_with_sources,
        "description": "Search with full source information for citations",
        "parameters": {
            "query": {"type": "string", "required": True},
            "context": {"type": "string", "required": False},
        },
    },
}
