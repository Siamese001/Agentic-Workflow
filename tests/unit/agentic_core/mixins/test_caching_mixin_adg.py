"""ADG-driven tests for agentic_core/mixins/caching_mixin.py — fan_in=2.

Contract tests: CacheEntry, CacheConfig, CachingMixin API.
"""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.caching_mixin import CacheConfig, CacheEntry, CachingMixin


class TestCacheEntry:
    def test_creates_with_value(self):
        entry = CacheEntry(value=42)
        assert entry.value == 42

    def test_default_ttl(self):
        entry = CacheEntry(value="x")
        assert entry.ttl_seconds == 300.0

    def test_default_hits_zero(self):
        entry = CacheEntry(value="x")
        assert entry.hits == 0

    def test_fresh_entry_not_expired(self):
        entry = CacheEntry(value="x", ttl_seconds=3600.0)
        assert entry.is_expired() is False

    def test_expired_entry_is_expired(self):
        entry = CacheEntry(value="x", created_at=time.time() - 1000, ttl_seconds=1.0)
        assert entry.is_expired() is True

    def test_created_at_is_float(self):
        entry = CacheEntry(value="x")
        assert isinstance(entry.created_at, float)


class TestCacheConfig:
    def test_defaults(self):
        cfg = CacheConfig()
        assert cfg.enabled is True
        assert cfg.max_size == 1000
        assert cfg.default_ttl == 300.0

    def test_custom_config(self):
        cfg = CacheConfig(enabled=False, max_size=50, default_ttl=60.0)
        assert cfg.enabled is False
        assert cfg.max_size == 50
        assert cfg.default_ttl == 60.0


class TestCachingMixinInterface:
    def test_class_importable(self):
        assert callable(CachingMixin)

    def test_has_cache_get(self):
        assert hasattr(CachingMixin, "cache_get")

    def test_has_cache_set(self):
        assert hasattr(CachingMixin, "cache_set")

    def test_has_cache_invalidate(self):
        assert hasattr(CachingMixin, "cache_invalidate")

    def test_has_cached_decorator(self):
        assert hasattr(CachingMixin, "cached")

    def test_instance_cache_get_miss_returns_tuple(self):
        class MyComponent(CachingMixin):
            pass
        comp = MyComponent()
        found, value = comp.cache_get("nonexistent_key_xyz")
        assert found is False
        assert value is None

    def test_instance_cache_set_and_get(self):
        class MyComponent(CachingMixin):
            pass
        comp = MyComponent()
        comp.cache_set("my_key", {"data": 42})
        found, value = comp.cache_get("my_key")
        assert found is True
        assert value == {"data": 42}

    def test_instance_cache_invalidate(self):
        class MyComponent(CachingMixin):
            pass
        comp = MyComponent()
        comp.cache_set("my_key", "value")
        comp.cache_invalidate("my_key")
        found, value = comp.cache_get("my_key")
        assert found is False
