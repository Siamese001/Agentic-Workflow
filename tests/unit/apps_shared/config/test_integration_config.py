"""Tests for IntegrationConfig."""

import pytest

from apps_shared.config.integration_config import (
    LIC_CONFIG,
    RG_CONFIG,
    IntegrationConfig,
    get_domain_config,
)


class TestIntegrationConfig:
    """Tests for IntegrationConfig dataclass."""

    def test_create_config(self):
        """Test creating an integration config."""
        config = IntegrationConfig(
            domain="test",
            domain_prefix="apps_test",
            similarity_threshold=0.85,
            ttl_seconds=3600,
        )
        assert config.domain == "test"
        assert config.domain_prefix == "apps_test"
        assert config.similarity_threshold == 0.85
        assert config.ttl_seconds == 3600

    def test_default_values(self):
        """Test default values."""
        config = IntegrationConfig(
            domain="test",
            domain_prefix="apps_test",
            similarity_threshold=0.85,
            ttl_seconds=3600,
        )
        assert config.rate_limit_requests == 100
        assert config.rate_limit_window_seconds == 60
        assert config.required_flags == []
        assert config.optional_flags == []

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = IntegrationConfig(
            domain="test",
            domain_prefix="apps_test",
            similarity_threshold=0.85,
            ttl_seconds=3600,
            required_flags=["FLAG1"],
        )
        d = config.to_dict()

        assert d["domain"] == "test"
        assert d["domain_prefix"] == "apps_test"
        assert d["similarity_threshold"] == 0.85
        assert d["ttl_seconds"] == 3600
        assert d["required_flags"] == ["FLAG1"]


class TestPredefinedConfigs:
    """Tests for predefined configurations."""

    def test_rg_config_values(self):
        """Test RG configuration values."""
        assert RG_CONFIG.domain == "rg"
        assert RG_CONFIG.domain_prefix == "apps_rg"
        assert RG_CONFIG.similarity_threshold == 0.85
        assert RG_CONFIG.ttl_seconds == 3600

    def test_rg_config_flags(self):
        """Test RG configuration flags."""
        assert "ENABLE_VERIFICATION_GATE" in RG_CONFIG.required_flags
        assert "ENABLE_AUDIT_TRAIL" in RG_CONFIG.required_flags
        assert "ENABLE_META_LEARNING" in RG_CONFIG.optional_flags

    def test_lic_config_values(self):
        """Test LIC configuration values."""
        assert LIC_CONFIG.domain == "lic"
        assert LIC_CONFIG.domain_prefix == "apps_lic"
        assert LIC_CONFIG.similarity_threshold == 0.92
        assert LIC_CONFIG.ttl_seconds == 7200

    def test_lic_config_stricter_threshold(self):
        """Test LIC has stricter threshold than RG."""
        assert LIC_CONFIG.similarity_threshold > RG_CONFIG.similarity_threshold

    def test_lic_config_longer_ttl(self):
        """Test LIC has longer TTL than RG."""
        assert LIC_CONFIG.ttl_seconds > RG_CONFIG.ttl_seconds

    def test_lic_config_requires_hitl(self):
        """Test LIC requires HITL workflow."""
        assert "ENABLE_HITL_WORKFLOW" in LIC_CONFIG.required_flags
        assert "ENABLE_HITL_WORKFLOW" not in RG_CONFIG.required_flags

    def test_lic_config_more_conservative_rate_limit(self):
        """Test LIC has more conservative rate limit."""
        assert LIC_CONFIG.rate_limit_requests < RG_CONFIG.rate_limit_requests


class TestGetDomainConfig:
    """Tests for get_domain_config function."""

    def test_get_rg_config(self):
        """Test getting RG config."""
        config = get_domain_config("rg")
        assert config is RG_CONFIG

    def test_get_lic_config(self):
        """Test getting LIC config."""
        config = get_domain_config("lic")
        assert config is LIC_CONFIG

    def test_get_config_with_apps_prefix(self):
        """Test getting config with apps_ prefix."""
        rg_config = get_domain_config("apps_rg")
        assert rg_config is RG_CONFIG

        lic_config = get_domain_config("apps_lic")
        assert lic_config is LIC_CONFIG

    def test_get_unknown_domain_raises(self):
        """Test getting unknown domain raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_domain_config("unknown")

        assert "Unknown domain" in str(exc_info.value)
        assert "unknown" in str(exc_info.value)
