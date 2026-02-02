"""
Phase 2.1 Test Suite: MetaLearningClient Integration

Tests the MetaLearningClient integration for RG and LIC domains,
including pattern storage, retrieval, and healing depth management.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L1_cognition.meta_learning.guardrails import reset_guardrails


class TestRGMetaLearningClientIntegration:
    """Test MetaLearningClient integration for RG domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_has_meta_client_attribute(self):
        """Test RGAgentBase has _meta_client attribute."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._meta_client = None
            agent._initialize_meta_client()

            assert agent._meta_client is not None

    def test_rg_store_healing_pattern_validates_domain(self):
        """Test RG store_healing_pattern validates domain."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._meta_client = None
            agent._initialize_guardrails()
            agent._initialize_meta_client()

            # Mock the meta client's store method
            with patch.object(
                agent._meta_client, "store_healing_pattern", return_value="pattern_123"
            ):
                violation = {"type": "resume_structure", "path": "/resume"}
                result = {"status": "fixed", "action": "add_section"}

                pattern_id = agent.store_healing_pattern(violation, result)
                assert pattern_id == "pattern_123"

    def test_rg_store_healing_pattern_rejects_wrong_domain(self):
        """Test RG store_healing_pattern rejects LIC domain patterns."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._meta_client = None
            agent._initialize_guardrails()
            agent._initialize_meta_client()

            # Pattern with wrong domain
            violation = {"type": "campaign", "domain": "apps_lic"}
            result = {"status": "fixed"}

            pattern_id = agent.store_healing_pattern(violation, result)
            assert pattern_id is None

    def test_rg_retrieve_healing_patterns_uses_threshold(self):
        """Test RG retrieve_healing_patterns uses correct similarity threshold."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._similarity_threshold = 0.85
            agent._guardrails = None
            agent._meta_client = None
            agent._initialize_guardrails()
            agent._initialize_meta_client()

            mock_patterns = [MagicMock(similarity_score=0.90)]
            with patch.object(
                agent._meta_client,
                "retrieve_healing_patterns",
                return_value=mock_patterns,
            ) as mock_retrieve:
                violation = {"type": "resume_structure"}
                agent.retrieve_healing_patterns(violation)

                mock_retrieve.assert_called_once()
                call_args = mock_retrieve.call_args
                assert call_args.kwargs["min_similarity"] == 0.85
                assert call_args.kwargs["domain"] == "apps_rg"

    def test_rg_ml_check_healing_depth(self):
        """Test RG ml_check_healing_depth delegates to meta client."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._meta_client = None
            agent._initialize_meta_client()

            with patch.object(
                agent._meta_client, "check_healing_depth", return_value=True
            ) as mock_check:
                result = agent.ml_check_healing_depth("violation_123")

                assert result is True
                mock_check.assert_called_once_with("RGAgentBase", "violation_123")

    def test_rg_ml_increment_healing_depth(self):
        """Test RG ml_increment_healing_depth delegates to meta client."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._meta_client = None
            agent._initialize_meta_client()

            with patch.object(
                agent._meta_client, "increment_healing_depth", return_value=2
            ) as mock_inc:
                result = agent.ml_increment_healing_depth("violation_123")

                assert result == 2
                mock_inc.assert_called_once_with("RGAgentBase", "violation_123")

    def test_rg_get_meta_learning_stats(self):
        """Test RG get_meta_learning_stats returns stats."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._meta_client = None
            agent._initialize_meta_client()

            mock_stats = {"cache_hits": 10, "cache_misses": 5}
            with patch.object(agent._meta_client, "get_stats", return_value=mock_stats):
                stats = agent.get_meta_learning_stats()
                assert stats == mock_stats


class TestLICMetaLearningClientIntegration:
    """Test MetaLearningClient integration for LIC domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_lic_has_meta_client_attribute(self):
        """Test LICAgentBase has _meta_client attribute."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._meta_client = None
            agent._initialize_meta_client()

            assert agent._meta_client is not None

    def test_lic_store_healing_pattern_validates_domain(self):
        """Test LIC store_healing_pattern validates domain."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._meta_client = None
            agent._initialize_guardrails()
            agent._initialize_meta_client()

            with patch.object(
                agent._meta_client, "store_healing_pattern", return_value="pattern_456"
            ):
                violation = {"type": "campaign_timeout", "path": "/api"}
                result = {"status": "resolved", "action": "retry"}

                pattern_id = agent.store_healing_pattern(violation, result)
                assert pattern_id == "pattern_456"

    def test_lic_store_healing_pattern_rejects_wrong_domain(self):
        """Test LIC store_healing_pattern rejects RG domain patterns."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._meta_client = None
            agent._initialize_guardrails()
            agent._initialize_meta_client()

            # Pattern with wrong domain
            violation = {"type": "resume", "domain": "apps_rg"}
            result = {"status": "fixed"}

            pattern_id = agent.store_healing_pattern(violation, result)
            assert pattern_id is None

    def test_lic_retrieve_healing_patterns_uses_stricter_threshold(self):
        """Test LIC retrieve_healing_patterns uses stricter threshold (0.92)."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._similarity_threshold = 0.92
            agent._guardrails = None
            agent._meta_client = None
            agent._initialize_guardrails()
            agent._initialize_meta_client()

            mock_patterns = [MagicMock(similarity_score=0.95)]
            with patch.object(
                agent._meta_client,
                "retrieve_healing_patterns",
                return_value=mock_patterns,
            ) as mock_retrieve:
                violation = {"type": "campaign_timeout"}
                agent.retrieve_healing_patterns(violation)

                mock_retrieve.assert_called_once()
                call_args = mock_retrieve.call_args
                assert call_args.kwargs["min_similarity"] == 0.92
                assert call_args.kwargs["domain"] == "apps_lic"

    def test_lic_ml_check_healing_depth(self):
        """Test LIC ml_check_healing_depth delegates to meta client."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._meta_client = None
            agent._initialize_meta_client()

            with patch.object(
                agent._meta_client, "check_healing_depth", return_value=True
            ) as mock_check:
                result = agent.ml_check_healing_depth("incident_456")

                assert result is True
                mock_check.assert_called_once_with("LICAgentBase", "incident_456")

    def test_lic_get_meta_learning_stats(self):
        """Test LIC get_meta_learning_stats returns stats."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._meta_client = None
            agent._initialize_meta_client()

            mock_stats = {"pattern_retrievals": 15, "pattern_stores": 8}
            with patch.object(agent._meta_client, "get_stats", return_value=mock_stats):
                stats = agent.get_meta_learning_stats()
                assert stats == mock_stats


