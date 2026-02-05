"""
Phase 3 MRO Refactoring Tests - PerformanceMixin Decomposition
==============================================================
Validates the split of PerformanceMixin into focused mixins.

Tests verify:
1. CachingMixin provides LRU caching with TTL
2. MetricsMixin provides performance timing
3. BatchingMixin provides batch operations and async pooling
4. Each mixin works independently
"""

import asyncio
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.base_agents.caching_mixin import CachingMixin
from agentic_core.base_agents.metrics_mixin import MetricsMixin
from agentic_core.base_agents.batching_mixin import BatchingMixin

pytestmark = pytest.mark.guardian


class TestCachingMixin:
    """Test CachingMixin functionality."""

    def test_cache_set_and_get(self):
        """Cache should store and retrieve values."""

        class TestAgent(CachingMixin):
            pass

        agent = TestAgent()
        agent.cache_set("key1", "value1")
        hit, value = agent.cache_get("key1")
        assert hit is True
        assert value == "value1"

    def test_cache_miss(self):
        """Cache should return miss for non-existent keys."""

        class TestAgent(CachingMixin):
            pass

        agent = TestAgent()
        hit, value = agent.cache_get("nonexistent")
        assert hit is False
        assert value is None

    def test_cache_invalidate(self):
        """Cache invalidation should remove entries."""

        class TestAgent(CachingMixin):
            pass

        agent = TestAgent()
        agent.cache_set("key1", "value1")
        assert agent.cache_invalidate("key1") is True
        hit, _ = agent.cache_get("key1")
        assert hit is False

    def test_cache_clear(self):
        """Cache clear should remove all entries."""

        class TestAgent(CachingMixin):
            pass

        agent = TestAgent()
        agent.cache_set("key1", "value1")
        agent.cache_set("key2", "value2")
        count = agent.cache_clear()
        assert count == 2
        assert agent.cache_stats()["size"] == 0

    def test_cache_lru_eviction(self):
        """Cache should evict LRU entries when full."""

        class TestAgent(CachingMixin):
            pass

        agent = TestAgent()
        agent.configure_cache(max_size=2)
        agent.cache_set("key1", "value1")
        agent.cache_set("key2", "value2")
        agent.cache_set("key3", "value3")  # Should evict key1

        hit1, _ = agent.cache_get("key1")
        hit2, _ = agent.cache_get("key2")
        hit3, _ = agent.cache_get("key3")

        assert hit1 is False  # Evicted
        assert hit2 is True
        assert hit3 is True

    def test_cached_decorator(self):
        """@cached decorator should cache method results."""

        class TestAgent(CachingMixin):
            def __init__(self):
                super().__init__()
                self.call_count = 0

            @CachingMixin.cached(ttl=60)
            def expensive_method(self, key: str) -> str:
                self.call_count += 1
                return f"result_{key}"

        agent = TestAgent()

        # First call - should execute
        result1 = agent.expensive_method("test")
        assert result1 == "result_test"
        assert agent.call_count == 1

        # Second call - should use cache
        result2 = agent.expensive_method("test")
        assert result2 == "result_test"
        assert agent.call_count == 1  # Not incremented


class TestMetricsMixin:
    """Test MetricsMixin functionality."""

    def test_record_timing(self):
        """Should record timing metrics."""

        class TestAgent(MetricsMixin):
            pass

        agent = TestAgent()
        agent.record_timing("test_op", 100.0)
        agent.record_timing("test_op", 200.0)

        metrics = agent.get_metrics("test_op")
        assert metrics["call_count"] == 2
        assert metrics["total_time_ms"] == 300.0
        assert metrics["avg_time_ms"] == 150.0

    def test_record_error(self):
        """Should track errors."""

        class TestAgent(MetricsMixin):
            pass

        agent = TestAgent()
        agent.record_timing("test_op", 100.0, error=True)
        metrics = agent.get_metrics("test_op")
        assert metrics["errors"] == 1

    def test_timed_decorator_sync(self):
        """@timed decorator should track sync method timing."""

        class TestAgent(MetricsMixin):
            @MetricsMixin.timed
            def slow_method(self) -> str:
                return "done"

        agent = TestAgent()
        result = agent.slow_method()
        assert result == "done"

        metrics = agent.get_metrics("slow_method")
        assert metrics["call_count"] == 1
        assert metrics["total_time_ms"] >= 0

    @pytest.mark.asyncio
    async def test_timed_decorator_async(self):
        """@timed decorator should track async method timing."""

        class TestAgent(MetricsMixin):
            @MetricsMixin.timed
            async def async_method(self) -> str:
                await asyncio.sleep(0.01)
                return "done"

        agent = TestAgent()
        result = await agent.async_method()
        assert result == "done"

        metrics = agent.get_metrics("async_method")
        assert metrics["call_count"] == 1
        assert metrics["total_time_ms"] >= 10  # At least 10ms

    def test_reset_metrics(self):
        """Should reset all metrics."""

        class TestAgent(MetricsMixin):
            pass

        agent = TestAgent()
        agent.record_timing("op1", 100.0)
        agent.record_timing("op2", 200.0)
        agent.reset_metrics()

        assert agent.get_metrics() == {}


