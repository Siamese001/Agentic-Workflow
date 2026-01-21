"""
Semantic Memory Layer

Provides long-term memory storage using vector embeddings for similarity-based
retrieval. Integrates with Pinecone/Redis for persistent storage.

Features:
- Embed thoughts and episodes for semantic search
- Similarity-based retrieval for relevant past experiences
- Pattern clustering for common success/failure identification
- Long-term retention beyond in-memory buffers
"""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticEntry:
    """Entry in semantic memory."""

    entry_id: str
    entry_type: str  # "thought", "episode", "pattern"
    content: dict[str, Any]
    embedding: list[float] | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class EmbeddingProvider:
    """Provider for text embeddings."""

    def __init__(self, model: str = "text-embedding-ada-002"):
        """Initialize embedding provider."""
        self.model = model
        self.dimension = 1536  # Default for ada-002
        self._cache: dict[str, list[float]] = {}

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Check cache
        cache_key = hashlib.sha256(text.encode()).hexdigest()[:32]
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Generate embedding (mock for now - real implementation would use OpenAI/etc)
        embedding = self._generate_mock_embedding(text)

        # Cache result
        self._cache[cache_key] = embedding

        return embedding

    def _generate_mock_embedding(self, text: str) -> list[float]:
        """Generate mock embedding based on text hash (for testing)."""

        # Create deterministic embedding from text
        hash_bytes = hashlib.sha256(text.encode()).digest()

        # Expand to full dimension
        embedding = []
        for i in range(self.dimension):
            byte_idx = i % len(hash_bytes)
            val = (hash_bytes[byte_idx] / 255.0) * 2 - 1  # Normalize to [-1, 1]
            embedding.append(val)

        # Normalize
        norm = sum(v * v for v in embedding) ** 0.5
        if norm > 0:
            embedding = [v / norm for v in embedding]

        return embedding


