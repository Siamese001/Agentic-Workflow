"""
Phase 5: Production Readiness & Monitoring Tests

Tests production readiness and monitoring capabilities:
- Load testing and stress testing
- Graceful degradation on failures
- Metrics dashboard data collection
- Alerting configuration
- Performance benchmarks

All tests use mocked dependencies to avoid external services.
"""

from __future__ import annotations

import time
import pytest
from unittest.mock import MagicMock, patch


# ==================== TEST 5.1: Load Testing ====================

class TestLoadTesting:
    """Test cache performance under load."""

    def test_high_volume_cache_operations(self):
        """Test cache handles high volume operations."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Simulate high volume
        start_time = time.time()
        
        for i in range(500):
            client.cache_set(f"load_test_key_{i}", {"index": i, "data": "x" * 100}, "agentic_core")
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0
        
        # Verify random access works
        result = client.cache_get("load_test_key_250", "agentic_core")
        assert result["index"] == 250

    def test_concurrent_domain_operations(self):
        """Test concurrent operations across domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        domains = ["agentic_core", "apps_lic", "apps_rg"]
        
        # Store in all domains
        for domain in domains:
            for i in range(100):
                client.cache_set(f"concurrent_key_{i}", {"domain": domain, "i": i}, domain)
        
        # Verify isolation
        for domain in domains:
            result = client.cache_get("concurrent_key_50", domain)
            assert result["domain"] == domain

    def test_rate_limit_under_load(self):
        """Test rate limiting remains effective under load."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Normal traffic should pass
        passed = 0
        for i in range(100):
            if guardrails.check_rate_limit("load_test_domain", "request"):
                passed += 1
        
        assert passed == 100  # All should pass under limit


# ==================== TEST 5.2: Stress Testing ====================

class TestStressTesting:
    """Test system behavior under stress."""

    def test_graceful_degradation_on_cache_full(self):
        """Test graceful degradation when cache is full."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails, CacheGuardrails
        
        # Create guardrails with small cache limit
        config = CacheGuardrails(max_cache_entries=10)
        guardrails = MetaLearningGuardrails(config)
        
        # Fill cache to limit
        for i in range(10):
            guardrails.update_cache_size("stress_domain", 1)
        
        # Should reject new entries
        can_add = guardrails.check_cache_size_limit("stress_domain")
        assert can_add is False

    def test_healing_depth_limit_enforcement(self):
        """Test healing depth limit is strictly enforced."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Hit depth limit
        for i in range(5):
            guardrails.increment_healing_depth("StressAgent", "stress_violation")
        
        # Should be blocked
        assert guardrails.check_healing_depth("StressAgent", "stress_violation") is False
        
        # Different violation should still work
        assert guardrails.check_healing_depth("StressAgent", "other_violation") is True

    def test_ttl_expiration_under_load(self):
        """Test TTL expiration works correctly under load."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Store many items with short TTL
        for i in range(50):
            client.cache_set(f"ttl_stress_{i}", {"data": i}, "agentic_core", ttl=1)
        
        # Should exist immediately
        assert client.cache_get("ttl_stress_25", "agentic_core") is not None
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should be expired
        assert client.cache_get("ttl_stress_25", "agentic_core") is None


# ==================== TEST 5.3: Metrics Dashboard ====================

class TestMetricsDashboard:
    """Test metrics collection for dashboard."""

    def test_cache_stats_collection(self):
        """Test cache statistics are collected."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Generate operations
        client.cache_set("stats_test", {"data": "value"}, "agentic_core")
        client.cache_get("stats_test", "agentic_core")  # Hit
        client.cache_get("nonexistent", "agentic_core")  # Miss
        
        # Verify stats
        assert "cache_hits" in client.stats
        assert "cache_misses" in client.stats
        assert client.stats["cache_hits"] >= 1
        assert client.stats["cache_misses"] >= 1

    def test_guardrails_stats_collection(self):
        """Test guardrails statistics are collected."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Generate some operations
        guardrails.check_rate_limit("metrics_domain", "request")
        guardrails.increment_healing_depth("MetricsAgent", "v1")
        guardrails.update_cache_size("metrics_domain", 1)
        
        stats = guardrails.get_stats()
        
        assert "cache_sizes" in stats
        assert "request_rates" in stats
        assert "depth_trackers" in stats

    def test_domain_specific_metrics(self):
        """Test domain-specific metrics are tracked."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Operations in different domains
        client.cache_set("domain_metric_1", {"d": "core"}, "agentic_core")
        client.cache_set("domain_metric_2", {"d": "lic"}, "apps_lic")
        client.cache_set("domain_metric_3", {"d": "rg"}, "apps_rg")
        
        # Verify domain isolation maintained
        assert client.cache_get("domain_metric_1", "agentic_core")["d"] == "core"
        assert client.cache_get("domain_metric_2", "apps_lic")["d"] == "lic"
        assert client.cache_get("domain_metric_3", "apps_rg")["d"] == "rg"

    def test_performance_metrics_tracking(self):
        """Test performance metrics are tracked."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Track performance
        start = time.time()
        
        for i in range(100):
            client.cache_set(f"perf_metric_{i}", {"i": i}, "agentic_core")
        
        write_time = time.time() - start
        
        start = time.time()
        
        for i in range(100):
            client.cache_get(f"perf_metric_{i}", "agentic_core")
        
        read_time = time.time() - start
        
        # Both operations should be fast
        assert write_time < 2.0
        assert read_time < 1.0


