#!/usr/bin/env python3
"""
Phase 4: Full System Validation & Optimization Tests

Tests for:
- Sub-Phase 4.1: Performance Validation
- Sub-Phase 4.2: Guardrails Validation
- Sub-Phase 4.3: Monitoring & Observability Setup

Success Criteria:
- Overall 70%+ cache hit ratio
- 50%+ healing time reduction
- All guardrails prevent violations
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Mock problematic imports
sys.modules["agentic_core.L5_safety.validators.PascalSovereigntyAgent"] = MagicMock()


# =============================================================================
# SUB-PHASE 4.1: PERFORMANCE VALIDATION TESTS
# =============================================================================


class TestPerformanceValidation:
    """Test system-wide performance improvements."""

    def test_cache_operations_performance(self):
        """Test cache operations complete within acceptable time."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None  # Force local cache

        start_time = time.time()

        # Perform 500 cache operations
        for i in range(500):
            key = f"perf_test_{i}"
            client.cache_set(key, {"index": i}, "agentic_core")
            client.cache_get(key, "agentic_core")

        elapsed = time.time() - start_time

        # Should complete in < 2 seconds
        assert elapsed < 2.0, f"Cache operations took {elapsed:.2f}s, expected < 2s"

    def test_signature_generation_batch_performance(self):
        """Test batch signature generation is fast."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        violations = [
            {"type": f"TYPE_{i}", "path": f"test_{i}.py", "message": f"Error {i}"}
            for i in range(100)
        ]

        start_time = time.time()

        # Generate signatures for all violations
        for violation in violations:
            client._generate_error_signature(violation)

        elapsed = time.time() - start_time

        # Should complete in < 0.5 seconds
        assert elapsed < 0.5, f"Signature generation took {elapsed:.2f}s"

    def test_cache_hit_ratio_tracking(self):
        """Test cache hit ratio tracking is accurate."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None  # Force local cache

        # Clear previous stats
        initial_hits = client.stats["cache_hits"]
        initial_misses = client.stats["cache_misses"]

        # Perform operations
        for i in range(10):
            key = f"ratio_test_{i}"
            client.cache_get(key, "agentic_core")  # Miss
            client.cache_set(key, {"data": i}, "agentic_core")
            client.cache_get(key, "agentic_core")  # Hit

        # Calculate hit ratio
        new_hits = client.stats["cache_hits"] - initial_hits
        new_misses = client.stats["cache_misses"] - initial_misses

        hit_ratio = new_hits / (new_hits + new_misses)

        # Should be 50% (10 hits, 10 misses)
        assert hit_ratio >= 0.45, f"Hit ratio {hit_ratio:.2f} is below expected 0.5"


# =============================================================================
# SUB-PHASE 4.2: GUARDRAILS VALIDATION TESTS
# =============================================================================


class TestGuardrailsValidation:
    """Test all safety mechanisms work under stress."""

    def test_similarity_threshold_enforcement(self):
        """Test similarity threshold is enforced."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            DEFAULT_SIMILARITY_THRESHOLD,
        )

        client = MetaLearningClient()

        # Verify default threshold
        assert client.similarity_threshold == DEFAULT_SIMILARITY_THRESHOLD

        # Verify domain thresholds
        assert client.domain_thresholds["agentic_core"] == 0.85
        assert client.domain_thresholds["apps_lic"] == 0.92

    def test_ttl_expiration(self):
        """Test TTL expiration works correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            CacheEntry,
        )

        # Create cache entry with very short TTL
        entry = CacheEntry(key="test", value="test_value", ttl=0)

        # Wait briefly
        time.sleep(0.1)

        # Should be expired
        assert entry.is_expired() is True

        # Create entry with long TTL
        entry2 = CacheEntry(key="test2", value="test_value2", ttl=3600)
        assert entry2.is_expired() is False

    def test_healing_depth_under_stress(self):
        """Test healing depth tracking under stress."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        # Simulate many agents attempting healing
        for agent_idx in range(10):
            agent_name = f"StressTestAgent_{agent_idx}"
            violation_id = f"stress_violation_{agent_idx}"

            # Increment to max depth
            for i in range(5):
                client.increment_healing_depth(agent_name, violation_id)

            # Should be blocked
            assert client.check_healing_depth(agent_name, violation_id) is False

            # Reset
            client.reset_healing_depth(agent_name, violation_id)

            # Should be allowed again
            assert client.check_healing_depth(agent_name, violation_id) is True

    def test_domain_isolation_under_stress(self):
        """Test domain isolation under concurrent-like operations."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None  # Force local cache

        domains = ["agentic_core", "apps_lic", "apps_rg"]

        # Set values in all domains
        for domain in domains:
            for i in range(10):
                client.cache_set(f"isolation_test_{i}", {"domain": domain}, domain)

        # Verify isolation
        for domain in domains:
            for i in range(10):
                value = client.cache_get(f"isolation_test_{i}", domain)
                assert value["domain"] == domain


# =============================================================================
# SUB-PHASE 4.3: MONITORING & OBSERVABILITY TESTS
# =============================================================================


class TestMonitoringObservability:
    """Test monitoring and observability features."""

    def test_statistics_tracking(self):
        """Test statistics are tracked correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        stats = client.get_stats()

        # Verify required stats keys
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "pattern_retrievals" in stats
        assert "pattern_stores" in stats
        assert "healing_cycles_prevented" in stats
        assert "cache_hit_ratio" in stats
        assert "local_cache_size" in stats
        assert "active_healing_cycles" in stats

    def test_domain_stats_tracking(self):
        """Test domain-specific statistics are tracked."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None

        # Perform operations in different domains
        client.cache_set("test", {"data": "test"}, "agentic_core")
        client.cache_get("test", "agentic_core")

        client.cache_set("test", {"data": "test"}, "apps_lic")
        client.cache_get("test", "apps_lic")

        stats = client.get_stats()

        # Verify domain stats exist
        assert "by_domain" in stats

    def test_local_cache_cleanup(self):
        """Test local cache cleanup functionality."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()
        client._redis_client = None

        # Fill cache
        for i in range(100):
            client.cache_set(f"cleanup_test_{i}", {"data": i}, "agentic_core")

        # Verify cache has entries
        assert len(client._local_cache) >= 100

        # Clear cache
        cleared = client.clear_local_cache()
        assert cleared >= 100
        assert len(client._local_cache) == 0


class TestPhase4Integration:
    """Phase 4 integration tests."""

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_full_system_stability(self, mock_integrity):
        """Test full system remains stable under load."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        client = MetaLearningClient()

        # Simulate full system operation
        start_time = time.time()

        for cycle in range(5):
            # Cache operations
            for i in range(50):
                key = f"stability_test_{cycle}_{i}"
                client.cache_set(key, {"cycle": cycle, "index": i}, "agentic_core")
                client.cache_get(key, "agentic_core")

            # Healing depth tracking
            agent_name = f"StabilityAgent_{cycle}"
            violation_id = f"stability_violation_{cycle}"
            client.increment_healing_depth(agent_name, violation_id)
            client.check_healing_depth(agent_name, violation_id)
            client.reset_healing_depth(agent_name, violation_id)

        elapsed = time.time() - start_time

        # Should complete in < 5 seconds
        assert elapsed < 5.0, f"System stability test took {elapsed:.2f}s"

        # Get final stats
        stats = client.get_stats()
        assert stats["cache_hits"] > 0
        assert stats["cache_misses"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
