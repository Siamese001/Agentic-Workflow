"""
Integration Test Suite for Meta-Learning System

Tests the complete Meta-Learning integration across all phases:
- Phase 1: MetaLearningClient core infrastructure
- Phase 2: SovereignBaseAgent integration
- Phase 3: LICAgentBase and RGAgentBase activation
- Phase 4: Healing orchestrators integration
- Phase 5: Learning agents integration
- Phase 6: Domain context managers and cross-domain sharing
- Phase 7: Observability and optimization
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


def reset_all_singletons():
    """Reset all meta-learning singletons for test isolation."""
    import agentic_core.L1_cognition.meta_learning.meta_learning_client_types as mlc
    import agentic_core.L1_cognition.meta_learning.healing_memory_embedder_types as hme
    import agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types as csm
    import agentic_core.L1_cognition.meta_learning.domain_context_manager_types as dcm
    import agentic_core.L1_cognition.meta_learning.meta_learning_observability_types as mlo
    from agentic_core.base_agents.meta_learning_client_mixin import (
        MetaLearningClientMixin,
    )

    mlc._meta_learning_client = None
    mlc._singleton_instance = None
    hme._healing_memory_embedder = None
    hme._embedder_singleton = None
    csm._cache_strategy_manager = None
    csm._csm_singleton = None
    dcm._domain_context_manager = None
    mlo._observability_instance = None
    MetaLearningClientMixin._ml_client = None
    MetaLearningClientMixin._ml_embedder = None
    MetaLearningClientMixin._ml_cache_manager = None


class TestFullStackIntegration:
    """Integration tests for the complete Meta-Learning stack."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_full_healing_workflow(self):
        """Test complete healing workflow with meta-learning."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types import (
            get_cache_strategy_manager,
        )
        from agentic_core.L1_cognition.meta_learning.meta_learning_observability_types import (
            get_meta_learning_observability,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            # Initialize all components
            client = get_meta_learning_client()
            cache_manager = get_cache_strategy_manager()
            observability = get_meta_learning_observability()

            # Simulate a healing workflow
            # 1. Check healing depth
            can_heal = cache_manager.check_healing_depth("TestAgent", "v_001")
            assert can_heal is True

            # 2. Increment depth
            cache_manager.increment_healing_depth("TestAgent", "v_001")

            # 3. Store healing pattern
            healing_result = {"status": "fixed", "changes": ["renamed"]}
            client.cache_set("healing:v_001", healing_result, "agentic_core")

            # 4. Record metrics
            observability.increment_stat("healing_operations")
            observability.record_operation_time("heal", 50.0)

            # 5. Verify pattern stored
            cached = client.cache_get("healing:v_001", "agentic_core")
            assert cached == healing_result

            # 6. Check stats
            stats = observability.get_stats()
            assert stats["healing_operations"] >= 1

    def test_cross_domain_pattern_sharing(self):
        """Test cross-domain pattern sharing workflow."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.domain_context_manager_types import (
            get_domain_context_manager,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()
            domain_manager = get_domain_context_manager()

            # Store pattern in agentic_core
            client.cache_set(
                "shared_healing_pattern",
                {"strategy": "rename_file", "success_rate": 0.95},
                "agentic_core",
            )

            # apps_lic should be able to read from agentic_core
            value, source = domain_manager.get_shared_pattern(
                "shared_healing_pattern",
                "apps_lic",
                pattern_type="healing_pattern",
            )

            assert value is not None
            assert source == "agentic_core"
            assert value["strategy"] == "rename_file"

    def test_domain_isolation(self):
        """Test that domains are properly isolated."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()

            # Store same key in different domains
            client.cache_set("isolated_key", {"domain": "core"}, "agentic_core")
            client.cache_set("isolated_key", {"domain": "lic"}, "apps_lic")
            client.cache_set("isolated_key", {"domain": "rg"}, "apps_rg")

            # Each domain should have its own value
            core_val = client.cache_get("isolated_key", "agentic_core")
            lic_val = client.cache_get("isolated_key", "apps_lic")
            rg_val = client.cache_get("isolated_key", "apps_rg")

            assert core_val["domain"] == "core"
            assert lic_val["domain"] == "lic"
            assert rg_val["domain"] == "rg"

    def test_observability_health_check(self):
        """Test observability health check across all components."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.meta_learning_observability_types import (
            get_meta_learning_observability,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            observability = get_meta_learning_observability()
            health = observability.get_health_summary()

            # Should have health data for all components
            assert "overall_healthy" in health
            assert "components" in health
            assert "MetaLearningClient" in health["components"]
            assert "CacheStrategyManager" in health["components"]
            assert "DomainContextManager" in health["components"]

    def test_dashboard_data_aggregation(self):
        """Test dashboard data aggregation from all components."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.meta_learning_observability_types import (
            get_meta_learning_observability,
            OperationTimer,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()
            observability = get_meta_learning_observability()

            # Perform some operations
            with OperationTimer("cache_set"):
                client.cache_set("dashboard_test", {"data": "test"}, "agentic_core")

            with OperationTimer("cache_get"):
                client.cache_get("dashboard_test", "agentic_core")

            observability.record_metric("test_metric", 1.0)
            observability.increment_stat("cache_hits")

            # Get dashboard data
            dashboard = observability.get_dashboard_data()

            assert "health" in dashboard
            assert "stats" in dashboard
            assert "performance" in dashboard
            assert "recent_metrics" in dashboard


class TestHealingPatternLearning:
    """Integration tests for healing pattern learning."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_pattern_store_and_recall(self):
        """Test storing and recalling healing patterns."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.healing_memory_embedder_types import (
            HealingMemoryEmbedder,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
        ):
            client = get_meta_learning_client()

            # Store a healing pattern
            violation = {"type": "import_error", "path": "/test.py"}
            healing_result = {
                "status": "fixed",
                "strategy": "add_import",
                "changes": ["added import statement"],
            }

            client.store_healing_pattern(violation, healing_result, "agentic_core")

            # Verify it's in local cache
            stats = client.get_stats()
            assert stats["local_cache_size"] > 0

    def test_healing_depth_prevents_infinite_loops(self):
        """Test that healing depth tracking prevents infinite loops."""
        from agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        # Simulate multiple healing attempts
        for _ in range(5):
            manager.increment_healing_depth("TestAgent", "loop_test")

        # Should be blocked now
        can_heal = manager.check_healing_depth("TestAgent", "loop_test")
        assert can_heal is False

        # Reset should allow healing again
        manager.reset_healing_depth("TestAgent", "loop_test")
        can_heal = manager.check_healing_depth("TestAgent", "loop_test")
        assert can_heal is True


class TestDomainSpecificBehavior:
    """Integration tests for domain-specific behavior."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_lic_domain_higher_threshold(self):
        """Test that LIC domain has higher similarity threshold."""
        from agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        lic_threshold = manager.get_similarity_threshold("apps_lic")
        core_threshold = manager.get_similarity_threshold("agentic_core")

        # LIC should have higher threshold (stricter matching)
        assert lic_threshold > core_threshold

    def test_domain_specific_ttl(self):
        """Test domain-specific TTL configuration."""
        from agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        core_ttl = manager.get_ttl("agentic_core")
        lic_ttl = manager.get_ttl("apps_lic")
        rg_ttl = manager.get_ttl("apps_rg")

        # All should have valid TTLs
        assert core_ttl > 0
        assert lic_ttl > 0
        assert rg_ttl > 0


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_complete_meta_learning_cycle(self):
        """Test a complete meta-learning cycle from violation to learned pattern."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types import (
            get_cache_strategy_manager,
        )
        from agentic_core.L1_cognition.meta_learning.domain_context_manager_types import (
            get_domain_context_manager,
        )
        from agentic_core.L1_cognition.meta_learning.meta_learning_observability_types import (
            get_meta_learning_observability,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            # Initialize all components
            client = get_meta_learning_client()
            cache_manager = get_cache_strategy_manager()
            domain_manager = get_domain_context_manager()
            observability = get_meta_learning_observability()

            # Step 1: Detect violation
            violation = {
                "id": "e2e_001",
                "type": "structure_violation",
                "path": "/apps_lic/test.py",
                "domain": "apps_lic",
            }

            # Step 2: Check if we can heal (depth limit)
            can_heal = cache_manager.check_healing_depth("E2EAgent", violation["id"])
            assert can_heal is True

            # Step 3: Increment healing depth
            cache_manager.increment_healing_depth("E2EAgent", violation["id"])

            # Step 4: Check for existing pattern in domain hierarchy
            existing, source = domain_manager.get_shared_pattern(
                f"healing:{violation['type']}",
                "apps_lic",
                pattern_type="healing_pattern",
            )

            # Step 5: Execute healing (simulated)
            healing_result = {
                "status": "fixed",
                "strategy": "restructure",
                "changes": ["moved file to correct location"],
            }

            # Step 6: Store successful pattern
            client.cache_set(
                f"healing:{violation['type']}",
                healing_result,
                "apps_lic",
            )

            # Step 7: Record metrics
            observability.increment_stat("healing_operations")
            observability.record_operation_time("heal_structure", 100.0)

            # Step 8: Reset healing depth (success)
            cache_manager.reset_healing_depth("E2EAgent", violation["id"])

            # Verify the pattern is now available
            cached = client.cache_get(f"healing:{violation['type']}", "apps_lic")
            assert cached is not None
            assert cached["status"] == "fixed"

            # Verify metrics recorded
            stats = observability.get_stats()
            assert stats["healing_operations"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
