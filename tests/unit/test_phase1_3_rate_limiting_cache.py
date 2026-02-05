"""
Phase 1.3 Test Suite: Rate Limiting and Cache Size Management

Tests rate limiting, cache capacity management, and safe cache operations
for RG and LIC domains.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L1_cognition.meta_learning.guardrails import reset_guardrails


class TestRGRateLimiting:
    """Test rate limiting for RG domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_rate_limit_allows_normal_operations(self):
        """Test RG allows operations under rate limit."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Should allow multiple operations under limit
            for i in range(50):
                assert agent.check_and_enforce_rate_limit("request"), (
                    f"Should allow request {i + 1}"
                )

    def test_rg_rate_limit_blocks_excessive_operations(self):
        """Test RG blocks operations when rate limit exceeded."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Set a very low limit for testing
            agent._guardrails.guardrails.max_requests_per_minute = 5

            # Should allow up to limit
            for i in range(5):
                assert agent.check_and_enforce_rate_limit("request")

            # Should block after limit
            assert not agent.check_and_enforce_rate_limit("request")

    def test_rg_pattern_rate_limit_separate_from_request(self):
        """Test RG pattern rate limit is separate from request limit."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Both should be allowed independently
            assert agent.check_and_enforce_rate_limit("request")
            assert agent.check_and_enforce_rate_limit("pattern")


class TestLICRateLimiting:
    """Test rate limiting for LIC domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_lic_rate_limit_allows_normal_operations(self):
        """Test LIC allows operations under rate limit."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Should allow multiple operations under limit
            for i in range(50):
                assert agent.check_and_enforce_rate_limit("request"), (
                    f"Should allow request {i + 1}"
                )

    def test_lic_rate_limit_blocks_excessive_operations(self):
        """Test LIC blocks operations when rate limit exceeded."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Set a very low limit for testing
            agent._guardrails.guardrails.max_requests_per_minute = 5

            # Should allow up to limit
            for i in range(5):
                assert agent.check_and_enforce_rate_limit("request")

            # Should block after limit
            assert not agent.check_and_enforce_rate_limit("request")


class TestRGCacheCapacity:
    """Test cache capacity management for RG domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_cache_capacity_allows_under_limit(self):
        """Test RG allows caching when under capacity."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            assert agent.check_cache_capacity()

    def test_rg_cache_capacity_blocks_at_limit(self):
        """Test RG blocks caching when at capacity."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Simulate cache at capacity
            agent._guardrails.guardrails._cache_sizes["apps_rg"] = 10000

            assert not agent.check_cache_capacity()

    def test_rg_cache_metrics_update(self):
        """Test RG cache metrics update correctly."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Update metrics
            agent.update_cache_metrics(5)
            assert agent._guardrails.guardrails._cache_sizes.get("apps_rg") == 5

            # Update more
            agent.update_cache_metrics(3)
            assert agent._guardrails.guardrails._cache_sizes.get("apps_rg") == 8

            # Decrement
            agent.update_cache_metrics(-2)
            assert agent._guardrails.guardrails._cache_sizes.get("apps_rg") == 6


class TestLICCacheCapacity:
    """Test cache capacity management for LIC domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_lic_cache_capacity_allows_under_limit(self):
        """Test LIC allows caching when under capacity."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            assert agent.check_cache_capacity()

    def test_lic_cache_capacity_blocks_at_limit(self):
        """Test LIC blocks caching when at capacity."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Simulate cache at capacity
            agent._guardrails.guardrails._cache_sizes["apps_lic"] = 10000

            assert not agent.check_cache_capacity()


class TestRGCacheHealth:
    """Test cache health monitoring for RG domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_cache_health_returns_correct_structure(self):
        """Test RG cache health returns expected structure."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            health = agent.get_cache_health()

            assert "domain" in health
            assert health["domain"] == "apps_rg"
            assert "cache_size" in health
            assert "request_rate" in health
            assert "pattern_rate" in health
            assert "active_healing_cycles" in health
            assert "healthy" in health
            assert health["healthy"] is True

    def test_rg_cache_health_reflects_activity(self):
        """Test RG cache health reflects cache activity."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Perform some operations
            agent.check_and_enforce_rate_limit("request")
            agent.check_and_enforce_rate_limit("request")
            agent.update_cache_metrics(10)

            health = agent.get_cache_health()

            assert health["cache_size"] == 10
            assert health["request_rate"] >= 2


class TestLICCacheHealth:
    """Test cache health monitoring for LIC domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_lic_cache_health_returns_correct_structure(self):
        """Test LIC cache health returns expected structure."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            health = agent.get_cache_health()

            assert "domain" in health
            assert health["domain"] == "apps_lic"
            assert "cache_size" in health
            assert "request_rate" in health
            assert "pattern_rate" in health
            assert "active_healing_cycles" in health
            assert "healthy" in health
            assert health["healthy"] is True


class TestSafeCacheOperations:
    """Test safe cache operations with full validation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_safe_cache_set_validates_all_checks(self):
        """Test RG safe_cache_set performs all validations."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._namespace = "apps_rg"
            agent._guardrails = None
            agent._initialize_guardrails()

            # Mock the ml_cache_set to return True
            with patch.object(agent, "ml_cache_set", return_value=True):
                result = agent.safe_cache_set("test_key", {"data": "test"})
                assert result is True

    def test_rg_safe_cache_set_blocks_rate_limited(self):
        """Test RG safe_cache_set blocks when rate limited."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._namespace = "apps_rg"
            agent._guardrails = None
            agent._initialize_guardrails()

            # Set low rate limit
            agent._guardrails.guardrails.max_requests_per_minute = 1

            # First should succeed
            with patch.object(agent, "ml_cache_set", return_value=True):
                agent.safe_cache_set("key1", {"data": "test"})

            # Second should be rate limited
            result = agent.safe_cache_set("key2", {"data": "test"})
            assert result is False

    def test_lic_safe_cache_set_validates_all_checks(self):
        """Test LIC safe_cache_set performs all validations."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"
            agent._namespace = "apps_lic"
            agent._guardrails = None
            agent._initialize_guardrails()

            # Mock the ml_cache_set to return True
            with patch.object(agent, "ml_cache_set", return_value=True):
                result = agent.safe_cache_set("test_key", {"data": "test"})
                assert result is True

    def test_safe_cache_get_respects_rate_limit(self):
        """Test safe_cache_get respects rate limits."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._namespace = "apps_rg"
            agent._guardrails = None
            agent._initialize_guardrails()

            # Set low rate limit
            agent._guardrails.guardrails.max_requests_per_minute = 1

            # First should succeed
            with patch.object(agent, "ml_cache_get", return_value={"data": "test"}):
                result = agent.safe_cache_get("test_key")
                assert result == {"data": "test"}

            # Second should be rate limited
            result = agent.safe_cache_get("test_key")
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
