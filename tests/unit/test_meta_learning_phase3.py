"""
Test Suite for Meta-Learning Phase 3: LICAgentBase and RGAgentBase Integration

Tests for:
- LICAgentBase meta-learning activation
- RGAgentBase meta-learning activation
- Domain-specific caching methods
- Cross-domain isolation
"""

from __future__ import annotations

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


class TestLICAgentBaseMetaLearning:
    """Tests for LICAgentBase meta-learning integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_lic_agent_base_has_ml_domain(self):
        """Test that LICAgentBase has correct ML domain."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

            agent = LICAgentBase()
            assert agent._ml_domain == "apps_lic"
            assert agent._get_ml_domain() == "apps_lic"

    def test_lic_agent_base_has_domain_specific_methods(self):
        """Test that LICAgentBase has LIC-specific meta-learning methods."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

            agent = LICAgentBase()

            # Verify LIC-specific methods exist
            assert hasattr(agent, "ml_cache_campaign_pattern")
            assert hasattr(agent, "ml_recall_campaign_pattern")
            assert hasattr(agent, "ml_cache_compliance_rule")
            assert hasattr(agent, "ml_recall_compliance_rule")

    def test_lic_campaign_pattern_caching(self):
        """Test LIC campaign pattern caching."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

            agent = LICAgentBase()

            # Cache a campaign pattern
            pattern_data = {
                "template": "professional_outreach",
                "timing": {"day": "tuesday", "hour": 10},
                "success_rate": 0.85,
            }
            result = agent.ml_cache_campaign_pattern("campaign_001", pattern_data)
            assert result is True

            # Recall the pattern
            recalled = agent.ml_recall_campaign_pattern("campaign_001")
            assert recalled == pattern_data

    def test_lic_compliance_rule_caching(self):
        """Test LIC compliance rule caching."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

            agent = LICAgentBase()

            # Cache a compliance rule
            rule_data = {
                "rule_type": "gdpr_consent",
                "resolution": "add_opt_out_link",
                "validated": True,
            }
            result = agent.ml_cache_compliance_rule("gdpr_001", rule_data)
            assert result is True

            # Recall the rule
            recalled = agent.ml_recall_compliance_rule("gdpr_001")
            assert recalled == rule_data

    def test_lic_context_includes_ml_domain(self):
        """Test that get_lic_context includes meta_learning_domain."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

            agent = LICAgentBase()
            context = agent.get_lic_context()

            assert "meta_learning_domain" in context
            assert context["meta_learning_domain"] == "apps_lic"


class TestRGAgentBaseMetaLearning:
    """Tests for RGAgentBase meta-learning integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_rg_agent_base_has_ml_domain(self):
        """Test that RGAgentBase has correct ML domain."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

            agent = RGAgentBase()
            assert agent._ml_domain == "apps_rg"
            assert agent._get_ml_domain() == "apps_rg"

    def test_rg_agent_base_has_domain_specific_methods(self):
        """Test that RGAgentBase has RG-specific meta-learning methods."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

            agent = RGAgentBase()

            # Verify RG-specific methods exist
            assert hasattr(agent, "ml_cache_resume_quality_pattern")
            assert hasattr(agent, "ml_recall_resume_quality_pattern")
            assert hasattr(agent, "ml_cache_ats_compatibility")
            assert hasattr(agent, "ml_recall_ats_compatibility")
            assert hasattr(agent, "ml_cache_section_balance")
            assert hasattr(agent, "ml_recall_section_balance")

    def test_rg_resume_quality_pattern_caching(self):
        """Test RG resume quality pattern caching."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

            agent = RGAgentBase()

            # Cache a resume quality pattern
            pattern_data = {
                "structure": "chronological",
                "sections": ["summary", "experience", "skills", "education"],
                "quality_score": 0.92,
            }
            result = agent.ml_cache_resume_quality_pattern("quality_001", pattern_data)
            assert result is True

            # Recall the pattern
            recalled = agent.ml_recall_resume_quality_pattern("quality_001")
            assert recalled == pattern_data

    def test_rg_ats_compatibility_caching(self):
        """Test RG ATS compatibility caching."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

            agent = RGAgentBase()

            # Cache ATS compatibility data
            compat_data = {
                "system": "workday",
                "requirements": ["no_tables", "standard_fonts", "pdf_format"],
                "fixes_applied": ["converted_tables_to_lists"],
            }
            result = agent.ml_cache_ats_compatibility("workday", compat_data)
            assert result is True

            # Recall the compatibility data
            recalled = agent.ml_recall_ats_compatibility("workday")
            assert recalled == compat_data

    def test_rg_section_balance_caching(self):
        """Test RG section balance caching."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

            agent = RGAgentBase()

            # Cache section balance data
            balance_data = {
                "summary": 0.15,
                "experience": 0.50,
                "skills": 0.20,
                "education": 0.15,
            }
            result = agent.ml_cache_section_balance("software_engineer", balance_data)
            assert result is True

            # Recall the balance data
            recalled = agent.ml_recall_section_balance("software_engineer")
            assert recalled == balance_data

    def test_rg_context_includes_ml_domain(self):
        """Test that get_rg_context includes meta_learning_domain."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

            agent = RGAgentBase()
            context = agent.get_rg_context()

            assert "meta_learning_domain" in context
            assert context["meta_learning_domain"] == "apps_rg"


class TestCrossDomainIsolation:
    """Tests for cross-domain isolation between LIC and RG."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_lic_and_rg_cache_isolation(self):
        """Test that LIC and RG caches are isolated."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase
            from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

            lic_agent = LICAgentBase()
            rg_agent = RGAgentBase()

            # Cache same key in both domains
            lic_agent.ml_cache_set("shared_key", {"source": "lic"})
            rg_agent.ml_cache_set("shared_key", {"source": "rg"})

            # Each should get their own value
            lic_value = lic_agent.ml_cache_get("shared_key")
            rg_value = rg_agent.ml_cache_get("shared_key")

            assert lic_value["source"] == "lic"
            assert rg_value["source"] == "rg"

    def test_lic_cannot_access_rg_cache(self):
        """Test that LIC agent cannot access RG-specific cache."""
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
                "agentic_core.domain.CoreIntegrityVerifier."
                "CoreIntegrityVerifier.verify_core_integrity"
            ),
        ):
            from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase
            from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

            lic_agent = LICAgentBase()
            rg_agent = RGAgentBase()

            # RG caches a value
            rg_agent.ml_cache_set("rg_only_key", {"data": "rg_secret"})

            # LIC should not see it (different domain namespace)
            lic_value = lic_agent.ml_cache_get("rg_only_key")
            assert lic_value is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