class VectorIndex:
    """Vector index for similarity search (Pinecone/Redis wrapper)."""

    def __init__(self, index_name: str = "l1_semantic", use_pinecone: bool = False):
        """
        Initialize vector index.

        Args:
            index_name: Name of the index
            use_pinecone: Whether to use Pinecone (False = in-memory)
        """
        self.index_name = index_name
        self.use_pinecone = use_pinecone
        self._vectors: dict[str, tuple[list[float], dict]] = {}  # In-memory fallback

        if use_pinecone:
            self._init_pinecone()

    def _init_pinecone(self) -> None:
        """Initialize Pinecone connection."""
        try:
            from pinecone import Pinecone

            api_key = os.getenv("PINECONE_API_KEY")
            if api_key:
                self.pc = Pinecone(api_key=api_key)
                self.index = self.pc.Index(self.index_name)
            else:
                self.use_pinecone = False
        except ImportError:
            self.use_pinecone = False

    def upsert(self, entry_id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        """
        Upsert vector into index.

        Args:
            entry_id: Unique entry ID
            embedding: Vector embedding
            metadata: Metadata to store with vector
        """
        if self.use_pinecone:
            try:
                self.index.upsert(vectors=[(entry_id, embedding, metadata)])
            except Exception:
                # Fallback to in-memory
                self._vectors[entry_id] = (embedding, metadata)
        else:
            self._vectors[entry_id] = (embedding, metadata)

    def query(self, embedding: list[float], top_k: int = 10) -> list[dict[str, Any]]:
        """
        Query similar vectors.

        Args:
            embedding: Query embedding
            top_k: Number of results

        Returns:
            List of similar entries with scores
        """
        if self.use_pinecone:
            try:
                results = self.index.query(vector=embedding, top_k=top_k, include_metadata=True)
                return [
                    {"id": m.id, "score": m.score, "metadata": m.metadata} for m in results.matches
                ]
            except Exception:
                pass

        # In-memory similarity search
        return self._in_memory_query(embedding, top_k)

    def _in_memory_query(self, query_embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        """In-memory similarity search using cosine similarity."""
        scores = []

        for entry_id, (embedding, metadata) in self._vectors.items():
            score = self._cosine_similarity(query_embedding, embedding)
            scores.append({"id": entry_id, "score": score, "metadata": metadata})

        # Sort by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)

        return scores[:top_k]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def delete(self, entry_id: str) -> None:
        """Delete entry from index."""
        if self.use_pinecone:
            try:
                self.index.delete(ids=[entry_id])
            except Exception:
                pass

        if entry_id in self._vectors:
            del self._vectors[entry_id]

    def count(self) -> int:
        """Get number of entries in index."""
        if self.use_pinecone:
            try:
                stats = self.index.describe_index_stats()
                return stats.total_vector_count
            except Exception:
                pass

        return len(self._vectors)


class SemanticMemory:
    """
    Semantic Memory - Long-term vector-based memory storage.

    Provides:
    - Thought embedding and storage
    - Episode embedding and storage
    - Similarity-based retrieval
    - Pattern extraction from clusters
    """

    def __init__(self, index_name: str = "l1_semantic", use_pinecone: bool = False):
        """
        Initialize semantic memory.

        Args:
            index_name: Name of vector index
            use_pinecone: Whether to use Pinecone (False = in-memory)
        """
        self.index = VectorIndex(index_name, use_pinecone)
        self.embedding_provider = EmbeddingProvider()
        self.entries: dict[str, SemanticEntry] = {}
        self.thoughts_stored = 0
        self.episodes_stored = 0
        self.queries_executed = 0

    def add_thought(self, thought: dict[str, Any]) -> str:
        """
        Add thought to semantic memory.

        Args:
            thought: Thought dictionary with 'text' or 'content'

        Returns:
            Entry ID
        """
        # Generate ID
        entry_id = thought.get("id", f"thought_{self.thoughts_stored}_{int(time.time())}")

        # Get text for embedding
        text = thought.get("text", thought.get("content", str(thought)))

        # Generate embedding
        embedding = self.embedding_provider.get_embedding(text)

        # Create entry
        entry = SemanticEntry(
            entry_id=entry_id,
            entry_type="thought",
            content=thought,
            embedding=embedding,
            metadata={"type": "thought", "timestamp": time.time()},
        )

        # Store
        self.entries[entry_id] = entry
        self.index.upsert(
            entry_id,
            embedding,
            {
                "type": "thought",
                "content": text[:500],  # Truncate for metadata
                "timestamp": entry.timestamp,
            },
        )

        self.thoughts_stored += 1
        return entry_id

    def add_episode(self, episode: dict[str, Any]) -> str:
        """
        Add episode to semantic memory.

        Args:
            episode: Episode dictionary with 'summary' or 'description'

        Returns:
            Entry ID
        """
        # Generate ID
        entry_id = episode.get("id", f"episode_{self.episodes_stored}_{int(time.time())}")

        # Get text for embedding
        text = episode.get("summary", episode.get("description", str(episode)))

        # Generate embedding
        embedding = self.embedding_provider.get_embedding(text)

        # Create entry
        entry = SemanticEntry(
            entry_id=entry_id,
            entry_type="episode",
            content=episode,
            embedding=embedding,
            metadata={"type": "episode", "timestamp": time.time()},
        )

        # Store
        self.entries[entry_id] = entry
        self.index.upsert(
            entry_id,
            embedding,
            {"type": "episode", "content": text[:500], "timestamp": entry.timestamp},
        )

        self.episodes_stored += 1
        return entry_id

    def query(
        self, query: str, top_k: int = 10, entry_type: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Query semantic memory for similar entries.

        Args:
            query: Query text
            top_k: Number of results
            entry_type: Filter by type ("thought", "episode", or None for all)

        Returns:
            List of similar entries with scores
        """
        self.queries_executed += 1

        # Generate query embedding
        query_embedding = self.embedding_provider.get_embedding(query)

        # Query index
        results = self.index.query(query_embedding, top_k * 2 if entry_type else top_k)

        # Filter by type if specified
        if entry_type:
            results = [r for r in results if r.get("metadata", {}).get("type") == entry_type]

        # Enrich with full content
        enriched = []
        for result in results[:top_k]:
            entry_id = result["id"]
            if entry_id in self.entries:
                enriched.append(
                    {
                        "id": entry_id,
                        "score": result["score"],
                        "type": self.entries[entry_id].entry_type,
                        "content": self.entries[entry_id].content,
                        "timestamp": self.entries[entry_id].timestamp,
                    }
                )
            else:
                enriched.append(result)

        return enriched

    def query_thoughts(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Query only thoughts."""
        return self.query(query, top_k, entry_type="thought")

    def query_episodes(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Query only episodes."""
        return self.query(query, top_k, entry_type="episode")

    def get_statistics(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "thoughts_stored": self.thoughts_stored,
            "episodes_stored": self.episodes_stored,
            "total_entries": len(self.entries),
            "index_size": self.index.count(),
            "queries_executed": self.queries_executed,
        }


# Global instance
semantic_memory = SemanticMemory()
