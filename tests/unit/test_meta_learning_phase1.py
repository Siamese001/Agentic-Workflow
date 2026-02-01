"""
Test Suite for Meta-Learning Phase 1: Core Infrastructure

Tests for:
- MetaLearningClient (Redis/Pinecone wrapper)
- HealingMemoryEmbedder (violation signature embedding)
- CacheStrategyManager (TTL and similarity threshold guardrails)

All tests use mocked Redis/Pinecone to ensure isolation.
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest


def reset_meta_learning_singletons():
    """Reset all meta-learning singletons for test isolation."""
    import agentic_core.L1_cognition.meta_learning.MetaLearningClient as mlc
    import agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder as hme
    import agentic_core.L1_cognition.meta_learning.CacheStrategyManager as csm

    # Reset module-level singletons (accessor functions)
    mlc._meta_learning_client = None
    hme._healing_memory_embedder = None
    csm._cache_strategy_manager = None

    # Reset module-level singleton instances
    mlc._singleton_instance = None
    hme._embedder_singleton = None
    csm._csm_singleton = None


class TestMetaLearningClient:
    """Tests for MetaLearningClient core functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singleton before each test."""
        reset_meta_learning_singletons()
        yield
        reset_meta_learning_singletons()

    def test_singleton_pattern(self):
        """Test that MetaLearningClient is a singleton."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client1 = MetaLearningClient()
            client2 = MetaLearningClient()
            assert client1 is client2

    def test_cache_get_miss(self):
        """Test cache miss returns None."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()
            result = client.cache_get("nonexistent_key", "agentic_core")
            assert result is None
            assert client.stats["cache_misses"] >= 1

    def test_cache_set_and_get_local_fallback(self):
        """Test cache set and get with local fallback."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()
            test_value = {"test": "data", "count": 42}

            # Set value
            result = client.cache_set("test_key", test_value, "agentic_core")
            assert result is True

            # Get value
            cached = client.cache_get("test_key", "agentic_core")
            assert cached == test_value
            assert client.stats["cache_hits"] >= 1

    def test_cache_domain_isolation(self):
        """Test that cache entries are isolated by domain."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()

            # Set same key in different domains
            client.cache_set("shared_key", {"domain": "core"}, "agentic_core")
            client.cache_set("shared_key", {"domain": "lic"}, "apps_lic")
            client.cache_set("shared_key", {"domain": "rg"}, "apps_rg")

            # Verify isolation
            assert client.cache_get("shared_key", "agentic_core")["domain"] == "core"
            assert client.cache_get("shared_key", "apps_lic")["domain"] == "lic"
            assert client.cache_get("shared_key", "apps_rg")["domain"] == "rg"

    def test_cache_ttl_expiration(self):
        """Test that cache entries expire based on TTL."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()

            # Set with very short TTL
            client.cache_set("expiring_key", {"data": "test"}, "agentic_core", ttl=1)

            # Should exist immediately
            assert client.cache_get("expiring_key", "agentic_core") is not None

            # Wait for expiration
            time.sleep(1.1)

            # Should be expired
            assert client.cache_get("expiring_key", "agentic_core") is None

    def test_input_validation_rejects_large_input(self):
        """Test that large inputs are rejected."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()

            # Create large string (>100KB)
            large_value = "x" * 200000
            result = client.cache_set("large_key", large_value, "agentic_core")
            assert result is False

    def test_healing_depth_tracking(self):
        """Test healing depth tracking prevents infinite loops."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()
            agent_name = "TestAgent"
            violation_id = "test_violation_001"

            # Should allow healing up to max depth
            for i in range(client.max_healing_depth):
                assert client.check_healing_depth(agent_name, violation_id) is True
                client.increment_healing_depth(agent_name, violation_id)

            # Should block at max depth
            assert client.check_healing_depth(agent_name, violation_id) is False
            assert client.stats["healing_cycles_prevented"] >= 1

            # Reset should allow healing again
            client.reset_healing_depth(agent_name, violation_id)
            assert client.check_healing_depth(agent_name, violation_id) is True

    def test_error_signature_generation(self):
        """Test error signature generation is consistent."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()

            violation = {
                "type": "naming_violation",
                "path": "/test/file.py",
                "message": "Invalid naming convention",
            }

            sig1 = client._generate_error_signature(violation)
            sig2 = client._generate_error_signature(violation)

            # Same violation should produce same signature
            assert sig1 == sig2
            assert len(sig1) == 16  # SHA256 truncated to 16 chars

    def test_domain_specific_thresholds(self):
        """Test domain-specific similarity thresholds."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()

            # Verify domain thresholds match existing base agents
            assert client.domain_thresholds["agentic_core"] == 0.85
            assert client.domain_thresholds["apps_lic"] == 0.92  # Higher for LIC
            assert client.domain_thresholds["apps_rg"] == 0.85

    def test_stats_tracking(self):
        """Test statistics tracking."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()

            # Perform some operations
            client.cache_get("miss_key", "agentic_core")
            client.cache_set("hit_key", {"data": "test"}, "apps_lic")
            client.cache_get("hit_key", "apps_lic")

            stats = client.get_stats()
            assert "cache_hits" in stats
            assert "cache_misses" in stats
            assert "cache_hit_ratio" in stats
            assert "by_domain" in stats


class TestHealingMemoryEmbedder:
    """Tests for HealingMemoryEmbedder functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singleton before each test."""
        reset_meta_learning_singletons()
        yield
        reset_meta_learning_singletons()

    def test_singleton_pattern(self):
        """Test that HealingMemoryEmbedder is a singleton."""
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
        )

        with patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"):
            embedder1 = HealingMemoryEmbedder()
            embedder2 = HealingMemoryEmbedder()
            assert embedder1 is embedder2

    def test_violation_signature_creation(self):
        """Test ViolationSignature creation from violation dict."""
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            ViolationSignature,
        )

        violation = {
            "type": "gravity_violation",
            "path": "/agentic_core/L3/file.py",
            "message": "L3 importing L5",
            "domain": "agentic_core",
        }

        signature = ViolationSignature.from_violation(violation)
        assert signature.violation_type == "gravity_violation"
        assert signature.path == "/agentic_core/L3/file.py"
        assert signature.domain == "agentic_core"

    def test_signature_to_text(self):
        """Test signature text generation for embedding."""
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            ViolationSignature,
        )

        signature = ViolationSignature(
            violation_type="naming_violation",
            path="/test/file.py",
            message="Invalid name",
            domain="apps_lic",
        )

        text = signature.to_text()
        assert "naming_violation" in text
        assert "/test/file.py" in text
        assert "apps_lic" in text

    def test_signature_hash_consistency(self):
        """Test hash signature is consistent."""
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            ViolationSignature,
        )

        signature = ViolationSignature(
            violation_type="test_violation",
            path="/test/path.py",
            message="Test message",
        )

        hash1 = signature.to_hash()
        hash2 = signature.to_hash()

        assert hash1 == hash2
        assert len(hash1) == 16

    def test_get_hash_signature_fallback(self):
        """Test hash signature fallback when embedding unavailable."""
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
            get_healing_memory_embedder,
        )

        with patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"):
            embedder = get_healing_memory_embedder()
            violation = {
                "type": "test_violation",
                "path": "/test/file.py",
                "message": "Test message",
            }

            hash_sig = embedder.get_hash_signature(violation)
            assert len(hash_sig) == 16
            assert isinstance(hash_sig, str)

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation."""
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
            get_healing_memory_embedder,
        )

        with patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"):
            embedder = get_healing_memory_embedder()

            # Identical vectors should have similarity 1.0
            vec1 = [1.0, 0.0, 0.0]
            vec2 = [1.0, 0.0, 0.0]
            assert embedder.compute_similarity(vec1, vec2) == pytest.approx(1.0)

            # Orthogonal vectors should have similarity 0.0
            vec3 = [1.0, 0.0, 0.0]
            vec4 = [0.0, 1.0, 0.0]
            assert embedder.compute_similarity(vec3, vec4) == pytest.approx(0.0)

            # Opposite vectors should have similarity -1.0
            vec5 = [1.0, 0.0, 0.0]
            vec6 = [-1.0, 0.0, 0.0]
            assert embedder.compute_similarity(vec5, vec6) == pytest.approx(-1.0)

    def test_stats_tracking(self):
        """Test statistics tracking."""
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
            get_healing_memory_embedder,
        )

        with patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"):
            embedder = get_healing_memory_embedder()

            # Generate some hash signatures (fallback)
            embedder.get_hash_signature({"type": "test1"})
            embedder.get_hash_signature({"type": "test2"})

            stats = embedder.get_stats()
            assert "fallback_hashes" in stats
            assert "embedding_available" in stats


