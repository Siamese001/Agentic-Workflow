"""
Phase 1.1 Test Suite: Guardrails Integration Foundation

Tests the critical security infrastructure added to RGAgentBase and LICAgentBase
for cache poisoning protection, healing depth tracking, and domain isolation.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Reset guardrails before importing to ensure clean state
from agentic_core.L1_cognition.meta_learning.guardrails import reset_guardrails

reset_guardrails()


class TestRGGuardrailsIntegration:
    """Test guardrails integration for RG domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_agent_has_guardrails_attribute(self):
        """Test RGAgentBase has _guardrails attribute after initialization."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            assert agent._guardrails is not None, "RG agent should have guardrails"

    def test_rg_guardrails_threshold_configuration(self):
        """Test RG guardrails uses correct similarity threshold (0.85)."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._similarity_threshold = 0.85
            agent._rg_ttl = 3600
            agent._guardrails = None
            agent._initialize_guardrails()

            assert agent._guardrails.guardrails.default_similarity_threshold == 0.85
            assert agent._guardrails.guardrails.default_ttl == 3600

    def test_rg_cache_key_validation_safe_keys(self):
        """Test RG guardrails accepts safe cache keys."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            safe_keys = [
                "resume_quality:pattern_001",
                "ats_compat:lever",
                "section_balance:software_engineer",
                "test-key-123",
                "key_with_underscores",
            ]

            for key in safe_keys:
                assert agent.guardrails_validate_cache_key(key), f"Should accept safe key: {key}"

    def test_rg_cache_key_validation_dangerous_keys(self):
        """Test RG guardrails rejects dangerous cache keys."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            dangerous_keys = [
                "../../../etc/passwd",
                "/absolute/path",
                "key\x00null",
                "key\ninjection",
                "key with spaces",
                "",
                None,
            ]

            for key in dangerous_keys:
                result = agent.guardrails_validate_cache_key(key) if key else False
                assert not result, f"Should reject dangerous key: {repr(key)}"

    def test_rg_cache_value_validation(self):
        """Test RG guardrails validates cache values correctly."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Safe values
            safe_values = [
                {"type": "test", "data": "small"},
                ["item1", "item2"],
                "simple string",
                123,
                None,
            ]

            for value in safe_values:
                assert agent.guardrails_validate_cache_value(value), (
                    f"Should accept safe value: {value}"
                )

            # Oversized value (>100KB)
            oversized = {"data": "x" * 200000}
            assert not agent.guardrails_validate_cache_value(oversized), (
                "Should reject oversized value"
            )

    def test_rg_healing_depth_tracking(self):
        """Test RG guardrails tracks healing depth correctly."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            violation_id = "test_violation_rg"

            # Should allow healing up to depth limit (5)
            for i in range(5):
                assert agent.guardrails_check_healing_depth(violation_id), (
                    f"Should allow healing at depth {i}"
                )
                agent.guardrails_increment_healing_depth(violation_id)

            # Should block at depth 5
            assert not agent.guardrails_check_healing_depth(violation_id), (
                "Should block healing at depth limit"
            )

            # Reset should allow healing again
            agent.guardrails_reset_healing_depth(violation_id)
            assert agent.guardrails_check_healing_depth(violation_id), (
                "Should allow healing after reset"
            )

    def test_rg_rate_limiting(self):
        """Test RG guardrails rate limiting works."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Should allow requests under limit
            for i in range(10):
                assert agent.guardrails_check_rate_limit("request"), f"Should allow request {i + 1}"

    def test_rg_statistics_tracking(self):
        """Test RG guardrails provides statistics."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            stats = agent.guardrails_get_stats()

            assert "cache_sizes" in stats
            assert "request_rates" in stats
            assert "pattern_rates" in stats
            assert "depth_trackers" in stats


