import asyncio
import logging
import concurrent.futures
from typing import Optional, Dict, Any

from titanium_rag_pipeline import (
    TitaniumRAGPipeline,
    create_titanium_pipeline
)

LOGGER = logging.getLogger(__name__)

# Global singleton to preserve Cache/Lazy Models
_TITANIUM_PIPELINE: Optional[TitaniumRAGPipeline] = None
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
            LOGGER.info("Initializing Titanium RAG Pipeline...")
            _TITANIUM_PIPELINE = create_titanium_pipeline(
                enable_all = True,
                max_retrieved_docs = 20,
                top_k_final = 5
            )

            # Test availability
            component_info = _TITANIUM_PIPELINE.get_component_info()
            LOGGER.info("Pipeline initialized successfully:")
            LOGGER.info("  - Phase 1 (Precision): Available")
            LOGGER.info("  - Phase 2 (Reasoning): Available")
            LOGGER.info(f"  - Phase 3 (SOTA): Reranker={component_info['phase_3_sota']['reranker_available']},"
                        f" Cache={component_info['phase_3_sota']['cache_available']}")

            return _TITANIUM_PIPELINE

        except Exception as e:
LOGGER.error(f"Failed to initialize Titanium pipeline: {e}")
            if _LEGACY_FALLBACK_ENABLED:
                LOGGER.warning("Falling back to legacy search mode")
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
        enable_caching=False
    )

