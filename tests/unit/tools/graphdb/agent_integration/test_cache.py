"""Tests for Query Cache - Phase 1 GraphDB integration."""

import pytest
import time
from unittest.mock import patch

from tools.graphdb.agent_integration.cache import QueryCache, SmartQueryCache, CacheEntry


class TestCacheEntry:
    """Test suite for CacheEntry."""

    def test_cache_entry_creation(self):
        """Test cache entry creation."""
        entry = CacheEntry(value="test_value", timestamp=time.time(), ttl=300.0)

        assert entry.value == "test_value"
        assert entry.ttl == 300.0
        assert entry.hit_count == 0
        assert entry.access_frequency == 0.0

    def test_is_expired(self):
        """Test expiration checking."""
        current_time = time.time()

        # Non-expired entry
        entry = CacheEntry(value="test", timestamp=current_time, ttl=300.0)
        assert not entry.is_expired()

        # Expired entry
        entry = CacheEntry(value="test", timestamp=current_time - 400.0, ttl=300.0)
        assert entry.is_expired()

    def test_record_hit(self):
        """Test hit recording."""
        entry = CacheEntry(value="test", timestamp=time.time() - 10.0, ttl=300.0)

        # Record first hit
        entry.record_hit()
        assert entry.hit_count == 1
        assert entry.access_frequency > 0.0

        # Record second hit
        entry.record_hit()
        assert entry.hit_count == 2
        assert entry.access_frequency > entry.access_frequency  # Should increase


