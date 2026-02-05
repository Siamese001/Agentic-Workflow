"""
Test suite for meta-learning guardrails integration in apps_* folders.

Tests the critical security and safety features that are missing from the current
apps_rg and apps_lic implementations compared to agentic_core.
"""

import time

import pytest

# Test imports - these will need to be implemented
try:
    from apps_lic.shared.core.lic_agent_base_agent_validator import LICAgentBase
    from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
except ImportError as e:
    pytest.skip(f"Apps not yet enhanced with guardrails: {e}", allow_module_level=True)


class TestMetaLearningGuardrails:
    """Test guardrails integration for both RG and LIC agents."""

    def test_rg_guardrails_initialization(self):
        """Test RG agent initializes guardrails with correct domain configuration."""
        agent = RGAgentBase()

        # Verify guardrails are initialized
        assert hasattr(agent, "_guardrails"), "RG agent missing guardrails attribute"
        assert agent._guardrails is not None, "RG agent guardrails not initialized"

        # Verify domain-specific configuration
        rg_config = agent._guardrails.get_domain_config("apps_rg")
        assert rg_config.similarity_threshold == 0.85, "RG similarity threshold incorrect"
        assert rg_config.ttl_seconds == 3600, "RG TTL incorrect"
        assert rg_config.max_healing_depth == 5, "RG healing depth limit incorrect"

    def test_lic_guardrails_initialization(self):
        """Test LIC agent initializes guardrails with correct domain configuration."""
        agent = LICAgentBase()

        # Verify guardrails are initialized
        assert hasattr(agent, "_guardrails"), "LIC agent missing guardrails attribute"
        assert agent._guardrails is not None, "LIC agent guardrails not initialized"

        # Verify domain-specific configuration
        lic_config = agent._guardrails.get_domain_config("apps_lic")
        assert lic_config.similarity_threshold == 0.92, "LIC similarity threshold incorrect"
        assert lic_config.ttl_seconds == 7200, "LIC TTL incorrect"
        assert lic_config.max_healing_depth == 5, "LIC healing depth limit incorrect"

    def test_cache_poisoning_protection(self):
        """Test guardrails block malicious cache inputs."""
        agent = RGAgentBase()

        # Test dangerous key patterns
        dangerous_keys = [
            "../../../etc/passwd",
            "key\x00null",
            "key\ninjection",
            "key\rcarriage",
            "../secret",
            "/absolute/path",
        ]

        for dangerous_key in dangerous_keys:
            assert not agent._guardrails.validate_cache_key(dangerous_key), (
                f"Guardrails should block dangerous key: {dangerous_key}"
            )

        # Test oversized values
        oversized_value = {"data": "x" * 1000000}  # 1MB
        assert not agent._guardrails.validate_cache_value(oversized_value), (
            "Guardrails should block oversized values"
        )

        # Test circular references
        circular_dict = {}
        circular_dict["self"] = circular_dict
        assert not agent._guardrails.validate_cache_value(circular_dict), (
            "Guardrails should block circular references"
        )

    def test_healing_depth_tracking(self):
        """Test healing depth limits prevent infinite loops."""
        agent = RGAgentBase()
        violation_id = "test_violation_123"
        agent_name = "TestRGAgent"

        # Should allow healing up to limit (5)
        for i in range(5):
            assert agent._guardrails.check_healing_depth(agent_name, violation_id), (
                f"Healing depth {i + 1} should be allowed"
            )
            agent._guardrails.increment_healing_depth(agent_name, violation_id)

        # Should block on 6th attempt
        assert not agent._guardrails.check_healing_depth(agent_name, violation_id), (
            "Healing depth limit should be enforced"
        )

        # Test depth reset
        agent._guardrails.reset_healing_depth(agent_name, violation_id)
        assert agent._guardrails.check_healing_depth(agent_name, violation_id), (
            "Healing should be allowed after reset"
        )

    def test_rate_limiting(self):
        """Test rate limiting prevents API abuse."""
        agent = LICAgentBase()
        domain = "apps_lic"

        # Test request rate limiting
        for i in range(100):  # Should be under 1000/min limit
            assert agent._guardrails.check_rate_limit(domain, "request"), (
                f"Request {i + 1} should be allowed"
            )

        # Test pattern rate limiting
        for i in range(100):  # Should be under 100/min limit
            assert agent._guardrails.check_rate_limit(domain, "pattern"), (
                f"Pattern {i + 1} should be allowed"
            )

    def test_domain_isolation(self):
        """Test domain isolation prevents cross-domain contamination."""
        rg_agent = RGAgentBase()
        lic_agent = LICAgentBase()

        # Test pattern validation
        rg_pattern = {
            "violation_type": "resume_structure",
            "healing_strategy": {"action": "add_section"},
            "domain": "apps_rg",
        }

        lic_pattern = {
            "violation_type": "campaign_timeout",
            "healing_strategy": {"action": "retry_with_backoff"},
            "domain": "apps_lic",
        }

        # RG should accept RG patterns
        assert rg_agent._guardrails.validate_domain_isolation("apps_rg", rg_pattern), (
            "RG should accept RG patterns"
        )

        # RG should reject LIC patterns
        assert not rg_agent._guardrails.validate_domain_isolation("apps_rg", lic_pattern), (
            "RG should reject LIC patterns"
        )

        # LIC should accept LIC patterns
        assert lic_agent._guardrails.validate_domain_isolation("apps_lic", lic_pattern), (
            "LIC should accept LIC patterns"
        )

        # LIC should reject RG patterns
        assert not lic_agent._guardrails.validate_domain_isolation("apps_lic", rg_pattern), (
            "LIC should reject RG patterns"
        )

    def test_ttl_validation(self):
        """Test TTL validation enforces reasonable limits."""
        agent = RGAgentBase()

        # Test default TTL
        default_ttl = agent._guardrails.validate_ttl(None)
        assert default_ttl == 3600, "Default TTL should be 3600 seconds"

        # Test valid TTL range
        valid_ttl = agent._guardrails.validate_ttl(1800)  # 30 minutes
        assert valid_ttl == 1800, "Valid TTL should be accepted"

        # Test TTL too large (should be capped)
        large_ttl = agent._guardrails.validate_ttl(100000)  # > 24 hours
        assert large_ttl == 86400, "TTL should be capped at 24 hours"

        # Test TTL too small (should use minimum)
        small_ttl = agent._guardrails.validate_ttl(10)  # < 1 minute
        assert small_ttl == 60, "TTL should use minimum of 1 minute"

    def test_similarity_threshold_validation(self):
        """Test similarity threshold validation enforces reasonable limits."""
        agent = LICAgentBase()

        # Test default threshold
        default_threshold = agent._guardrails.validate_similarity_threshold(None)
        assert default_threshold == 0.92, "Default threshold should be 0.92 for LIC"

        # Test valid threshold range
        valid_threshold = agent._guardrails.validate_similarity_threshold(0.88)
        assert valid_threshold == 0.88, "Valid threshold should be accepted"

        # Test threshold too high (should be capped)
        high_threshold = agent._guardrails.validate_similarity_threshold(1.5)
        assert high_threshold == 1.0, "Threshold should be capped at 1.0"

        # Test threshold too low (should use minimum)
        low_threshold = agent._guardrails.validate_similarity_threshold(0.5)
        assert low_threshold == 0.70, "Threshold should use minimum of 0.70"


