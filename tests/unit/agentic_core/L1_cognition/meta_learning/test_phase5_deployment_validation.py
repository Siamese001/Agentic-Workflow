#!/usr/bin/env python3
"""
Phase 5: Production Deployment Validation Tests

Tests for:
- Sub-Phase 5.1: Staging Environment Validation
- Sub-Phase 5.2: Production Rollout Readiness
- Sub-Phase 5.3: Post-Deployment Optimization

Success Criteria:
- All tests pass in production-like environment
- Rollback procedures verified
- Performance targets met
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Mock problematic imports
sys.modules["agentic_core.L5_safety.validators.PascalSovereigntyAgent"] = MagicMock()


# =============================================================================
# SUB-PHASE 5.1: STAGING ENVIRONMENT VALIDATION TESTS
# =============================================================================


class TestStagingEnvironmentValidation:
    """Test staging environment readiness."""

    def test_meta_learning_client_initialization(self):
        """Test MetaLearningClient initializes correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            get_meta_learning_client,
        )

        client = get_meta_learning_client()
        assert client is not None
        assert hasattr(client, "cache_get")
        assert hasattr(client, "cache_set")
        assert hasattr(client, "retrieve_healing_patterns")
        assert hasattr(client, "store_healing_pattern")

    def test_singleton_reset_for_testing(self):
        """Test singleton can be reset for testing."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        # Verify reset method exists
        assert hasattr(MetaLearningClient, "reset_instance")

    def test_mixin_reset_for_testing(self):
        """Test mixin singletons can be reset for testing."""
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        # Verify reset method exists
        assert hasattr(MetaLearningClientMixin, "reset_ml_singletons")

    def test_fallback_mechanisms_work(self):
        """Test fallback mechanisms work when Redis/Pinecone unavailable."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        # Force fallback mode
        client._redis_client = None
        client._pinecone_index = None

        # Operations should still work via local cache
        result = client.cache_set("fallback_test", {"data": "test"}, "agentic_core")
        assert result is True

        value = client.cache_get("fallback_test", "agentic_core")
        assert value == {"data": "test"}

        # Pattern retrieval should return empty (graceful degradation)
        patterns = client.retrieve_healing_patterns({"type": "TEST"})
        assert patterns == []


# =============================================================================
# SUB-PHASE 5.2: PRODUCTION ROLLOUT READINESS TESTS
# =============================================================================


class TestProductionRolloutReadiness:
    """Test production rollout readiness."""

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_sovereign_base_agent_production_ready(self, mock_integrity):
        """Test SovereignBaseAgent is production ready."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Verify core capabilities
        capabilities = agent.get_sovereign_capabilities()

        assert capabilities["meta_learning"] is True
        assert capabilities["security_validated"] is True
        assert capabilities["mro_hardened"] is True

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_method_production_safe(self, mock_integrity):
        """Test heal method is production safe."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Test with various violation types
        test_violations = [
            {"type": "GRAVITY", "file": "test.py"},
            {"type": "NAMING", "file": "test.py"},
            {"type": "STRUCTURE", "file": "test.py"},
            {"type": "UNKNOWN", "file": "test.py"},
            {},  # Empty violation
        ]

        for violation in test_violations:
            # Should not raise exceptions
            result = agent.heal(violation)
            assert isinstance(result, dict)
            assert "status" in result

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        # Test with invalid inputs - should not raise
        result = client.cache_set("", None)  # Empty key, None value
        assert result is False

        result = client.cache_get("nonexistent_key", "agentic_core")
        assert result is None

        # Test healing depth with edge cases
        can_heal = client.check_healing_depth("", "")  # Empty strings
        assert isinstance(can_heal, bool)


# =============================================================================
# SUB-PHASE 5.3: POST-DEPLOYMENT OPTIMIZATION TESTS
# =============================================================================


class TestPostDeploymentOptimization:
    """Test post-deployment optimization capabilities."""

    def test_cache_clear_functionality(self):
        """Test cache can be cleared for optimization."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None

        # Fill cache
        for i in range(50):
            client.cache_set(f"opt_test_{i}", {"data": i}, "agentic_core")

        # Clear and verify
        cleared = client.clear_local_cache()
        assert cleared >= 50
        assert len(client._local_cache) == 0

    def test_stats_provide_optimization_insights(self):
        """Test stats provide useful optimization insights."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        stats = client.get_stats()

        # Stats should include optimization-relevant metrics
        assert "cache_hit_ratio" in stats
        assert "local_cache_size" in stats
        assert "active_healing_cycles" in stats
        assert "by_domain" in stats

    def test_domain_threshold_configurability(self):
        """Test domain thresholds can be configured."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        # Verify thresholds are configurable
        assert hasattr(client, "domain_thresholds")
        assert hasattr(client, "domain_ttls")

        # Verify current values
        assert client.domain_thresholds["agentic_core"] == 0.85
        assert client.domain_thresholds["apps_lic"] == 0.92
        assert client.domain_ttls["agentic_core"] == 3600
        assert client.domain_ttls["apps_lic"] == 7200


class TestPhase5Integration:
    """Phase 5 integration tests."""

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_end_to_end_healing_cycle(self, mock_integrity):
        """Test end-to-end healing cycle in production-like environment."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        # Setup
        client = MetaLearningClient()
        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Simulate healing cycle
        violation = {"type": "GRAVITY", "file": "test.py", "message": "Test violation"}

        # 1. Check healing depth
        violation_id = client._generate_error_signature(violation)
        can_heal = client.check_healing_depth(agent.__class__.__name__, violation_id)
        assert can_heal is True

        # 2. Increment depth
        depth = client.increment_healing_depth(agent.__class__.__name__, violation_id)
        assert depth == 1

        # 3. Perform heal
        result = agent.heal(violation)
        assert isinstance(result, dict)

        # 4. Reset depth
        client.reset_healing_depth(agent.__class__.__name__, violation_id)

        # Verify reset worked
        can_heal = client.check_healing_depth(agent.__class__.__name__, violation_id)
        assert can_heal is True

    def test_rollback_procedure(self):
        """Test rollback procedure works."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.base_agents.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )

        # Simulate rollback by resetting singletons
        MetaLearningClient.reset_instance()
        MetaLearningClientMixin.reset_ml_singletons()

        # Verify new instance can be created
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            get_meta_learning_client,
        )

        client = get_meta_learning_client()
        assert client is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
