"""
SemanticMemory - Semantic memory storage for cognitive agents.

Provides semantic memory capabilities with embedding-based retrieval.
"""
import logging
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class EmbeddingProvider:
    """Provider for embeddings."""

    def __init__(self, model: str='BAAI/bge-m3'):
        self.model = model

    def embed(self, text: str) -> list[float]:
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text
            result = bmg_embed_text(text)
            if result:
                return result
        except (ImportError, AttributeError, ValueError) as e:
            print(f'Embedding failed: {e}')
        return [0.0] * 1024

class VectorIndex:
    """Index for vector storage and retrieval."""

    def __init__(self, dimension: int=1024):
        self.dimension = dimension
        self._vectors: dict[str, list[float]] = {}

    def add(self, key: str, vector: list[float]) -> None:
        self._vectors[key] = vector

    def search(self, query: list[float], top_k: int=5) -> list[str]:
        if not self._vectors:
            return []
        try:
            import numpy as np
            q = np.array(query, dtype=np.float32)
            q_norm = q / (np.linalg.norm(q) + 1e-08)
            scored = []
            for key, vec in self._vectors.items():
                v = np.array(vec, dtype=np.float32)
                v_norm = v / (np.linalg.norm(v) + 1e-08)
                scored.append((float(np.dot(q_norm, v_norm)), key))
            scored.sort(reverse=True)
            return [k for _, k in scored[:top_k]]
        except (ImportError, AttributeError, ValueError) as e:
            print(f'Vector search failed: {e}')
            return list(self._vectors.keys())[:top_k]

class SemanticEntry:
    """Entry in semantic memory."""

    def __init__(self, key: str, value: Any, embedding: list[float] | None=None):
        self.key = key
        self.value = value
        self.embedding = embedding
        self.metadata: dict[str, Any] = {}

class SemanticMemory:
    """Semantic memory store with embedding-based retrieval."""

    def __init__(self):
        self._memories: dict[str, dict[str, Any]] = {}
        self._embeddings: dict[str, list[float]] = {}

    def store(self, key: str, value: Any, embedding: list[float] | None=None) -> None:
        """Store a memory with optional embedding."""
        self._memories[key] = {'value': value, 'metadata': {}}
        if embedding:
            self._embeddings[key] = embedding

    def retrieve(self, key: str) -> Any | None:
        """Retrieve a memory by key."""
        memory = self._memories.get(key)
        return memory['value'] if memory else None

    def search(self, query_embedding: list[float], top_k: int=5) -> list[dict[str, Any]]:
        """Search memories by embedding similarity (normalized cosine)."""
        if not self._embeddings:
            return []
        try:
            import numpy as np
            q = np.array(query_embedding, dtype=np.float32)
            q_norm = q / (np.linalg.norm(q) + 1e-08)
            results = []
            for key, embedding in self._embeddings.items():
                if key in self._memories:
                    v = np.array(embedding, dtype=np.float32)
                    v_norm = v / (np.linalg.norm(v) + 1e-08)
                    similarity = float(np.dot(q_norm, v_norm))
                    results.append({'key': key, 'value': self._memories[key]['value'], 'similarity': similarity})
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
        except (ImportError, AttributeError, KeyError) as e:
            print(f'Memory search failed: {e}')
            return []

    def delete(self, key: str) -> None:
        """Delete a memory."""
        if key in self._memories:
            del self._memories[key]
        if key in self._embeddings:
            del self._embeddings[key]

    def clear(self) -> None:
        """Clear all memories."""
        self._memories.clear()
        self._embeddings.clear()
__all__ = ['SemanticMemory', 'SemanticEntry', 'EmbeddingProvider', 'VectorIndex']
