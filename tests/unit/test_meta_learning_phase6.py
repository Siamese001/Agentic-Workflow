"""
Test Suite for Meta-Learning Phase 6: Domain Context Managers and Cross-Domain Sharing

Tests for:
- DomainContextManager functionality
- Cross-domain pattern sharing
- Domain isolation and policies
- Context inheritance
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


def reset_all_singletons():
    """Reset all meta-learning singletons for test isolation."""
    import agentic_core.L1_cognition.meta_learning.MetaLearningClient as mlc
    import agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder as hme
    import agentic_core.L1_cognition.meta_learning.CacheStrategyManager as csm
    import agentic_core.L1_cognition.meta_learning.DomainContextManager as dcm
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
    MetaLearningClientMixin._ml_client = None
    MetaLearningClientMixin._ml_embedder = None
    MetaLearningClientMixin._ml_cache_manager = None


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
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager1 = get_domain_context_manager()
        manager2 = get_domain_context_manager()

        assert manager1 is manager2

    def test_default_contexts_initialized(self):
        """Test that default domain contexts are initialized."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()

        # Check default domains exist
        assert manager.get_context("agentic_core") is not None
        assert manager.get_context("apps_lic") is not None
        assert manager.get_context("apps_rg") is not None

    def test_agentic_core_is_root(self):
        """Test that agentic_core is the root domain."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()
        core_context = manager.get_context("agentic_core")

        assert core_context is not None
        assert core_context.parent_domain is None

    def test_apps_inherit_from_core(self):
        """Test that apps domains inherit from agentic_core."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()

        lic_context = manager.get_context("apps_lic")
        rg_context = manager.get_context("apps_rg")

        assert lic_context.parent_domain == "agentic_core"
        assert rg_context.parent_domain == "agentic_core"

    def test_domain_hierarchy(self):
        """Test domain hierarchy retrieval."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()
        hierarchy = manager.get_domain_hierarchy()

        # agentic_core should be at root level
        assert "root" in hierarchy
        assert "agentic_core" in hierarchy["root"]

        # apps should be under agentic_core
        assert "agentic_core" in hierarchy
        assert "apps_lic" in hierarchy["agentic_core"]
        assert "apps_rg" in hierarchy["agentic_core"]


class TestSharingPolicies:
    """Tests for cross-domain sharing policies."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_same_domain_always_allowed(self):
        """Test that same domain sharing is always allowed."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()

        assert manager.can_share("apps_lic", "apps_lic") is True
        assert manager.can_share("apps_rg", "apps_rg") is True
        assert manager.can_share("agentic_core", "agentic_core") is True

    def test_core_can_share_bidirectionally(self):
        """Test that agentic_core can share with all domains."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()

        # Core can share to apps
        assert manager.can_share("agentic_core", "apps_lic") is True
        assert manager.can_share("agentic_core", "apps_rg") is True

    def test_apps_can_read_from_core(self):
        """Test that apps can read from agentic_core."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()

        lic_context = manager.get_context("apps_lic")
        rg_context = manager.get_context("apps_rg")

        assert lic_context.can_read_from("agentic_core") is True
        assert rg_context.can_read_from("agentic_core") is True

    def test_apps_cannot_read_from_each_other(self):
        """Test that apps cannot read from each other by default."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()

        lic_context = manager.get_context("apps_lic")
        rg_context = manager.get_context("apps_rg")

        assert lic_context.can_read_from("apps_rg") is False
        assert rg_context.can_read_from("apps_lic") is False

    def test_selective_pattern_type_sharing(self):
        """Test selective pattern type sharing."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        manager = get_domain_context_manager()

        lic_context = manager.get_context("apps_lic")

        # Allowed pattern types
        assert lic_context.can_share_pattern_type("healing_pattern") is True
        assert lic_context.can_share_pattern_type("compliance_rule") is True

        # Not allowed pattern types
        assert lic_context.can_share_pattern_type("random_pattern") is False


class TestCrossDomainSharing:
    """Tests for cross-domain pattern sharing."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_get_shared_pattern_from_own_domain(self):
        """Test getting a pattern from own domain."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
                get_meta_learning_client,
            )

            client = get_meta_learning_client()
            manager = get_domain_context_manager()

            # Store pattern in apps_lic
            client.cache_set("test_pattern", {"data": "lic_data"}, "apps_lic")

            # Get from own domain
            value, source = manager.get_shared_pattern("test_pattern", "apps_lic")

            assert value == {"data": "lic_data"}
            assert source == "apps_lic"

    def test_get_shared_pattern_from_parent_domain(self):
        """Test getting a pattern from parent domain."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
                get_meta_learning_client,
            )

            client = get_meta_learning_client()
            manager = get_domain_context_manager()

            # Store pattern in agentic_core
            client.cache_set("core_pattern", {"data": "core_data"}, "agentic_core")

            # Get from apps_lic (should find in parent)
            value, source = manager.get_shared_pattern("core_pattern", "apps_lic")

            assert value == {"data": "core_data"}
            assert source == "agentic_core"

    def test_share_pattern_to_multiple_domains(self):
        """Test sharing a pattern to multiple domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            manager = get_domain_context_manager()

            # Share from core to all domains
            results = manager.share_pattern(
                "shared_pattern",
                {"data": "shared"},
                "agentic_core",
                target_domains=["agentic_core", "apps_lic", "apps_rg"],
            )

            # Core should succeed sharing to all
            assert results["agentic_core"] is True
            assert results["apps_lic"] is True
            assert results["apps_rg"] is True

    def test_statistics_tracking(self):
        """Test that cross-domain statistics are tracked."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
                get_meta_learning_client,
            )

            client = get_meta_learning_client()
            manager = get_domain_context_manager()

            # Perform some operations
            client.cache_set("stat_test", {"data": "test"}, "agentic_core")
            manager.get_shared_pattern("stat_test", "apps_lic")

            stats = manager.get_stats()

            assert "cross_domain_reads" in stats
            assert "context_lookups" in stats
            assert "registered_domains" in stats


class TestCustomContextRegistration:
    """Tests for custom domain context registration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_register_custom_context(self):
        """Test registering a custom domain context."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
            DomainContext,
            SharingPolicy,
        )

        manager = get_domain_context_manager()

        # Register custom domain
        custom_context = DomainContext(
            domain="apps_custom",
            parent_domain="agentic_core",
            sharing_policy=SharingPolicy.READ_ONLY,
            allowed_sources=["agentic_core", "apps_lic"],
        )
        manager.register_context(custom_context)

        # Verify registration
        retrieved = manager.get_context("apps_custom")
        assert retrieved is not None
        assert retrieved.domain == "apps_custom"
        assert retrieved.parent_domain == "agentic_core"

    def test_custom_context_sharing_policy(self):
        """Test custom context sharing policy."""
        from agentic_core.L1_cognition.meta_learning.DomainContextManager import (
            get_domain_context_manager,
            DomainContext,
            SharingPolicy,
        )

        manager = get_domain_context_manager()

        # Register custom domain with read-only policy
        custom_context = DomainContext(
            domain="apps_readonly",
            parent_domain="agentic_core",
            sharing_policy=SharingPolicy.READ_ONLY,
            allowed_sources=["agentic_core"],
        )
        manager.register_context(custom_context)

        # Can read from allowed sources
        assert custom_context.can_read_from("agentic_core") is True

        # Cannot read from non-allowed sources
        assert custom_context.can_read_from("apps_lic") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
