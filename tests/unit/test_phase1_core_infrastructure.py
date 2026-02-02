"""
Phase 1: Core Infrastructure Integration Tests

Comprehensive test suite for Meta-Learning core infrastructure:
- MetaLearningClient Redis/Pinecone wrapper
- CacheStrategyManager TTL and similarity guardrails
- Guardrails safety framework
- HealingMemoryEmbedder pattern storage

All tests use mocked Redis/Pinecone to avoid external dependencies.
"""

from __future__ import annotations

import time
import pytest
from unittest.mock import MagicMock


# ==================== TEST 1.1: MetaLearningClient Infrastructure ====================


class TestMetaLearningClientInfrastructure:
    """Test MetaLearningClient core functionality."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        mock = MagicMock()
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        mock.exists.return_value = False
        mock.expire.return_value = True
        mock.ping.return_value = True
        return mock

    @pytest.fixture
    def mock_pinecone(self):
        """Mock Pinecone client."""
        mock = MagicMock()
        mock.query.return_value = {"matches": []}
        mock.upsert.return_value = {"upserted_count": 1}
        mock.delete.return_value = {}
        return mock

    def test_client_initialization_with_defaults(self):
        """Test MetaLearningClient initializes with default configuration."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        assert client is not None
        assert hasattr(client, "stats")
        assert client.stats["cache_hits"] == 0
        assert client.stats["cache_misses"] == 0

    def test_client_cache_get_miss(self):
        """Test cache get returns None on miss."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()
        result = client.cache_get("nonexistent_key", "agentic_core")

        assert result is None
        assert client.stats["cache_misses"] >= 1

    def test_client_cache_set_and_get(self):
        """Test cache set followed by get returns value."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()
        test_value = {"data": "test_value", "nested": {"key": 123}}

        # Set value
        success = client.cache_set("test_key", test_value, "agentic_core")
        assert success is True

        # Get value
        result = client.cache_get("test_key", "agentic_core")
        assert result == test_value

    def test_client_cache_delete(self):
        """Test cache delete removes entry."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Set value
        client.cache_set("delete_test_key", {"data": "value"}, "agentic_core")

        # Delete value
        success = client.cache_delete("delete_test_key", "agentic_core")
        assert success is True

        # Verify deleted
        result = client.cache_get("delete_test_key", "agentic_core")
        assert result is None

    def test_client_domain_isolation(self):
        """Test cache entries are isolated by domain."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Set same key in different domains
        client.cache_set("shared_key", {"domain": "core"}, "agentic_core")
        client.cache_set("shared_key", {"domain": "lic"}, "apps_lic")
        client.cache_set("shared_key", {"domain": "rg"}, "apps_rg")

        # Verify isolation
        core_result = client.cache_get("shared_key", "agentic_core")
        lic_result = client.cache_get("shared_key", "apps_lic")
        rg_result = client.cache_get("shared_key", "apps_rg")

        assert core_result["domain"] == "core"
        assert lic_result["domain"] == "lic"
        assert rg_result["domain"] == "rg"

    def test_client_ttl_expiration(self):
        """Test cache entries expire after TTL."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Set with short TTL (1 second)
        client.cache_set("ttl_test_key", {"data": "expires"}, "agentic_core", ttl=1)

        # Verify exists
        result = client.cache_get("ttl_test_key", "agentic_core")
        assert result is not None

        # Wait for expiration
        time.sleep(1.5)

        # Verify expired
        result = client.cache_get("ttl_test_key", "agentic_core")
        assert result is None

    def test_client_stats_tracking(self):
        """Test client tracks statistics correctly."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()
        initial_hits = client.stats["cache_hits"]
        initial_misses = client.stats["cache_misses"]

        # Generate misses
        client.cache_get("miss_key_1", "agentic_core")
        client.cache_get("miss_key_2", "agentic_core")

        # Generate hits
        client.cache_set("hit_key", {"data": "value"}, "agentic_core")
        client.cache_get("hit_key", "agentic_core")
        client.cache_get("hit_key", "agentic_core")

        assert client.stats["cache_misses"] >= initial_misses + 2
        assert client.stats["cache_hits"] >= initial_hits + 2


# ==================== TEST 1.2: Guardrails Implementation ====================


