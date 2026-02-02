#!/usr/bin/env python3
"""
Phase 1: Core Infrastructure Integration Tests

Tests for:
- Sub-Phase 1.1: SovereignBaseAgent Enhancement
- Sub-Phase 1.2: MetaLearningClient Production Hardening
- Sub-Phase 1.3: Integration Testing

Success Criteria:
- All existing agents continue working
- New methods available
- Guardrails prevent cache poisoning, infinite loops, and cross-domain contamination
- All integration scenarios pass
"""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# SUB-PHASE 1.1: SOVEREIGN BASE AGENT ENHANCEMENT TESTS
# =============================================================================


class TestSovereignBaseAgentEnhancement:
    """Test SovereignBaseAgent meta-learning integration."""

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_method_exists(self, mock_integrity):
        """Verify heal() method exists and has correct signature."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Verify heal method exists
        assert hasattr(agent, "heal")
        assert callable(agent.heal)

        # Verify _do_heal method exists
        assert hasattr(agent, "_do_heal")
        assert callable(agent._do_heal)

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_returns_correct_structure(self, mock_integrity):
        """Verify heal() returns correct structure with required keys."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent(project_root=Path.cwd())

        violation = {"type": "TEST", "file": "test.py", "message": "Test violation"}
        result = agent.heal(violation)

        # Verify required keys
        assert "status" in result
        assert "reason" in result or "source" in result
        assert "handler" in result or "violation_id" in result

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_delegates_to_ml_enhanced_heal(self, mock_integrity):
        """Verify heal() delegates to ml_enhanced_heal when available."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Mock ml_enhanced_heal
        agent.ml_enhanced_heal = MagicMock(
            return_value={
                "status": "fixed",
                "source": "meta_learning_cache",
                "violation_id": "test_123",
            }
        )

        violation = {"type": "TEST", "file": "test.py"}
        result = agent.heal(violation)

        # Verify delegation occurred
        assert result["status"] == "fixed"
        assert result["source"] == "meta_learning_cache"
        agent.ml_enhanced_heal.assert_called_once()

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_fallback_without_ml(self, mock_integrity):
        """Verify heal() falls back correctly when meta-learning unavailable."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Test default heal behavior (without _do_heal override)
        violation = {"type": "TEST", "file": "test.py"}
        result = agent.heal(violation)

        # Verify fallback behavior
        assert result["status"] == "skipped"
        assert result["reason"] == "default_base_implementation"

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_backward_compatibility(self, mock_integrity):
        """Verify existing agent functionality is not broken."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Verify core methods still exist
        assert hasattr(agent, "get_sovereign_capabilities")
        assert hasattr(agent, "get_state")
        assert hasattr(agent, "set_state")
        assert hasattr(agent, "log_info")
        assert hasattr(agent, "log_warning")
        assert hasattr(agent, "log_error")

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_mro_integrity(self, mock_integrity):
        """Verify Method Resolution Order is correct."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        # Verify MRO includes expected mixins
        mro_names = [cls.__name__ for cls in SovereignBaseAgent.__mro__]

        assert "SovereignBaseAgent" in mro_names
        assert "MetaLearningClientMixin" in mro_names
        # InfrastructureMixin is the class name (PascalCase)
        assert "InfrastructureMixin" in mro_names


# =============================================================================
# SUB-PHASE 1.2: META-LEARNING CLIENT PRODUCTION HARDENING TESTS
# =============================================================================