class TestCacheStrategyManager:
    """Tests for CacheStrategyManager functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singleton before each test."""
        reset_meta_learning_singletons()
        yield
        reset_meta_learning_singletons()

    def test_singleton_pattern(self):
        """Test that CacheStrategyManager is a singleton."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
        )

        manager1 = CacheStrategyManager()
        manager2 = CacheStrategyManager()
        assert manager1 is manager2

    def test_default_domain_configs(self):
        """Test default domain configurations."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        # Verify default configs exist
        assert "agentic_core" in manager.domain_configs
        assert "apps_lic" in manager.domain_configs
        assert "apps_rg" in manager.domain_configs

        # Verify LIC has higher threshold
        assert manager.domain_configs["apps_lic"].similarity_threshold == 0.92
        assert manager.domain_configs["agentic_core"].similarity_threshold == 0.85

    def test_ttl_management(self):
        """Test TTL get/set operations."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        # Get default TTL
        ttl = manager.get_ttl("agentic_core")
        assert ttl == 3600  # 1 hour

        # Set custom TTL
        manager.set_ttl("agentic_core", 7200)
        assert manager.get_ttl("agentic_core") == 7200

        # TTL should be clamped to valid range
        manager.set_ttl("agentic_core", 10)  # Below minimum
        assert manager.get_ttl("agentic_core") == 60  # Clamped to minimum

    def test_similarity_threshold_management(self):
        """Test similarity threshold get/set operations."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        # Get default threshold
        threshold = manager.get_similarity_threshold("apps_lic")
        assert threshold == 0.92

        # Set custom threshold
        manager.set_similarity_threshold("apps_lic", 0.95)
        assert manager.get_similarity_threshold("apps_lic") == 0.95

        # Threshold should be clamped to valid range
        manager.set_similarity_threshold("apps_lic", 1.5)  # Above maximum
        assert manager.get_similarity_threshold("apps_lic") == 0.99  # Clamped

    def test_meets_similarity_threshold(self):
        """Test similarity threshold checking."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        # Above threshold should pass
        assert manager.meets_similarity_threshold(0.90, "agentic_core") is True

        # Below threshold should fail
        assert manager.meets_similarity_threshold(0.80, "agentic_core") is False
        assert manager.stats["threshold_rejections"] >= 1

    def test_healing_depth_tracking(self):
        """Test healing depth tracking."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()
        agent_name = "TestAgent"
        violation_id = "test_001"

        # Initial depth should be 0
        assert manager.get_healing_depth(agent_name, violation_id) == 0

        # Increment depth
        manager.increment_healing_depth(agent_name, violation_id)
        assert manager.get_healing_depth(agent_name, violation_id) == 1

        # Check should pass until max depth
        for _ in range(4):
            assert manager.check_healing_depth(agent_name, violation_id) is True
            manager.increment_healing_depth(agent_name, violation_id)

        # Should fail at max depth
        assert manager.check_healing_depth(agent_name, violation_id) is False

        # Reset should clear depth
        manager.reset_healing_depth(agent_name, violation_id)
        assert manager.get_healing_depth(agent_name, violation_id) == 0

    def test_cache_poisoning_protection(self):
        """Test cache poisoning protection."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        # Valid input should pass
        assert manager.validate_cache_input("valid_key", {"data": "test"}) is True

        # Empty key should fail
        assert manager.validate_cache_input("", {"data": "test"}) is False

        # Key with path traversal should fail
        assert manager.validate_cache_input("../../../etc/passwd", {}) is False
        assert manager.stats["poisoning_attempts_blocked"] >= 1

        # Key with null byte should fail
        assert manager.validate_cache_input("key\x00injection", {}) is False

        # Very long key should fail
        assert manager.validate_cache_input("x" * 600, {}) is False

    def test_eviction_tracking(self):
        """Test cache eviction tracking."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        # Record some accesses
        manager.record_access("meta_learning:agentic_core:key1")
        manager.record_access("meta_learning:agentic_core:key2")
        time.sleep(0.1)
        manager.record_access("meta_learning:agentic_core:key1")  # Access again

        # key1 should be more recently accessed
        stats = manager.get_stats()
        assert stats["tracked_keys"] >= 2

    def test_domain_stats(self):
        """Test domain-specific statistics."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        manager = get_cache_strategy_manager()

        # Trigger some threshold rejections
        manager.meets_similarity_threshold(0.50, "apps_lic")
        manager.meets_similarity_threshold(0.60, "apps_rg")

        # Get domain stats
        lic_stats = manager.get_domain_stats("apps_lic")
        assert "config" in lic_stats
        assert "stats" in lic_stats
        # Verify threshold is within valid range (may have been modified by previous tests)
        assert 0.70 <= lic_stats["config"]["similarity_threshold"] <= 0.99


class TestIntegration:
    """Integration tests for Phase 1 components."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset all singletons before each test."""
        reset_meta_learning_singletons()
        yield
        reset_meta_learning_singletons()

    def test_full_healing_pattern_workflow(self):
        """Test complete workflow: cache -> embed -> store pattern."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
            HealingMemoryEmbedder,
            get_healing_memory_embedder,
        )
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
            patch.object(HealingMemoryEmbedder, "_initialize_embedding_agent"),
        ):
            client = get_meta_learning_client()
            embedder = get_healing_memory_embedder()
            manager = get_cache_strategy_manager()

            # Simulate a violation
            violation = {
                "type": "naming_violation",
                "path": "/agentic_core/test.py",
                "message": "Invalid naming convention",
            }

            # Check healing depth
            assert manager.check_healing_depth("TestAgent", "v001") is True
            manager.increment_healing_depth("TestAgent", "v001")

            # Generate signature
            signature = embedder.get_hash_signature(violation)
            assert len(signature) == 16

            # Cache the violation analysis
            analysis_result = {"ast_nodes": 42, "complexity": 5}
            client.cache_set(f"analysis:{signature}", analysis_result, "agentic_core")

            # Retrieve from cache
            cached = client.cache_get(f"analysis:{signature}", "agentic_core")
            assert cached == analysis_result

            # Simulate successful healing
            healing_result = {
                "status": "fixed",
                "strategy": "rename_file",
                "changes": ["renamed test.py to TestAgent.py"],
            }

            # Store healing pattern (will use local cache as fallback)
            client.store_healing_pattern(violation, healing_result, "agentic_core")
            # Pattern ID may be None if Pinecone unavailable, but cache fallback should work

            # Reset healing depth after success
            manager.reset_healing_depth("TestAgent", "v001")
            assert manager.get_healing_depth("TestAgent", "v001") == 0

    def test_domain_isolation_workflow(self):
        """Test that domains are properly isolated."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()
            manager = get_cache_strategy_manager()

            # Store data in different domains
            client.cache_set("pattern:001", {"domain": "core"}, "agentic_core")
            client.cache_set("pattern:001", {"domain": "lic"}, "apps_lic")
            client.cache_set("pattern:001", {"domain": "rg"}, "apps_rg")

            # Verify isolation
            assert client.cache_get("pattern:001", "agentic_core")["domain"] == "core"
            assert client.cache_get("pattern:001", "apps_lic")["domain"] == "lic"
            assert client.cache_get("pattern:001", "apps_rg")["domain"] == "rg"

            # Verify domain-specific thresholds
            assert manager.get_similarity_threshold("apps_lic") > manager.get_similarity_threshold(
                "agentic_core"
            )

    def test_guardrails_prevent_abuse(self):
        """Test that guardrails prevent cache abuse."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
            get_meta_learning_client,
        )
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            get_cache_strategy_manager,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            client = get_meta_learning_client()
            manager = get_cache_strategy_manager()

            # Test healing depth limit
            agent_name = "AbusingAgent"
            violation_id = "abuse_001"

            for _ in range(10):  # Try to exceed limit
                if manager.check_healing_depth(agent_name, violation_id):
                    manager.increment_healing_depth(agent_name, violation_id)

            # Should have been blocked
            assert manager.stats["depth_limit_hits"] >= 1

            # Test cache poisoning protection
            assert manager.validate_cache_input("../../../etc/passwd", {}) is False
            assert manager.stats["poisoning_attempts_blocked"] >= 1

            # Test large input rejection
            large_data = "x" * 200000
            assert client.cache_set("large_key", large_data, "agentic_core") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
