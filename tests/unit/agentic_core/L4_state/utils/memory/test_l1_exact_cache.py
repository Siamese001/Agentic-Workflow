"""Tests for L1 Exact Cache implementation."""

import pytest

# Check if l1_exact_cache is available
try:
    from agentic_core.L4_state.utils.memory.l1_exact_cache import (
        CacheHit,
        L1CacheManager,
        L1ExactCache,
        get_global_l1_cache,
        l1_cache_get,
        l1_cache_set,
    )

    L1_CACHE_AVAILABLE = True
except ImportError:
    L1_CACHE_AVAILABLE = False


@pytest.mark.skipif(not L1_CACHE_AVAILABLE, reason="L1 exact cache not available")
class TestL1ExactCache:
    """Test L1 Exact Cache functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.cache = L1ExactCache()

    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = self.cache._generate_key("test query")
        key2 = self.cache._generate_key("test query")
        key3 = self.cache._generate_key("Test Query")

        assert key1 == key2  # Same query
        assert key1 == key3  # Case insensitive
        assert key1.startswith("l1_exact:")
        assert len(key1) > 10  # Has hash

    def test_cache_set_and_get(self):
        """Test cache set and get operations."""
        query = "test query"
        response = "test response"

        # Set cache
        success = self.cache.set(query, response)
        assert success is True

        # Get from cache
        hit = self.cache.get(query)
        assert hit is not None
        assert isinstance(hit, CacheHit)
        assert hit.response == response
        assert hit.query_hash == hit.cache_key[len("l1_exact:") :]

    def test_cache_miss(self):
        """Test cache miss handling."""
        query = "nonexistent query"

        hit = self.cache.get(query)
        assert hit is None

    def test_cache_delete(self):
        """Test cache deletion."""
        query = "test query"
        response = "test response"

        # Set and verify
        self.cache.set(query, response)
        assert self.cache.get(query) is not None

        # Delete and verify
        success = self.cache.delete(query)
        assert success is True
        assert self.cache.get(query) is None

    def test_cache_clear(self):
        """Test cache clearing."""
        # Add multiple entries
        self.cache.set("query1", "response1")
        self.cache.set("query2", "response2")

        assert self.cache.get("query1") is not None
        assert self.cache.get("query2") is not None

        # Clear all
        success = self.cache.clear()
        assert success is True
        assert self.cache.get("query1") is None
        assert self.cache.get("query2") is None

    def test_cache_stats(self):
        """Test cache statistics."""
        # Add entries
        self.cache.set("query1", "response1")
        self.cache.set("query2", "response2")

        # Generate hits and misses
        self.cache.get("query1")  # hit
        self.cache.get("query2")  # hit
        self.cache.get("nonexistent")  # miss

        stats = self.cache.get_stats()
        assert stats["hit_count"] == 2
        assert stats["miss_count"] == 1
        assert stats["hit_rate"] == 2 / 3
        assert stats["cache_type"] == "local"

    def test_cache_ttl(self):
        """Test cache TTL."""
        query = "test query"
        response = "test response"
        ttl = 3600

        self.cache.set(query, response, ttl=ttl)
        hit = self.cache.get(query)

        assert hit is not None
        assert hit.ttl_seconds == ttl

    def test_cache_metadata(self):
        """Test cache metadata preservation."""
        query = "test query"
        response = "test response"
        metadata = {"source": "test", "version": 1}

        self.cache.set(query, response, metadata=metadata)
        hit = self.cache.get(query)

        assert hit is not None
        assert hit.metadata == metadata

    def test_pattern_invalidation(self):
        """Test pattern-based invalidation."""
        # Add entries
        self.cache.set("query about cats", "response about cats and kittens")
        self.cache.set("query about dogs", "response about dogs and puppies")
        self.cache.set("query about birds", "response about birds and parrots")

        # Invalidate pattern
        count = self.cache.invalidate_pattern("cats")
        assert count == 1

        # Verify specific entry removed
        assert self.cache.get("query about cats") is None
        assert self.cache.get("query about dogs") is not None
        assert self.cache.get("query about birds") is not None


class TestL1CacheManager:
    """Test L1 Cache Manager."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = L1CacheManager()

    def test_zone_caches(self):
        """Test zone-specific caches."""
        queries_cache = self.manager.get_cache("queries")
        embeddings_cache = self.manager.get_cache("embeddings")
        completions_cache = self.manager.get_cache("completions")

        assert queries_cache is not None
        assert embeddings_cache is not None
        assert completions_cache is not None

        # Different instances
        assert queries_cache is not embeddings_cache
        assert embeddings_cache is not completions_cache

    def test_all_stats(self):
        """Test aggregated statistics."""
        # Add entries to different zones
        self.manager.get_cache("queries").set("query1", "response1")
        self.manager.get_cache("embeddings").set("embed1", "vector1")

        stats = self.manager.get_all_stats()

        assert "queries" in stats
        assert "embeddings" in stats
        assert "completions" in stats
        assert stats["queries"]["hit_count"] == 0
        assert stats["embeddings"]["hit_count"] == 0

    def test_clear_all(self):
        """Test clearing all zones."""
        # Add entries
        self.manager.get_cache("queries").set("query1", "response1")
        self.manager.get_cache("embeddings").set("embed1", "vector1")

        # Clear all
        success = self.manager.clear_all()
        assert success is True

        # Verify all cleared
        assert self.manager.get_cache("queries").get("query1") is None
        assert self.manager.get_cache("embeddings").get("embed1") is None


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_global_cache(self):
        """Test global cache instance."""
        cache = get_global_l1_cache()
        assert cache is not None
        assert isinstance(cache, L1ExactCache)

        # Same instance on subsequent calls
        cache2 = get_global_l1_cache()
        assert cache is cache2

    def test_convenience_functions(self):
        """Test convenience functions."""
        query = "test query"
        response = "test response"

        # Set using convenience function
        success = l1_cache_set(query, response)
        assert success is True

        # Get using convenience function
        retrieved = l1_cache_get(query)
        assert retrieved == response
