"""
Phase 3 Test Suite: Domain-Specific Patterns and Statistics

Tests domain-specific pattern types, statistics tracking, and monitoring
for both RG and LIC domains.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L1_cognition.meta_learning.guardrails import reset_guardrails


class TestRGDomainPatterns:
    """Test RG domain-specific pattern types."""

    @pytest.fixture(autouse=True)
    def setup(self):
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_resume_quality_pattern_caching(self):
        """Test RG resume quality pattern caching."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            with patch.object(agent, "ml_cache_set", return_value=True) as mock:
                result = agent.ml_cache_resume_quality_pattern(
                    "pattern_001", {"structure": "optimal", "score": 0.95}
                )
                assert result is True
                mock.assert_called_once()

    def test_rg_ats_compatibility_pattern_caching(self):
        """Test RG ATS compatibility pattern caching."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            with patch.object(agent, "ml_cache_set", return_value=True):
                result = agent.ml_cache_ats_compatibility(
                    "lever", {"format": "standard", "keywords": True}
                )
                assert result is True

    def test_rg_section_balance_pattern_caching(self):
        """Test RG section balance pattern caching."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            with patch.object(agent, "ml_cache_set", return_value=True):
                result = agent.ml_cache_section_balance(
                    "engineer", {"experience": 40, "skills": 30, "education": 30}
                )
                assert result is True


class TestLICDomainPatterns:
    """Test LIC domain-specific pattern types."""

    @pytest.fixture(autouse=True)
    def setup(self):
        reset_guardrails()
        yield
        reset_guardrails()

    def test_lic_campaign_pattern_caching(self):
        """Test LIC campaign pattern caching."""
        from apps_lic.shared.core.lic_agent_base_agent_validator import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            with patch.object(agent, "ml_cache_set", return_value=True):
                result = agent.ml_cache_campaign_pattern(
                    "campaign_001", {"template": "professional", "timing": "morning"}
                )
                assert result is True

    def test_lic_compliance_rule_caching(self):
        """Test LIC compliance rule caching."""
        from apps_lic.shared.core.lic_agent_base_agent_validator import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            with patch.object(agent, "ml_cache_set", return_value=True):
                result = agent.ml_cache_compliance_rule(
                    "gdpr_consent", {"required": True, "action": "request_consent"}
                )
                assert result is True


class TestStatisticsAndMonitoring:
    """Test statistics and monitoring capabilities."""

    @pytest.fixture(autouse=True)
    def setup(self):
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_get_cache_health_returns_domain_stats(self):
        """Test RG get_cache_health includes domain."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            health = agent.get_cache_health()

            assert health["domain"] == "apps_rg"
            assert "cache_size" in health
            assert "healthy" in health

    def test_lic_get_cache_health_returns_domain_stats(self):
        """Test LIC get_cache_health includes domain."""
        from apps_lic.shared.core.lic_agent_base_agent_validator import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            health = agent.get_cache_health()

            assert health["domain"] == "apps_lic"
            assert "cache_size" in health
            assert "healthy" in health

    def test_rg_guardrails_get_stats_returns_structure(self):
        """Test RG guardrails_get_stats returns proper structure."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            stats = agent.guardrails_get_stats()

            assert isinstance(stats, dict)
            assert "cache_sizes" in stats
            assert "request_rates" in stats

    def test_lic_guardrails_get_stats_returns_structure(self):
        """Test LIC guardrails_get_stats returns proper structure."""
        from apps_lic.shared.core.lic_agent_base_agent_validator import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            stats = agent.guardrails_get_stats()

            assert isinstance(stats, dict)
            assert "cache_sizes" in stats

    def test_rg_meta_learning_stats(self):
        """Test RG get_meta_learning_stats returns client stats."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._meta_client = None
            agent._initialize_meta_client()

            mock_stats = {"cache_hits": 10, "cache_misses": 5}
            with patch.object(agent._meta_client, "get_stats", return_value=mock_stats):
                stats = agent.get_meta_learning_stats()
                assert stats == mock_stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
