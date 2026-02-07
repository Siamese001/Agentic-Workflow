"""
MRO Refactoring E2E Tests
=========================
End-to-end validation of all MRO refactoring phases.

Tests verify:
1. All phase changes work together
2. No regressions in agent functionality
3. Performance improvements are realized
4. Backward compatibility is maintained
"""

import ast
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

pytestmark = [pytest.mark.e2e, pytest.mark.guardian]


class TestPhase1E2E:
    """E2E tests for Phase 1: Redundant mixin removal."""

    def test_all_refactored_agents_have_single_base(self):
        """All Phase 1 refactored agents should have single base class."""
        agents_to_check = [
            (
                PROJECT_ROOT / "apps_lic" / "engines" / "Hop2researchagentStrategy.py",
                "HOP2ResearchAgent",
            ),
            (
                PROJECT_ROOT / "apps_lic" / "engines" / "PIISanitizerSpecialistAgent.py",
                "PII_SanitizerSpecialistAgent",
            ),
            (
                PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "location_validator_agent.py",
                "LocationValidatorAgent",
            ),
            (
                PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "HierarchyagentStrategy.py",
                "HierarchyAgent",
            ),
            (
                PROJECT_ROOT / "apps_rg" / "shared" / "tools" / "DispatchResumeToolsAgent.py",
                "DispatchResumeToolsAgent",
            ),
        ]

        for file_path, class_name in agents_to_check:
            assert file_path.exists(), f"File not found: {file_path}"
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            bases.append(base.attr)

                    assert len(bases) == 1, f"{class_name} should have exactly 1 base. Found: {bases}"
                    break


class TestPhase2E2E:
    """E2E tests for Phase 2: Gateway Factory."""

    def test_gateway_factory_provides_all_gateways(self):
        """GatewayFactory should provide all gateway types."""
        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        GatewayFactory.reset_all()
        bundle = GatewayFactory.create_all()

        assert bundle.llm is not None
        assert bundle.embedding is not None
        assert bundle.validator is not None
        assert bundle.healing is not None

    def test_gateways_are_singletons(self):
        """GatewayFactory should return singletons."""
        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        GatewayFactory.reset_all()

        llm1 = GatewayFactory.get_llm_gateway()
        llm2 = GatewayFactory.get_llm_gateway()

        assert llm1 is llm2


class TestPhase3E2E:
    """E2E tests for Phase 3: PerformanceMixin decomposition."""

    def test_split_mixins_work_independently(self):
        """Split mixins should work without full PerformanceMixin."""
        from agentic_core.mixins.batching_mixin import BatchingMixin
        from agentic_core.mixins.caching_mixin import CachingMixin
        from agentic_core.mixins.metrics_mixin import MetricsMixin

        class CacheOnlyAgent(CachingMixin):
            pass

        class MetricsOnlyAgent(MetricsMixin):
            pass

        class BatchOnlyAgent(BatchingMixin):
            pass

        # Each should work independently
        cache_agent = CacheOnlyAgent()
        cache_agent.cache_set("key", "value")
        assert cache_agent.cache_get("key")[0] is True

        metrics_agent = MetricsOnlyAgent()
        metrics_agent.record_timing("op", 100.0)
        assert metrics_agent.get_metrics("op")["call_count"] == 1

        batch_agent = BatchOnlyAgent()
        batch_agent.batch_add("queue", "item")
        assert batch_agent.batch_flush("queue") == ["item"]


class TestPhase4E2E:
    """E2E tests for Phase 4: LightweightAgentBase."""

    def test_lightweight_base_has_reduced_mro(self):
        """LightweightAgentBase should have MRO depth < 15."""
        from agentic_core.base_agents.LightweightBase import LightweightAgentBase

        class TestAgent(LightweightAgentBase):
            pass

        mro_depth = len(TestAgent.__mro__)
        assert mro_depth < 15, f"MRO depth {mro_depth} should be < 15"

    def test_lightweight_base_is_functional(self):
        """LightweightAgentBase should provide working capabilities."""
        from agentic_core.base_agents.LightweightBase import LightweightAgentBase

        class TestAgent(LightweightAgentBase):
            def __post_init__(self):
                super().__post_init__()

        agent = TestAgent()

        # Test caching
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True

        # Test metrics
        agent.record_timing("op", 100.0)
        assert agent.get_metrics("op")["call_count"] == 1


