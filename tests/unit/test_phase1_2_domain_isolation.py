"""
Phase 1.2 Test Suite: Domain Isolation Enforcement

Tests namespace separation and domain validation for RG and LIC domains
to prevent cross-domain contamination.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L1_cognition.meta_learning.guardrails import reset_guardrails


class TestRGDomainIsolation:
    """Test domain isolation for RG domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_namespaced_cache_key_format(self):
        """Test RG generates correctly namespaced cache keys."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"

            key = agent.get_namespaced_cache_key("test_key")

            assert key.startswith("apps_rg:"), "Key should start with apps_rg:"
            assert "rg:" in key, "Key should contain resource prefix"
            assert key == "apps_rg:rg:test_key"

    def test_rg_namespaced_cache_key_uniqueness(self):
        """Test RG namespaced keys are unique per pattern type."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"

            key1 = agent.get_namespaced_cache_key("resume_quality:pattern1")
            key2 = agent.get_namespaced_cache_key("ats_compat:lever")
            key3 = agent.get_namespaced_cache_key("section_balance:engineer")

            # All keys should be unique
            assert len({key1, key2, key3}) == 3

            # All keys should have RG namespace
            for key in [key1, key2, key3]:
                assert key.startswith("apps_rg:")

    def test_rg_validates_own_domain_patterns(self):
        """Test RG accepts patterns from its own domain."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()

            rg_pattern = {"type": "resume_quality", "domain": "apps_rg", "data": "test"}

            assert agent.validate_domain_pattern(rg_pattern)

    def test_rg_rejects_lic_domain_patterns(self):
        """Test RG rejects patterns from LIC domain."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()

            lic_pattern = {"type": "campaign", "domain": "apps_lic", "data": "test"}

            assert not agent.validate_domain_pattern(lic_pattern)

    def test_rg_accepts_patterns_without_domain(self):
        """Test RG accepts patterns without explicit domain field."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()

            generic_pattern = {"type": "test", "data": "test"}

            assert agent.validate_domain_pattern(generic_pattern)

    def test_rg_isolate_cache_operation_adds_metadata(self):
        """Test RG cache operation adds domain metadata."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._namespace = "apps_rg"
            agent._guardrails = None
            agent._initialize_guardrails()

            value = {"type": "test", "data": "test_data"}
            success, key = agent.isolate_cache_operation("set", "test_key", value)

            assert success
            assert key == "apps_rg:rg:test_key"
            assert value["_domain"] == "apps_rg"
            assert value["_namespace"] == "apps_rg"

    def test_rg_isolate_cache_operation_validates_key(self):
        """Test RG cache operation validates dangerous keys."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            agent = RGAgentBase()
            agent._resource_prefix = "rg"
            agent._guardrails = None
            agent._initialize_guardrails()

            # Dangerous key with path traversal
            success, _ = agent.isolate_cache_operation("set", "../../../etc", {})

            assert not success


class TestLICDomainIsolation:
    """Test domain isolation for LIC domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_lic_namespaced_cache_key_format(self):
        """Test LIC generates correctly namespaced cache keys."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"

            key = agent.get_namespaced_cache_key("test_key")

            assert key.startswith("apps_lic:"), "Key should start with apps_lic:"
            assert "lic:" in key, "Key should contain resource prefix"
            assert key == "apps_lic:lic:test_key"

    def test_lic_namespaced_cache_key_uniqueness(self):
        """Test LIC namespaced keys are unique per pattern type."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"

            key1 = agent.get_namespaced_cache_key("campaign:campaign1")
            key2 = agent.get_namespaced_cache_key("compliance:gdpr")
            key3 = agent.get_namespaced_cache_key("incident:timeout")

            # All keys should be unique
            assert len({key1, key2, key3}) == 3

            # All keys should have LIC namespace
            for key in [key1, key2, key3]:
                assert key.startswith("apps_lic:")

    def test_lic_validates_own_domain_patterns(self):
        """Test LIC accepts patterns from its own domain."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()

            lic_pattern = {"type": "campaign", "domain": "apps_lic", "data": "test"}

            assert agent.validate_domain_pattern(lic_pattern)

    def test_lic_rejects_rg_domain_patterns(self):
        """Test LIC rejects patterns from RG domain."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()

            rg_pattern = {"type": "resume", "domain": "apps_rg", "data": "test"}

            assert not agent.validate_domain_pattern(rg_pattern)

    def test_lic_accepts_patterns_without_domain(self):
        """Test LIC accepts patterns without explicit domain field."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()

            generic_pattern = {"type": "test", "data": "test"}

            assert agent.validate_domain_pattern(generic_pattern)

    def test_lic_isolate_cache_operation_adds_metadata(self):
        """Test LIC cache operation adds domain metadata."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"
            agent._namespace = "apps_lic"
            agent._guardrails = None
            agent._initialize_guardrails()

            value = {"type": "test", "data": "test_data"}
            success, key = agent.isolate_cache_operation("set", "test_key", value)

            assert success
            assert key == "apps_lic:lic:test_key"
            assert value["_domain"] == "apps_lic"
            assert value["_namespace"] == "apps_lic"

    def test_lic_isolate_cache_operation_validates_key(self):
        """Test LIC cache operation validates dangerous keys."""
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(LICAgentBase, "__post_init__", lambda self: None):
            agent = LICAgentBase()
            agent._resource_prefix = "lic"
            agent._guardrails = None
            agent._initialize_guardrails()

            # Dangerous key with path traversal
            success, _ = agent.isolate_cache_operation("set", "../../../etc", {})

            assert not success


