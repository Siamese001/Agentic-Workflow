"""
Phase 5 MRO Refactoring Tests - Trait System
=============================================
Validates the trait-based composition system.

Tests verify:
1. Traits can be applied via decorator
2. Applied traits inject correct methods
3. Multiple traits can be combined
4. Trait introspection works correctly
"""

import asyncio
import pytest
from pathlib import Path
import sys
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.base_agents.trait_system import (
    CachingTrait,
    MetricsTrait,
    BatchingTrait,
    with_traits,
    get_applied_traits,
    has_trait,
)

pytestmark = pytest.mark.guardian


class TestCachingTrait:
    """Test CachingTrait functionality."""

    def test_applies_caching_methods(self):
        """CachingTrait should add caching methods to class."""

        @with_traits(CachingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        assert hasattr(agent, "cache_get")
        assert hasattr(agent, "cache_set")
        assert hasattr(agent, "cache_clear")

    def test_caching_works(self):
        """CachingTrait should provide working cache."""

        @with_traits(CachingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        agent.cache_set("key1", "value1")
        hit, value = agent.cache_get("key1")
        assert hit is True
        assert value == "value1"

    def test_cache_miss(self):
        """CachingTrait should return miss for non-existent keys."""

        @with_traits(CachingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        hit, value = agent.cache_get("nonexistent")
        assert hit is False

    def test_cache_clear(self):
        """CachingTrait should support cache clearing."""

        @with_traits(CachingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        agent.cache_set("key1", "value1")
        agent.cache_set("key2", "value2")
        count = agent.cache_clear()
        assert count == 2


class TestMetricsTrait:
    """Test MetricsTrait functionality."""

    def test_applies_metrics_methods(self):
        """MetricsTrait should add metrics methods to class."""

        @with_traits(MetricsTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        assert hasattr(agent, "record_timing")
        assert hasattr(agent, "get_metrics")
        assert hasattr(agent, "reset_metrics")

    def test_metrics_recording(self):
        """MetricsTrait should record timing metrics."""

        @with_traits(MetricsTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        agent.record_timing("test_op", 100.0)
        agent.record_timing("test_op", 200.0)

        metrics = agent.get_metrics("test_op")
        assert metrics["call_count"] == 2
        assert metrics["total_time_ms"] == 300.0

    def test_metrics_reset(self):
        """MetricsTrait should support metrics reset."""

        @with_traits(MetricsTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        agent.record_timing("test_op", 100.0)
        agent.reset_metrics()
        assert agent.get_metrics() == {}


class TestBatchingTrait:
    """Test BatchingTrait functionality."""

    def test_applies_batching_methods(self):
        """BatchingTrait should add batching methods to class."""

        @with_traits(BatchingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        assert hasattr(agent, "batch_add")
        assert hasattr(agent, "batch_flush")
        assert hasattr(agent, "should_flush_batch")
        assert hasattr(agent, "run_pooled")

    def test_batch_operations(self):
        """BatchingTrait should provide working batch operations."""

        @with_traits(BatchingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        agent.batch_add("queue1", "item1")
        agent.batch_add("queue1", "item2")

        items = agent.batch_flush("queue1")
        assert items == ["item1", "item2"]

    @pytest.mark.asyncio
    async def test_run_pooled(self):
        """BatchingTrait should provide async pooling."""

        @with_traits(BatchingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()

        async def task():
            await asyncio.sleep(0.01)
            return "done"

        result = await agent.run_pooled(task())
        assert result == "done"


class TestMultipleTraits:
    """Test combining multiple traits."""

    def test_multiple_traits_combined(self):
        """Multiple traits should work together."""

        @with_traits(CachingTrait, MetricsTrait, BatchingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()

        # All methods should be available
        assert hasattr(agent, "cache_get")
        assert hasattr(agent, "record_timing")
        assert hasattr(agent, "batch_add")

    def test_all_traits_functional(self):
        """All applied traits should be functional."""

        @with_traits(CachingTrait, MetricsTrait, BatchingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()

        # Test caching
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True

        # Test metrics
        agent.record_timing("op", 100.0)
        assert agent.get_metrics("op")["call_count"] == 1

        # Test batching
        agent.batch_add("queue", "item")
        assert agent.batch_flush("queue") == ["item"]


class TestTraitIntrospection:
    """Test trait introspection utilities."""

    def test_get_applied_traits(self):
        """get_applied_traits should return list of applied traits."""

        @with_traits(CachingTrait, MetricsTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()
        traits = get_applied_traits(agent)

        assert "CachingTrait" in traits
        assert "MetricsTrait" in traits

    def test_has_trait(self):
        """has_trait should detect applied traits."""

        @with_traits(CachingTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        agent = TestAgent()

        assert has_trait(agent, "CachingTrait") is True
        assert has_trait(agent, "MetricsTrait") is False

    def test_introspection_on_class(self):
        """Introspection should work on class, not just instance."""

        @with_traits(CachingTrait, MetricsTrait)
        @dataclass
        class TestAgent:
            def __post_init__(self):
                pass

        traits = get_applied_traits(TestAgent)
        assert "CachingTrait" in traits
        assert "MetricsTrait" in traits


class TestPhase5FileStructure:
    """Test that Phase 5 files are properly structured."""

    def test_trait_system_file_exists(self):
        """trait_system.py file should exist."""
        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "trait_system.py"
        assert path.exists()

    def test_file_is_valid_python(self):
        """trait_system.py file should be valid Python."""
        import ast

        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "trait_system.py"
        content = path.read_text(encoding="utf-8")
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in trait_system.py: {e}")