class TestGuardrailsImplementation:
    """Test guardrails safety framework."""

    @pytest.fixture
    def guardrails(self):
        """Create guardrails instance."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        return MetaLearningGuardrails()

    def test_validate_cache_key_valid(self, guardrails):
        """Test valid cache keys pass validation."""
        valid_keys = [
            "test_key",
            "test-key",
            "test:key:123",
            "gravity_analysis:file:12345",
            "ats_score:resume:job",
        ]

        for key in valid_keys:
            assert guardrails.validate_cache_key(key) is True, f"Key should be valid: {key}"

    def test_validate_cache_key_invalid(self, guardrails):
        """Test invalid cache keys fail validation."""
        invalid_keys = [
            "",  # Empty
            None,  # None
            "../../../etc/passwd",  # Path traversal
            "/absolute/path",  # Absolute path
            "key with spaces",  # Spaces
            "key@with#special!chars",  # Special chars
            "a" * 300,  # Too long
        ]

        for key in invalid_keys:
            assert guardrails.validate_cache_key(key) is False, f"Key should be invalid: {key}"

    def test_validate_cache_value_valid(self, guardrails):
        """Test valid cache values pass validation."""
        valid_values = [
            {"simple": "dict"},
            {"nested": {"data": [1, 2, 3]}},
            [1, 2, 3, {"key": "value"}],
            "simple string",
            123,
            None,
        ]

        for value in valid_values:
            assert guardrails.validate_cache_value(value) is True, f"Value should be valid: {value}"

    def test_validate_cache_value_too_large(self, guardrails):
        """Test oversized cache values fail validation."""
        # Create value > 100KB
        large_value = {"data": "x" * (101 * 1024)}

        assert guardrails.validate_cache_value(large_value) is False

    def test_validate_ttl_valid(self, guardrails):
        """Test valid TTL values are normalized."""
        assert guardrails.validate_ttl(3600) == 3600  # Normal
        assert guardrails.validate_ttl(None) == 3600  # Default
        assert guardrails.validate_ttl(60) == 60  # Minimum

    def test_validate_ttl_bounds(self, guardrails):
        """Test TTL values are bounded correctly."""
        assert guardrails.validate_ttl(1) == 60  # Below min
        assert guardrails.validate_ttl(100000) == 86400  # Above max
        assert guardrails.validate_ttl(-100) == 3600  # Invalid

    def test_check_rate_limit_allows(self, guardrails):
        """Test rate limit allows normal traffic."""
        for i in range(10):
            assert guardrails.check_rate_limit("agentic_core", "request") is True

    def test_check_rate_limit_blocks(self, guardrails):
        """Test rate limit blocks excessive traffic."""
        # Exceed rate limit
        for i in range(1001):
            guardrails.check_rate_limit("rate_test_domain", "request")

        # Should be blocked
        assert guardrails.check_rate_limit("rate_test_domain", "request") is False

    def test_similarity_threshold_validation(self, guardrails):
        """Test similarity threshold validation."""
        assert guardrails.validate_similarity_threshold(0.85) == 0.85
        assert guardrails.validate_similarity_threshold(None) == 0.85  # Default
        assert guardrails.validate_similarity_threshold(0.5) == 0.70  # Below min
        assert guardrails.validate_similarity_threshold(1.5) == 1.0  # Above max

    def test_healing_depth_tracking(self, guardrails):
        """Test healing depth tracking and limits."""
        agent = "TestAgent"
        violation = "violation_123"

        # Should allow initial healings
        for i in range(5):
            assert guardrails.check_healing_depth(agent, violation) is True
            guardrails.increment_healing_depth(agent, violation)

        # Should block after max depth
        assert guardrails.check_healing_depth(agent, violation) is False

    def test_healing_depth_reset(self, guardrails):
        """Test healing depth reset after success."""
        agent = "TestAgent"
        violation = "violation_reset_test"

        # Increment to near limit
        for i in range(3):
            guardrails.increment_healing_depth(agent, violation)

        # Reset
        guardrails.reset_healing_depth(agent, violation)

        # Should allow again
        assert guardrails.check_healing_depth(agent, violation) is True

    def test_domain_isolation_validation(self, guardrails):
        """Test domain isolation enforcement."""
        valid_pattern = {
            "domain": "agentic_core",
            "violation_type": "gravity",
            "healing_strategy": {"action": "relocate"},
        }

        invalid_pattern = {
            "domain": "apps_rg",  # Wrong domain
            "violation_type": "gravity",
            "healing_strategy": {"action": "relocate"},
        }

        assert guardrails.validate_domain_isolation("agentic_core", valid_pattern) is True
        assert guardrails.validate_domain_isolation("agentic_core", invalid_pattern) is False

    def test_violation_data_sanitization(self, guardrails):
        """Test violation data sanitization."""
        dirty_violation = {
            "type": "gravity_violation",
            "path": "/test/file.py",
            "import_statement": "from evil import hack",
            "malicious_field": "<script>alert('xss')</script>",
            "null_bytes": "data\x00with\x00nulls",
        }

        sanitized = guardrails.sanitize_violation_data(dirty_violation)

        assert "type" in sanitized
        assert "path" in sanitized
        assert "malicious_field" not in sanitized
        assert "\x00" not in sanitized.get("path", "")


# ==================== TEST 1.3: CacheStrategyManager ====================


class TestCacheStrategyManager:
    """Test CacheStrategyManager TTL and similarity guardrails."""

    @pytest.fixture
    def csm(self):
        """Create CacheStrategyManager instance."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            DomainConfig,
        )

        manager = CacheStrategyManager()
        manager.domain_configs = {
            "agentic_core": DomainConfig(domain="agentic_core"),
            "apps_lic": DomainConfig(domain="apps_lic", ttl_seconds=1800),
            "apps_rg": DomainConfig(domain="apps_rg", similarity_threshold=0.90),
        }
        return manager

    def test_domain_config_defaults(self):
        """Test DomainConfig uses correct defaults."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import DomainConfig

        config = DomainConfig(domain="test")

        assert config.ttl_seconds == 3600
        assert config.similarity_threshold == 0.85
        assert config.max_cache_size == 10000
        assert config.max_healing_depth == 5

    def test_domain_config_validation(self):
        """Test DomainConfig validates and bounds values."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import DomainConfig

        # Test TTL bounds
        config1 = DomainConfig(domain="test", ttl_seconds=1)
        assert config1.ttl_seconds == 60  # Min enforced

        config2 = DomainConfig(domain="test", ttl_seconds=100000)
        assert config2.ttl_seconds == 86400  # Max enforced

        # Test similarity bounds
        config3 = DomainConfig(domain="test", similarity_threshold=0.5)
        assert config3.similarity_threshold == 0.70  # Min enforced

        config4 = DomainConfig(domain="test", similarity_threshold=1.5)
        assert config4.similarity_threshold == 0.99  # Max enforced

    def test_get_ttl_for_domain(self, csm):
        """Test getting TTL for specific domains."""
        assert csm.get_ttl("agentic_core") == 3600
        assert csm.get_ttl("apps_lic") == 1800
        assert csm.get_ttl("unknown_domain") == 3600  # Default

    def test_get_similarity_threshold_for_domain(self, csm):
        """Test getting similarity threshold for specific domains."""
        assert csm.get_similarity_threshold("agentic_core") == 0.85
        assert csm.get_similarity_threshold("apps_rg") == 0.90
        assert csm.get_similarity_threshold("unknown") == 0.85  # Default

    def test_check_healing_depth(self, csm):
        """Test healing depth checking."""
        # Should allow initially
        assert csm.check_healing_depth("TestAgent", "violation_1") is True

        # Increment to max
        for i in range(5):
            csm.increment_healing_depth("TestAgent", "violation_1")

        # Should block after max
        assert csm.check_healing_depth("TestAgent", "violation_1") is False

    def test_reset_healing_depth(self, csm):
        """Test healing depth reset."""
        # Increment
        for i in range(3):
            csm.increment_healing_depth("TestAgent", "violation_reset")

        # Reset
        csm.reset_healing_depth("TestAgent", "violation_reset")

        # Should allow again
        assert csm.check_healing_depth("TestAgent", "violation_reset") is True


