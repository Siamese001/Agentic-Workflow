"""Scripts Cache Vector Searcher - Search operations for scripts cache vectors.

This module provides vector search capabilities for scripts cache operations,
including semantic search, similarity matching, and cache-aware retrieval.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import numpy as np
from datetime import datetime, timedelta
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class CacheSearchMode(Enum):
    """Search modes for cache vector operations."""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    METADATA = "metadata"
    RECENT = "recent"


class CacheHitStrategy(Enum):
    """Strategies for cache hit prioritization."""
    RELEVANCE_FIRST = "relevance_first"
    RECENCY_FIRST = "recency_first"
    FREQUENCY_FIRST = "frequency_first"
    SIZE_FIRST = "size_first"


@dataclass
class CacheVectorEntry:
    """Entry in the cache vector store."""
    id: str
    key: str
    vector: List[float]
    content: str
    timestamp: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheSearchQuery:
    """Search query for cache vectors."""
    query_text: str
    query_vector: Optional[List[float]] = None
    search_mode: CacheSearchMode = CacheSearchMode.SEMANTIC
    hit_strategy: CacheHitStrategy = CacheHitStrategy.RELEVANCE_FIRST
    top_k: int = 10
    threshold: float = 0.7
    max_age_hours: Optional[int] = None
    min_access_count: int = 0
    metadata_filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheSearchResult:
    """Result of cache vector search."""
    entries: List[CacheVectorEntry]
    scores: List[float]
    hit_count: int
    miss_count: int
    search_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheVectorConfig:
    """Configuration for cache vector operations."""
    max_entries: int = 10000
    default_ttl_seconds: int = 3600
    cleanup_interval_seconds: int = 300
    enable_persistence: bool = True
    storage_path: str = "data/scripts_cache_vectors.json"
    dimension: int = 1536
    similarity_threshold: float = 0.7


class ScriptsCacheVectorSearcher:
    """Main class for scripts cache vector search operations."""

    def __init__(self, config: Optional[CacheVectorConfig] = None):
        self.config = config or CacheVectorConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._vector_store: Dict[str, CacheVectorEntry] = {}
        self._vector_index: Dict[str, np.ndarray] = {}
        self._last_cleanup = datetime.utcnow()

    def search_cache_vectors(self, query: CacheSearchQuery) -> CacheSearchResult:
        """Search cache vectors based on query.
        
        Args:
            query: Cache search query configuration
            
        Returns:
            CacheSearchResult: Search results with cache statistics
        """
        self.logger.info(f"Searching cache vectors with mode: {query.search_mode.value}")
        
        start_time = datetime.utcnow()
        hit_count = 0
        miss_count = 0
        
        try:
            # Generate query vector if not provided
            if query.query_vector is None and query.search_mode != CacheSearchMode.METADATA:
                query.query_vector = self._generate_query_vector(query.query_text)
            
            # Filter entries based on criteria
            filtered_entries = self._filter_entries(query)
            
            # Perform search based on mode
            if query.search_mode == CacheSearchMode.SEMANTIC:
                results, scores = self._semantic_search(query, filtered_entries)
            elif query.search_mode == CacheSearchMode.HYBRID:
                results, scores = self._hybrid_search(query, filtered_entries)
            elif query.search_mode == CacheSearchMode.METADATA:
                results, scores = self._metadata_search(query, filtered_entries)
            else:  # RECENT
                results, scores = self._recent_search(query, filtered_entries)
            
            # Update access statistics
            for entry in results:
                self._update_access_stats(entry.id)
                hit_count += 1
            
            # Calculate search time
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            search_result = CacheSearchResult(
                entries=results,
                scores=scores,
                hit_count=hit_count,
                miss_count=len(filtered_entries) - hit_count,
                search_time_ms=search_time,
                metadata={
                    "searched_at": datetime.utcnow().isoformat(),
                    "search_mode": query.search_mode.value,
                    "hit_strategy": query.hit_strategy.value,
                    "total_entries": len(self._vector_store)
                }
            )
            
            self.logger.info(
                f"Cache vector search completed: {hit_count} hits in {search_time:.2f}ms"
            )
            
            return search_result
            
        except Exception as e:
            self.logger.error(f"Cache vector search failed: {str(e)}")
            return CacheSearchResult(
                entries=[],
                scores=[],
                hit_count=0,
                miss_count=0,
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                metadata={"error": str(e)}
            )

    def add_cache_vector(self, key: str, vector: List[float], content: str, 
                        ttl_seconds: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a vector to the cache.
        
        Args:
            key: Cache key
            vector: Vector embedding
            content: Content associated with the vector
            ttl_seconds: Time to live in seconds
            metadata: Optional metadata
            
        Returns:
            str: ID of the cached entry
        """
        try:
            # Generate unique ID
            entry_id = self._generate_entry_id(key, content)
            
            # Create cache entry
            entry = CacheVectorEntry(
                id=entry_id,
                key=key,
                vector=vector,
                content=content,
                timestamp=datetime.utcnow(),
                ttl_seconds=ttl_seconds or self.config.default_ttl_seconds,
                size_bytes=len(content.encode('utf-8')) + len(vector) * 4,
                metadata=metadata or {}
            )
            
            # Add to store
            self._vector_store[entry_id] = entry
            self._vector_index[entry_id] = np.array(vector)
            
            # Trigger cleanup if needed
            self._maybe_cleanup()
            
            # Persist if enabled
            if self.config.enable_persistence:
                self._save_to_disk()
            
            self.logger.debug(f"Added cache vector: {entry_id}")
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Failed to add cache vector: {str(e)}")
            return ""

    def get_cache_vector(self, entry_id: str) -> Optional[CacheVectorEntry]:
        """Get a cached vector by ID.
        
        Args:
            entry_id: ID of the cached entry
            
        Returns:
            CacheVectorEntry: Entry if found and valid, None otherwise
        """
        if entry_id in self._vector_store:
            entry = self._vector_store[entry_id]
            
            # Check if expired
            if self._is_expired(entry):
                self._remove_entry(entry_id)
                return None
            
            # Update access stats
            self._update_access_stats(entry_id)
            
            return entry
        
        return None

    def remove_cache_vector(self, entry_id: str) -> bool:
        """Remove a cached vector.
        
        Args:
            entry_id: ID of the entry to remove
            
        Returns:
            bool: True if entry was removed
        """
        return self._remove_entry(entry_id)

    def clear_expired(self) -> int:
        """Clear all expired entries from cache.
        
        Returns:
            int: Number of entries cleared
        """
        expired_ids = []
        now = datetime.utcnow()
        
        for entry_id, entry in self._vector_store.items():
            if self._is_expired(entry, now):
                expired_ids.append(entry_id)
        
        for entry_id in expired_ids:
            self._remove_entry(entry_id)
        
        if expired_ids:
            self.logger.info(f"Cleared {len(expired_ids)} expired cache entries")
        
        return len(expired_ids)

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dict: Cache statistics
        """
        now = datetime.utcnow()
        total_entries = len(self._vector_store)
        expired_count = sum(1 for e in self._vector_store.values() if self._is_expired(e, now))
        
        # Calculate total size
        total_size = sum(e.size_bytes for e in self._vector_store.values())
        
        # Calculate average access count
        access_counts = [e.access_count for e in self._vector_store.values()]
        avg_access = sum(access_counts) / len(access_counts) if access_counts else 0
        
        # Find most accessed entries
        most_accessed = sorted(self._vector_store.values(), key=lambda x: x.access_count, reverse=True)[:5]
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_count,
            "valid_entries": total_entries - expired_count,
            "total_size_bytes": total_size,
            "average_access_count": avg_access,
            "most_accessed": [
                {"id": e.id, "key": e.key, "access_count": e.access_count}
                for e in most_accessed
            ],
            "config": {
                "max_entries": self.config.max_entries,
                "default_ttl_seconds": self.config.default_ttl_seconds,
                "dimension": self.config.dimension
            }
        }

    def _filter_entries(self, query: CacheSearchQuery) -> List[CacheVectorEntry]:
        """Filter cache entries based on query criteria."""
        filtered = []
        now = datetime.utcnow()
        
        for entry in self._vector_store.values():
            # Skip expired entries
            if self._is_expired(entry, now):
                continue
            
            # Filter by age
            if query.max_age_hours:
                age_hours = (now - entry.timestamp).total_seconds() / 3600
                if age_hours > query.max_age_hours:
                    continue
            
            # Filter by access count
            if entry.access_count < query.min_access_count:
                continue
            
            # Filter by metadata
            if query.metadata_filters:
                if not all(entry.metadata.get(k) == v for k, v in query.metadata_filters.items()):
                    continue
            
            filtered.append(entry)
        
        return filtered

    def _semantic_search(self, query: CacheSearchQuery, entries: List[CacheVectorEntry]) -> Tuple[List[CacheVectorEntry], List[float]]:
        """Perform semantic search on cache entries."""
        if not query.query_vector:
            return [], []
        
        query_vector = np.array(query.query_vector)
        scored_entries = []
        
        for entry in entries:
            if entry.id in self._vector_index:
                vector = self._vector_index[entry.id]
                similarity = np.dot(query_vector, vector) / (np.linalg.norm(query_vector) * np.linalg.norm(vector))
                
                if similarity >= query.threshold:
                    scored_entries.append((entry, similarity))
        
        # Sort by similarity
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        
        # Apply hit strategy
        results = self._apply_hit_strategy(scored_entries, query.hit_strategy, query.top_k)
        
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]
        
        return entries, scores

    def _hybrid_search(self, query: CacheSearchQuery, entries: List[CacheVectorEntry]) -> Tuple[List[CacheVectorEntry], List[float]]:
        """Perform hybrid search combining semantic and metadata."""
        # Get semantic results
        semantic_entries, semantic_scores = self._semantic_search(query, entries)
        
        # Get metadata matches
        metadata_entries = []
        for entry in entries:
            score = 0.0
            
            # Score based on recency
            recency_hours = (datetime.utcnow() - entry.timestamp).total_seconds() / 3600
            recency_score = max(0, 1 - recency_hours / 24)  # Decay over 24 hours
            
            # Score based on frequency
            frequency_score = min(1, entry.access_count / 10)  # Normalize to 0-1
            
            # Combined metadata score
            metadata_score = (recency_score + frequency_score) / 2
            
            if metadata_score > 0.1:  # Minimum threshold
                metadata_entries.append((entry, metadata_score))
        
        # Combine results
        combined = {}
        
        # Add semantic results with higher weight
        for entry, score in zip(semantic_entries, semantic_scores):
            combined[entry.id] = (entry, score * 0.7)
        
        # Add metadata results
        for entry, score in metadata_entries:
            if entry.id in combined:
                # Boost existing score
                combined[entry.id] = (entry, combined[entry.id][1] + score * 0.3)
            else:
                combined[entry.id] = (entry, score * 0.3)
        
        # Sort and return top results
        results = sorted(combined.values(), key=lambda x: x[1], reverse=True)[:query.top_k]
        
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]
        
        return entries, scores

    def _metadata_search(self, query: CacheSearchQuery, entries: List[CacheVectorEntry]) -> Tuple[List[CacheVectorEntry], List[float]]:
        """Search based on metadata only."""
        scored_entries = []
        
        for entry in entries:
            score = 0.0
            
            # Score based on access count
            if entry.access_count > 0:
                score += min(1, entry.access_count / 10) * 0.4
            
            # Score based on recency
            age_hours = (datetime.utcnow() - entry.timestamp).total_seconds() / 3600
            if age_hours < 24:
                score += (1 - age_hours / 24) * 0.3
            
            # Score based on size (prefer smaller entries for cache)
            if entry.size_bytes > 0:
                size_score = 1 - min(1, entry.size_bytes / 10000)  # Normalize to 0-1
                score += size_score * 0.3
            
            if score > 0:
                scored_entries.append((entry, score))
        
        # Sort and apply hit strategy
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        results = self._apply_hit_strategy(scored_entries, query.hit_strategy, query.top_k)
        
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]
        
        return entries, scores

    def _recent_search(self, query: CacheSearchQuery, entries: List[CacheVectorEntry]) -> Tuple[List[CacheVectorEntry], List[float]]:
        """Search based on recency only."""
        # Sort by timestamp (newest first)
        sorted_entries = sorted(entries, key=lambda x: x.timestamp, reverse=True)
        
        # Score based on recency
        results = []
        scores = []
        
        for entry in sorted_entries[:query.top_k]:
            age_hours = (datetime.utcnow() - entry.timestamp).total_seconds() / 3600
            score = max(0, 1 - age_hours / 24)  # Decay over 24 hours
            
            results.append(entry)
            scores.append(score)
        
        return results, scores

    def _apply_hit_strategy(self, scored_entries: List[Tuple[CacheVectorEntry, float]], 
                          strategy: CacheHitStrategy, top_k: int) -> List[Tuple[CacheVectorEntry, float]]:
        """Apply hit strategy to ranked entries."""
        if strategy == CacheHitStrategy.RELEVANCE_FIRST:
            # Already sorted by relevance
            return scored_entries[:top_k]
        
        elif strategy == CacheHitStrategy.RECENCY_FIRST:
            # Sort by timestamp first, then by score
            scored_entries.sort(key=lambda x: (x[0].timestamp, x[1]), reverse=True)
            return scored_entries[:top_k]
        
        elif strategy == CacheHitStrategy.FREQUENCY_FIRST:
            # Sort by access count first, then by score
            scored_entries.sort(key=lambda x: (x[0].access_count, x[1]), reverse=True)
            return scored_entries[:top_k]
        
        elif strategy == CacheHitStrategy.SIZE_FIRST:
            # Sort by size (smallest first), then by score
            scored_entries.sort(key=lambda x: (-x[0].size_bytes, x[1]))
            return scored_entries[:top_k]
        
        else:
            return scored_entries[:top_k]

    def _generate_query_vector(self, query_text: str) -> List[float]:
        """Generate vector embedding for query text."""
        # Placeholder for actual embedding generation
        return [0.0] * self.config.dimension

    def _generate_entry_id(self, key: str, content: str) -> str:
        """Generate unique entry ID."""
        hash_input = f"{key}:{content}:{datetime.utcnow().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _is_expired(self, entry: CacheVectorEntry, now: Optional[datetime] = None) -> bool:
        """Check if a cache entry is expired."""
        if not entry.ttl_seconds:
            return False
        
        now = now or datetime.utcnow()
        age_seconds = (now - entry.timestamp).total_seconds()
        return age_seconds > entry.ttl_seconds

    def _update_access_stats(self, entry_id: str) -> None:
        """Update access statistics for an entry."""
        if entry_id in self._vector_store:
            entry = self._vector_store[entry_id]
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()

    def _remove_entry(self, entry_id: str) -> bool:
        """Remove an entry from cache."""
        if entry_id in self._vector_store:
            del self._vector_store[entry_id]
            if entry_id in self._vector_index:
                del self._vector_index[entry_id]
            return True
        return False

    def _maybe_cleanup(self) -> None:
        """Perform cleanup if interval has passed."""
        now = datetime.utcnow()
        if (now - self._last_cleanup).total_seconds() > self.config.cleanup_interval_seconds:
            self.clear_expired()
            
            # Limit total entries
            if len(self._vector_store) > self.config.max_entries:
                # Remove least recently used entries
                sorted_entries = sorted(
                    self._vector_store.items(),
                    key=lambda x: (x[1].last_accessed or x[1].timestamp, x[1].access_count)
                )
                
                # Remove oldest entries
                excess = len(self._vector_store) - self.config.max_entries
                for entry_id, _ in sorted_entries[:excess]:
                    self._remove_entry(entry_id)
                
                self.logger.info(f"Removed {excess} excess cache entries")
            
            self._last_cleanup = now

    def _save_to_disk(self) -> None:
        """Save cache to disk."""
        # Placeholder for persistence implementation
        pass

    def _load_from_disk(self) -> None:
        """Load cache from disk."""
        # Placeholder for persistence implementation
        pass


# Factory function for easy instantiation
def create_scripts_cache_vector_searcher(
    max_entries: int = 10000,
    default_ttl_seconds: int = 3600,
    dimension: int = 1536,
    **kwargs
) -> ScriptsCacheVectorSearcher:
    """Create a configured scripts cache vector searcher."""
    config = CacheVectorConfig(
        max_entries=max_entries,
        default_ttl_seconds=default_ttl_seconds,
        dimension=dimension,
        **kwargs
    )
    return ScriptsCacheVectorSearcher(config)


# Convenience function for direct usage
def search_scripts_cache_vectors(
    query_text: str,
    search_mode: str = "semantic",
    hit_strategy: str = "relevance_first",
    top_k: int = 10,
    threshold: float = 0.7,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Search scripts cache vectors.
    
    Args:
        query_text: Text to search for
        search_mode: Search mode to use
        hit_strategy: Strategy for prioritizing hits
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        config: Optional searcher configuration
        
    Returns:
        Dict: Search results
    """
    # Create searcher and execute search
    searcher_config = CacheVectorConfig(**config or {})
    searcher = ScriptsCacheVectorSearcher(searcher_config)
    
    query = CacheSearchQuery(
        query_text=query_text,
        search_mode=CacheSearchMode(search_mode),
        hit_strategy=CacheHitStrategy(hit_strategy),
        top_k=top_k,
        threshold=threshold
    )
    
    result = searcher.search_cache_vectors(query)
    
    # Convert results to dict for JSON serialization
    return {
        "entries": [
            {
                "id": e.id,
                "key": e.key,
                "content": e.content,
                "timestamp": e.timestamp.isoformat(),
                "access_count": e.access_count,
                "last_accessed": e.last_accessed.isoformat() if e.last_accessed else None,
                "size_bytes": e.size_bytes,
                "metadata": e.metadata
            }
            for e in result.entries
        ],
        "scores": result.scores,
        "hit_count": result.hit_count,
        "miss_count": result.miss_count,
        "search_time_ms": result.search_time_ms,
        "metadata": result.metadata
    }
