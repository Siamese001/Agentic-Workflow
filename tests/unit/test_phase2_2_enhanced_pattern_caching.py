"""
Phase 2.2 Test Suite: Enhanced Pattern Caching

Tests enhanced pattern caching with metadata, success tracking, and learning signals.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L1_cognition.meta_learning.guardrails import reset_guardrails


class TestRGEnhancedPatternCaching:
    """Test enhanced pattern caching for RG domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_cache_pattern_with_metadata_adds_metadata(self):
        """Test RG cache_pattern_with_metadata adds proper metadata."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._namespace = "apps_rg"
            agent._similarity_threshold = 0.85
            agent._guardrails = None
            agent._initialize_guardrails()

            with patch.object(agent, "ml_cache_set", return_value=True):
                result = agent.cache_pattern_with_metadata(
                    "resume_quality", "pattern_001", {"type": "test", "data": "value"}
                )
                assert result is True

    def test_rg_cache_pattern_respects_rate_limit(self):
        """Test RG cache_pattern_with_metadata respects rate limits."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._namespace = "apps_rg"
            agent._guardrails = None
            agent._initialize_guardrails()

            # Set low pattern rate limit
            agent._guardrails.guardrails.max_patterns_per_minute = 1

            with patch.object(agent, "ml_cache_set", return_value=True):
                # First should succeed
                agent.cache_pattern_with_metadata("type1", "id1", {"data": "test"})
                # Second should be rate limited
                result = agent.cache_pattern_with_metadata("type2", "id2", {"data": "test"})
                assert result is False

    def test_rg_retrieve_pattern_with_metadata(self):
        """Test RG retrieve_pattern_with_metadata works correctly."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._guardrails = None
            agent._initialize_guardrails()

            mock_pattern = {"type": "test", "_metadata": {"success_count": 5}}
            with patch.object(agent, "ml_cache_get", return_value=mock_pattern):
                result = agent.retrieve_pattern_with_metadata("resume_quality", "p1")
                assert result == mock_pattern


class TestLICEnhancedPatternCaching:
    """Test enhanced pattern caching for LIC domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        reset_guardrails()
        yield
        reset_guardrails()

    def test_lic_cache_pattern_with_metadata_adds_metadata(self):
        """Test LIC cache_pattern_with_metadata adds proper metadata."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"
            agent._namespace = "apps_lic"
            agent._similarity_threshold = 0.92
            agent._guardrails = None
            agent._initialize_guardrails()

            with patch.object(agent, "ml_cache_set", return_value=True):
                result = agent.cache_pattern_with_metadata(
                    "campaign", "campaign_001", {"type": "test", "data": "value"}
                )
                assert result is True

    def test_lic_cache_pattern_respects_rate_limit(self):
        """Test LIC cache_pattern_with_metadata respects rate limits."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"
            agent._namespace = "apps_lic"
            agent._guardrails = None
            agent._initialize_guardrails()

            # Set low pattern rate limit
            agent._guardrails.guardrails.max_patterns_per_minute = 1

            with patch.object(agent, "ml_cache_set", return_value=True):
                # First should succeed
                agent.cache_pattern_with_metadata("type1", "id1", {"data": "test"})
                # Second should be rate limited
                result = agent.cache_pattern_with_metadata("type2", "id2", {"data": "test"})
                assert result is False

    def test_lic_retrieve_pattern_with_metadata(self):
        """Test LIC retrieve_pattern_with_metadata works correctly."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"
            agent._guardrails = None
            agent._initialize_guardrails()

            mock_pattern = {"type": "test", "_metadata": {"success_count": 10}}
            with patch.object(agent, "ml_cache_get", return_value=mock_pattern):
                result = agent.retrieve_pattern_with_metadata("campaign", "c1")
                assert result == mock_pattern


class TestPatternSuccessTracking:
    """Test pattern success tracking for learning."""

    @pytest.fixture(autouse=True)
    def setup(self):
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_increment_pattern_success(self):
        """Test RG increment_pattern_success updates count."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._namespace = "apps_rg"
            agent._similarity_threshold = 0.85
            agent._guardrails = None
            agent._initialize_guardrails()

            existing_pattern = {"type": "test", "_metadata": {"success_count": 5}}

            with patch.object(
                agent, "retrieve_pattern_with_metadata", return_value=existing_pattern
            ):
                with patch.object(
                    agent, "cache_pattern_with_metadata", return_value=True
                ) as mock_cache:
                    result = agent.increment_pattern_success("resume_quality", "p1")
                    assert result is True
                    # Verify success_count was incremented to 6
                    call_args = mock_cache.call_args
                    assert call_args.args[3] == 6

    def test_lic_increment_pattern_success(self):
        """Test LIC increment_pattern_success updates count."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"
            agent._namespace = "apps_lic"
            agent._similarity_threshold = 0.92
            agent._guardrails = None
            agent._initialize_guardrails()

            existing_pattern = {"type": "test", "_metadata": {"success_count": 3}}

            with patch.object(
                agent, "retrieve_pattern_with_metadata", return_value=existing_pattern
            ):
                with patch.object(
                    agent, "cache_pattern_with_metadata", return_value=True
                ) as mock_cache:
                    result = agent.increment_pattern_success("campaign", "c1")
                    assert result is True
                    call_args = mock_cache.call_args
                    assert call_args.args[3] == 4

    def test_increment_returns_false_if_pattern_not_found(self):
        """Test increment_pattern_success returns False if pattern not found."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            with patch.object(agent, "retrieve_pattern_with_metadata", return_value=None):
                result = agent.increment_pattern_success("resume_quality", "nonexistent")
                assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