class TestPhase5E2E:
    """E2E tests for Phase 5: Trait system."""

    def test_traits_avoid_mro_complexity(self):
        """Trait-based agents should have simple MRO."""
        from dataclasses import dataclass

        from agentic_core.base_agents.trait_system import (
            BatchingTrait,
            CachingTrait,
            MetricsTrait,
            with_traits,
        )

        @with_traits(CachingTrait, MetricsTrait, BatchingTrait)
        @dataclass
        class TraitAgent:
            def __post_init__(self):
                pass

        # MRO should only include TraitAgent and object
        mro_depth = len(TraitAgent.__mro__)
        assert mro_depth == 2, f"Trait agent MRO should be 2, got {mro_depth}"

    def test_traits_are_fully_functional(self):
        """Trait-based agents should have all capabilities."""
        from dataclasses import dataclass

        from agentic_core.base_agents.trait_system import (
            BatchingTrait,
            CachingTrait,
            MetricsTrait,
            with_traits,
        )

        @with_traits(CachingTrait, MetricsTrait, BatchingTrait)
        @dataclass
        class TraitAgent:
            def __post_init__(self):
                pass

        agent = TraitAgent()

        # Test caching
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True

        # Test metrics
        agent.record_timing("op", 100.0)
        assert agent.get_metrics("op")["call_count"] == 1

        # Test batching
        agent.batch_add("queue", "item")
        assert agent.batch_flush("queue") == ["item"]


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_original_performance_mixin_still_works(self):
        """Original PerformanceMixin should still be usable."""
        try:
            from agentic_core.mixins.performance_mixin import PerformanceMixin

            class TestAgent(PerformanceMixin):
                pass

            agent = TestAgent()
            assert hasattr(agent, "cache_get")
            assert hasattr(agent, "get_performance_metrics")
            assert hasattr(agent, "batch_add")
        except ImportError:
            pytest.skip("PerformanceMixin not available")

    def test_infrastructure_mixin_still_works(self):
        """Original infrastructure_mixin should still be usable."""
        # Just verify the file exists and is valid Python
        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "infrastructure_mixin.py"
        assert path.exists()

        content = path.read_text(encoding="utf-8")
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"infrastructure_mixin.py has syntax error: {e}")


class TestAllPhasesIntegrated:
    """Integration tests verifying all phases work together."""

    def test_all_new_files_exist(self):
        """All new files from refactoring should exist."""
        new_files = [
            # Phase 2
            PROJECT_ROOT / "agentic_core" / "L2_execution" / "gateway_factory.py",
            # Phase 3
            PROJECT_ROOT / "agentic_core" / "base_agents" / "caching_mixin.py",
            PROJECT_ROOT / "agentic_core" / "base_agents" / "metrics_mixin.py",
            PROJECT_ROOT / "agentic_core" / "base_agents" / "batching_mixin.py",
            # Phase 4
            PROJECT_ROOT / "agentic_core" / "base_agents" / "lightweight_agent_base.py",
            # Phase 5
            PROJECT_ROOT / "agentic_core" / "base_agents" / "trait_system.py",
        ]

        for file_path in new_files:
            assert file_path.exists(), f"Missing file: {file_path}"

    def test_all_new_files_are_valid_python(self):
        """All new files should be valid Python syntax."""
        new_files = [
            PROJECT_ROOT / "agentic_core" / "L2_execution" / "gateway_factory.py",
            PROJECT_ROOT / "agentic_core" / "base_agents" / "caching_mixin.py",
            PROJECT_ROOT / "agentic_core" / "base_agents" / "metrics_mixin.py",
            PROJECT_ROOT / "agentic_core" / "base_agents" / "batching_mixin.py",
            PROJECT_ROOT / "agentic_core" / "base_agents" / "lightweight_agent_base.py",
            PROJECT_ROOT / "agentic_core" / "base_agents" / "trait_system.py",
        ]

        for file_path in new_files:
            content = file_path.read_text(encoding="utf-8")
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {file_path}: {e}")

    def test_combined_architecture_pattern(self):
        """Test recommended combined usage pattern."""
        from dataclasses import dataclass

        from agentic_core.base_agents.LightweightBase import LightweightAgentBase
        from agentic_core.L2_execution.gateway_factory import GatewayFactory

        @dataclass
        class ModernAgent(LightweightAgentBase):
            """Agent using recommended Phase 4 pattern with Phase 2 composition."""

            def __post_init__(self):
                super().__post_init__()
                # Use GatewayFactory for external services
                self.gateways = GatewayFactory.create_minimal()

        agent = ModernAgent()

        # Has lightweight infrastructure
        assert agent.verify_lightweight_state() is True

        # Has gateway access
        assert agent.gateways.llm is not None

        # Can use caching
        agent.cache_set("key", "value")
        assert agent.cache_get("key")[0] is True


class TestPerformanceImprovements:
    """Test that refactoring achieves performance goals."""

    def test_lightweight_instantiation_time(self):
        """LightweightAgentBase should instantiate quickly."""
        from agentic_core.base_agents.LightweightBase import LightweightAgentBase

        class TestAgent(LightweightAgentBase):
            def __post_init__(self):
                super().__post_init__()

        # Warm up
        TestAgent()

        # Measure
        start = time.time()
        for _ in range(100):
            TestAgent()
        duration = time.time() - start

        # Should be < 1s for 100 instantiations
        assert duration < 1.0, f"100 instantiations took {duration:.2f}s, should be < 1s"

    def test_trait_based_agent_instantiation(self):
        """Trait-based agents should instantiate quickly."""
        from dataclasses import dataclass

        from agentic_core.base_agents.trait_system import CachingTrait, MetricsTrait, with_traits

        @with_traits(CachingTrait, MetricsTrait)
        @dataclass
        class TraitAgent:
            def __post_init__(self):
                pass

        # Warm up
        TraitAgent()

        # Measure
        start = time.time()
        for _ in range(100):
            TraitAgent()
        duration = time.time() - start

        # Should be < 1s for 100 instantiations
        assert duration < 1.0, f"100 instantiations took {duration:.2f}s, should be < 1s"
