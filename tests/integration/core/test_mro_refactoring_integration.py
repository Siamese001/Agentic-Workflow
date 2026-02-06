"""
MRO Refactoring Integration Tests
=================================
Integration tests verifying cross-phase functionality.

Tests verify:
1. Phase components integrate correctly
2. No circular dependencies
3. Import chains work
4. Feature combinations function together
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

pytestmark = [pytest.mark.integration, pytest.mark.guardian]


class TestCrossPhaseImports:
    """Test that all phase components can be imported together."""

    def test_phase2_gateway_factory_imports(self):
        """Phase 2 GatewayFactory should import cleanly."""
        from agentic_core.L2_execution.gateway_factory import (
            GatewayBundle,
            GatewayFactory,
        )

        assert GatewayFactory is not None
        assert GatewayBundle is not None

    def test_phase3_split_mixins_import(self):
        """Phase 3 split mixins should import cleanly."""
        from agentic_core.mixins.batching_mixin import BatchingMixin
        from agentic_core.mixins.caching_mixin import CachingMixin
        from agentic_core.mixins.metrics_mixin import MetricsMixin

        assert CachingMixin is not None
        assert MetricsMixin is not None
        assert BatchingMixin is not None

    def test_phase4_lightweight_base_imports(self):
        """Phase 4 LightweightAgentBase should import cleanly."""
        from agentic_core.base_agents.LightweightBase import (
            LightweightAgentBase,
        )

        assert LightweightAgentBase is not None

    def test_phase5_trait_system_imports(self):
        """Phase 5 trait system should import cleanly."""
        from agentic_core.base_agents.trait_system import (
            Trait,
            with_traits,
        )

        assert Trait is not None
        assert with_traits is not None

    def test_all_phases_import_together(self):
        """All phase components should import without conflicts."""
        from agentic_core.mixins.caching_mixin import CachingMixin
        from agentic_core.base_agents.LightweightBase import LightweightAgentBase
        from agentic_core.base_agents.trait_system import with_traits
        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        # All imports successful
        assert GatewayFactory is not None
        assert CachingMixin is not None
        assert LightweightAgentBase is not None
        assert with_traits is not None


class TestGatewayFactoryWithMixins:
    """Test GatewayFactory integrates with mixin-based agents."""

    def test_gateway_factory_with_caching_mixin(self):
        """GatewayFactory should work with CachingMixin agents."""
        from agentic_core.mixins.caching_mixin import CachingMixin
        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        class TestAgent(CachingMixin):
            def __init__(self):
                super().__init__()
                self.gateways = GatewayFactory.create_minimal()

        GatewayFactory.reset_all()
        agent = TestAgent()

        # Both work together
        assert agent.gateways.llm is not None
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True

    def test_gateway_factory_with_lightweight_base(self):
        """GatewayFactory should work with LightweightAgentBase."""
        from dataclasses import dataclass

        from agentic_core.base_agents.LightweightBase import LightweightAgentBase
        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        @dataclass
        class TestAgent(LightweightAgentBase):
            def __post_init__(self):
                super().__post_init__()
                self.gateways = GatewayFactory.create_all()

        GatewayFactory.reset_all()
        agent = TestAgent()

        # Both work together
        assert agent.gateways.llm is not None
        assert agent.gateways.validator is not None
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True


class TestTraitSystemWithGatewayFactory:
    """Test trait system integrates with GatewayFactory."""

    def test_traits_with_gateway_factory(self):
        """Trait-based agents should work with GatewayFactory."""
        from dataclasses import dataclass

        from agentic_core.base_agents.trait_system import CachingTrait, MetricsTrait, with_traits
        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        @with_traits(CachingTrait, MetricsTrait)
        @dataclass
        class TestAgent:
            gateways: object = None

            def __post_init__(self):
                self.gateways = GatewayFactory.create_minimal()

        GatewayFactory.reset_all()
        agent = TestAgent()

        # All work together
        assert agent.gateways.llm is not None
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True
        agent.record_timing("op", 100.0)
        assert agent.get_metrics("op")["call_count"] == 1


class TestSplitMixinsCombined:
    """Test split mixins work together."""

    def test_all_split_mixins_combined(self):
        """CachingMixin, MetricsMixin, BatchingMixin should combine."""
        from agentic_core.mixins.batching_mixin import BatchingMixin
        from agentic_core.mixins.caching_mixin import CachingMixin
        from agentic_core.mixins.metrics_mixin import MetricsMixin

        class TestAgent(CachingMixin, MetricsMixin, BatchingMixin):
            pass

        agent = TestAgent()

        # All work
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True

        agent.record_timing("op", 100.0)
        assert agent.get_metrics("op")["call_count"] == 1

        agent.batch_add("queue", "item")
        assert agent.batch_flush("queue") == ["item"]

    def test_split_mixins_no_conflicts(self):
        """Split mixins should have no attribute conflicts."""
        from agentic_core.mixins.batching_mixin import BatchingMixin
        from agentic_core.mixins.caching_mixin import CachingMixin
        from agentic_core.mixins.metrics_mixin import MetricsMixin

        class TestAgent(CachingMixin, MetricsMixin, BatchingMixin):
            pass

        agent = TestAgent()

        # Each mixin has its own state
        assert hasattr(agent, "_cache_config")
        assert hasattr(agent, "_metrics_config")
        assert hasattr(agent, "_batching_config")


class TestLightweightBaseWithTraits:
    """Test LightweightAgentBase can be enhanced with traits."""

    def test_lightweight_with_batching_trait(self):
        """LightweightAgentBase can be extended with BatchingTrait."""
        from dataclasses import dataclass

        from agentic_core.base_agents.LightweightBase import LightweightAgentBase
        from agentic_core.base_agents.trait_system import BatchingTrait, with_traits

        # Note: traits are applied to the class before dataclass
        @with_traits(BatchingTrait)
        @dataclass
        class ExtendedAgent(LightweightAgentBase):
            def __post_init__(self):
                super().__post_init__()

        agent = ExtendedAgent()

        # Has LightweightAgentBase capabilities
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True

        # Has BatchingTrait capabilities
        agent.batch_add("queue", "item")
        assert agent.batch_flush("queue") == ["item"]


class TestNoCircularDependencies:
    """Test no circular import dependencies."""

    def test_gateway_factory_imports_independently(self):
        """GatewayFactory should import without mixin dependencies."""
        # Reset imports
        import importlib

        import agentic_core.L2_execution.gateway_factory

        importlib.reload(agentic_core.L2_execution.gateway_factory)

        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        assert GatewayFactory is not None

    def test_trait_system_imports_independently(self):
        """Trait system should import without base agent dependencies."""
        import importlib

        import agentic_core.base_agents.trait_system

        importlib.reload(agentic_core.base_agents.trait_system)

        from agentic_core.base_agents.trait_system import Trait, with_traits

        assert Trait is not None
        assert with_traits is not None


class TestThreadSafety:
    """Test thread safety of new components."""

    def test_gateway_factory_thread_safe(self):
        """GatewayFactory should provide working gateways from multiple threads."""
        import threading

        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        GatewayFactory.reset_all()
        # Pre-initialize to ensure singleton is set
        GatewayFactory.get_llm_gateway()

        gateways = []

        def get_gateway():
            gateways.append(GatewayFactory.get_llm_gateway())

        threads = [threading.Thread(target=get_gateway) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should return working gateways (after pre-init, should be same singleton)
        assert len(gateways) == 10
        assert all(g is not None for g in gateways)

    def test_caching_mixin_thread_safe(self):
        """CachingMixin should be thread-safe."""
        import threading

        from agentic_core.mixins.caching_mixin import CachingMixin

        class TestAgent(CachingMixin):
            pass

        agent = TestAgent()
        results = []

        def cache_operation(i):
            agent.cache_set(f"key{i}", f"value{i}")
            hit, value = agent.cache_get(f"key{i}")
            results.append((hit, value))

        threads = [threading.Thread(target=cache_operation, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All operations should succeed
        assert len(results) == 10
        assert all(hit for hit, _ in results)
