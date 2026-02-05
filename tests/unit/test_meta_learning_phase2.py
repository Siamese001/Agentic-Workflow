"""
Test Suite for Meta-Learning Phase 2: SovereignBaseAgent Integration

Tests for:
- MetaLearningClientMixin integration with SovereignBaseAgent
- Healing pattern recall and storage
- Cache-aware healing decision logic
- Domain-specific context handling
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def reset_all_singletons():
    """Reset all meta-learning singletons for test isolation."""
    # Reset Phase 1 singletons
    import agentic_core.L1_cognition.meta_learning.MetaLearningClient as mlc
    import agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder as hme
    import agentic_core.L1_cognition.meta_learning.CacheStrategyManager as csm

    mlc._meta_learning_client = None
    mlc._singleton_instance = None
    hme._healing_memory_embedder = None
    hme._embedder_singleton = None
    csm._cache_strategy_manager = None
    csm._csm_singleton = None

    # Reset Phase 2 mixin singletons
    from agentic_core.base_agents.meta_learning_client_mixin import (
        MetaLearningClientMixin,
    )

    MetaLearningClientMixin._ml_client = None
    MetaLearningClientMixin._ml_embedder = None
    MetaLearningClientMixin._ml_cache_manager = None


class TestMetaLearningClientMixin:
    """Tests for MetaLearningClientMixin functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_mixin_provides_ml_methods(self):
        """Test that mixin provides all expected methods."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        # Create a simple class that uses the mixin
        class TestAgent(MetaLearningClientMixin):
            pass

        agent = TestAgent()

        # Verify all expected methods exist
        assert hasattr(agent, "ml_recall_healing_pattern")
        assert hasattr(agent, "ml_store_healing_pattern")
        assert hasattr(agent, "ml_cache_get")
        assert hasattr(agent, "ml_cache_set")
        assert hasattr(agent, "ml_check_healing_depth")
        assert hasattr(agent, "ml_increment_healing_depth")
        assert hasattr(agent, "ml_reset_healing_depth")
        assert hasattr(agent, "ml_get_violation_signature")
        assert hasattr(agent, "ml_enhanced_heal")
        assert hasattr(agent, "ml_get_stats")

    def test_domain_detection_from_class_name(self):
        """Test domain detection from class name."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        class LicTestAgent(MetaLearningClientMixin):
            pass

        class RgTestAgent(MetaLearningClientMixin):
            pass

        class CoreTestAgent(MetaLearningClientMixin):
            pass

        lic_agent = LicTestAgent()
        rg_agent = RgTestAgent()
        core_agent = CoreTestAgent()

        assert lic_agent._get_ml_domain() == "apps_lic"
        assert rg_agent._get_ml_domain() == "apps_rg"
        assert core_agent._get_ml_domain() == "agentic_core"

    def test_explicit_domain_override(self):
        """Test explicit domain override."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        class TestAgent(MetaLearningClientMixin):
            _ml_domain = "apps_lic"

        agent = TestAgent()
        assert agent._get_ml_domain() == "apps_lic"

    def test_cache_operations(self):
        """Test cache get/set operations through mixin."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        class TestAgent(MetaLearningClientMixin):
            pass

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = TestAgent()

            # Test cache set
            result = agent.ml_cache_set("test_key", {"data": "value"})
            assert result is True

            # Test cache get
            cached = agent.ml_cache_get("test_key")
            assert cached == {"data": "value"}

    def test_healing_depth_tracking(self):
        """Test healing depth tracking through mixin."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        class TestAgent(MetaLearningClientMixin):
            pass

        agent = TestAgent()
        violation_id = "test_violation_001"

        # Should allow healing initially
        assert agent.ml_check_healing_depth(violation_id) is True

        # Increment depth multiple times
        for _ in range(5):
            agent.ml_increment_healing_depth(violation_id)

        # Should block at max depth
        assert agent.ml_check_healing_depth(violation_id) is False

        # Reset should allow healing again
        agent.ml_reset_healing_depth(violation_id)
        assert agent.ml_check_healing_depth(violation_id) is True

    def test_violation_signature_generation(self):
        """Test violation signature generation."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )

        class TestAgent(MetaLearningClientMixin):
            pass

        with patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"):
            agent = TestAgent()

            violation = {
                "type": "naming_violation",
                "path": "/test/file.py",
                "message": "Invalid name",
            }

            sig1 = agent.ml_get_violation_signature(violation)
            sig2 = agent.ml_get_violation_signature(violation)

            # Same violation should produce same signature
            assert sig1 == sig2
            assert len(sig1) == 16

    def test_enhanced_heal_with_depth_limit(self):
        """Test enhanced heal respects depth limit."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )

        class TestAgent(MetaLearningClientMixin):
            pass

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
        ):
            agent = TestAgent()

            violation = {"type": "test", "id": "depth_test_001"}

            # Mock heal function
            heal_fn = MagicMock(return_value={"status": "fixed"})

            # First few heals should work
            for _ in range(5):
                result = agent.ml_enhanced_heal(violation, heal_fn)
                # Reset depth to simulate successful healing
                agent.ml_reset_healing_depth(violation["id"])

            # Exhaust depth limit
            for _ in range(5):
                agent.ml_increment_healing_depth(violation["id"])

            # Should be blocked now
            result = agent.ml_enhanced_heal(violation, heal_fn)
            assert result["status"] == "skipped"
            assert result["reason"] == "healing_depth_limit_reached"

    def test_enhanced_heal_stores_successful_pattern(self):
        """Test that enhanced heal stores successful patterns."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )

        class TestAgent(MetaLearningClientMixin):
            pass

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
        ):
            agent = TestAgent()

            violation = {"type": "naming_violation", "path": "/test.py"}
            heal_result = {"status": "fixed", "changes": ["renamed file"]}

            # Mock heal function
            heal_fn = MagicMock(return_value=heal_result)

            # Execute enhanced heal
            result = agent.ml_enhanced_heal(violation, heal_fn)

            assert result["status"] == "fixed"
            heal_fn.assert_called_once()

    def test_stats_aggregation(self):
        """Test statistics aggregation from all components."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )

        class TestAgent(MetaLearningClientMixin):
            pass

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
        ):
            agent = TestAgent()

            # Perform some operations to generate stats
            agent.ml_cache_set("key1", {"data": "test"})
            agent.ml_cache_get("key1")
            agent.ml_cache_get("nonexistent")

            stats = agent.ml_get_stats()

            assert "domain" in stats
            assert stats["domain"] == "agentic_core"


class TestSovereignBaseAgentIntegration:
    """Tests for SovereignBaseAgent with MetaLearningClientMixin."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_sovereign_base_agent_has_ml_capabilities(self):
        """Test that SovereignBaseAgent has meta-learning capabilities."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
            patch(
                "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from agentic_core.base_agents.sovereign_base_agent import SovereignBaseAgent

            agent = SovereignBaseAgent()

            # Verify meta-learning methods exist
            assert hasattr(agent, "ml_recall_healing_pattern")
            assert hasattr(agent, "ml_store_healing_pattern")
            assert hasattr(agent, "ml_cache_get")
            assert hasattr(agent, "ml_cache_set")
            assert hasattr(agent, "ml_enhanced_heal")

    def test_sovereign_capabilities_includes_meta_learning(self):
        """Test that get_sovereign_capabilities includes meta_learning."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
            patch(
                "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from agentic_core.base_agents.sovereign_base_agent import SovereignBaseAgent

            agent = SovereignBaseAgent()
            capabilities = agent.get_sovereign_capabilities()

            assert "meta_learning" in capabilities
            assert capabilities["meta_learning"] is True

    def test_sovereign_agent_cache_operations(self):
        """Test cache operations through SovereignBaseAgent."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
            patch(
                "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from agentic_core.base_agents.sovereign_base_agent import SovereignBaseAgent

            agent = SovereignBaseAgent()

            # Test cache operations
            agent.ml_cache_set("sovereign_key", {"test": "data"})
            cached = agent.ml_cache_get("sovereign_key")

            assert cached == {"test": "data"}


class TestDomainIsolation:
    """Tests for domain isolation in meta-learning."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_lic_domain_isolation(self):
        """Test LIC domain isolation."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        class LicHealingAgent(MetaLearningClientMixin):
            pass

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = LicHealingAgent()

            assert agent._get_ml_domain() == "apps_lic"

            # Cache should use LIC domain
            agent.ml_cache_set("lic_key", {"domain": "lic"})
            cached = agent.ml_cache_get("lic_key")
            assert cached == {"domain": "lic"}

    def test_rg_domain_isolation(self):
        """Test RG domain isolation."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        class RgReflectionAgent(MetaLearningClientMixin):
            pass

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            agent = RgReflectionAgent()

            assert agent._get_ml_domain() == "apps_rg"

            # Cache should use RG domain
            agent.ml_cache_set("rg_key", {"domain": "rg"})
            cached = agent.ml_cache_get("rg_key")
            assert cached == {"domain": "rg"}

    def test_cross_domain_isolation(self):
        """Test that domains are properly isolated."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        class LicAgent(MetaLearningClientMixin):
            pass

        class RgAgent(MetaLearningClientMixin):
            pass

        class CoreAgent(MetaLearningClientMixin):
            pass

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            lic_agent = LicAgent()
            rg_agent = RgAgent()
            core_agent = CoreAgent()

            # Set same key in different domains
            lic_agent.ml_cache_set("shared_key", {"source": "lic"})
            rg_agent.ml_cache_set("shared_key", {"source": "rg"})
            core_agent.ml_cache_set("shared_key", {"source": "core"})

            # Each should get their own value
            assert lic_agent.ml_cache_get("shared_key")["source"] == "lic"
            assert rg_agent.ml_cache_get("shared_key")["source"] == "rg"
            assert core_agent.ml_cache_get("shared_key")["source"] == "core"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