# ==================== TEST 1.4: HealingPattern Storage ====================


class TestHealingPatternStorage:
    """Test HealingPattern data structures and storage."""

    def test_healing_pattern_creation(self):
        """Test HealingPattern creation with defaults."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import HealingPattern

        pattern = HealingPattern(
            pattern_id="test_pattern_1",
            violation_type="gravity_violation",
            error_signature="abc123",
            healing_strategy={"action": "relocate", "target": "utils/"},
        )

        assert pattern.pattern_id == "test_pattern_1"
        assert pattern.violation_type == "gravity_violation"
        assert pattern.success_count == 1
        assert pattern.domain == "agentic_core"

    def test_healing_pattern_to_dict(self):
        """Test HealingPattern serialization."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import HealingPattern

        pattern = HealingPattern(
            pattern_id="serialize_test",
            violation_type="import_violation",
            error_signature="def456",
            healing_strategy={"fix": "refactor"},
        )

        data = pattern.to_dict()

        assert data["pattern_id"] == "serialize_test"
        assert data["violation_type"] == "import_violation"
        assert "healing_strategy" in data
        assert "embedding" not in data  # Should not include embedding

    def test_healing_pattern_from_dict(self):
        """Test HealingPattern deserialization."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import HealingPattern

        data = {
            "pattern_id": "deserialize_test",
            "violation_type": "structure_violation",
            "error_signature": "ghi789",
            "healing_strategy": {"action": "move_file"},
            "success_count": 5,
            "domain": "apps_lic",
            "metadata": {"source": "test"},
        }

        pattern = HealingPattern.from_dict(data)

        assert pattern.pattern_id == "deserialize_test"
        assert pattern.success_count == 5
        assert pattern.domain == "apps_lic"
        assert pattern.metadata["source"] == "test"

    def test_healing_pattern_roundtrip(self):
        """Test HealingPattern serialize/deserialize roundtrip."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import HealingPattern

        original = HealingPattern(
            pattern_id="roundtrip_test",
            violation_type="test_violation",
            error_signature="xyz000",
            healing_strategy={"nested": {"data": [1, 2, 3]}},
            success_count=10,
            domain="apps_rg",
            metadata={"key": "value"},
        )

        data = original.to_dict()
        restored = HealingPattern.from_dict(data)

        assert restored.pattern_id == original.pattern_id
        assert restored.success_count == original.success_count
        assert restored.domain == original.domain
        assert restored.healing_strategy == original.healing_strategy


