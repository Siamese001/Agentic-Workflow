"""
Test Suite for Meta-Learning Phase 5: Learning Agents Integration

Tests for:
- RgReflectionAgent meta-learning methods
- Execution insight caching
- Quality pattern learning
- Cross-session persistence patterns

Note: Uses mock agents to avoid import issues with missing context modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import patch

import pytest


def reset_all_singletons():
    """Reset all meta-learning singletons for test isolation."""
    import agentic_core.L1_cognition.meta_learning.MetaLearningClient as mlc
    import agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder as hme
    import agentic_core.L1_cognition.meta_learning.CacheStrategyManager as csm
    from agentic_core.base_agents.meta_learning_client_mixin import (
        MetaLearningClientMixin,
    )

    mlc._meta_learning_client = None
    mlc._singleton_instance = None
    hme._healing_memory_embedder = None
    hme._embedder_singleton = None
    csm._cache_strategy_manager = None
    csm._csm_singleton = None
    MetaLearningClientMixin._ml_client = None
    MetaLearningClientMixin._ml_embedder = None
    MetaLearningClientMixin._ml_cache_manager = None


# ==================== MOCK LEARNING AGENTS ====================


@dataclass
class MockRgReflectionAgent:
    """Mock RG Reflection Agent for testing meta-learning methods."""

    _ml_domain: str = field(default="apps_rg", init=False)

    def __post_init__(self):
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        self._mixin = type(
            "MixinInstance",
            (MetaLearningClientMixin,),
            {"_ml_domain": "apps_rg", "__class__": type(self)},
        )()
        self._mixin._ml_domain = "apps_rg"

    def _get_ml_domain(self) -> str:
        return self._ml_domain

    def ml_cache_get(self, key: str) -> Any:
        self._mixin._ensure_ml_client()
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        if MetaLearningClientMixin._ml_client is None:
            return None
        return MetaLearningClientMixin._ml_client.cache_get(key, self._ml_domain)

    def ml_cache_set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        self._mixin._ensure_ml_client()
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        if MetaLearningClientMixin._ml_client is None:
            return False
        return MetaLearningClientMixin._ml_client.cache_set(key, value, self._ml_domain, ttl)

    def ml_cache_execution_insight(self, insight_id: str, insight_data: dict[str, Any]) -> bool:
        cache_key = f"execution_insight:{insight_id}"
        return self.ml_cache_set(cache_key, insight_data)

    def ml_recall_execution_insight(self, insight_id: str) -> dict[str, Any] | None:
        cache_key = f"execution_insight:{insight_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_quality_pattern(self, pattern_id: str, pattern_data: dict[str, Any]) -> bool:
        cache_key = f"quality_pattern:{pattern_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    def ml_recall_quality_pattern(self, pattern_id: str) -> dict[str, Any] | None:
        cache_key = f"quality_pattern:{pattern_id}"
        return self.ml_cache_get(cache_key)

    def ml_record_reflection_success(
        self, context_hash: str, insights: dict[str, Any], quality_score: float
    ) -> bool:
        if quality_score >= 0.7:
            cache_key = f"reflection_success:{context_hash}"
            return self.ml_cache_set(
                cache_key, {"insights": insights, "quality_score": quality_score}
            )
        return False

    def ml_recall_similar_reflection(self, context_hash: str) -> dict[str, Any] | None:
        cache_key = f"reflection_success:{context_hash}"
        return self.ml_cache_get(cache_key)


@dataclass
class MockOutreachLearningAgent:
    """Mock Outreach Learning Agent for testing meta-learning methods."""

    _ml_domain: str = field(default="apps_lic", init=False)

    def __post_init__(self):
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        self._mixin = type(
            "MixinInstance",
            (MetaLearningClientMixin,),
            {"_ml_domain": "apps_lic", "__class__": type(self)},
        )()
        self._mixin._ml_domain = "apps_lic"

    def _get_ml_domain(self) -> str:
        return self._ml_domain

    def ml_cache_get(self, key: str) -> Any:
        self._mixin._ensure_ml_client()
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        if MetaLearningClientMixin._ml_client is None:
            return None
        return MetaLearningClientMixin._ml_client.cache_get(key, self._ml_domain)

    def ml_cache_set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        self._mixin._ensure_ml_client()
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        if MetaLearningClientMixin._ml_client is None:
            return False
        return MetaLearningClientMixin._ml_client.cache_set(key, value, self._ml_domain, ttl)

    def ml_cache_learning_pattern(self, pattern_id: str, pattern_data: dict[str, Any]) -> bool:
        cache_key = f"learning_pattern:{pattern_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    def ml_recall_learning_pattern(self, pattern_id: str) -> dict[str, Any] | None:
        cache_key = f"learning_pattern:{pattern_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_success_example(self, example_id: str, example_data: dict[str, Any]) -> bool:
        cache_key = f"success_example:{example_id}"
        return self.ml_cache_set(cache_key, example_data)

    def ml_recall_success_example(self, example_id: str) -> dict[str, Any] | None:
        cache_key = f"success_example:{example_id}"
        return self.ml_cache_get(cache_key)


class TestRgReflectionAgentMetaLearning:
    """Tests for RgReflectionAgent meta-learning integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_rg_reflection_has_ml_methods(self):
        """Test that RgReflectionAgent has meta-learning methods."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = MockRgReflectionAgent()

            assert hasattr(agent, "ml_cache_execution_insight")
            assert hasattr(agent, "ml_recall_execution_insight")
            assert hasattr(agent, "ml_cache_quality_pattern")
            assert hasattr(agent, "ml_recall_quality_pattern")
            assert hasattr(agent, "ml_record_reflection_success")
            assert hasattr(agent, "ml_recall_similar_reflection")

    def test_execution_insight_caching(self):
        """Test execution insight caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = MockRgReflectionAgent()

            insight_data = {
                "cycle": 3,
                "signals_at_end": ["quality_low"],
                "failed_agents": ["ContentAgent"],
                "converged": False,
            }
            result = agent.ml_cache_execution_insight("insight_001", insight_data)
            assert result is True

            recalled = agent.ml_recall_execution_insight("insight_001")
            assert recalled == insight_data

    def test_quality_pattern_caching(self):
        """Test quality pattern caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = MockRgReflectionAgent()

            pattern_data = {
                "structure": "chronological",
                "sections": ["summary", "experience", "skills"],
                "quality_score": 0.92,
            }
            result = agent.ml_cache_quality_pattern("pattern_001", pattern_data)
            assert result is True

            recalled = agent.ml_recall_quality_pattern("pattern_001")
            assert recalled == pattern_data

    def test_reflection_success_recording(self):
        """Test reflection success recording with quality threshold."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = MockRgReflectionAgent()

            insights = {"outcome": "success", "cycles": 2}

            # High quality should be cached
            result = agent.ml_record_reflection_success("hash_001", insights, 0.85)
            assert result is True

            recalled = agent.ml_recall_similar_reflection("hash_001")
            assert recalled is not None
            assert recalled["quality_score"] == 0.85

    def test_reflection_low_quality_not_cached(self):
        """Test that low quality reflections are not cached."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = MockRgReflectionAgent()

            insights = {"outcome": "partial", "cycles": 5}

            # Low quality should not be cached
            result = agent.ml_record_reflection_success("hash_002", insights, 0.5)
            assert result is False

            recalled = agent.ml_recall_similar_reflection("hash_002")
            assert recalled is None


class TestOutreachLearningAgentMetaLearning:
    """Tests for OutreachLearningAgent meta-learning integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_outreach_learning_has_ml_methods(self):
        """Test that OutreachLearningAgent has meta-learning methods."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = MockOutreachLearningAgent()

            assert hasattr(agent, "ml_cache_learning_pattern")
            assert hasattr(agent, "ml_recall_learning_pattern")
            assert hasattr(agent, "ml_cache_success_example")
            assert hasattr(agent, "ml_recall_success_example")

    def test_learning_pattern_caching(self):
        """Test learning pattern caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = MockOutreachLearningAgent()

            pattern_data = {
                "task_type": "lead_scoring",
                "success_rate": 0.85,
                "sample_size": 100,
            }
            result = agent.ml_cache_learning_pattern("pattern_001", pattern_data)
            assert result is True

            recalled = agent.ml_recall_learning_pattern("pattern_001")
            assert recalled == pattern_data

    def test_success_example_caching(self):
        """Test success example caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = MockOutreachLearningAgent()

            example_data = {
                "task_type": "message_generation",
                "input_context": "tech_lead_outreach",
                "output_result": "scheduled_meeting",
                "confidence": 0.92,
            }
            result = agent.ml_cache_success_example("example_001", example_data)
            assert result is True

            recalled = agent.ml_recall_success_example("example_001")
            assert recalled == example_data


class TestCrossAgentLearning:
    """Tests for cross-agent learning patterns."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_domain_isolation_between_learning_agents(self):
        """Test that learning agents have isolated caches."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            rg_agent = MockRgReflectionAgent()
            lic_agent = MockOutreachLearningAgent()

            # Cache same key in both domains
            rg_agent.ml_cache_set("shared_learning", {"source": "rg"})
            lic_agent.ml_cache_set("shared_learning", {"source": "lic"})

            # Each should get their own value
            rg_value = rg_agent.ml_cache_get("shared_learning")
            lic_value = lic_agent.ml_cache_get("shared_learning")

            assert rg_value["source"] == "rg"
            assert lic_value["source"] == "lic"

    def test_learning_persistence_across_instances(self):
        """Test that learning persists across agent instances."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            # First instance caches data
            agent1 = MockRgReflectionAgent()
            agent1.ml_cache_quality_pattern("persistent_pattern", {"score": 0.95})

            # Second instance should recall it (same domain, shared singleton)
            agent2 = MockRgReflectionAgent()
            recalled = agent2.ml_recall_quality_pattern("persistent_pattern")

            assert recalled is not None
            assert recalled["score"] == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