# ==================== TEST 5.4: Alerting Configuration ====================

class TestAlertingConfiguration:
    """Test alerting thresholds and triggers."""

    def test_rate_limit_breach_detection(self):
        """Test rate limit breach is detected."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails, CacheGuardrails
        
        # Create with low limit for testing
        config = CacheGuardrails(max_requests_per_minute=10)
        guardrails = MetaLearningGuardrails(config)
        
        # Exceed rate limit
        breached = False
        for i in range(15):
            if not guardrails.check_rate_limit("alert_domain", "request"):
                breached = True
                break
        
        assert breached is True

    def test_cache_size_threshold_alert(self):
        """Test cache size threshold triggers alert."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails, CacheGuardrails
        
        config = CacheGuardrails(max_cache_entries=5)
        guardrails = MetaLearningGuardrails(config)
        
        # Fill to threshold
        for i in range(5):
            guardrails.update_cache_size("alert_cache_domain", 1)
        
        # Should trigger alert condition
        at_limit = not guardrails.check_cache_size_limit("alert_cache_domain")
        assert at_limit is True

    def test_healing_depth_alert(self):
        """Test healing depth alert threshold."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Track depths approaching limit
        for i in range(4):
            guardrails.increment_healing_depth("AlertAgent", "deep_violation")
        
        # Still allowed (4 < 5)
        assert guardrails.check_healing_depth("AlertAgent", "deep_violation") is True
        
        # One more increment
        guardrails.increment_healing_depth("AlertAgent", "deep_violation")
        
        # Now at limit (5 = 5)
        assert guardrails.check_healing_depth("AlertAgent", "deep_violation") is False


# ==================== TEST 5.5: Service Health ====================

class TestServiceHealth:
    """Test service health monitoring."""

    def test_client_initialization_health(self):
        """Test client initializes in healthy state."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        client = MetaLearningClient()
        
        # Should initialize successfully
        assert client is not None
        assert hasattr(client, 'stats')
        assert hasattr(client, '_local_cache')

    def test_guardrails_initialization_health(self):
        """Test guardrails initializes in healthy state."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Should initialize successfully
        assert guardrails is not None
        assert hasattr(guardrails, 'guardrails')
        
        # Should have valid defaults
        assert guardrails.guardrails.max_cache_entries == 10000
        assert guardrails.guardrails.default_ttl == 3600

    def test_recovery_from_invalid_data(self):
        """Test system recovers from invalid data gracefully."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        guardrails = MetaLearningGuardrails()
        
        # Invalid cache key should fail gracefully
        assert guardrails.validate_cache_key("") is False
        assert guardrails.validate_cache_key(None) is False
        assert guardrails.validate_cache_key("../../../etc/passwd") is False
        
        # Invalid TTL should return default
        assert guardrails.validate_ttl(-1) == 3600
        assert guardrails.validate_ttl("invalid") == 3600

    def test_singleton_pattern_health(self):
        """Test singleton pattern maintains consistency."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import get_meta_learning_client
        
        # Get client twice
        client1 = get_meta_learning_client()
        client2 = get_meta_learning_client()
        
        # Should be same instance
        assert client1 is client2
        
        # Operations on one affect the other
        client1.cache_set("singleton_test", {"data": "value"}, "agentic_core")
        result = client2.cache_get("singleton_test", "agentic_core")
        assert result is not None


# ==================== TEST 5.6: Documentation Validation ====================

class TestDocumentationValidation:
    """Test documentation and API consistency."""

    def test_mixin_public_methods_documented(self):
        """Test MetaLearningClientMixin public methods exist."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin
        
        required_methods = [
            "ml_recall_healing_pattern",
            "ml_store_healing_pattern",
            "ml_cache_get",
            "ml_cache_set",
            "ml_cache_delete",
            "ml_check_healing_depth",
            "ml_increment_healing_depth",
            "ml_reset_healing_depth",
            "ml_get_violation_signature",
            "ml_enhanced_heal",
            "ml_get_stats",
        ]
        
        for method in required_methods:
            assert hasattr(MetaLearningClientMixin, method), f"Missing: {method}"

    def test_guardrails_public_methods_documented(self):
        """Test MetaLearningGuardrails public methods exist."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails
        
        required_methods = [
            "validate_cache_key",
            "validate_cache_value",
            "validate_ttl",
            "check_cache_size_limit",
            "check_rate_limit",
            "validate_similarity_threshold",
            "check_healing_depth",
            "increment_healing_depth",
            "reset_healing_depth",
            "validate_domain_isolation",
            "sanitize_violation_data",
            "get_stats",
        ]
        
        guardrails = MetaLearningGuardrails()
        
        for method in required_methods:
            assert hasattr(guardrails, method), f"Missing: {method}"

    def test_client_public_methods_documented(self):
        """Test MetaLearningClient public methods exist."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        
        required_methods = [
            "cache_get",
            "cache_set",
            "cache_delete",
        ]
        
        client = MetaLearningClient()
        
        for method in required_methods:
            assert hasattr(client, method), f"Missing: {method}"


# ==================== RUN CONFIGURATION ====================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",
    ])
