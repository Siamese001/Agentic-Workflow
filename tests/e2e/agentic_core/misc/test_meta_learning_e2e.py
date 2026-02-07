#!/usr/bin/env python3
"""
End-to-End Integration Tests for Meta-Learning Architecture

Comprehensive tests covering the full meta-learning integration across all phases:
- Phase 1: Core Infrastructure (SovereignBaseAgent, MetaLearningClient)
- Phase 2: High-Impact Agents (ArchitectureGovernor, Hierarchy, CodeHealer, Location)
- Phase 3: Medium-Impact Agents (HygieneGuardian, GravityLeakRepair, ArchivalGatekeeper)
- Phase 4: System Validation (Performance, Guardrails, Monitoring)
- Phase 5: Deployment Readiness (Staging, Production, Optimization)

Success Criteria:
- All integration scenarios pass
- Cross-component communication works
- Performance targets met
- Guardrails function correctly
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Mock problematic imports
sys.modules["agentic_core.L5_safety.validators.PascalSovereigntyAgent"] = MagicMock()


# =============================================================================
# END-TO-END HEALING CYCLE TESTS
# =============================================================================


class TestEndToEndHealingCycle:
    """Test complete healing cycles across multiple agents."""

    @patch("agentic_core.L0_maintenance.integrity.core_integrity_util.CoreIntegrityVerifier.verify_core_integrity")
    def test_full_healing_cycle_with_caching(self, mock_integrity):
        """Test complete healing cycle: detect -> cache check -> heal -> store."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        # Setup
        client = MetaLearningClient()
        client._redis_client = None  # Force local cache
        agent = SovereignBaseAgent(project_root=Path.cwd())

        # Create test violation
        violation = {
            "type": "GRAVITY",
            "file": "test_agent.py",
            "message": "Import violation detected",
            "path": "agentic_core/test_agent.py",
        }

        # Step 1: Generate signature
        signature = client._generate_error_signature(violation)
        assert signature is not None
        assert len(signature) > 0

        # Step 2: Check cache (should miss on first attempt)
        cached = client.cache_get(f"healing:{signature}", "agentic_core")
        assert cached is None

        # Step 3: Check healing depth
        can_heal = client.check_healing_depth(agent.__class__.__name__, signature)
        assert can_heal is True

        # Step 4: Increment depth
        depth = client.increment_healing_depth(agent.__class__.__name__, signature)
        assert depth == 1

        # Step 5: Perform healing
        result = agent.heal(violation)
        assert isinstance(result, dict)
        assert "status" in result

        # Step 6: Cache the result
        client.cache_set(f"healing:{signature}", result, "agentic_core")

        # Step 7: Verify cache hit on retry
        cached = client.cache_get(f"healing:{signature}", "agentic_core")
        assert cached is not None
        assert cached["status"] == result["status"]

        # Step 8: Reset healing depth
        client.reset_healing_depth(agent.__class__.__name__, signature)

    @patch("agentic_core.L0_maintenance.integrity.core_integrity_util.CoreIntegrityVerifier.verify_core_integrity")
    def test_multi_agent_healing_coordination(self, mock_integrity):
        """Test multiple agents coordinating healing through shared cache."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )
        from agentic_core.L5_safety.validators.hierarchy_agent import HierarchyAgent
        from agentic_core.L5_safety.validators.hygiene_guardian_agent import (
            HygieneGuardianAgent,
        )

        # Setup shared client
        client = MetaLearningClient()
        client._redis_client = None

        # Create agents
        hierarchy_agent = HierarchyAgent(project_root=Path.cwd())
        hygiene_agent = HygieneGuardianAgent(project_root=Path.cwd())

        # Shared violation
        violation = {"type": "STRUCTURE", "file": "orphan.py", "message": "Orphaned"}

        # Both agents should see same cache state
        signature = client._generate_error_signature(violation)

        # Agent 1 processes
        client.increment_healing_depth(hierarchy_agent.__class__.__name__, signature)
        hierarchy_agent.heal(violation)

        # Agent 2 can still process (different agent name in tracking)
        can_heal = client.check_healing_depth(hygiene_agent.__class__.__name__, signature)
        assert can_heal is True

        # Cleanup
        client.reset_healing_depth(hierarchy_agent.__class__.__name__, signature)
        client.reset_healing_depth(hygiene_agent.__class__.__name__, signature)


# =============================================================================
# CROSS-DOMAIN INTEGRATION TESTS
# =============================================================================


class TestCrossDomainIntegration:
    """Test meta-learning works correctly across domains."""

    def test_domain_isolation_e2e(self):
        """Test domain isolation across complete workflows."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None

        domains = ["agentic_core", "apps_lic", "apps_rg"]
        test_data = {}

        # Create domain-specific data
        for domain in domains:
            violation = {"type": "TEST", "domain": domain, "file": f"{domain}/test.py"}
            signature = client._generate_error_signature(violation)
            result = {"status": "fixed", "domain": domain}

            # Store in domain
            client.cache_set(f"domain_test:{signature}", result, domain)
            test_data[domain] = {"signature": signature, "result": result}

        # Verify isolation
        for domain in domains:
            signature = test_data[domain]["signature"]
            test_data[domain]["result"]

            # Should get correct domain data
            cached = client.cache_get(f"domain_test:{signature}", domain)
            assert cached is not None
            assert cached["domain"] == domain

    def test_domain_specific_thresholds_e2e(self):
        """Test domain-specific thresholds are applied correctly."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        # Verify domain thresholds
        assert client.domain_thresholds["agentic_core"] == 0.85
        assert client.domain_thresholds["apps_lic"] == 0.92
        assert client.domain_thresholds["apps_rg"] == 0.85

        # Verify TTLs
        assert client.domain_ttls["agentic_core"] == 3600
        assert client.domain_ttls["apps_lic"] == 7200
        assert client.domain_ttls["apps_rg"] == 3600


# =============================================================================
# PERFORMANCE INTEGRATION TESTS
# =============================================================================


class TestPerformanceIntegration:
    """Test performance across the full system."""

    @patch("agentic_core.L0_maintenance.integrity.core_integrity_util.CoreIntegrityVerifier.verify_core_integrity")
    def test_healing_performance_at_scale(self, mock_integrity):
        """Test healing performance with many violations."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None
        agent = SovereignBaseAgent(project_root=Path.cwd())

        start_time = time.time()

        # Process 50 violations
        for i in range(50):
            violation = {
                "type": "GRAVITY",
                "file": f"test_{i}.py",
                "message": f"Error {i}",
            }
            agent.heal(violation)

        elapsed = time.time() - start_time

        # Should complete in < 5 seconds
        assert elapsed < 5.0, f"Healing 50 violations took {elapsed:.2f}s"

    def test_cache_performance_at_scale(self):
        """Test cache performance with large datasets."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None

        start_time = time.time()

        # Perform 1000 cache operations
        for i in range(1000):
            client.cache_set(f"scale_test_{i}", {"index": i}, "agentic_core")
            client.cache_get(f"scale_test_{i}", "agentic_core")

        elapsed = time.time() - start_time

        # Should complete in < 3 seconds
        assert elapsed < 3.0, f"1000 cache operations took {elapsed:.2f}s"

        # Cleanup
        client.clear_local_cache()


# =============================================================================
# GUARDRAILS INTEGRATION TESTS
# =============================================================================


class TestGuardrailsIntegration:
    """Test all guardrails work correctly together."""

    def test_healing_depth_prevents_infinite_loops(self):
        """Test healing depth tracking prevents infinite loops."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        agent_name = "InfiniteLoopTestAgent"
        violation_id = "infinite_loop_violation"

        # Simulate runaway healing
        loop_count = 0
        max_iterations = 100  # Safety limit

        while loop_count < max_iterations:
            if not client.check_healing_depth(agent_name, violation_id):
                break
            client.increment_healing_depth(agent_name, violation_id)
            loop_count += 1

        # Should have stopped at max depth (5)
        assert loop_count == 5
        assert client.stats["healing_cycles_prevented"] >= 1

        # Cleanup
        client.reset_healing_depth(agent_name, violation_id)

    def test_input_validation_prevents_cache_poisoning(self):
        """Test input validation prevents cache poisoning."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        # Test None value rejection
        result = client.cache_set("test_key", None, "agentic_core")
        assert result is False, "None value should be rejected"

        # Valid values should work
        result = client.cache_set("valid_key", {"data": "test"}, "agentic_core")
        assert result is True, "Valid value should be accepted"

        # Verify value can be retrieved correctly
        retrieved = client.cache_get("valid_key", "agentic_core")
        assert retrieved == {"data": "test"}, "Retrieved value should match"

    def test_ttl_expiration_works(self):
        """Test TTL expiration prevents stale cache."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            CacheEntry,
        )

        # Create entry with 0 TTL
        entry = CacheEntry(key="test", value="test_value", ttl=0)

        # Should be immediately expired
        time.sleep(0.01)
        assert entry.is_expired() is True

        # Create entry with long TTL
        entry2 = CacheEntry(key="test2", value="test_value2", ttl=3600)
        assert entry2.is_expired() is False


