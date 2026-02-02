"""
Phase 1 Optimization Tests - Configuration Loader
Tests for centralized configuration loading system.
"""

import pytest
from pathlib import Path
from apps_shared.config.config_loader_config import (
    ConfigLoader,
    ConfigLoadResult,
    load_agent_config,
    get_config_loader,
)


class TestConfigLoader:
    """Test suite for ConfigLoader class."""

    def test_config_loader_initialization(self):
        """Test that ConfigLoader initializes correctly."""
        loader = ConfigLoader()
        assert loader.config_root == Path("config/agent_configs")
        assert isinstance(loader._cache, dict)
        assert len(loader._cache) == 0

    def test_config_loader_custom_root(self):
        """Test ConfigLoader with custom root directory."""
        custom_root = "custom/config/path"
        loader = ConfigLoader(config_root=custom_root)
        assert loader.config_root == Path(custom_root)

    def test_load_ats_compatibility_config(self):
        """Test loading ATS Compatibility configuration."""
        config = load_agent_config("ats_compatibility")

        assert isinstance(config, dict)
        assert "standard_headers" in config
        assert "ats_unfriendly_patterns" in config
        assert "allowed_non_standard_sections" in config
        assert "keyword_optimization" in config

        # Verify structure
        assert isinstance(config["standard_headers"], dict)
        assert "summary" in config["standard_headers"]
        assert "experience" in config["standard_headers"]
        assert isinstance(config["ats_unfriendly_patterns"], list)
        assert len(config["ats_unfriendly_patterns"]) > 0

    def test_load_brand_compliance_config(self):
        """Test loading Brand Compliance configuration."""
        config = load_agent_config("brand_compliance")

        assert isinstance(config, dict)
        assert "forbidden_phrases" in config
        assert "power_verbs" in config
        assert "compliance_rules" in config

        # Verify lists
        assert isinstance(config["forbidden_phrases"], list)
        assert isinstance(config["power_verbs"], list)
        assert len(config["forbidden_phrases"]) > 0
        assert len(config["power_verbs"]) > 0

    def test_load_campaign_planner_config(self):
        """Test loading Campaign Planner configuration."""
        config = load_agent_config("campaign_planner")

        assert isinstance(config, dict)
        assert "agent_defaults" in config
        assert "channel_configuration" in config
        assert "strategy_parameters" in config

    def test_load_content_quality_config(self):
        """Test loading Content Quality configuration."""
        config = load_agent_config("content_quality")

        assert isinstance(config, dict)
        assert "placeholder_patterns" in config
        assert "min_section_lengths" in config
        assert "quality_metrics" in config
        assert "validation_rules" in config

    def test_load_section_balance_config(self):
        """Test loading Section Balance configuration."""
        config = load_agent_config("section_balance")

        assert isinstance(config, dict)
        assert "required_sections" in config
        assert "recommended_sections" in config
        assert "max_section_ratios" in config
        assert "balance_rules" in config

    def test_config_caching(self):
        """Test that configurations are cached."""
        loader = get_config_loader()

        # Load config first time
        config1 = loader.load_config("ats_compatibility")
        cache_size_1 = len(loader._cache)

        # Load same config again
        config2 = loader.load_config("ats_compatibility")
        cache_size_2 = len(loader._cache)

        # Cache should not grow
        assert cache_size_1 == cache_size_2
        assert config1.config == config2.config

    def test_config_reload(self):
        """Test configuration reload functionality."""
        loader = get_config_loader()

        # Load and cache
        result1 = loader.load_config("brand_compliance")

        # Reload (clears cache)
        result2 = loader.reload_config("brand_compliance")

        assert result1.config == result2.config
        assert result2.success

    def test_nonexistent_config_with_fallback(self):
        """Test loading nonexistent config with fallback."""
        loader = ConfigLoader()
        fallback = {"test": "value"}

        result = loader.load_config("nonexistent_agent", fallback_config=fallback)

        assert result.success
        assert result.config == fallback
        assert result.source == "fallback"
        assert len(result.errors) > 0

    def test_nonexistent_config_without_fallback(self):
        """Test loading nonexistent config without fallback raises error."""
        with pytest.raises(RuntimeError):
            load_agent_config("nonexistent_agent_no_fallback")

    def test_config_validation(self):
        """Test configuration validation."""
        loader = ConfigLoader()

        valid_config = {"key1": "value1", "key2": 123}
        result = loader.validate_config(valid_config)

        assert result.success
        assert result.config == valid_config
        assert len(result.errors) == 0

    def test_invalid_config_type(self):
        """Test validation of invalid config type."""
        loader = ConfigLoader()

        invalid_config = "not a dict"
        result = loader.validate_config(invalid_config)

        assert not result.success
        assert len(result.errors) > 0
        assert "must be a dictionary" in result.errors[0]


class TestConfigLoadResult:
    """Test suite for ConfigLoadResult dataclass."""

    def test_config_load_result_creation(self):
        """Test creating ConfigLoadResult."""
        result = ConfigLoadResult(
            success=True, config={"test": "data"}, errors=[], source="test.yaml"
        )

        assert result.success
        assert result.config == {"test": "data"}
        assert result.errors == []
        assert result.source == "test.yaml"

    def test_config_load_result_with_errors(self):
        """Test ConfigLoadResult with errors."""
        result = ConfigLoadResult(
            success=False, config={}, errors=["Error 1", "Error 2"], source="none"
        )

        assert not result.success
        assert len(result.errors) == 2
        assert result.config == {}


class TestGlobalConfigLoader:
    """Test suite for global config loader instance."""

    def test_get_config_loader_singleton(self):
        """Test that get_config_loader returns singleton."""
        loader1 = get_config_loader()
        loader2 = get_config_loader()

        assert loader1 is loader2

    def test_load_agent_config_convenience(self):
        """Test convenience function load_agent_config."""
        config = load_agent_config("ats_compatibility")

        assert isinstance(config, dict)
        assert len(config) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