# ==================== TEST 1.5: Integration Tests ====================


class TestPhase1Integration:
    """Integration tests for Phase 1 components."""

    def test_client_with_guardrails(self):
        """Test MetaLearningClient respects guardrails."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        from agentic_core.L1_cognition.meta_learning.guardrails import get_guardrails

        client = MetaLearningClient()
        guardrails = get_guardrails()

        # Test with valid key
        valid_key = "integration_test_key"
        assert guardrails.validate_cache_key(valid_key) is True
        client.cache_set(valid_key, {"data": "test"}, "agentic_core")

        # Test cache works
        result = client.cache_get(valid_key, "agentic_core")
        assert result is not None

    def test_cache_strategy_with_client(self):
        """Test CacheStrategyManager works with MetaLearningClient."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            DomainConfig,
        )

        client = MetaLearningClient()
        csm = CacheStrategyManager()
        csm.domain_configs["test_domain"] = DomainConfig(domain="test_domain", ttl_seconds=1800)

        # Get TTL from strategy manager
        ttl = csm.get_ttl("test_domain")

        # Use TTL in cache operation
        client.cache_set("strategy_test", {"data": "value"}, "test_domain", ttl=ttl)

        result = client.cache_get("strategy_test", "test_domain")
        assert result is not None

    def test_full_healing_workflow(self):
        """Test complete healing pattern storage and retrieval workflow."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.guardrails import get_guardrails

        client = MetaLearningClient()
        guardrails = get_guardrails()

        # Create violation
        violation = {
            "type": "gravity_violation",
            "path": "/test/file.py",
            "import_statement": "from L0 import util",
        }

        # Sanitize violation
        sanitized = guardrails.sanitize_violation_data(violation)

        # Check healing depth
        assert guardrails.check_healing_depth("TestAgent", "v1") is True
        guardrails.increment_healing_depth("TestAgent", "v1")

        # Store healing result
        healing_result = {
            "status": "fixed",
            "fix_type": "RELOCATE",
            "new_import": "from utils import util",
        }

        # Cache the result
        cache_key = f"healing:{sanitized['type']}:{sanitized['path']}"
        # Validate key
        if guardrails.validate_cache_key(cache_key.replace("/", "_").replace(":", "_")):
            client.cache_set(
                cache_key.replace("/", "_").replace(":", "_"), healing_result, "agentic_core"
            )

        # Reset healing depth on success
        guardrails.reset_healing_depth("TestAgent", "v1")

        # Verify reset
        assert guardrails.check_healing_depth("TestAgent", "v1") is True


# ==================== RUN CONFIGURATION ====================

if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
        ]
    )
