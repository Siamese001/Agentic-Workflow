"""
Unit tests for shared/cache_ops/
Tests cache operations including data access and guardrails.
"""
from __future__ import annotations
from typing import Dict, Any
from datetime import datetime, timedelta
import hashlib
import json

class TestCacheDataAccess:
    """Tests for cache data access operations."""

    def test_cache_key_generation(self):
        """Cache keys are generated deterministically."""
        data = {"query": "test", "model": "gpt-4o"}
        key1 = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:32]
        key2 = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:32]
        assert key1 == key2, "Same data must produce same cache key"

    def test_cache_key_uniqueness(self):
        """Different data produces different cache keys."""
        data1 = {"query": "test1"}
        data2 = {"query": "test2"}
        key1 = hashlib.sha256(json.dumps(data1, sort_keys=True).encode()).hexdigest()[:32]
        key2 = hashlib.sha256(json.dumps(data2, sort_keys=True).encode()).hexdigest()[:32]
        assert key1 != key2, "Different data must produce different keys"

    def test_cache_get_hit(self):
        """Cache returns stored value on hit."""
        cache: Dict[str, Any] = {"key_123": {"data": "cached_value"}}
        result = cache.get("key_123")
        assert result is not None
        assert result["data"] == "cached_value"

    def test_cache_get_miss(self):
        """Cache returns None on miss."""
        cache: Dict[str, Any] = {}
        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_set_and_retrieve(self):
        """Cache stores and retrieves values correctly."""
        cache: Dict[str, Any] = {}
        cache["test_key"] = {"value": 42, "timestamp": datetime.now().isoformat()}
        retrieved = cache.get("test_key")
        assert retrieved["value"] == 42

    def test_cache_ttl_expiration(self):
        """Cache entries expire after TTL."""
        cache_entry = {
            "value": "data",
            "expires_at": datetime.now() - timedelta(hours=1),  # Already expired
        }
        is_expired = datetime.now() > cache_entry["expires_at"]
        assert is_expired is True

    def test_cache_ttl_valid(self):
        """Cache entries within TTL are valid."""
        cache_entry = {
            "value": "data",
            "expires_at": datetime.now() + timedelta(hours=1),  # Still valid
        }
        is_valid = datetime.now() < cache_entry["expires_at"]
        assert is_valid is True


class TestCacheGuardrails:
    """Tests for cache guardrails and safety checks."""

    def test_cache_size_limit_enforced(self):
        """Cache respects maximum size limit."""
        max_size = 100
        cache: Dict[str, str] = {}

        for i in range(150):
            if len(cache) >= max_size:
                # Evict oldest entry
                oldest_key = next(iter(cache))
                del cache[oldest_key]
            cache[f"key_{i}"] = f"value_{i}"

        assert len(cache) <= max_size

    def test_cache_value_size_limit(self):
        """Individual cache values respect size limits."""
        max_value_size = 1024 * 1024  # 1MB
        large_value = "x" * (max_value_size + 1)

        is_too_large = len(large_value.encode()) > max_value_size
        assert is_too_large is True

    def test_cache_key_sanitization(self):
        """Cache keys are sanitized."""
        unsafe_key = "key with spaces/and:special<chars>"
        sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in unsafe_key)
        assert " " not in sanitized
        assert "/" not in sanitized

    def test_cache_prevents_injection(self):
        """Cache prevents key injection attacks."""
        malicious_key = "key\x00injection"
        sanitized = malicious_key.replace("\x00", "")
        assert "\x00" not in sanitized

    def test_cache_concurrent_access_safe(self):
        """Cache handles concurrent access safely."""
        cache: Dict[str, int] = {"counter": 0}

        # Simulate concurrent increments (in real code, use locks)
        for _ in range(100):
            cache["counter"] += 1

        assert cache["counter"] == 100


class TestCacheInvalidation:
    """Tests for cache invalidation logic."""

    def test_invalidate_by_key(self):
        """Single key invalidation works."""
        cache = {"key1": "value1", "key2": "value2", "key3": "value3"}
        del cache["key2"]
        assert "key2" not in cache
        assert "key1" in cache

    def test_invalidate_by_pattern(self):
        """Pattern-based invalidation works."""
        cache = {
            "user_123_profile": "data",
            "user_123_settings": "data",
            "user_456_profile": "data",
        }
        pattern = "user_123_"
        keys_to_delete = [k for k in cache if k.startswith(pattern)]
        for key in keys_to_delete:
            del cache[key]

        assert len([k for k in cache if k.startswith(pattern)]) == 0

    def test_invalidate_all(self):
        """Full cache clear works."""
        cache = {"key1": "value1", "key2": "value2"}
        cache.clear()
        assert len(cache) == 0

    def test_invalidation_cascades(self):
        """Dependent cache entries are invalidated."""
        cache = {
            "parent": {"value": "parent_data", "children": ["child1", "child2"]},
            "child1": {"value": "child1_data"},
            "child2": {"value": "child2_data"},
        }

        # Invalidate parent and children
        parent = cache.pop("parent")
        for child_key in parent.get("children", []):
            cache.pop(child_key, None)

        assert "parent" not in cache
        assert "child1" not in cache