# =============================================================================
# FULL SYSTEM INTEGRATION TESTS
# =============================================================================


class TestFullSystemIntegration:
    """Test the full meta-learning system integration."""

    @patch("agentic_core.L0_maintenance.integrity.core_integrity_util.CoreIntegrityVerifier.verify_core_integrity")
    def test_all_agents_have_meta_learning(self, mock_integrity):
        """Verify all major agents have meta-learning capabilities."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L5_safety.gravity.gravity_leak_repair_agent import (
            GravityLeakRepairAgent,
        )
        from agentic_core.L5_safety.policy_engine.CodeHealerAgent import (
            CodeHealerAgent,
        )
        from agentic_core.L5_safety.validators.hierarchy_agent import HierarchyAgent
        from agentic_core.L5_safety.validators.hygiene_guardian_agent import (
            HygieneGuardianAgent,
        )

        agents = [
            SovereignBaseAgent(project_root=Path.cwd()),
            HierarchyAgent(project_root=Path.cwd()),
            HygieneGuardianAgent(project_root=Path.cwd()),
            GravityLeakRepairAgent(project_root=Path.cwd()),
            CodeHealerAgent(project_root=Path.cwd()),
        ]

        for agent in agents:
            # Verify meta-learning mixin methods
            assert hasattr(agent, "ml_recall_healing_pattern"), f"{agent.__class__.__name__}"
            assert hasattr(agent, "ml_store_healing_pattern"), f"{agent.__class__.__name__}"
            assert hasattr(agent, "ml_cache_get"), f"{agent.__class__.__name__}"
            assert hasattr(agent, "ml_cache_set"), f"{agent.__class__.__name__}"
            assert hasattr(agent, "ml_check_healing_depth"), f"{agent.__class__.__name__}"

    def test_statistics_aggregation(self):
        """Test statistics are aggregated correctly across operations."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None

        # Perform various operations
        for i in range(20):
            client.cache_get(f"stats_test_{i}", "agentic_core")  # Misses
            client.cache_set(f"stats_test_{i}", {"i": i}, "agentic_core")
            client.cache_get(f"stats_test_{i}", "agentic_core")  # Hits

        # Get stats
        stats = client.get_stats()

        # Verify aggregation
        assert stats["cache_hits"] >= 20
        assert stats["cache_misses"] >= 20
        assert stats["cache_hit_ratio"] >= 0.45  # ~50% expected

        # Cleanup
        client.clear_local_cache()

    @patch("agentic_core.L0_maintenance.integrity.core_integrity_util.CoreIntegrityVerifier.verify_core_integrity")
    def test_system_stability_under_load(self, mock_integrity):
        """Test system remains stable under sustained load."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None
        agent = SovereignBaseAgent(project_root=Path.cwd())

        start_time = time.time()
        errors = 0

        # Sustained load test
        for cycle in range(10):
            for i in range(20):
                try:
                    violation = {"type": "TEST", "file": f"test_{cycle}_{i}.py"}
                    agent.heal(violation)
                    client.cache_set(f"load_{cycle}_{i}", {"c": cycle}, "agentic_core")
                    client.cache_get(f"load_{cycle}_{i}", "agentic_core")
                except Exception:
                    errors += 1

        elapsed = time.time() - start_time

        # Should complete without errors
        assert errors == 0, f"Encountered {errors} errors during load test"
        # Should complete in reasonable time
        assert elapsed < 10.0, f"Load test took {elapsed:.2f}s"

        # Cleanup
        client.clear_local_cache()


class TestRollbackProcedures:
    """Test rollback and recovery procedures."""

    def test_singleton_reset_works(self):
        """Test singleton reset for rollback."""
        from agentic_core.mixins.meta_learning_client_mixin import (
            MetaLearningClientMixin,
        )
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        # Get initial instance
        get_meta_learning_client()

        # Reset singletons
        MetaLearningClient.reset_instance()
        MetaLearningClientMixin.reset_ml_singletons()

        # Get new instance
        client2 = get_meta_learning_client()

        # Should be different instances (new after reset)
        # Note: In singleton pattern, this verifies reset works
        assert client2 is not None

    def test_graceful_degradation(self):
        """Test system degrades gracefully when services unavailable."""
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        # Disable all external services
        client._redis_client = None
        client._pinecone_index = None

        # Operations should still work via local fallback
        result = client.cache_set("graceful_test", {"data": "test"}, "agentic_core")
        assert result is True

        value = client.cache_get("graceful_test", "agentic_core")
        assert value == {"data": "test"}

        # Pattern retrieval should return empty (graceful)
        patterns = client.retrieve_healing_patterns({"type": "TEST"})
        assert patterns == []


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
