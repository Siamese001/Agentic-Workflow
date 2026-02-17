"""
Unit Tests for Unified Configuration Helper - Phase 1.2

Tests the configuration system integration including:
- Category defaults
- Configuration merging
- Unified config loading
- Configuration validation
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from apps_shared.config.config_loader_config import ConfigLoadResult
from apps_shared.config.unified_config_helper import (
    CATEGORY_DEFAULTS,
    UnifiedConfigLoader,
    deep_merge,
    get_category_defaults,
    get_unified_config_loader,
    load_unified_config,
    merge_with_defaults,
    validate_unified_config,
)


class TestCategoryDefaults:
    """Tests for category defaults."""

    def test_all_categories_have_defaults(self):
        """Test all expected categories have defaults defined."""
        expected_categories = [
            "validator",
            "orchestrator",
            "healer",
            "generic",
            "executor",
            "monitor",
            "analyzer",
            "governor",
        ]
        for category in expected_categories:
            assert category in CATEGORY_DEFAULTS
            assert isinstance(CATEGORY_DEFAULTS[category], dict)

    def test_validator_defaults(self):
        """Test validator category defaults."""
        defaults = CATEGORY_DEFAULTS["validator"]
        assert "validation_rules" in defaults
        assert "forbidden_content" in defaults
        assert "required_content" in defaults
        assert "thresholds" in defaults
        assert "stop_words" in defaults

    def test_orchestrator_defaults(self):
        """Test orchestrator category defaults."""
        defaults = CATEGORY_DEFAULTS["orchestrator"]
        assert "workflow_steps" in defaults
        assert "signal_handlers" in defaults
        assert "retry_config" in defaults
        assert "timeout_config" in defaults

    def test_healer_defaults(self):
        """Test healer category defaults."""
        defaults = CATEGORY_DEFAULTS["healer"]
        assert "healing_rules" in defaults
        assert "auto_fix" in defaults
        assert defaults["auto_fix"] is False
        assert "dry_run_default" in defaults
        assert defaults["dry_run_default"] is True

    def test_generic_defaults(self):
        """Test generic category defaults."""
        defaults = CATEGORY_DEFAULTS["generic"]
        assert "execution_mode" in defaults
        assert "logging_level" in defaults


class TestGetCategoryDefaults:
    """Tests for get_category_defaults function."""

    def test_returns_copy(self):
        """Test that function returns a copy, not the original."""
        defaults1 = get_category_defaults("validator")
        defaults2 = get_category_defaults("validator")

        defaults1["test_key"] = "test_value"

        assert "test_key" not in defaults2
        assert "test_key" not in CATEGORY_DEFAULTS["validator"]

    def test_case_insensitive(self):
        """Test category lookup is case insensitive."""
        defaults_lower = get_category_defaults("validator")
        defaults_upper = get_category_defaults("VALIDATOR")
        defaults_mixed = get_category_defaults("Validator")

        assert defaults_lower == defaults_upper == defaults_mixed

    def test_unknown_category_returns_empty(self):
        """Test unknown category returns empty dict."""
        defaults = get_category_defaults("unknown_category")
        assert defaults == {}


class TestDeepMerge:
    """Tests for deep_merge function."""

    def test_simple_merge(self):
        """Test simple dictionary merge."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = deep_merge(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self):
        """Test nested dictionary merge."""
        base = {"outer": {"a": 1, "b": 2}}
        override = {"outer": {"b": 3, "c": 4}}

        result = deep_merge(base, override)

        assert result == {"outer": {"a": 1, "b": 3, "c": 4}}

    def test_deep_nested_merge(self):
        """Test deeply nested dictionary merge."""
        base = {"l1": {"l2": {"l3": {"a": 1}}}}
        override = {"l1": {"l2": {"l3": {"b": 2}}}}

        result = deep_merge(base, override)

        assert result == {"l1": {"l2": {"l3": {"a": 1, "b": 2}}}}

    def test_override_non_dict_with_dict(self):
        """Test overriding non-dict value with dict."""
        base = {"key": "string_value"}
        override = {"key": {"nested": "value"}}

        result = deep_merge(base, override)

        assert result == {"key": {"nested": "value"}}

    def test_override_dict_with_non_dict(self):
        """Test overriding dict value with non-dict."""
        base = {"key": {"nested": "value"}}
        override = {"key": "string_value"}

        result = deep_merge(base, override)

        assert result == {"key": "string_value"}

    def test_preserves_base(self):
        """Test that base dictionary is not modified."""
        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"d": 3}}

        deep_merge(base, override)

        assert base == {"a": 1, "b": {"c": 2}}


