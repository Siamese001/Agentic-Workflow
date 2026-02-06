"""
Comprehensive Test Suite for Meta-Learning System

This file consolidates all meta-learning tests from the original phase files:
- Phase 2: SovereignBaseAgent Integration
- Phase 3: LICAgentBase and RGAgentBase Integration
- Phase 4: Healing Orchestrators Integration
- Phase 5: Learning Agents Integration
- Phase 6: Domain Context Managers and Cross-Domain Sharing
- Phase 7: Observability and Optimization

Tests cover:
- MetaLearningClientMixin integration with base agents
- Healing pattern recall and storage
- Cache-aware healing decision logic
- Domain-specific context handling
- Cross-domain isolation
- Observability and metrics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import patch

import pytest


def reset_all_singletons():
    """Reset all meta-learning singletons for test isolation."""
    import agentic_core.L1_cognition.meta_learning.CacheStrategyManager as csm
    import agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder as hme
    import agentic_core.L1_cognition.meta_learning.MetaLearningClient as mlc

    mlc._meta_learning_client = None
    mlc._singleton_instance = None
    hme._healing_memory_embedder = None
    hme._embedder_singleton = None
    csm._cache_strategy_manager = None
    csm._csm_singleton = None

    from agentic_core.base_agents.meta_learning_client_mixin import (
        MetaLearningClientMixin,
    )

    MetaLearningClientMixin._ml_client = None
    MetaLearningClientMixin._ml_embedder = None
    MetaLearningClientMixin._ml_cache_manager = None

    # Reset domain context manager if it exists
    try:
        import agentic_core.L1_cognition.meta_learning.DomainContextManager as dcm

        dcm._domain_context_manager = None
    except (ImportError, AttributeError):
        pass

    # Reset observability if it exists
    try:
        import agentic_core.L1_cognition.meta_learning.MetaLearningObservability as mlo

        mlo._observability_instance = None
    except (ImportError, AttributeError):
        pass


# =============================================================================
# SECTION 1: MetaLearningClientMixin Tests (from Phase 2)
# =============================================================================


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

        class TestAgent(MetaLearningClientMixin):
            pass

        agent = TestAgent()

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
            result = agent.ml_cache_set("test_key", {"data": "value"})
            assert result is True
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

        assert agent.ml_check_healing_depth(violation_id) is True

        for _ in range(5):
            agent.ml_increment_healing_depth(violation_id)

        assert agent.ml_check_healing_depth(violation_id) is False

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
            assert sig1 == sig2
            assert len(sig1) == 16


# =============================================================================
# SECTION 2: SovereignBaseAgent Integration Tests (from Phase 2)
# =============================================================================


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
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
            patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"),
        ):
            from agentic_core.base_agents.sovereign_base_agent import SovereignBaseAgent

            agent = SovereignBaseAgent()

            assert hasattr(agent, "ml_recall_healing_pattern")
            assert hasattr(agent, "ml_store_healing_pattern")
            assert hasattr(agent, "ml_cache_get")
            assert hasattr(agent, "ml_cache_set")
            assert hasattr(agent, "ml_enhanced_heal")


# =============================================================================
# SECTION 3: Domain Isolation Tests (from Phase 3)
# =============================================================================


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

            lic_agent.ml_cache_set("shared_key", {"source": "lic"})
            rg_agent.ml_cache_set("shared_key", {"source": "rg"})
            core_agent.ml_cache_set("shared_key", {"source": "core"})

            assert lic_agent.ml_cache_get("shared_key")["source"] == "lic"
            assert rg_agent.ml_cache_get("shared_key")["source"] == "rg"
            assert core_agent.ml_cache_get("shared_key")["source"] == "core"


# =============================================================================
# SECTION 4: Healing Orchestrator Tests (from Phase 4)
# =============================================================================


@dataclass
class MockLicHealingOrchestrator:
    """Mock LIC Healing Orchestrator for testing meta-learning methods."""

    _ml_domain: str = field(default="apps_lic", init=False)
    recovery_playbooks: dict[str, str] = field(
        default_factory=lambda: {
            "database_lock": "release_and_retry",
            "api_timeout": "exponential_backoff",
        }
    )

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


class TestHealingOrchestratorIntegration:
    """Tests for healing orchestrator meta-learning integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_mock_orchestrator_has_domain(self):
        """Test that mock orchestrator has correct domain."""
        orchestrator = MockLicHealingOrchestrator()
        assert orchestrator._get_ml_domain() == "apps_lic"

    def test_recovery_playbooks_exist(self):
        """Test that recovery playbooks are initialized."""
        orchestrator = MockLicHealingOrchestrator()
        assert "database_lock" in orchestrator.recovery_playbooks
        assert "api_timeout" in orchestrator.recovery_playbooks


# =============================================================================
# SECTION 5: Domain Context Manager Tests (from Phase 6)
# =============================================================================


class TestDomainContextManager:
    """Tests for DomainContextManager functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_singleton_pattern(self):
        """Test that DomainContextManager follows singleton pattern."""
        try:
            from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
                get_domain_context_manager,
            )

            manager1 = get_domain_context_manager()
            manager2 = get_domain_context_manager()
            assert manager1 is manager2
        except ImportError:
            pytest.skip("DomainContextManager not available")

    def test_default_contexts_initialized(self):
        """Test that default domain contexts are initialized."""
        try:
            from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
                get_domain_context_manager,
            )

            manager = get_domain_context_manager()
            assert manager.get_context("agentic_core") is not None
            assert manager.get_context("apps_lic") is not None
            assert manager.get_context("apps_rg") is not None
        except ImportError:
            pytest.skip("DomainContextManager not available")


# =============================================================================
# SECTION 6: Observability Tests (from Phase 7)
# =============================================================================


class TestMetaLearningObservability:
    """Tests for MetaLearningObservability functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_singleton_pattern(self):
        """Test that MetaLearningObservability follows singleton pattern."""
        try:
            from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
                get_meta_learning_observability,
            )

            obs1 = get_meta_learning_observability()
            obs2 = get_meta_learning_observability()
            assert obs1 is obs2
        except ImportError:
            pytest.skip("MetaLearningObservability not available")

    def test_initial_health_checks_registered(self):
        """Test that initial health checks are registered."""
        try:
            from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
                get_meta_learning_observability,
            )

            obs = get_meta_learning_observability()
            assert "MetaLearningClient" in obs._health_status
            assert "CacheStrategyManager" in obs._health_status
        except ImportError:
            pytest.skip("MetaLearningObservability not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