class TestQueryCache:
    """Test suite for QueryCache."""

    @pytest.fixture
    def cache(self):
        """Create cache for testing."""
        return QueryCache(max_size=10, default_ttl=60.0)

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = QueryCache(max_size=100, default_ttl=300.0)

        assert cache.max_size == 100
        assert cache.default_ttl == 300.0
        assert len(cache._cache) == 0
        assert cache._hits == 0
        assert cache._misses == 0

    def test_set_and_get(self, cache):
        """Test basic set and get operations."""
        cache.set("test_key", "test_value")
        result = cache.get("test_key")

        assert result == "test_value"
        assert cache._hits == 1
        assert cache._misses == 0

    def test_get_nonexistent(self, cache):
        """Test getting non-existent key."""
        result = cache.get("nonexistent_key")

        assert result is None
        assert cache._hits == 0
        assert cache._misses == 1

    def test_get_expired(self, cache):
        """Test getting expired entry."""
        # Set with very short TTL
        cache.set("expired_key", "expired_value", ttl=0.1)

        # Wait for expiration
        time.sleep(0.2)

        result = cache.get("expired_key")

        assert result is None
        assert cache._hits == 0
        assert cache._misses == 1
        assert "expired_key" not in cache._cache

    def test_delete(self, cache):
        """Test entry deletion."""
        cache.set("delete_key", "delete_value")

        # Delete existing entry
        result = cache.delete("delete_key")
        assert result is True
        assert cache.get("delete_key") is None

        # Delete non-existent entry
        result = cache.delete("nonexistent")
        assert result is False

    def test_clear(self, cache):
        """Test cache clearing."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert len(cache._cache) == 2

        cache.clear()

        assert len(cache._cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cleanup_expired(self, cache):
        """Test cleanup of expired entries."""
        # Add entries with different TTLs
        cache.set("fresh_key", "fresh_value", ttl=60.0)
        cache.set("expired_key1", "expired_value1", ttl=0.1)
        cache.set("expired_key2", "expired_value2", ttl=0.1)

        # Wait for expiration
        time.sleep(0.2)

        # Cleanup expired entries
        removed_count = cache.cleanup_expired()

        assert removed_count == 2
        assert len(cache._cache) == 1
        assert cache.get("fresh_key") == "fresh_value"
        assert cache.get("expired_key1") is None
        assert cache.get("expired_key2") is None

    def test_max_size_eviction(self, cache):
        """Test eviction when max size is reached."""
        # Fill cache to max size
        for i in range(10):
            cache.set(f"key_{i}", f"value_{i}")

        assert len(cache._cache) == 10

        # Add one more entry (should trigger eviction)
        cache.set("new_key", "new_value")

        assert len(cache._cache) == 10
        assert cache.get("new_key") == "new_value"
        # One of the old keys should be evicted
        evicted_count = sum(1 for i in range(10) if cache.get(f"key_{i}") is None)
        assert evicted_count == 1

    def test_get_statistics(self, cache):
        """Test cache statistics."""
        # Add some entries and perform operations
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.get("key1")  # Hit
        cache.get("key3")  # Miss

        stats = cache.get_statistics()

        assert stats["size"] == 2
        assert stats["max_size"] == 10
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["memory_estimate_bytes"] > 0
        assert stats["average_age_seconds"] >= 0

    def test_get_hot_keys(self, cache):
        """Test hot keys detection."""
        # Add entries with different access patterns
        cache.set("hot_key1", "value1")
        cache.set("hot_key2", "value2")
        cache.set("cold_key", "value3")

        # Access hot keys multiple times
        for _ in range(5):
            cache.get("hot_key1")
        for _ in range(3):
            cache.get("hot_key2")

        # Access cold key once
        cache.get("cold_key")

        hot_keys = cache.get_hot_keys(top_n=3)

        assert len(hot_keys) == 3
        assert hot_keys[0]["key"] == "hot_key1"  # Most accessed
        assert hot_keys[0]["hit_count"] == 5
        assert hot_keys[1]["key"] == "hot_key2"
        assert hot_keys[1]["hit_count"] == 3
        assert hot_keys[2]["key"] == "cold_key"
        assert hot_keys[2]["hit_count"] == 1

    def test_thread_safety(self, cache):
        """Test thread safety with RLock."""
        # This is a basic test - in real scenarios, you'd test with multiple threads
        assert hasattr(cache, "_lock")

        # Lock should be usable
        with cache._lock:
            cache.set("thread_test", "thread_value")

        assert cache.get("thread_test") == "thread_value"


class TestSmartQueryCache:
    """Test suite for SmartQueryCache."""

    @pytest.fixture
    def smart_cache(self):
        """Create smart cache for testing."""
        return SmartQueryCache(max_size=10, default_ttl=300.0)

    def test_smart_cache_initialization(self, smart_cache):
        """Test smart cache initialization."""
        assert smart_cache.max_size == 10
        assert smart_cache.default_ttl == 300.0
        assert len(smart_cache._ttl_multipliers) > 0
        assert len(smart_cache._query_patterns) == 0

    def test_adaptive_ttl_calculation(self, smart_cache):
        """Test adaptive TTL calculation."""
        # Test different query types
        illegal_paths_ttl = smart_cache._calculate_adaptive_ttl("illegal_paths_test")
        blast_radius_ttl = smart_cache._calculate_adaptive_ttl("blast_radius_test")
        spine_ttl = smart_cache._calculate_adaptive_ttl("spine_completeness_test")
        general_ttl = smart_cache._calculate_adaptive_ttl("general_test")

        # Spine completeness should have longer TTL
        assert spine_ttl > general_ttl
        # Illegal paths should have shorter TTL
        assert illegal_paths_ttl < general_ttl
        # Blast radius should be moderate
        assert illegal_paths_ttl < blast_radius_ttl < spine_ttl

    def test_extract_query_type(self, smart_cache):
        """Test query type extraction."""
        assert smart_cache._extract_query_type("illegal_paths_module123") == "illegal_paths"
        assert smart_cache._extract_query_type("blast_radius_analysis") == "blast_radius"
        assert smart_cache._extract_query_type("spine_completeness_check") == "spine_completeness"
        assert smart_cache._extract_query_type("historical_comparison") == "historical"
        assert smart_cache._extract_query_type("structural_analysis") == "structural"
        assert smart_cache._extract_query_type("unknown_query") == "general"

    def test_query_pattern_learning(self, smart_cache):
        """Test query pattern learning."""
        # Set a value to trigger pattern learning
        smart_cache.set("test_key", "test_value")

        # Check that pattern was recorded
        assert "test_key" in smart_cache._query_patterns
        pattern = smart_cache._query_patterns["test_key"]

        assert pattern["access_count"] == 1
        assert "first_access" in pattern
        assert "last_access" in pattern
        assert "avg_interval" in pattern

    def test_pattern_based_ttl_adjustment(self, smart_cache):
        """Test TTL adjustment based on query patterns."""
        # Simulate frequent access pattern
        current_time = time.time()
        smart_cache._query_patterns["frequent_key"] = {
            "first_access": current_time - 100.0,
            "last_access": current_time - 10.0,
            "access_count": 10,
            "avg_interval": 10.0,  # Very frequent
        }

        # Should get shorter TTL for frequent queries
        ttl = smart_cache._calculate_adaptive_ttl("frequent_key")
        assert ttl < smart_cache.default_ttl

        # Simulate infrequent access pattern
        smart_cache._query_patterns["infrequent_key"] = {
            "first_access": current_time - 7200.0,  # 2 hours ago
            "last_access": current_time - 3600.0,  # 1 hour ago
            "access_count": 2,
            "avg_interval": 3600.0,  # Very infrequent
        }

        # Should get longer TTL for infrequent queries
        ttl = smart_cache._calculate_adaptive_ttl("infrequent_key")
        assert ttl > smart_cache.default_ttl

    def test_smart_cache_set_with_adaptive_ttl(self, smart_cache):
        """Test smart cache set with adaptive TTL."""
        # Set different types of queries
        smart_cache.set("illegal_paths_test", "value1")
        smart_cache.set("spine_completeness_test", "value2")

        # Check that entries exist
        assert smart_cache.get("illegal_paths_test") == "value1"
        assert smart_cache.get("spine_completeness_test") == "value2"

        # Check that patterns were learned
        assert "illegal_paths_test" in smart_cache._query_patterns
        assert "spine_completeness_test" in smart_cache._query_patterns
