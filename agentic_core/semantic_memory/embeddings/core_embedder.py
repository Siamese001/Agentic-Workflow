from __future__ import annotations
"""
Sovereign Core Embedder – Primary Embedding Engine
Uses OpenAI text-embedding-3-large (SOTA as of Dec 2025).
Configurable dimensions for Pinecone cost/accuracy trade-off.
SSOT for all embedding calls in the agentic core.
"""
from typing import Any, List
import hashlib
import openai
from cachetools import LRUCache
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# Global deterministic embedding cache (LRU in-memory; extend to diskcache if needed)
_embedding_cache: LRUCache = LRUCache(maxsize=10000)  # ~10k entries × 6KB ≈ 60MB RAM

def get_embedding(text: str, model: str=config.DEFAULT_EMBEDDING_MODEL, dimensions: int=config.DEFAULT_EMBEDDING_DIM) -> List[float]:
    """
    Cached sovereign embedding function – used by bootstrap, healers, and RAG pipelines.
    
    :param text: Input string (will be auto-truncated to model max ~8k tokens)
    :param model: OpenAI embedding model (defaults to config)
    :param dimensions: Output dimensionality (defaults to config: 1024)
    :return: Normalized float vector
    """
    # Normalize text (strip whitespace, replace newlines)
    normalized_text = text.strip().replace('\n', ' ').replace('\r', ' ')
    
    # Cache key: hash of text + model + dimensions
    cache_key = hashlib.sha256(
        f"{normalized_text}{model}{dimensions}".encode('utf-8')
    ).hexdigest()
    
    # Cache hit
    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]
    
    # Cache miss → API call
    if not config.OPENAI_API_KEY:
        raise ValueError('OPENAI_API_KEY environment variable required for core embedder')
    client: Any = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    response: Any = client.embeddings.create(input=normalized_text, model=model, dimensions=dimensions)
    embedding = response.data[0].embedding
    
    # Cache and return
    _embedding_cache[cache_key] = embedding
    return embedding

def clear_embedding_cache() -> None:
    """Utility to clear embedding cache (e.g., for tests or model change)."""
    _embedding_cache.clear()
