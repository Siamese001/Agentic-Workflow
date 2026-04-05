"""
tests/unit/agentic_core/L6_observability/evaluation/test_evaluation_cache.py

Unit tests for Wave 3.1: Evaluation Caching
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L6_observability.utils.evaluation.evaluation_cache import (
    EvaluationCache,
    get_eval_cache,
    reset_eval_cache,
)


class TestEvaluationCache:
    """Test suite for EvaluationCache."""

    def test_cache_miss(self):
        """Test cache miss."""
        cache = EvaluationCache()
        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_hit(self):
        """Test cache hit."""
        cache = EvaluationCache()
        cache.put("test_key", {"score": 0.85})
        result = cache.get("test_key")
        assert result == {"score": 0.85}

    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = EvaluationCache()
        cache.put("test_key", {"score": 0.85}, ttl_sec=0.1)
        time.sleep(0.2)
        result = cache.get("test_key")
        assert result is None

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        cache = EvaluationCache()
        cache.put("test_key", {"score": 0.85})
        assert cache.invalidate("test_key") is True
        assert cache.get("test_key") is None

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = EvaluationCache()
        cache.put("key1", {"score": 0.85})
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_generate_key(self):
        """Test cache key generation."""
        key1 = EvaluationCache.generate_key("test", {"a": 1, "b": 2})
        key2 = EvaluationCache.generate_key("test", {"b": 2, "a": 1})
        assert key1 == key2  # Order-independent


class TestGlobalInstance:
    """Test global instance management."""

    def test_singleton_pattern(self):
        """Test cache singleton pattern."""
        reset_eval_cache()
        cache1 = get_eval_cache()
        cache2 = get_eval_cache()
        assert cache1 is cache2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