class TestMergeWithDefaults:
    """Tests for merge_with_defaults function."""

    def test_fills_missing_fields(self):
        """Test that missing fields are filled from defaults."""
        config = {"validation_rules": {"rule1": {}}}

        result = merge_with_defaults(config, "validator")

        assert "forbidden_content" in result
        assert "required_content" in result
        assert "thresholds" in result
        assert result["validation_rules"] == {"rule1": {}}

    def test_preserves_user_values(self):
        """Test that user values are preserved over defaults."""
        config = {
            "validation_rules": {"custom_rule": {}},
            "forbidden_content": ["bad_word"],
        }

        result = merge_with_defaults(config, "validator")

        assert result["forbidden_content"] == ["bad_word"]
        assert result["validation_rules"] == {"custom_rule": {}}

    def test_unknown_category_returns_config_only(self):
        """Test unknown category returns config without defaults."""
        config = {"custom_key": "custom_value"}

        result = merge_with_defaults(config, "unknown")

        assert result == {"custom_key": "custom_value"}


class TestLoadUnifiedConfig:
    """Tests for load_unified_config function."""

    def test_loads_with_defaults_on_missing_file(self):
        """Test loading returns defaults when file is missing."""
        with patch("apps_shared.config.unified_config_helper.load_agent_config") as mock_load:
            mock_load.side_effect = RuntimeError("File not found")

            result = load_unified_config("nonexistent_agent", "validator")

            assert "validation_rules" in result
            assert "forbidden_content" in result

    def test_merges_file_config_with_defaults(self):
        """Test file config is merged with defaults."""
        file_config = {"validation_rules": {"rule1": {}}, "custom_field": "value"}

        with patch("apps_shared.config.unified_config_helper.load_agent_config") as mock_load:
            mock_load.return_value = file_config

            result = load_unified_config("test_agent", "validator")

            assert result["validation_rules"] == {"rule1": {}}
            assert result["custom_field"] == "value"
            assert "forbidden_content" in result  # From defaults


class TestValidateUnifiedConfig:
    """Tests for validate_unified_config function."""

    def test_valid_validator_config(self):
        """Test valid validator config passes validation."""
        config = {
            "validation_rules": {"rule1": {}},
            "forbidden_content": [],
            "required_content": [],
        }

        result = validate_unified_config(config, "validator")

        assert result.success is True
        assert len(result.errors) == 0

    def test_missing_required_field(self):
        """Test missing required field fails validation."""
        config = {"forbidden_content": []}  # Missing validation_rules

        result = validate_unified_config(config, "validator")

        assert result.success is False
        assert any("validation_rules" in error for error in result.errors)

    def test_wrong_field_type(self):
        """Test wrong field type fails validation."""
        config = {
            "validation_rules": "should_be_dict",  # Wrong type
            "forbidden_content": [],
        }

        result = validate_unified_config(config, "validator")

        assert result.success is False
        assert any("validation_rules" in error for error in result.errors)

    def test_orchestrator_validation(self):
        """Test orchestrator config validation."""
        config = {"workflow_steps": [{"name": "step1"}]}

        result = validate_unified_config(config, "orchestrator")

        assert result.success is True

    def test_healer_validation_no_required_fields(self):
        """Test healer config with no required fields passes."""
        config = {}

        result = validate_unified_config(config, "healer")

        assert result.success is True


