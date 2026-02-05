"""
Phase 4 Test Suite: Architecture Refinement, Performance Tuning

Tests for:
- PerformanceMixin: Caching, lazy initialization, batch operations, metrics
"""

from __future__ import annotations

import asyncio
import pytest
import time

from agentic_core.base_agents.performance_mixin import (
    PerformanceMixin,
    PerformanceMetrics,
    CacheEntry,
)


# =============================================================================
# Test Fixtures
# =============================================================================


class MockPerformanceAgent(PerformanceMixin):
    """Mock agent for testing PerformanceMixin."""

    def __init__(self):
        super().__init__()

    @PerformanceMixin.cached(ttl=60)
    def cached_method(self, key: str) -> str:
        return f"computed_{key}"

    @PerformanceMixin.timed
    def timed_method(self, duration: float = 0.01) -> str:
        time.sleep(duration)
        return "done"

    @PerformanceMixin.timed
    async def async_timed_method(self, duration: float = 0.01) -> str:
        await asyncio.sleep(duration)
        return "async_done"


@pytest.fixture
def perf_agent():
    """Create a fresh performance agent for each test."""
    return MockPerformanceAgent()


# =============================================================================
# PerformanceMixin Initialization Tests
# =============================================================================


class TestPerformanceInitialization:
    """Test PerformanceMixin initialization."""

    def test_initialization_flag_set(self, perf_agent):
        """Verify initialization flag is set."""
        assert perf_agent._performance_initialized is True

    def test_default_config(self, perf_agent):
        """Verify default configuration."""
        config = perf_agent._perf_config
        assert config.cache_enabled is True
        assert config.cache_max_size == 1000
        assert config.cache_default_ttl == 300.0
        assert config.metrics_enabled is True

    def test_empty_state_on_init(self, perf_agent):
        """Verify empty state on initialization."""
        assert len(perf_agent._method_cache) == 0
        assert len(perf_agent._perf_metrics) == 0
        assert len(perf_agent._lazy_registry) == 0


class TestPerformanceConfiguration:
    """Test performance configuration methods."""

    def test_configure_partial(self, perf_agent):
        """Test partial configuration."""
        perf_agent.configure_performance(cache_max_size=500)
        assert perf_agent._perf_config.cache_max_size == 500
        assert perf_agent._perf_config.cache_enabled is True  # Unchanged

    def test_configure_full(self, perf_agent):
        """Test full configuration."""
        perf_agent.configure_performance(
            cache_enabled=False,
            cache_max_size=200,
            cache_default_ttl=60.0,
            metrics_enabled=False,
            lazy_init_enabled=False,
            batch_size=50,
            async_pool_size=5,
        )
        config = perf_agent._perf_config
        assert config.cache_enabled is False
        assert config.cache_max_size == 200
        assert config.cache_default_ttl == 60.0
        assert config.metrics_enabled is False
        assert config.lazy_init_enabled is False
        assert config.batch_size == 50
        assert config.async_pool_size == 5


# =============================================================================
# Caching Tests
# =============================================================================