class TestLICGuardrailsIntegration:
    """Test guardrails integration for LIC domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_lic_agent_has_guardrails_attribute(self):
        """Test LICAgentBase has _guardrails attribute after initialization."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            assert agent._guardrails is not None, "LIC agent should have guardrails"

    def test_lic_guardrails_threshold_configuration(self):
        """Test LIC guardrails uses correct similarity threshold (0.92 - stricter)."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._similarity_threshold = 0.92
            agent._lic_ttl = 7200
            agent._guardrails = None
            agent._initialize_guardrails()

            assert agent._guardrails.guardrails.default_similarity_threshold == 0.92
            assert agent._guardrails.guardrails.default_ttl == 7200

    def test_lic_cache_key_validation_safe_keys(self):
        """Test LIC guardrails accepts safe cache keys."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            safe_keys = [
                "campaign_pattern:campaign_001",
                "compliance_rule:gdpr",
                "incident_resolution:api_timeout",
                "test-key-456",
                "key_with_underscores",
            ]

            for key in safe_keys:
                assert agent.guardrails_validate_cache_key(key), f"Should accept safe key: {key}"

    def test_lic_cache_key_validation_dangerous_keys(self):
        """Test LIC guardrails rejects dangerous cache keys."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            dangerous_keys = [
                "../../../etc/passwd",
                "/absolute/path",
                "key\x00null",
                "key\ninjection",
                "key with spaces",
                "",
                None,
            ]

            for key in dangerous_keys:
                result = agent.guardrails_validate_cache_key(key) if key else False
                assert not result, f"Should reject dangerous key: {repr(key)}"

    def test_lic_healing_depth_tracking(self):
        """Test LIC guardrails tracks healing depth correctly."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            violation_id = "test_violation_lic"

            # Should allow healing up to depth limit (5)
            for i in range(5):
                assert agent.guardrails_check_healing_depth(violation_id), (
                    f"Should allow healing at depth {i}"
                )
                agent.guardrails_increment_healing_depth(violation_id)

            # Should block at depth 5
            assert not agent.guardrails_check_healing_depth(violation_id), (
                "Should block healing at depth limit"
            )

            # Reset should allow healing again
            agent.guardrails_reset_healing_depth(violation_id)
            assert agent.guardrails_check_healing_depth(violation_id), (
                "Should allow healing after reset"
            )

    def test_lic_rate_limiting(self):
        """Test LIC guardrails rate limiting works."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            # Should allow requests under limit
            for i in range(10):
                assert agent.guardrails_check_rate_limit("request"), f"Should allow request {i + 1}"

    def test_lic_statistics_tracking(self):
        """Test LIC guardrails provides statistics."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            stats = agent.guardrails_get_stats()

            assert "cache_sizes" in stats
            assert "request_rates" in stats
            assert "pattern_rates" in stats
            assert "depth_trackers" in stats


class TestCrossDomainIsolation:
    """Test that domains are properly isolated."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_domain_isolation_accepts_rg_patterns(self):
        """Test RG accepts patterns marked for RG domain."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            rg_pattern = {
                "violation_type": "resume_structure",
                "healing_strategy": {"action": "add_section"},
                "domain": "apps_rg",
            }

            assert agent.guardrails_validate_domain_isolation(rg_pattern), (
                "RG should accept RG patterns"
            )

    def test_rg_domain_isolation_rejects_lic_patterns(self):
        """Test RG rejects patterns marked for LIC domain."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            lic_pattern = {
                "violation_type": "campaign_timeout",
                "healing_strategy": {"action": "retry"},
                "domain": "apps_lic",
            }

            assert not agent.guardrails_validate_domain_isolation(lic_pattern), (
                "RG should reject LIC patterns"
            )

    def test_lic_domain_isolation_accepts_lic_patterns(self):
        """Test LIC accepts patterns marked for LIC domain."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            lic_pattern = {
                "violation_type": "campaign_timeout",
                "healing_strategy": {"action": "retry"},
                "domain": "apps_lic",
            }

            assert agent.guardrails_validate_domain_isolation(lic_pattern), (
                "LIC should accept LIC patterns"
            )

    def test_lic_domain_isolation_rejects_rg_patterns(self):
        """Test LIC rejects patterns marked for RG domain."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            rg_pattern = {
                "violation_type": "resume_structure",
                "healing_strategy": {"action": "add_section"},
                "domain": "apps_rg",
            }

            assert not agent.guardrails_validate_domain_isolation(rg_pattern), (
                "LIC should reject RG patterns"
            )


class TestViolationSanitization:
    """Test violation data sanitization."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_sanitizes_violation_removes_dangerous_content(self):
        """Test RG sanitizes violation data to remove dangerous content."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            malicious_violation = {
                "type": "test_violation",
                "path": "/normal/path",
                "message": "Normal message\x00malicious content",
                "extra_field": "should_be_removed",
                "dangerous_script": "<script>alert('xss')</script>",
            }

            sanitized = agent.guardrails_sanitize_violation(malicious_violation)

            # Should keep safe fields
            assert "type" in sanitized
            assert "path" in sanitized
            assert "message" in sanitized

            # Should remove dangerous fields
            assert "extra_field" not in sanitized
            assert "dangerous_script" not in sanitized

            # Should remove null bytes
            assert "\x00" not in sanitized.get("message", "")

    def test_lic_sanitizes_violation_removes_dangerous_content(self):
        """Test LIC sanitizes violation data to remove dangerous content."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._guardrails = None
            agent._initialize_guardrails()

            malicious_violation = {
                "type": "test_violation",
                "path": "/normal/path",
                "message": "Normal message\x00malicious content",
                "extra_field": "should_be_removed",
            }

            sanitized = agent.guardrails_sanitize_violation(malicious_violation)

            # Should keep safe fields
            assert "type" in sanitized
            assert "path" in sanitized

            # Should remove dangerous fields
            assert "extra_field" not in sanitized

            # Should remove null bytes
            assert "\x00" not in sanitized.get("message", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