class TestCrossDomainPrevention:
    """Test that cross-domain access is prevented."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset guardrails state before each test."""
        reset_guardrails()
        yield
        reset_guardrails()

    def test_rg_and_lic_keys_are_distinct(self):
        """Test RG and LIC generate distinct namespaced keys."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            with patch.object(LICAgentBase, "__post_init__", lambda self: None):
                rg_agent = RGAgentBase()
                rg_agent._resource_prefix = "rg"

                lic_agent = LICAgentBase()
                lic_agent._resource_prefix = "lic"

                # Same base key
                base_key = "shared_pattern:pattern1"

                rg_key = rg_agent.get_namespaced_cache_key(base_key)
                lic_key = lic_agent.get_namespaced_cache_key(base_key)

                # Keys should be different
                assert rg_key != lic_key
                assert rg_key.startswith("apps_rg:")
                assert lic_key.startswith("apps_lic:")

    def test_domain_metadata_prevents_cross_access(self):
        """Test domain metadata in cached values prevents cross-access."""
        from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
        from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase

        with patch.object(RGAgentBase, "__post_init__", lambda self: None):
            with patch.object(LICAgentBase, "__post_init__", lambda self: None):
                rg_agent = RGAgentBase()
                rg_agent._resource_prefix = "rg"
                rg_agent._namespace = "apps_rg"
                rg_agent._guardrails = None
                rg_agent._initialize_guardrails()

                lic_agent = LICAgentBase()
                lic_agent._resource_prefix = "lic"
                lic_agent._namespace = "apps_lic"
                lic_agent._guardrails = None
                lic_agent._initialize_guardrails()

                # RG creates a value
                rg_value = {"type": "resume", "data": "test"}
                rg_agent.isolate_cache_operation("set", "test", rg_value)

                # LIC creates a value
                lic_value = {"type": "campaign", "data": "test"}
                lic_agent.isolate_cache_operation("set", "test", lic_value)

                # Values should have correct domain metadata
                assert rg_value["_domain"] == "apps_rg"
                assert lic_value["_domain"] == "apps_lic"

                # RG should reject LIC patterns
                assert not rg_agent.validate_domain_pattern(lic_value)
                # LIC should reject RG patterns
                assert not lic_agent.validate_domain_pattern(rg_value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