class TestCaching:
    """Test caching functionality."""

    def test_cache_set_and_get(self, perf_agent):
        """Test basic cache set and get."""
        perf_agent.cache_set("key1", "value1")
        hit, value = perf_agent.cache_get("key1")
        assert hit is True
        assert value == "value1"

    def test_cache_miss(self, perf_agent):
        """Test cache miss."""
        hit, value = perf_agent.cache_get("nonexistent")
        assert hit is False
        assert value is None

    def test_cache_expiration(self, perf_agent):
        """Test cache entry expiration."""
        perf_agent.cache_set("key1", "value1", ttl=0.01)
        time.sleep(0.02)
        hit, value = perf_agent.cache_get("key1")
        assert hit is False

    def test_cache_invalidate(self, perf_agent):
        """Test cache invalidation."""
        perf_agent.cache_set("key1", "value1")
        result = perf_agent.cache_invalidate("key1")
        assert result is True
        hit, _ = perf_agent.cache_get("key1")
        assert hit is False

    def test_cache_invalidate_nonexistent(self, perf_agent):
        """Test invalidating nonexistent key."""
        result = perf_agent.cache_invalidate("nonexistent")
        assert result is False

    def test_cache_clear(self, perf_agent):
        """Test cache clear."""
        perf_agent.cache_set("key1", "value1")
        perf_agent.cache_set("key2", "value2")
        count = perf_agent.cache_clear()
        assert count == 2
        assert len(perf_agent._method_cache) == 0

    def test_cache_lru_eviction(self, perf_agent):
        """Test LRU eviction when cache is full."""
        perf_agent.configure_performance(cache_max_size=3)

        perf_agent.cache_set("key1", "value1")
        perf_agent.cache_set("key2", "value2")
        perf_agent.cache_set("key3", "value3")
        perf_agent.cache_set("key4", "value4")  # Should evict key1

        hit, _ = perf_agent.cache_get("key1")
        assert hit is False
        hit, _ = perf_agent.cache_get("key4")
        assert hit is True

    def test_cache_disabled(self, perf_agent):
        """Test caching when disabled."""
        perf_agent.configure_performance(cache_enabled=False)
        perf_agent.cache_set("key1", "value1")
        hit, _ = perf_agent.cache_get("key1")
        assert hit is False

    def test_cache_stats(self, perf_agent):
        """Test cache statistics."""
        perf_agent.cache_set("key1", "value1")
        perf_agent.cache_get("key1")
        perf_agent.cache_get("key1")

        stats = perf_agent.cache_stats()
        assert stats["size"] == 1
        assert stats["total_hits"] == 2
        assert stats["enabled"] is True


class TestCachedDecorator:
    """Test @cached decorator."""

    def test_cached_decorator_caches_result(self, perf_agent):
        """Test that cached decorator caches results."""
        result1 = perf_agent.cached_method("test")
        result2 = perf_agent.cached_method("test")

        assert result1 == result2
        assert result1 == "computed_test"

    def test_cached_decorator_different_keys(self, perf_agent):
        """Test cached decorator with different keys."""
        result1 = perf_agent.cached_method("key1")
        result2 = perf_agent.cached_method("key2")

        assert result1 == "computed_key1"
        assert result2 == "computed_key2"


# =============================================================================
# Performance Metrics Tests
# =============================================================================


class TestPerformanceMetrics:
    """Test performance metrics functionality."""

    def test_timed_decorator_records_timing(self, perf_agent):
        """Test that timed decorator records timing."""
        perf_agent.timed_method(0.01)

        metrics = perf_agent.get_performance_metrics("timed_method")
        assert metrics["call_count"] == 1
        assert metrics["total_time_ms"] >= 10  # At least 10ms

    def test_timed_decorator_multiple_calls(self, perf_agent):
        """Test timed decorator with multiple calls."""
        for _ in range(3):
            perf_agent.timed_method(0.01)

        metrics = perf_agent.get_performance_metrics("timed_method")
        assert metrics["call_count"] == 3

    @pytest.mark.asyncio
    async def test_async_timed_decorator(self, perf_agent):
        """Test async timed decorator."""
        await perf_agent.async_timed_method(0.01)

        metrics = perf_agent.get_performance_metrics("async_timed_method")
        assert metrics["call_count"] == 1
        assert metrics["total_time_ms"] >= 10

    def test_get_all_metrics(self, perf_agent):
        """Test getting all metrics."""
        perf_agent.timed_method()
        perf_agent.cached_method("test")

        all_metrics = perf_agent.get_performance_metrics()
        assert "timed_method" in all_metrics

    def test_reset_metrics(self, perf_agent):
        """Test resetting metrics."""
        perf_agent.timed_method()
        perf_agent.reset_metrics()

        metrics = perf_agent.get_performance_metrics("timed_method")
        assert metrics == {}

    def test_metrics_disabled(self, perf_agent):
        """Test metrics when disabled."""
        perf_agent.configure_performance(metrics_enabled=False)
        perf_agent.timed_method()

        metrics = perf_agent.get_performance_metrics("timed_method")
        assert metrics == {}