class TestCacheStrategyManagement:
    """Test cache strategy management features."""

    def test_cache_size_limits(self):
        """Test cache size limits prevent memory exhaustion."""
        agent = RGAgentBase()
        domain = "apps_rg"

        # Should allow caching under limit
        assert agent._guardrails.check_cache_size_limit(domain), (
            "Caching should be allowed under size limit"
        )

        # Simulate cache at limit
        agent._guardrails.update_cache_size(domain, 10000)  # At limit

        # Should block when at limit
        assert not agent._guardrails.check_cache_size_limit(domain), (
            "Caching should be blocked at size limit"
        )

    def test_eviction_policies(self):
        """Test cache eviction policies work correctly."""
        from agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types import (
            EvictionPolicy,
        )

        agent = LICAgentBase()
        domain = "apps_lic"

        # Test LRU eviction
        config = agent._guardrails.get_domain_config(domain)
        config.eviction_policy = EvictionPolicy.LRU

        # Record some accesses
        keys = [f"meta_learning:apps_rg:key_{i}" for i in range(10)]
        for i, key in enumerate(keys):
            agent._guardrails._access_times[key] = time.time() - (10 - i) * 100  # Older first

        # Get eviction candidates
        candidates = agent._guardrails.get_eviction_candidates(domain, 100)
        assert len(candidates) > 0, "Should have eviction candidates"
        assert candidates[0].endswith("key_0"), "Should evict oldest first"

    def test_statistics_tracking(self):
        """Test statistics tracking provides observability."""
        agent = RGAgentBase()

        # Trigger some statistics
        agent._guardrails.check_rate_limit("apps_rg", "request")
        agent._guardrails.validate_cache_key("../../../etc/passwd")
        agent._guardrails.check_healing_depth("TestAgent", "test_violation")

        # Get statistics
        stats = agent._guardrails.get_stats()

        assert "cache_sizes" in stats, "Should track cache sizes"
        assert "request_rates" in stats, "Should track request rates"
        assert "depth_trackers" in stats, "Should track healing depth"
        assert stats["depth_trackers"]["TestAgent"] == 1, "Should track healing depth"


class TestInputSanitization:
    """Test input sanitization prevents cache poisoning."""

    def test_violation_data_sanitization(self):
        """Test violation data is properly sanitized."""
        agent = LICAgentBase()

        # Test malicious violation data
        malicious_violation = {
            "type": "test_violation",
            "path": "/normal/path",
            "message": "Normal message\x00malicious content",
            "extra_field": "should_be_removed",
            "dangerous_script": "<script>alert('xss')</script>",
        }

        sanitized = agent._guardrails.sanitize_violation_data(malicious_violation)

        # Should only allow safe fields
        allowed_fields = {
            "type",
            "path",
            "message",
            "file_path",
            "import_statement",
            "file_layer",
            "import_layer",
            "violation_type",
            "line_number",
        }

        for field in sanitized.keys():
            assert field in allowed_fields, f"Field {field} should not be allowed"

        # Should remove null bytes and limit length
        assert "\x00" not in sanitized["message"], "Null bytes should be removed"
        assert len(sanitized["message"]) <= 1000, "Message should be length-limited"

    def test_safe_cache_key_generation(self):
        """Test cache key generation is deterministic and safe."""
        agent = RGAgentBase()

        data = {"type": "test", "path": "/path/to/file", "message": "test message"}
        key1 = agent._guardrails.generate_safe_cache_key("test", data)
        key2 = agent._guardrails.generate_safe_cache_key("test", data)

        # Should be deterministic
        assert key1 == key2, "Cache key generation should be deterministic"

        # Should be safe format
        assert ":" in key1, "Key should contain separator"
        assert len(key1) < 100, "Key should be reasonable length"
        assert key1.replace(":", "").replace("-", "").replace("_", "").isalnum(), (
            "Key should contain only safe characters"
        )


if __name__ == "__main__":
    pytest.main([__file__])
