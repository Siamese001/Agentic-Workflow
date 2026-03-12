"""ADG-driven tests for mixins/performance_mixin.py — fan_in=1."""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.performance_mixin import CacheEntry, PerformanceMixin


class TestCacheEntry:
    def test_creates(self):
        entry = CacheEntry(value={"result": True})
        assert entry.value == {"result": True}

    def test_not_expired_fresh(self):
        entry = CacheEntry(value="test", ttl_seconds=60.0)
        assert entry.is_expired() is False

    def test_expired_old(self):
        entry = CacheEntry(value="test", created_at=time.time() - 400, ttl_seconds=300.0)
        assert entry.is_expired() is True

    def test_hits_default_zero(self):
        entry = CacheEntry(value="v")
        assert entry.hits == 0


class TestPerformanceMixin:
    def test_importable(self):
        assert callable(PerformanceMixin)

    def test_has_cache_get(self):
        assert hasattr(PerformanceMixin, "cache_get")

    def test_has_cache_set(self):
        assert hasattr(PerformanceMixin, "cache_set")
