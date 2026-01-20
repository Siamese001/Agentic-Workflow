"""Enhanced Semantic Cache for RAG systems.

Provides semantic similarity-based caching for query results.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json
import time
from datetime import datetime, timedelta


@dataclass
class VectorSimilarityResult:
    """Result of vector similarity search."""
    cache_key: str
    similarity_score: float
    cached_content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CacheEntry:
    """Entry in the semantic cache."""
    key: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime
    ttl_seconds: int = 3600
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)


class EnhancedSemanticCache:
    """Enhanced semantic cache with similarity-based retrieval."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600, similarity_threshold: float = 0.8):
        """Initialize enhanced semantic cache.
        
        Args:
            max_size: Maximum number of entries in cache
            ttl_seconds: Time-to-live for cache entries in seconds
            similarity_threshold: Minimum similarity threshold for matches
        """
        self.entries: Dict[str, CacheEntry] = {}
        self.max_entries = max_size
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.default_ttl = ttl_seconds
        self.similarity_threshold = similarity_threshold
        self.embedding_cache: Dict[str, List[float]] = {}
        
    def get(self, 
            query: str,
            query_embedding: Optional[List[float]] = None,
            top_k: int = 5) -> List[VectorSimilarityResult]:
        """Retrieve cached entries similar to query.
        
        Args:
            query: Query string
            query_embedding: Optional pre-computed query embedding
            top_k: Maximum number of results to return
            
        Returns:
            List of similar cached entries
        """
        if not query_embedding:
            query_embedding = self._get_embedding(query)
        
        results = []
        
        for key, entry in self.entries.items():
            # Skip expired entries
            if entry.is_expired():
                continue
            
            # Calculate similarity
            similarity = self._cosine_similarity(query_embedding, entry.embedding)
            
            if similarity >= self.similarity_threshold:
                result = VectorSimilarityResult(
                    cache_key=key,
                    similarity_score=similarity,
                    cached_content=entry.content,
                    metadata=entry.metadata,
                    timestamp=entry.timestamp
                )
                results.append(result)
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]
    
    def put(self, 
            query: str,
            content: str,
            metadata: Optional[Dict[str, Any]] = None,
            embedding: Optional[List[float]] = None,
            ttl_seconds: Optional[int] = None) -> str:
        """Store content in semantic cache.
        
        Args:
            query: Query string
            content: Content to cache
            metadata: Optional metadata
            embedding: Optional pre-computed embedding
            ttl_seconds: Optional custom TTL
            
        Returns:
            Cache key for the stored entry
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, content)
        
        # Get or generate embedding
        if not embedding:
            embedding = self._get_embedding(query + " " + content)
        
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            timestamp=datetime.now(),
            ttl_seconds=ttl_seconds or self.default_ttl
        )
        
        # Add to cache (evict if necessary)
        if len(self.entries) >= self.max_size:
            self._evict_oldest()
        
        self.entries[cache_key] = entry
        return cache_key
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self.entries.clear()
        self.embedding_cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self.entries.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.entries[key]
            
        return len(expired_keys)
    
    def _generate_cache_key(self, query: str, content: str) -> str:
        """Generate cache key from query and content."""
        combined = f"{query}:{content}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text (mock implementation)."""
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # Mock embedding - in real implementation would use actual embedding model
        # Create deterministic pseudo-random embedding based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        embedding = []
        
        for i in range(0, len(text_hash), 2):
            # Convert hex pairs to float values between -1 and 1
            hex_pair = text_hash[i:i+2]
            value = int(hex_pair, 16) / 255.0 * 2 - 1
            embedding.append(value)
        
        # Cache the embedding
        self.embedding_cache[text] = embedding
        return embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def generate_fingerprint(self, prompt: str, model: str, temperature: float = 0.7, system_prompt: Optional[str] = None) -> str:
        """Generate fingerprint for cache lookup.
        
        Args:
            prompt: Prompt string
            model: Model name
            temperature: Temperature setting
            system_prompt: Optional system prompt
            
        Returns:
            Fingerprint string
        """
        # Strip whitespace from all string inputs
        components = [
            prompt.strip() if isinstance(prompt, str) else str(prompt),
            model.strip() if isinstance(model, str) else str(model),
            str(temperature)
        ]
        if system_prompt is not None:
            components.append(system_prompt.strip() if isinstance(system_prompt, str) else str(system_prompt))
        combined = "|".join(components)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def lookup(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        """Lookup cache entries by fingerprint.
        
        Args:
            fingerprint: Cache fingerprint
            
        Returns:
            Cached data or None
        """
        if fingerprint in self.entries:
            entry = self.entries[fingerprint]
            if not entry.is_expired():
                # Return a copy to prevent modification of cache
                return dict(entry.content)
            else:
                # Remove expired entry
                del self.entries[fingerprint]
        return None
    
    def store(self, fingerprint: str, data: Dict[str, Any], ttl_hours: Optional[float] = None) -> None:
        """Store content in cache.
        
        Args:
            fingerprint: Cache fingerprint
            data: Data to cache
            ttl_hours: Optional TTL in hours
        """
        ttl_seconds = self.ttl_seconds
        if ttl_hours is not None:
            ttl_seconds = int(ttl_hours * 3600)
        
        entry = CacheEntry(
            key=fingerprint,
            content=data,
            embedding=[],  # Not used for fingerprint-based cache
            metadata={"stored_at": datetime.now().isoformat()},
            timestamp=datetime.now(),
            ttl_seconds=ttl_seconds
        )
        
        self.entries[fingerprint] = entry
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary of cache stats
        """
        # Remove expired entries first
        self.cleanup_expired()
        
        fresh_entries = len(self.entries)
        stale_entries = 0  # After cleanup, no stale entries
        
        return {
            "total_entries": fresh_entries,
            "fresh_entries": fresh_entries,
            "stale_entries": stale_entries,
            "embedding_cache_size": len(self.embedding_cache),
            "max_entries": self.max_entries,
            "ttl_seconds": self.ttl_seconds
        }
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match against cached content
            
        Returns:
            Number of entries invalidated
        """
        keys_to_remove = []
        pattern_lower = pattern.lower()
        
        for key, entry in self.entries.items():
            # Check if pattern exists in content (case-insensitive)
            content = str(entry.content).lower()
            if isinstance(entry.content, dict):
                # If content is a dict, check all string values
                for value in entry.content.values():
                    if isinstance(value, str) and pattern_lower in value.lower():
                        keys_to_remove.append(key)
                        break
            elif pattern_lower in content:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.entries[key]
        
        return len(keys_to_remove)


# Import math for cosine similarity
import math
