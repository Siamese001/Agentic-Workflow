"""Native Persistent Cache for L2 Semantic Cache Layer

Implements spec-compliant L2 Semantic Cache using SQLite (scalar) and ChromaDB (vector)
with BGE-M3 embeddings via ChromaDB's built-in embedding function and zero-token return protocols. No GPTCache dependency.
"""

from __future__ import annotations

import hashlib
import logging
import sqlite3
from pathlib import Path
from typing import Any

import chromadb

Logger = logging.getLogger(__name__)


class NativePersistentCacheClient:
    """Native persistent semantic cache for L2 layer.

    Implements spec-compliant semantic caching with:
    - SQLite scalar store (query, response, metadata)
    - ChromaDB vector store (embeddings)
    - Cosine similarity > 0.95 threshold
    - LRU eviction (via last_access_at)
    - Zero-token return on cache hit
    """

    def __init__(
        self,
        cache_dir: str = "artifacts/gptcache",
        similarity_threshold: float = 0.95,
        max_entries: int = 10000,
        embedding_provider: str = "chromadb-default",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """Initialize native persistent cache client.

        Args:
            cache_dir: Directory for cache storage
            similarity_threshold: Similarity threshold for cache hits (default 0.95)
            max_entries: Maximum cache entries (LRU eviction)
            embedding_provider: Provider for embeddings (chromadb-default)
            embedding_model: Model name for embeddings (ChromaDB default)
        """
        self.cache_dir = Path(cache_dir)
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model

        self._hit_count = 0
        self._miss_count = 0
        self._token_savings = 0
        self._cache = None

        self._init_cache()

    def _init_cache(self) -> None:
        """Initialize SQLite scalar store and ChromaDB vector store with built-in embeddings."""
        try:
            # Create cache directory
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Initialize SQLite scalar store
            sqlite_path = self.cache_dir / "l2_cache.db"
            self._sqlite_conn = sqlite3.connect(str(sqlite_path), check_same_thread=False)
            self._sqlite_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS l2_cache (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_access_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._sqlite_conn.commit()

            # Initialize ChromaDB vector store (persistent) with built-in embeddings
            chroma_path = self.cache_dir / "chroma"
            self._chroma_client = chromadb.PersistentClient(path=str(chroma_path))
            # ChromaDB uses default embedding function (all-MiniLM-L6-v2) automatically
            self._chroma_collection = self._chroma_client.get_or_create_collection(
                name="l2_semantic_cache",
                metadata={"hnsw:space": "cosine"}
            )

            self._cache = "real"
            Logger.info(f"Native L2 cache initialized at {self.cache_dir} with SQLite + ChromaDB (built-in embeddings)")

        except ImportError as e:
            Logger.warning(f"ChromaDB not installed: {e}, using mock implementation")
            self._cache = "mock"
        except Exception as e:
            Logger.error(f"Failed to initialize native L2 cache: {e}, using mock")
            self._cache = "mock"

    def _get_id(self, query: str) -> str:
        """Generate deterministic ID from query (SHA256)."""
        return hashlib.sha256(query.encode()).hexdigest()

    def _evict_if_needed(self) -> None:
        """Evict least-recently-accessed entries if over max_entries."""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                cursor = self._sqlite_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM l2_cache")
                count = cursor.fetchone()[0]

                if count > self.max_entries:
                    evict_count = count - self.max_entries
                    # Get least recently accessed entries
                    cursor.execute(
                        """
                        SELECT id FROM l2_cache
                        ORDER BY last_access_at ASC
                        LIMIT ?
                        """,
                        (evict_count,)
                    )
                    ids_to_evict = [row[0] for row in cursor.fetchall()]

                    # Delete from SQLite
                    placeholders = ",".join("?" * len(ids_to_evict))
                    cursor.execute(
                        f"DELETE FROM l2_cache WHERE id IN ({placeholders})",
                        ids_to_evict
                    )
                    self._sqlite_conn.commit()

                    # Delete from ChromaDB
                    if ids_to_evict:
                        self._chroma_collection.delete(ids=ids_to_evict)

                    Logger.info(f"Evicted {evict_count} entries from L2 cache")
                return  # Success, exit retry loop
            except Exception as e:
                if attempt == max_retries - 1:
                    Logger.error(f"Eviction failed after {max_retries} retries: {e}")
                else:
                    Logger.warning(f"Eviction attempt {attempt + 1} failed: {e}, retrying...")

    def get(self, query: str) -> str | None:
        """Get cached response for query.

        Args:
            query: User query string

        Returns:
            Cached response if semantic match > 0.95, else None
            Returns None on error but logs distinct error message
        """
        if self._cache == "mock":
            return self._mock_get(query)

        try:
            # Search ChromaDB for similar entries (ChromaDB handles embeddings automatically)
            results = self._chroma_collection.query(
                query_texts=[query],
                n_results=1
            )

            if results["ids"] and results["ids"][0]:
                top_id = results["ids"][0][0]
                distance = results["distances"][0][0] if results["distances"] else 1.0

                # Convert distance to similarity (cosine: 1 - distance)
                similarity = 1.0 - distance

                if similarity >= self.similarity_threshold:
                    # Fetch response from SQLite
                    cursor = self._sqlite_conn.cursor()
                    cursor.execute(
                        "SELECT response FROM l2_cache WHERE id = ?",
                        (top_id,)
                    )
                    row = cursor.fetchone()

                    if row:
                        # Update last_access_at
                        cursor.execute(
                            "UPDATE l2_cache SET last_access_at = CURRENT_TIMESTAMP WHERE id = ?",
                            (top_id,)
                        )
                        self._sqlite_conn.commit()

                        self._hit_count += 1
                        self._token_savings += len(query.split()) * 2
                        Logger.debug(f"L2 cache HIT for query: {query[:50]}...")
                        return row[0]

            self._miss_count += 1
            Logger.debug(f"L2 cache MISS for query: {query[:50]}...")
            return None

        except Exception as e:
            Logger.error(f"L2 cache get error (returning None): {e}")
            self._miss_count += 1  # Count as miss to avoid silent failure
            return None

    def set(self, query: str, response: str) -> None:
        """Cache response for query.

        Args:
            query: User query string
            response: Response to cache
        """
        if self._cache == "mock":
            self._mock_set(query, response)
            return

        try:
            query_id = self._get_id(query)

            # Upsert to ChromaDB (ChromaDB handles embeddings automatically via documents parameter)
            self._chroma_collection.upsert(
                ids=[query_id],
                documents=[query],
                metadatas={"created_at": "now"}
            )

            # Upsert to SQLite (scalar store)
            self._sqlite_conn.execute(
                """
                INSERT OR REPLACE INTO l2_cache (id, query, response)
                VALUES (?, ?, ?)
                """,
                (query_id, query, response)
            )
            self._sqlite_conn.commit()

            # Evict if over max_entries
            self._evict_if_needed()

            Logger.debug(f"L2 cache SET for query: {query[:50]}...")

        except Exception as e:
            Logger.error(f"L2 cache set error (data may be lost): {e}")
            # Re-raise to alert caller of data loss risk
            raise

    def _mock_get(self, query: str) -> str | None:
        """Mock cache get for testing/development."""
        self._miss_count += 1
        return None

    def _mock_set(self, query: str, response: str) -> None:
        """Mock cache set for testing/development."""
        pass

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total if total > 0 else 0.0

        return {
            "layer": "L2_Semantic_Cache_Native",
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": hit_rate,
            "similarity_threshold": self.similarity_threshold,
            "token_savings_estimate": self._token_savings,
            "max_entries": self.max_entries,
            "provider": self.embedding_provider,
            "model": self.embedding_model,
        }

    def clear(self) -> None:
        """Clear all cached entries."""
        if self._cache == "mock":
            return

        try:
            # Clear ChromaDB collection
            self._chroma_client.delete_collection("l2_semantic_cache")
            self._chroma_collection = self._chroma_client.get_or_create_collection(
                name="l2_semantic_cache"
            )

            # Clear SQLite table
            self._sqlite_conn.execute("DELETE FROM l2_cache")
            self._sqlite_conn.commit()

            Logger.info("Native L2 cache cleared")
        except Exception as e:
            Logger.error(f"Failed to clear native L2 cache: {e}")

    def search_similar(self, query_text: str, threshold: float | None = None) -> list[dict[str, Any]]:
        """Search for semantically similar entries.

        Compatibility method for SemanticCacheManager integration.
        Returns list of results with 'score' and 'metadata' metadata.

        Args:
            query_text: Query text to search for
            threshold: Override similarity threshold (defaults to instance threshold)

        Returns:
            List of dicts with keys: {'score': float, 'metadata': dict}
        """
        if self._cache == "mock":
            self._miss_count += 1
            return []

        try:
            # Use instance threshold if not overridden
            effective_threshold = threshold if threshold is not None else self.similarity_threshold

            # Search ChromaDB (ChromaDB handles embeddings automatically via query_texts)
            results = self._chroma_collection.query(
                query_texts=[query_text],
                n_results=5  # Return top 5 results
            )

            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i, entry_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i] if results["distances"] else 1.0
                    similarity = 1.0 - distance

                    if similarity >= effective_threshold:
                        # Fetch response from SQLite
                        cursor = self._sqlite_conn.cursor()
                        cursor.execute(
                            "SELECT response FROM l2_cache WHERE id = ?",
                            (entry_id,)
                        )
                        row = cursor.fetchone()

                        if row:
                            formatted_results.append({
                                "score": similarity,
                                "metadata": {"payload": row[0]}
                            })

            if formatted_results:
                self._hit_count += 1
            else:
                self._miss_count += 1

            return formatted_results

        except Exception as e:
            Logger.error(f"L2 cache search_similar error: {e}")
            self._miss_count += 1
            return []

    def close(self) -> None:
        """Close database connections."""
        if self._cache == "mock":
            return

        try:
            if hasattr(self, "_sqlite_conn"):
                self._sqlite_conn.close()
            if hasattr(self, "_chroma_client"):
                self._chroma_client.close()
            Logger.info("Native L2 cache connections closed")
        except Exception as e:
            Logger.error(f"Failed to close native L2 cache: {e}")


# Global instance
_global_l2_cache: NativePersistentCacheClient | None = None


def get_global_l2_cache() -> NativePersistentCacheClient:
    """Get or create global L2 cache client."""
    global _global_l2_cache
    if _global_l2_cache is None:
        _global_l2_cache = NativePersistentCacheClient()
    return _global_l2_cache


def get_cached_response(query: str) -> str | None:
    """Convenience function to get cached response."""
    return get_global_l2_cache().get(query)


def cache_response(query: str, response: str) -> None:
    """Convenience function to cache response."""
    return get_global_l2_cache().set(query, response)


# Backward compatibility aliases
GPTCacheClient = NativePersistentCacheClient
get_global_gptcache = get_global_l2_cache