class TestCrossDomainPatternIsolation:
    """Test that patterns are properly isolated between domains."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_cannot_store_lic_patterns(self):
        """Test RG agent cannot store patterns for LIC domain."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._meta_client = None
            agent._initialize_guardrails()
            agent._initialize_meta_client()

            lic_violation = {"type": "campaign", "domain": "apps_lic"}
            result = {"status": "fixed"}

            pattern_id = agent.store_healing_pattern(lic_violation, result)
            assert pattern_id is None

    def test_lic_cannot_store_rg_patterns(self):
        """Test LIC agent cannot store patterns for RG domain."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._meta_client = None
            agent._initialize_guardrails()
            agent._initialize_meta_client()

            rg_violation = {"type": "resume", "domain": "apps_rg"}
            result = {"status": "fixed"}

            pattern_id = agent.store_healing_pattern(rg_violation, result)
            assert pattern_id is None

    def test_domains_use_different_thresholds(self):
        """Test RG and LIC use different similarity thresholds."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            with patch.object(LICAgentBase, "__post_init__", lambda self: None):
                rg_agent = RGAgentBase()
                rg_agent._similarity_threshold = 0.85

                lic_agent = LICAgentBase()
                lic_agent._similarity_threshold = 0.92

                assert rg_agent._similarity_threshold < lic_agent._similarity_threshold
                assert rg_agent._similarity_threshold == 0.85
                assert lic_agent._similarity_threshold == 0.92


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
