"""
Phase 4 MRO Refactoring Tests - LightweightAgentBase
=====================================================
Validates the LightweightAgentBase for simple agents.

Tests verify:
1. LightweightAgentBase has reduced MRO depth
2. Essential capabilities are available
3. Optional mixins can be added explicitly
4. Initialization works correctly
"""

import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.base_agents.lightweight_agent_base import LightweightAgentBase
from agentic_core.base_agents.caching_mixin import CachingMixin
from agentic_core.base_agents.metrics_mixin import MetricsMixin
from agentic_core.base_agents.context_management_mixin import ContextManagementMixin
from agentic_core.base_agents.cost_guardrail_mixin import CostGuardrailMixin
from agentic_core.base_agents.tracing_mixin import TracingMixin

pytestmark = pytest.mark.guardian


class TestLightweightAgentBaseMRO:
    """Test LightweightAgentBase MRO characteristics."""

    def test_mro_depth_is_reduced(self):
        """LightweightAgentBase should have reduced MRO depth."""

        class TestAgent(LightweightAgentBase):
            pass

        mro = TestAgent.__mro__
        # Should be significantly less than 20+ for full SovereignBaseAgent
        assert len(mro) < 15, f"MRO depth {len(mro)} should be < 15"

    def test_has_essential_mixins_in_mro(self):
        """LightweightAgentBase should have essential mixins in MRO."""

        class TestAgent(LightweightAgentBase):
            pass

        mro = TestAgent.__mro__

        # Essential mixins should be present
        assert CostGuardrailMixin in mro
        assert ContextManagementMixin in mro
        assert TracingMixin in mro
        assert CachingMixin in mro
        assert MetricsMixin in mro


class TestLightweightAgentBaseCapabilities:
    """Test LightweightAgentBase capabilities."""

    def test_has_caching_methods(self):
        """LightweightAgentBase should have caching methods."""

        class TestAgent(LightweightAgentBase):
            pass

        agent = TestAgent()
        assert hasattr(agent, "cache_get")
        assert hasattr(agent, "cache_set")
        assert hasattr(agent, "cache_clear")

    def test_has_metrics_methods(self):
        """LightweightAgentBase should have metrics methods."""

        class TestAgent(LightweightAgentBase):
            pass

        agent = TestAgent()
        assert hasattr(agent, "record_timing")
        assert hasattr(agent, "get_metrics")
        assert hasattr(agent, "reset_metrics")

    def test_caching_works(self):
        """Caching should work on LightweightAgentBase."""

        class TestAgent(LightweightAgentBase):
            pass

        agent = TestAgent()
        agent.cache_set("key1", "value1")
        hit, value = agent.cache_get("key1")
        assert hit is True
        assert value == "value1"

    def test_metrics_work(self):
        """Metrics should work on LightweightAgentBase."""

        class TestAgent(LightweightAgentBase):
            pass

        agent = TestAgent()
        agent.record_timing("test_op", 100.0)
        metrics = agent.get_metrics("test_op")
        assert metrics["call_count"] == 1


class TestLightweightAgentBaseInitialization:
    """Test LightweightAgentBase initialization."""

    def test_post_init_sets_flag(self):
        """__post_init__ should set _lightweight_initialized flag."""

        class TestAgent(LightweightAgentBase):
            def __post_init__(self):
                super().__post_init__()

        agent = TestAgent()
        assert agent._lightweight_initialized is True

    def test_verify_state_passes(self):
        """verify_lightweight_state should pass for properly initialized agent."""

        class TestAgent(LightweightAgentBase):
            def __post_init__(self):
                super().__post_init__()

        agent = TestAgent()
        assert agent.verify_lightweight_state() is True

    def test_get_status_returns_info(self):
        """get_lightweight_status should return status info."""

        class TestAgent(LightweightAgentBase):
            def __post_init__(self):
                super().__post_init__()

        agent = TestAgent()
        status = agent.get_lightweight_status()

        assert status["lightweight_initialized"] is True
        assert "mro_depth" in status
        assert "capabilities" in status
        assert "caching" in status["capabilities"]
        assert "metrics" in status["capabilities"]


class TestLightweightAgentBaseExtensibility:
    """Test that LightweightAgentBase can be extended with additional mixins."""

    def test_can_add_batching_mixin(self):
        """Should be able to add BatchingMixin for batch operations."""
        from agentic_core.base_agents.batching_mixin import BatchingMixin

        class ExtendedAgent(BatchingMixin, LightweightAgentBase):
            def __post_init__(self):
                super().__post_init__()

        agent = ExtendedAgent()
        assert hasattr(agent, "batch_add")
        assert hasattr(agent, "batch_flush")

    def test_can_add_healer_mixin(self):
        """Should be able to add HealerMixin for healing capabilities."""
        # Note: HealerMixin may have import issues in test environment
        # so we just verify it's possible to inherit
        try:
            from agentic_core.base_agents.healer_mixin import HealerMixin

            class HealingAgent(HealerMixin, LightweightAgentBase):
                pass

            # Just verify the class definition works
            assert HealerMixin in HealingAgent.__mro__
        except ImportError:
            pytest.skip("HealerMixin not available in test environment")


class TestPhase4FileStructure:
    """Test that Phase 4 files are properly structured."""

    def test_lightweight_agent_base_file_exists(self):
        """LightweightAgentBase file should exist."""
        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "lightweight_agent_base.py"
        assert path.exists()

    def test_file_is_valid_python(self):
        """LightweightAgentBase file should be valid Python."""
        import ast

        path = PROJECT_ROOT / "agentic_core" / "base_agents" / "lightweight_agent_base.py"
        content = path.read_text(encoding="utf-8")
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in LightweightAgentBase: {e}")


class TestMROComparison:
    """Compare MRO depth between lightweight and full agents."""

    def test_lightweight_has_fewer_classes_than_sovereign(self):
        """LightweightAgentBase should have fewer classes in MRO than SovereignBaseAgent."""

        class LightAgent(LightweightAgentBase):
            pass

        lightweight_mro_depth = len(LightAgent.__mro__)

        # Try to get SovereignBaseAgent MRO for comparison
        try:
            from agentic_core.base_agents.sovereign_base_agent import SovereignBaseAgent

            class FullAgent(SovereignBaseAgent):
                pass

            full_mro_depth = len(FullAgent.__mro__)
            assert lightweight_mro_depth < full_mro_depth, (
                f"Lightweight MRO ({lightweight_mro_depth}) should be < "
                f"SovereignBaseAgent MRO ({full_mro_depth})"
            )
        except ImportError:
            # If SovereignBaseAgent can't be imported, just verify lightweight is reasonable
            assert lightweight_mro_depth < 15