class TestBatchingMixin:
    """Test BatchingMixin functionality."""

    def test_batch_add_and_flush(self):
        """Should add items to batch and flush."""

        class TestAgent(BatchingMixin):
            pass

        agent = TestAgent()
        agent.batch_add("queue1", "item1")
        agent.batch_add("queue1", "item2")

        assert agent.batch_size("queue1") == 2

        items = agent.batch_flush("queue1")
        assert items == ["item1", "item2"]
        assert agent.batch_size("queue1") == 0

    def test_should_flush_batch(self):
        """Should detect when batch is full."""

        class TestAgent(BatchingMixin):
            pass

        agent = TestAgent()
        agent.configure_batching(batch_size=2)

        agent.batch_add("queue1", "item1")
        assert agent.should_flush_batch("queue1") is False

        agent.batch_add("queue1", "item2")
        assert agent.should_flush_batch("queue1") is True

    def test_batch_queue_limit(self):
        """Should enforce queue count limit."""

        class TestAgent(BatchingMixin):
            pass

        agent = TestAgent()
        agent.configure_batching(max_batch_queues=2)

        agent.batch_add("queue1", "item1")
        agent.batch_add("queue2", "item2")

        with pytest.raises(ValueError, match="Maximum batch queues"):
            agent.batch_add("queue3", "item3")

    def test_lazy_initialization(self):
        """Should lazily initialize resources."""

        class TestAgent(BatchingMixin):
            pass

        agent = TestAgent()
        init_count = [0]

        def create_resource():
            init_count[0] += 1
            return {"resource": True}

        agent.register_lazy("my_resource", create_resource)

        # Not initialized yet
        assert agent.is_lazy_initialized("my_resource") is False
        assert init_count[0] == 0

        # First access - initializes
        resource = agent.get_lazy("my_resource")
        assert resource == {"resource": True}
        assert init_count[0] == 1

        # Second access - uses cached
        resource = agent.get_lazy("my_resource")
        assert init_count[0] == 1  # Not called again

    @pytest.mark.asyncio
    async def test_run_pooled(self):
        """Should limit concurrent async operations."""

        class TestAgent(BatchingMixin):
            pass

        agent = TestAgent()
        agent.configure_batching(async_pool_size=2)

        results = []

        async def task(n):
            await asyncio.sleep(0.01)
            results.append(n)
            return n

        # Run 4 tasks with pool size 2
        coros = [agent.run_pooled(task(i)) for i in range(4)]
        await asyncio.gather(*coros)

        assert sorted(results) == [0, 1, 2, 3]


class TestMixinIndependence:
    """Test that mixins work independently."""

    def test_caching_mixin_standalone(self):
        """CachingMixin should work without other mixins."""

        class CacheOnlyAgent(CachingMixin):
            pass

        agent = CacheOnlyAgent()
        agent.cache_set("key", "value")
        hit, value = agent.cache_get("key")
        assert hit is True

    def test_metrics_mixin_standalone(self):
        """MetricsMixin should work without other mixins."""

        class MetricsOnlyAgent(MetricsMixin):
            pass

        agent = MetricsOnlyAgent()
        agent.record_timing("op", 100.0)
        metrics = agent.get_metrics("op")
        assert metrics["call_count"] == 1

    def test_batching_mixin_standalone(self):
        """BatchingMixin should work without other mixins."""

        class BatchOnlyAgent(BatchingMixin):
            pass

        agent = BatchOnlyAgent()
        agent.batch_add("queue", "item")
        items = agent.batch_flush("queue")
        assert items == ["item"]

    def test_all_mixins_combined(self):
        """All mixins should work together."""

        class FullAgent(CachingMixin, MetricsMixin, BatchingMixin):
            pass

        agent = FullAgent()

        # Test caching
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True

        # Test metrics
        agent.record_timing("op", 100.0)
        assert agent.get_metrics("op")["call_count"] == 1

        # Test batching
        agent.batch_add("queue", "item")
        assert agent.batch_flush("queue") == ["item"]


class TestPhase3FileStructure:
    """Test that Phase 3 files are properly structured."""

    def test_caching_mixin_file_exists(self):
        """CachingMixin file should exist."""
        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "caching_mixin.py"
        assert path.exists()

    def test_metrics_mixin_file_exists(self):
        """MetricsMixin file should exist."""
        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "metrics_mixin.py"
        assert path.exists()

    def test_batching_mixin_file_exists(self):
        """BatchingMixin file should exist."""
        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "batching_mixin.py"
        assert path.exists()

    def test_original_performance_mixin_still_exists(self):
        """Original PerformanceMixin should still exist for backward compatibility."""
        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "performance_mixin.py"
        assert path.exists()