class TestUnifiedConfigLoader:
    """Tests for UnifiedConfigLoader class."""

    @pytest.fixture
    def loader(self):
        """Create a UnifiedConfigLoader instance."""
        return UnifiedConfigLoader()

    def test_load_caches_result(self, loader):
        """Test that load caches results."""
        with patch("apps_shared.config.unified_config_helper.load_unified_config") as mock_load:
            mock_load.return_value = {"test": "config"}

            result1 = loader.load("test_agent", "validator")
            result2 = loader.load("test_agent", "validator")

            assert result1 == result2
            assert mock_load.call_count == 1

    def test_load_force_reload(self, loader):
        """Test force reload bypasses cache."""
        with patch("apps_shared.config.unified_config_helper.load_unified_config") as mock_load:
            mock_load.return_value = {"test": "config"}

            loader.load("test_agent", "validator")
            loader.load("test_agent", "validator", force_reload=True)

            assert mock_load.call_count == 2

    def test_validate_returns_result(self, loader):
        """Test validate returns ConfigLoadResult."""
        with patch("apps_shared.config.unified_config_helper.load_unified_config") as mock_load:
            mock_load.return_value = {"validation_rules": {}}

            result = loader.validate("test_agent", "validator")

            assert isinstance(result, ConfigLoadResult)
            assert result.success is True

    def test_clear_cache(self, loader):
        """Test clear_cache empties the cache."""
        with patch("apps_shared.config.unified_config_helper.load_unified_config") as mock_load:
            mock_load.return_value = {"test": "config"}

            loader.load("test_agent", "validator")
            loader.clear_cache()
            loader.load("test_agent", "validator")

            assert mock_load.call_count == 2


class TestGetUnifiedConfigLoader:
    """Tests for get_unified_config_loader function."""

    def test_returns_singleton(self):
        """Test function returns singleton instance."""
        # Reset global state
        import apps_shared.config.unified_config_helper as module

        module._unified_loader = None

        loader1 = get_unified_config_loader()
        loader2 = get_unified_config_loader()

        assert loader1 is loader2

    def test_creates_loader_with_config_root(self):
        """Test loader is created with config root."""
        from pathlib import Path

        import apps_shared.config.unified_config_helper as module

        module._unified_loader = None

        loader = get_unified_config_loader(Path("/custom/path"))

        assert loader is not None


class TestIntegration:
    """Integration tests for configuration system."""

    def test_full_config_flow(self):
        """Test full configuration loading and validation flow."""
        # Create a complete config
        config = {
            "validation_rules": {
                "pattern_check": {"type": "pattern_match", "pattern": r"test"},
                "keyword_check": {
                    "type": "keyword_check",
                    "keywords": ["python", "java"],
                },
            },
            "forbidden_content": ["bad_word"],
            "required_content": ["good_word"],
            "thresholds": {"min_score": 0.5},
        }

        # Merge with defaults
        merged = merge_with_defaults(config, "validator")

        # Validate
        result = validate_unified_config(merged, "validator")

        assert result.success is True
        assert merged["validation_rules"] == config["validation_rules"]
        assert merged["forbidden_content"] == ["bad_word"]
        assert "stop_words" in merged  # From defaults

    def test_orchestrator_config_flow(self):
        """Test orchestrator configuration flow."""
        config = {
            "workflow_steps": [
                {"name": "validate", "type": "validation"},
                {"name": "process", "type": "agent_call"},
            ],
            "signal_handlers": {"validation_failed": "retry"},
        }

        merged = merge_with_defaults(config, "orchestrator")
        result = validate_unified_config(merged, "orchestrator")

        assert result.success is True
        assert len(merged["workflow_steps"]) == 2
        assert "retry_config" in merged  # From defaults

    def test_healer_config_flow(self):
        """Test healer configuration flow."""
        config = {"auto_fix": True, "healing_rules": {"rule1": {}}}

        merged = merge_with_defaults(config, "healer")
        result = validate_unified_config(merged, "healer")

        assert result.success is True
        assert merged["auto_fix"] is True
        assert merged["dry_run_default"] is True  # From defaults


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
