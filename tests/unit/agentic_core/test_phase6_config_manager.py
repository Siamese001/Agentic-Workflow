"""
Test Suite for Phase 6 configuration Manager

Tests TC-PHASE6-001 through TC-PHASE6-004:
- Config defaults
- Environment variable override
- Mixin access
- Type safety on invalid values
"""

import os
import pytest
from unittest import mock
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


class TestSovereignConfigManager:
    """Tests for SovereignConfigManager."""

    def setup_method(self):
        """Reset singleton and clear env vars before each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager

        SovereignConfigManager.reset_instance()
        # Clear relevant env vars
        keys = ["SOVEREIGN_MAX_AUDIT_LOG_SIZE", "OPENAI_MODEL", "SOVEREIGN_MAX_HEALING_ATTEMPTS"]
        for k in keys:
            if k in os.environ:
                del os.environ[k]

    def teardown_method(self):
        """Clean up singleton after each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager

        SovereignConfigManager.reset_instance()
        # Clear env vars again
        keys = ["SOVEREIGN_MAX_AUDIT_LOG_SIZE", "OPENAI_MODEL", "SOVEREIGN_MAX_HEALING_ATTEMPTS"]
        for k in keys:
            if k in os.environ:
                del os.environ[k]

    def test_singleton_integrity(self):
        """Test that get_sovereign_config returns the same instance."""
        from agentic_core.config.SovereignConfigManager import get_sovereign_config

        c1 = get_sovereign_config()
        c2 = get_sovereign_config()

        assert c1 is c2
        assert id(c1) == id(c2)

    def test_tc_phase6_001_config_defaults(self):
        """
        TC-PHASE6-001: Config Defaults

        Procedure:
        1. Reset instance
        2. Get instance
        3. Check max_audit_log_size

        Expected:
        - Should equal 1000 (Default constant)
        - Verifies defaults are hardcoded correctly
        """
        from agentic_core.config.SovereignConfigManager import get_sovereign_config

        config = get_sovereign_config()

        assert config.max_audit_log_size == 1000
        assert config.max_healing_attempts == 3
        assert config.openai_model == "gpt-4o"
        assert config.anthropic_model == "claude-3-5-sonnet-20241022"
        assert config.google_model == "gemini-1.5-pro"

    def test_tc_phase6_002_env_override(self):
        """
        TC-PHASE6-002: Environment Override

        Procedure:
        1. Reset instance
        2. Set os.environ["SOVEREIGN_MAX_AUDIT_LOG_SIZE"] = "50"
        3. Get instance and check value

        Expected:
        - Should equal 50
        - Verifies strict type casting (str -> int)
        """
        from agentic_core.config.SovereignConfigManager import get_sovereign_config

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_AUDIT_LOG_SIZE": "999"}):
            config = get_sovereign_config()
            assert config.max_audit_log_size == 999

    def test_tc_phase6_004_type_safety(self):
        """
        TC-PHASE6-004: Type Safety

        Procedure:
        1. Set env var SOVEREIGN_MAX_AUDIT_LOG_SIZE = "invalid"
        2. Access property

        Expected:
        - Should return default 1000
        - Should NOT crash (Exception caught)
        - Verifies resilience
        """
        from agentic_core.config.SovereignConfigManager import get_sovereign_config

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_AUDIT_LOG_SIZE": "not-an-int"}):
            config = get_sovereign_config()
            # Should fall back to default, not crash
            assert config.max_audit_log_size == 1000

    def test_get_bool_true_values(self):
        """Test that get_bool correctly parses true values."""
        from agentic_core.config.SovereignConfigManager import get_sovereign_config

        config = get_sovereign_config()

        for true_val in ["true", "True", "TRUE", "1", "yes", "on"]:
            with mock.patch.dict(os.environ, {"TEST_BOOL": true_val}):
                assert config.get_bool("TEST_BOOL", False) is True

    def test_get_bool_false_values(self):
        """Test that get_bool correctly parses false values."""
        from agentic_core.config.SovereignConfigManager import get_sovereign_config

        config = get_sovereign_config()

        for false_val in ["false", "False", "0", "no", "off", "anything"]:
            with mock.patch.dict(os.environ, {"TEST_BOOL": false_val}):
                assert config.get_bool("TEST_BOOL", True) is False

    def test_get_str_default(self):
        """Test that get_str returns default when env var not set."""
        from agentic_core.config.SovereignConfigManager import get_sovereign_config

        config = get_sovereign_config()

        result = config.get_str("NONEXISTENT_KEY", "default_value")
        assert result == "default_value"

    def test_reset_instance(self):
        """Test that reset_instance creates a new singleton."""
        from agentic_core.config.SovereignConfigManager import (
            SovereignConfigManager,
            get_sovereign_config,
        )

        c1 = get_sovereign_config()
        SovereignConfigManager.reset_instance()
        c2 = get_sovereign_config()

        assert id(c1) != id(c2)


class TestConfigMixin:
    """Tests for ConfigMixin."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager

        SovereignConfigManager.reset_instance()

    def teardown_method(self):
        """Clean up singleton after each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager

        SovereignConfigManager.reset_instance()

    def test_tc_phase6_003_mixin_access(self):
        """
        TC-PHASE6-003: Mixin Access

        Procedure:
        1. Create dummy class with ConfigMixin
        2. Access self.config.openai_model

        Expected:
        - Should return default "gpt-4o"
        - Verifies mixin singleton wiring
        """
        from agentic_core.config.config_mixin import ConfigMixin

        class Agent(ConfigMixin):
            pass

        agent = Agent()
        assert agent.config.google_model == "gemini-1.5-pro"
        assert agent.config.openai_model == "gpt-4o"

    def test_mixin_lazy_loads_config(self):
        """Test that mixin lazy-loads the config manager."""
        from agentic_core.config.config_mixin import ConfigMixin

        class TestAgent(ConfigMixin):
            pass

        agent = TestAgent()

        assert agent._config_manager is None

        config = agent.config

        assert config is not None
        assert agent._config_manager is config

    def test_mixin_returns_same_instance(self):
        """Test that mixin returns the same config instance."""
        from agentic_core.config.config_mixin import ConfigMixin

        class TestAgent(ConfigMixin):
            pass

        agent = TestAgent()

        config1 = agent.config
        config2 = agent.config

        assert config1 is config2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