class TestPerformanceMetricsDataclass:
    """Test PerformanceMetrics dataclass."""

    def test_avg_time_calculation(self):
        """Test average time calculation."""
        metrics = PerformanceMetrics(operation_name="test", call_count=4, total_time_ms=100.0)
        assert metrics.avg_time_ms == 25.0

    def test_avg_time_zero_calls(self):
        """Test average time with zero calls."""
        metrics = PerformanceMetrics(operation_name="test")
        assert metrics.avg_time_ms == 0.0

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        metrics = PerformanceMetrics(operation_name="test", cache_hits=3, cache_misses=1)
        assert metrics.cache_hit_rate == 0.75

    def test_to_dict(self):
        """Test to_dict method."""
        metrics = PerformanceMetrics(operation_name="test", call_count=5, total_time_ms=50.0)
        data = metrics.to_dict()
        assert data["operation_name"] == "test"
        assert data["call_count"] == 5
        assert data["avg_time_ms"] == 10.0


# =============================================================================
# Lazy Initialization Tests
# =============================================================================


class TestLazyInitialization:
    """Test lazy initialization functionality."""

    def test_register_and_get_lazy(self, perf_agent):
        """Test registering and getting lazy resource."""
        perf_agent.register_lazy("resource1", lambda: {"data": "initialized"})

        result = perf_agent.get_lazy("resource1")
        assert result == {"data": "initialized"}

    def test_lazy_only_initializes_once(self, perf_agent):
        """Test lazy resource only initializes once."""
        call_count = [0]

        def initializer():
            call_count[0] += 1
            return f"init_{call_count[0]}"

        perf_agent.register_lazy("resource1", initializer)

        result1 = perf_agent.get_lazy("resource1")
        result2 = perf_agent.get_lazy("resource1")

        assert result1 == result2
        assert call_count[0] == 1

    def test_is_lazy_initialized(self, perf_agent):
        """Test checking if lazy resource is initialized."""
        perf_agent.register_lazy("resource1", lambda: "value")

        assert perf_agent.is_lazy_initialized("resource1") is False
        perf_agent.get_lazy("resource1")
        assert perf_agent.is_lazy_initialized("resource1") is True

    def test_get_lazy_unregistered_raises(self, perf_agent):
        """Test getting unregistered lazy resource raises error."""
        with pytest.raises(KeyError, match="not registered"):
            perf_agent.get_lazy("unregistered")

    def test_lazy_disabled(self, perf_agent):
        """Test lazy initialization when disabled."""
        perf_agent.configure_performance(lazy_init_enabled=False)
        call_count = [0]

        def initializer():
            call_count[0] += 1
            return "value"

        perf_agent.register_lazy("resource1", initializer)

        # Should call initializer each time when disabled
        perf_agent.get_lazy("resource1")
        perf_agent.get_lazy("resource1")

        assert call_count[0] == 2


# =============================================================================
# Batch Operations Tests
# =============================================================================


class TestBatchOperations:
    """Test batch operation functionality."""

    def test_batch_add(self, perf_agent):
        """Test adding items to batch queue."""
        size = perf_agent.batch_add("queue1", "item1")
        assert size == 1

        size = perf_agent.batch_add("queue1", "item2")
        assert size == 2

    def test_batch_flush(self, perf_agent):
        """Test flushing batch queue."""
        perf_agent.batch_add("queue1", "item1")
        perf_agent.batch_add("queue1", "item2")

        items = perf_agent.batch_flush("queue1")
        assert items == ["item1", "item2"]
        assert perf_agent.batch_size("queue1") == 0

    def test_batch_flush_empty(self, perf_agent):
        """Test flushing empty queue."""
        items = perf_agent.batch_flush("nonexistent")
        assert items == []

    def test_batch_size(self, perf_agent):
        """Test getting batch queue size."""
        assert perf_agent.batch_size("queue1") == 0

        perf_agent.batch_add("queue1", "item1")
        assert perf_agent.batch_size("queue1") == 1

    def test_should_flush_batch(self, perf_agent):
        """Test should_flush_batch check."""
        perf_agent.configure_performance(batch_size=3)

        perf_agent.batch_add("queue1", "item1")
        assert perf_agent.should_flush_batch("queue1") is False

        perf_agent.batch_add("queue1", "item2")
        perf_agent.batch_add("queue1", "item3")
        assert perf_agent.should_flush_batch("queue1") is True