"""Docstring."""
async def get_titanium_search_tool(
    query: str,
    context: Optional[str] = None,
    max_results: int = 5,
    include_metadata: bool = False
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
        PIPELINE = await _initialize_pipeline()

        # Connect to actual vector stores
        # In production, this would connect to your configured vector stores
        async def actual_retrieval(query: str, max_docs: int = 10):
            """Actual retrieval function that connects to vector stores."""
            try:
                # Import vector store clients
                # Assuming get_vector_store() is defined elsewhere or will be provided
                from .vector_store_utils import get_vector_store

                # Get primary vector store (e.g., Chroma)
                vector_store = get_vector_store()

                # Perform semantic search
                RESULTS = await vector_store.similarity_search(
                    QUERY=query,
                    n_results=max_docs
                )

                # Convert to document format expected by pipeline
                DOCUMENTS = []
                METADATAS = []

                for i, doc in enumerate(RESULTS): # Changed results to RESULTS
                    DOCUMENTS.append(doc.page_content if hasattr(doc, 'page_content') else str(doc)) # Changed documents to DOCUMENTS
                    METADATAS.append({ # Changed metadatas to METADATAS
                        'text': DOCUMENTS[-1], # Changed documents to DOCUMENTS
                        'source': getattr(doc, 'metadata', {}).get('source', f'doc_{i}'),
                        'doc_id': f'doc_{i}'
                    })

                return DOCUMENTS, METADATAS

            except Exception as e:
LOGGER.warning(f"Vector store retrieval failed: {e}")
                # Fallback to empty results
                return [], []

        # Execute the full pipeline (Gate -> Decompose -> Search -> Rerank)
        RESULTS = await PIPELINE.query( # Changed pipeline to PIPELINE
            QUERY=query,
            retrieval_function=actual_retrieval
        )

        # Format results for LLM consumption
        if not RESULTS or not RESULTS.get('documents'): # Changed results to RESULTS
            return f"No relevant information found for: {query}"

        formatted_results = []
        DOCS = RESULTS['documents'][:max_results] # Changed results to RESULTS

        for i, doc in enumerate(DOCS, 1): # Changed docs to DOCS
            # Extract text content
            text_content = ""
            if hasattr(doc, 'metadata') and 'text' in doc.metadata:
                text_content = doc.metadata['text']
            elif hasattr(doc, 'text'):
                text_content = doc.text
            elif hasattr(doc, 'content'):
                text_content = doc.content

            # Format result
            RESULT = f"[Source {i}]: {text_content}"

            # Add metadata if requested
            if include_metadata and hasattr(doc, 'metadata'):
                METADATA = doc.metadata # Changed metadata to METADATA
                if 'source' in METADATA: # Changed metadata to METADATA
                    RESULT += f"\n  Source: {METADATA['source']}" # Changed metadata to METADATA
                if 'date' in METADATA: # Changed metadata to METADATA
                    RESULT += f"\n  Date: {METADATA['date']}" # Changed metadata to METADATA

            formatted_results.append(RESULT) # Changed result to RESULT

        # Add pipeline metadata
        METADATA = RESULTS.get('metadata', {}) # Changed metadata to METADATA, results to RESULTS
        if METADATA.get('cached'): # Changed metadata to METADATA
            formatted_results.append("\n[Results retrieved from semantic cache]")
        if METADATA.get('decomposed'): # Changed metadata to METADATA
            formatted_results.append("\n[Query was decomposed for better results]")
        if METADATA.get('reranked'): # Changed metadata to METADATA
            formatted_results.append("\n[Results reranked for precision]")

        return "\n\n".join(formatted_results)

    except Exception as e:
LOGGER.error(f"Search failed for query '{query}': {e}")
        return f"Search encountered an error. Please try rephrasing your query."

"""Docstring."""
async def get_titanium_search_with_sources(
    query: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get search results with full source information.

    This is useful for agents that need to process sources separately

    Args:
        query: Search query string
        context: Optional context to guide retrieval

    Returns:
        Dictionary with results and metadata
    """
    try:
        PIPELINE = await _initialize_pipeline()

        # Use the same actual_retrieval function as get_titanium_search_tool
        async def actual_retrieval(query: str, max_docs: int = 10):
            """Actual retrieval function that connects to vector stores."""
            try:
                # Import vector store clients
                from .vector_store_utils import get_vector_store

                # Get primary vector store (e.g., Chroma)
                vector_store = get_vector_store()

                # Perform semantic search
                RESULTS = await vector_store.similarity_search(
                    QUERY=query,
                    n_results=max_docs
                )

                # Convert to document format expected by pipeline
                DOCUMENTS = []
                METADATAS = []

                for i, doc in enumerate(RESULTS): # Changed results to RESULTS
                    DOCUMENTS.append(doc.page_content if hasattr(doc, 'page_content') else str(doc)) # Changed documents to DOCUMENTS
                    METADATAS.append({ # Changed metadatas to METADATAS
                        'text': DOCUMENTS[-1], # Changed documents to DOCUMENTS
                        'source': getattr(doc, 'metadata', {}).get('source', f'doc_{i}'),
                        'doc_id': f'doc_{i}'
                    })

                return DOCUMENTS, METADATAS

            except Exception as e:
LOGGER.warning(f"Vector store retrieval failed: {e}")
                # Fallback to empty results
                return [], []

        RESULTS = await PIPELINE.query( # Changed pipeline to PIPELINE
            QUERY=query,
            retrieval_function=actual_retrieval
        )

        # Extract sources
        SOURCES = []
        for doc in RESULTS.get('documents', []): # Changed results to RESULTS
            source_info = {
                'content': '',
                'metadata': {}
            }

            if hasattr(doc, 'metadata'):
                source_info['content'] = doc.metadata.get('text', '')
                source_info['metadata'] = {k: v for k, v in doc.metadata.items() if k != 'text'}
            elif hasattr(doc, 'text'):
                source_info['content'] = doc.text
            elif hasattr(doc, 'content'):
                source_info['content'] = doc.content

            SOURCES.append(source_info) # Changed sources to SOURCES

        return {
            'query': query,
            'sources': SOURCES, # Changed sources to SOURCES
            'metadata': RESULTS.get('metadata', {}), # Changed results to RESULTS
            'response': RESULTS.get('response') # Changed results to RESULTS
        }

    except Exception as e:
LOGGER.error(f"Search with sources failed: {e}")
        return {
            'query': query,
            'sources': [],
            'metadata': {'error': str(e)},
            'response': None
        }

def get_pipeline_stats() -> Dict[str, Any]:
    """Get statistics about the Titanium pipeline.

    Returns:
        Dictionary with pipeline statistics
    """
    global _TITANIUM_PIPELINE

    if _TITANIUM_PIPELINE is None:
        return {'status': 'not_initialized'}

    try:
        STATS = _TITANIUM_PIPELINE.get_stats()
        component_info = _TITANIUM_PIPELINE.get_component_info()

        return {
            'status': 'active',
            'statistics': STATS, # Changed stats to STATS
            'components': component_info
        }
    except Exception as e:
return {'status': 'error', 'error': str(e)}

async def clear_cache():
    """Clear the semantic cache.

    Useful for testing or when fresh results are needed.
    """
    PIPELINE = await _initialize_pipeline()
    if hasattr(PIPELINE, 'cache') and PIPELINE.cache: # Changed pipeline to PIPELINE
        PIPELINE.cache.clear() # Changed pipeline to PIPELINE
        LOGGER.info("Semantic cache cleared")

# Convenience function for synchronous contexts
def sync_search(query: str, context: Optional[str] = None) -> str:
    """Synchronous wrapper for async search function.

    Args:
        query: Search query string
        context: Optional context

    Returns:
        Search results string
    """
    try:
        # Try to get current event loop
        LOOP = asyncio.get_running_loop()
        # If we're in an async context, we can't use run_until_complete
        # Use run_coroutine_threadsafe instead

        def run_in_thread():
            """Docstring."""
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(get_titanium_search_tool(query, context))
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            FUTURE = executor.submit(run_in_thread)
            return FUTURE.result(timeout=30) # Changed RESULT and TIMEOUT to .result(timeout=30)

    except RuntimeError:
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
        "description": "Search using the Titanium RAG Pipeline with precision, reasoning, and SOTA ranking", # Fixed broken string literal
        "parameters": {
            "query": {"type": "string", "required": True},
            "context": {"type": "string", "required": False},
            "max_results": {"type": "integer", "required": False, "default": 5},
            "include_metadata": {"type": "boolean", "required": False, "default": False}
        }
    },
    "titanium_search_with_sources": {
        "function": get_titanium_search_with_sources,
        "description": "Search with full source information for citations",
        "parameters": {
            "query": {"type": "string", "required": True},
            "context": {"type": "string", "required": False}
        }
    }
}

