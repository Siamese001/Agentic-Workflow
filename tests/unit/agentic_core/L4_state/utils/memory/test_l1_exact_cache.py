"""Tests for L1 Exact Cache implementation."""

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
_l1_exact_cache_module = import_or_skip(
    "agentic_core.L4_state.utils.memory.l1_exact_cache",
    reason="L1 exact cache module unavailable for cache tests",
)
CacheHit = _l1_exact_cache_module.CacheHit
L1CacheManager = _l1_exact_cache_module.L1CacheManager
L1ExactCache = _l1_exact_cache_module.L1ExactCache
get_global_l1_cache = _l1_exact_cache_module.get_global_l1_cache
l1_cache_get = _l1_exact_cache_module.l1_cache_get
l1_cache_set = _l1_exact_cache_module.l1_cache_set


class TestL1ExactCache:
    """Test L1 Exact Cache functionality."""

    def setup_method(self):
        self.cache = L1ExactCache()

    def test_cache_key_generation(self):
        key1 = self.cache._generate_key("test query")
        key2 = self.cache._generate_key("test query")
        key3 = self.cache._generate_key("Test Query")
        assert key1 == key2
        assert key1 == key3
        assert key1.startswith("l1_exact:")
        assert len(key1) > 10

    def test_cache_set_and_get(self):
        query = "test query"
        response = "test response"
        success = self.cache.set(query, response)
        assert success is True
        hit = self.cache.get(query)
        assert hit is not None
        assert isinstance(hit, CacheHit)
        assert hit.response == response
        assert hit.query_hash == hit.cache_key[len("l1_exact:") :]

    def test_cache_miss(self):
        assert self.cache.get("nonexistent query") is None

    def test_cache_delete(self):
        query = "test query"
        self.cache.set(query, "test response")
        assert self.cache.get(query) is not None
        assert self.cache.delete(query) is True
        assert self.cache.get(query) is None

    def test_cache_clear(self):
        self.cache.set("query1", "response1")
        self.cache.set("query2", "response2")
        assert self.cache.clear() is True
        assert self.cache.get("query1") is None
        assert self.cache.get("query2") is None

    def test_cache_stats(self):
        self.cache.set("query1", "response1")
        self.cache.set("query2", "response2")
        self.cache.get("query1")
        self.cache.get("query2")
        self.cache.get("nonexistent")
        stats = self.cache.get_stats()
        assert stats["hit_count"] == 2
        assert stats["miss_count"] == 1
        assert stats["hit_rate"] == 2 / 3
        assert stats["cache_type"] == "local"

    def test_cache_ttl(self):
        self.cache.set("test query", "test response", ttl=3600)
        hit = self.cache.get("test query")
        assert hit is not None
        assert hit.ttl_seconds == 3600

    def test_cache_metadata(self):
        metadata = {"source": "test", "version": 1}
        self.cache.set("test query", "test response", metadata=metadata)
        hit = self.cache.get("test query")
        assert hit is not None
        assert hit.metadata == metadata

    def test_pattern_invalidation(self):
        self.cache.set("query about cats", "response about cats and kittens")
        self.cache.set("query about dogs", "response about dogs and puppies")
        self.cache.set("query about birds", "response about birds and parrots")
        assert self.cache.invalidate_pattern("cats") == 1
        assert self.cache.get("query about cats") is None
        assert self.cache.get("query about dogs") is not None
        assert self.cache.get("query about birds") is not None


class TestL1CacheManager:
    """Test L1 Cache Manager."""

    def setup_method(self):
        self.manager = L1CacheManager()

    def test_zone_caches(self):
        queries_cache = self.manager.get_cache("queries")
        embeddings_cache = self.manager.get_cache("embeddings")
        completions_cache = self.manager.get_cache("completions")
        assert queries_cache is not None
        assert embeddings_cache is not None
        assert completions_cache is not None
        assert queries_cache is not embeddings_cache
        assert embeddings_cache is not completions_cache

    def test_all_stats(self):
        self.manager.get_cache("queries").set("query1", "response1")
        self.manager.get_cache("embeddings").set("embed1", "vector1")
        stats = self.manager.get_all_stats()
        assert "queries" in stats
        assert "embeddings" in stats
        assert "completions" in stats
        assert stats["queries"]["hit_count"] == 0
        assert stats["embeddings"]["hit_count"] == 0

    def test_clear_all(self):
        self.manager.get_cache("queries").set("query1", "response1")
        self.manager.get_cache("embeddings").set("embed1", "vector1")
        assert self.manager.clear_all() is True
        assert self.manager.get_cache("queries").get("query1") is None
        assert self.manager.get_cache("embeddings").get("embed1") is None


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_global_cache(self):
        cache = get_global_l1_cache()
        assert cache is not None
        assert isinstance(cache, L1ExactCache)
        assert cache is get_global_l1_cache()

    def test_convenience_functions(self):
        assert l1_cache_set("test query", "test response") is True
        assert l1_cache_get("test query") == "test response"