# =============================================================================
# Async Pooling Tests
# =============================================================================


class TestAsyncPooling:
    """Test async pooling functionality."""

    @pytest.mark.asyncio
    async def test_get_async_semaphore(self, perf_agent):
        """Test getting async semaphore."""
        semaphore = await perf_agent.get_async_semaphore()
        assert isinstance(semaphore, asyncio.Semaphore)

    @pytest.mark.asyncio
    async def test_run_pooled(self, perf_agent):
        """Test running pooled coroutine."""

        async def task():
            await asyncio.sleep(0.01)
            return "result"

        result = await perf_agent.run_pooled(task())
        assert result == "result"

    @pytest.mark.asyncio
    async def test_pool_limits_concurrency(self, perf_agent):
        """Test that pool limits concurrency."""
        perf_agent.configure_performance(async_pool_size=2)

        concurrent_count = [0]
        max_concurrent = [0]

        async def task():
            concurrent_count[0] += 1
            max_concurrent[0] = max(max_concurrent[0], concurrent_count[0])
            await asyncio.sleep(0.05)
            concurrent_count[0] -= 1
            return "done"

        # Run 5 tasks with pool size 2
        tasks = [perf_agent.run_pooled(task()) for _ in range(5)]
        await asyncio.gather(*tasks)

        assert max_concurrent[0] <= 2


# =============================================================================
# Cache Entry Tests
# =============================================================================


class TestCacheEntry:
    """Test CacheEntry dataclass."""

    def test_cache_entry_not_expired(self):
        """Test cache entry is not expired."""
        entry = CacheEntry(value="test", ttl_seconds=60.0)
        assert entry.is_expired() is False

    def test_cache_entry_expired(self):
        """Test cache entry expiration."""
        entry = CacheEntry(value="test", ttl_seconds=0.01)
        time.sleep(0.02)
        assert entry.is_expired() is True


# =============================================================================
# Performance Status Tests
# =============================================================================


class TestPerformanceStatus:
    """Test performance status reporting."""

    def test_get_performance_status(self, perf_agent):
        """Test getting performance status."""
        perf_agent.cache_set("key1", "value1")
        perf_agent.register_lazy("resource1", lambda: "value")
        perf_agent.batch_add("queue1", "item1")

        status = perf_agent.get_performance_status()

        assert "cache" in status
        assert status["cache"]["size"] == 1
        assert status["lazy_registered"] == 1
        assert status["lazy_initialized"] == 0
        assert "queue1" in status["batch_queues"]
        assert status["batch_queues"]["queue1"] == 1


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_thread_safety_cache(self, perf_agent):
        """Test thread safety of cache operations."""
        import threading

        errors = []

        def cache_operations():
            try:
                for i in range(100):
                    perf_agent.cache_set(f"key_{i}", f"value_{i}")
                    perf_agent.cache_get(f"key_{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=cache_operations) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_cache_with_complex_values(self, perf_agent):
        """Test caching complex values."""
        complex_value = {
            "list": [1, 2, 3],
            "nested": {"a": "b"},
            "tuple": (1, 2),
        }
        perf_agent.cache_set("complex", complex_value)
        hit, value = perf_agent.cache_get("complex")

        assert hit is True
        assert value == complex_value

    def test_metrics_min_max_tracking(self, perf_agent):
        """Test min/max time tracking."""
        # First call - slow
        perf_agent._record_timing("test_op", 100.0)
        # Second call - fast
        perf_agent._record_timing("test_op", 10.0)
        # Third call - medium
        perf_agent._record_timing("test_op", 50.0)

        metrics = perf_agent.get_performance_metrics("test_op")
        assert metrics["min_time_ms"] == 10.0
        assert metrics["max_time_ms"] == 100.0
        assert metrics["avg_time_ms"] == pytest.approx(53.33, rel=0.1)