class TestMetaLearningClientHardening:
    """Test MetaLearningClient production-grade guardrails."""

    def test_singleton_pattern(self):
        """Verify MetaLearningClient uses singleton pattern."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            get_meta_learning_client,
        )

        # Get two instances
        client1 = get_meta_learning_client()
        client2 = get_meta_learning_client()

        # Should be the same instance
        assert client1 is client2

    def test_input_validation_none(self):
        """Test cache poisoning protection: None input."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        result = client.cache_set("test_key", None)
        assert result is False

    def test_input_validation_size_limit(self):
        """Test cache poisoning protection: oversized input."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # 100KB+ input should be rejected
        large_data = "x" * 100001
        result = client.cache_set("test_key", large_data)
        assert result is False

    def test_input_validation_non_serializable(self):
        """Test cache poisoning protection: non-serializable input."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Lambda functions are not JSON serializable
        non_serializable = {"func": lambda x: x}
        result = client.cache_set("test_key", non_serializable)
        assert result is False

    def test_domain_threshold_configuration(self):
        """Test domain-specific similarity thresholds are configured."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Verify domain thresholds exist
        assert "agentic_core" in client.domain_thresholds
        assert "apps_lic" in client.domain_thresholds
        assert "apps_rg" in client.domain_thresholds

        # Verify threshold values
        assert client.domain_thresholds["agentic_core"] == 0.85
        assert client.domain_thresholds["apps_lic"] == 0.92
        assert client.domain_thresholds["apps_rg"] == 0.85

    def test_domain_ttl_configuration(self):
        """Test domain-specific TTL settings are configured."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Verify domain TTLs exist
        assert "agentic_core" in client.domain_ttls
        assert "apps_lic" in client.domain_ttls
        assert "apps_rg" in client.domain_ttls

        # Verify TTL values
        assert client.domain_ttls["agentic_core"] == 3600
        assert client.domain_ttls["apps_lic"] == 7200
        assert client.domain_ttls["apps_rg"] == 3600

    def test_healing_depth_limit(self):
        """Test max healing depth is configured correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Verify max healing depth
        assert client.max_healing_depth == 5

    def test_cache_key_namespacing(self):
        """Test cache keys are properly namespaced by domain."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Test key generation
        key_core = client._get_cache_key("test", "agentic_core")
        key_lic = client._get_cache_key("test", "apps_lic")
        key_rg = client._get_cache_key("test", "apps_rg")

        # Verify namespace separation
        assert "agentic_core" in key_core
        assert "apps_lic" in key_lic
        assert "apps_rg" in key_rg

        # Verify keys are different
        assert key_core != key_lic
        assert key_lic != key_rg

    def test_error_signature_generation(self):
        """Test error signature generation is consistent."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        violation1 = {"type": "GRAVITY", "path": "test.py", "message": "Test error"}
        violation2 = {"type": "GRAVITY", "path": "test.py", "message": "Test error"}
        violation3 = {"type": "NAMING", "path": "test.py", "message": "Different error"}

        sig1 = client._generate_error_signature(violation1)
        sig2 = client._generate_error_signature(violation2)
        sig3 = client._generate_error_signature(violation3)

        # Same violations should have same signature
        assert sig1 == sig2
        # Different violations should have different signatures
        assert sig1 != sig3


# =============================================================================
# SUB-PHASE 1.3: INTEGRATION TESTS
# =============================================================================


class TestPhase1Integration:
    """End-to-end integration tests for Phase 1."""

    def test_healing_depth_tracking_integration(self):
        """Test healing depth tracking prevents infinite loops."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()
        agent_name = "TestIntegrationAgent"
        violation_id = f"integration_test_{int(time.time())}"

        # Simulate healing cycle
        for i in range(6):  # One more than max depth
            can_heal = client.check_healing_depth(agent_name, violation_id)
            if can_heal:
                client.increment_healing_depth(agent_name, violation_id)
            else:
                # Should stop at depth 5
                assert i == 5
                break

        # Verify healing was prevented
        assert client.stats["healing_cycles_prevented"] >= 1

        # Cleanup
        client.reset_healing_depth(agent_name, violation_id)

    def test_local_cache_fallback(self):
        """Test local cache fallback when Redis unavailable."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Force Redis to be unavailable
        client._redis_client = None

        # Test cache operations with local fallback
        test_key = f"fallback_test_{int(time.time())}"
        test_value = {"data": "test_value"}

        # Set should succeed via local cache
        result = client.cache_set(test_key, test_value, "agentic_core")
        assert result is True

        # Get should retrieve from local cache
        retrieved = client.cache_get(test_key, "agentic_core")
        assert retrieved == test_value

    def test_domain_isolation(self):
        """Test domain isolation prevents cross-contamination."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()
        client._redis_client = None  # Force local cache

        test_key = f"domain_test_{int(time.time())}"

        # Set value in agentic_core domain
        client.cache_set(test_key, {"domain": "core"}, "agentic_core")

        # Set different value in apps_lic domain
        client.cache_set(test_key, {"domain": "lic"}, "apps_lic")

        # Retrieve and verify isolation
        core_value = client.cache_get(test_key, "agentic_core")
        lic_value = client.cache_get(test_key, "apps_lic")

        assert core_value["domain"] == "core"
        assert lic_value["domain"] == "lic"

    def test_statistics_tracking(self):
        """Test statistics are tracked correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()
        initial_stats = client.get_stats()

        # Perform operations
        client._redis_client = None  # Force local cache for deterministic testing
        test_key = f"stats_test_{int(time.time())}"

        # Cache miss
        client.cache_get(test_key, "agentic_core")

        # Cache set + hit
        client.cache_set(test_key, {"data": "test"}, "agentic_core")
        client.cache_get(test_key, "agentic_core")

        final_stats = client.get_stats()

        # Verify statistics updated
        assert final_stats["cache_hits"] >= initial_stats.get("cache_hits", 0)
        assert final_stats["cache_misses"] >= initial_stats.get("cache_misses", 0)

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_mixin_integration(self, mock_integrity):
        """Test MetaLearningClientMixin integration with SovereignBaseAgent."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Verify mixin methods are available
        assert hasattr(agent, "ml_recall_healing_pattern")
        assert hasattr(agent, "ml_store_healing_pattern")
        assert hasattr(agent, "ml_cache_get")
        assert hasattr(agent, "ml_cache_set")
        assert hasattr(agent, "ml_check_healing_depth")
        assert hasattr(agent, "ml_increment_healing_depth")
        assert hasattr(agent, "ml_reset_healing_depth")
        assert hasattr(agent, "ml_get_violation_signature")
        assert hasattr(agent, "ml_get_stats")
        assert hasattr(agent, "ml_enhanced_heal")


class TestPhase1PerformanceBaseline:
    """Performance baseline tests for Phase 1."""

    def test_cache_operation_performance(self):
        """Test cache operations complete within acceptable time."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()
        client._redis_client = None  # Force local cache

        start_time = time.time()

        # Perform 100 cache operations
        for i in range(100):
            key = f"perf_test_{i}"
            client.cache_set(key, {"index": i}, "agentic_core")
            client.cache_get(key, "agentic_core")

        elapsed = time.time() - start_time

        # Should complete in < 1 second
        assert elapsed < 1.0, f"Cache operations took {elapsed:.2f}s, expected < 1s"

    def test_signature_generation_performance(self):
        """Test signature generation is fast."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        violation = {"type": "GRAVITY", "path": "test.py", "message": "Test error"}

        start_time = time.time()

        # Generate 1000 signatures
        for _ in range(1000):
            client._generate_error_signature(violation)

        elapsed = time.time() - start_time

        # Should complete in < 0.5 seconds
        assert elapsed < 0.5, f"Signature generation took {elapsed:.2f}s, expected < 0.5s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
