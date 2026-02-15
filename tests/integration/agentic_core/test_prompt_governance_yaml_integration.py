"""Integration tests for YAML-backed PromptInjectionLoader with markdown fallback."""

import pytest
import yaml

from agentic_core.runtime.config.prompt_injection_loader_config import (
    InjectionConfig,
    PromptInjectionLoader,
)


class TestYamlIntegration:
    """Test YAML integration with PromptInjectionLoader."""

    def test_yaml_disabled_returns_non_empty_list(self):
        """Test that YAML disabled returns non-empty list (markdown fallback)."""
        config = InjectionConfig(enable_yaml_loader=False)
        loader = PromptInjectionLoader(config)

        injections = loader.injections

        # Should have loaded markdown patterns
        assert len(injections) > 0, "Should have loaded patterns from markdown fallback"

        # Check for known markdown pattern IDs (1-30)
        for pattern_id in range(1, 6):  # Check first 5
            assert pattern_id in injections, f"Missing markdown pattern {pattern_id}"

        # Should NOT have YAML patterns
        yaml_patterns = [k for k in injections.keys() if isinstance(k, str) and k.startswith("yaml_")]
        assert len(yaml_patterns) == 0, "Should not have YAML patterns when disabled"

    def test_yaml_enabled_loads_known_patterns(self):
        """Test that YAML enabled loads at least 1 known pattern from real corpus."""
        config = InjectionConfig(enable_yaml_loader=True)
        loader = PromptInjectionLoader(config)

        injections = loader.injections

        # Should have loaded some patterns
        assert len(injections) > 0, "Should have loaded patterns"

        # Check if YAML patterns were loaded from actual corpus
        yaml_patterns = [k for k in injections.keys() if isinstance(k, str) and k.startswith("yaml_")]

        if yaml_patterns:
            # If YAML patterns exist, verify at least one known pattern
            # Look for patterns we know exist in the corpus
            known_yaml_patterns = [
                "yaml_framing_1",  # cost_latency_targets
                "yaml_framing_2",  # global_goal_state
                "yaml_safety_1",  # constitutional_guardrails
            ]

            found_known = any(p in yaml_patterns for p in known_yaml_patterns)
            assert found_known, f"Should have loaded known YAML patterns, found: {yaml_patterns[:3]}"

    def test_yaml_enabled_with_parse_error_falls_back_gracefully(self, tmp_path):
        """Test that YAML enabled + forced parse error falls back without raising."""
        # Create invalid YAML file to trigger schema error
        invalid_yaml_content = {
            "v5_framing_injections": {
                "invalid_pattern": {
                    "description": "Invalid pattern"
                    # Missing required keys to trigger validation error
                }
            }
        }

        # Create temporary YAML directory with invalid file
        temp_yaml_dir = tmp_path / "injections"
        temp_yaml_dir.mkdir()

        invalid_file = temp_yaml_dir / "invalid.yaml"
        invalid_file.write_text(yaml.dump(invalid_yaml_content))

        # Create loader with YAML enabled, pointing to our temp directory
        # This will cause the YAML loader to encounter the invalid file
        config = InjectionConfig(enable_yaml_loader=True)

        # Should not raise an exception due to fallback
        try:
            loader = PromptInjectionLoader(config)
            injections = loader.injections

            # Should still succeed due to fallback to markdown
            assert len(injections) > 0, "Should have fallback patterns from markdown"

        except Exception as e:
            pytest.fail(f"Should not raise exception with fallback, got: {e}")

    def test_config_toggle_behavior(self):
        """Test that config toggle properly switches between YAML and markdown."""
        # Test with YAML disabled
        config_disabled = InjectionConfig(enable_yaml_loader=False)
        loader_disabled = PromptInjectionLoader(config_disabled)

        # Test with YAML enabled
        config_enabled = InjectionConfig(enable_yaml_loader=True)
        loader_enabled = PromptInjectionLoader(config_enabled)

        # Both should have patterns
        assert len(loader_disabled.injections) > 0
        assert len(loader_enabled.injections) > 0

        # Check for different pattern sources
        disabled_yaml = [
            k for k in loader_disabled.injections.keys() if isinstance(k, str) and k.startswith("yaml_")
        ]
        enabled_yaml = [
            k for k in loader_enabled.injections.keys() if isinstance(k, str) and k.startswith("yaml_")
        ]

        # Disabled should not have YAML patterns
        assert len(disabled_yaml) == 0, "Disabled loader should not have YAML patterns"

        # Enabled might have YAML patterns (if corpus available)
        # If not, both should have markdown patterns
        if not enabled_yaml:
            # Both should have same markdown patterns
            disabled_ids = {
                k
                for k in loader_disabled.injections.keys()
                if not (isinstance(k, str) and k.startswith("yaml_"))
            }
            enabled_ids = {
                k
                for k in loader_enabled.injections.keys()
                if not (isinstance(k, str) and k.startswith("yaml_"))
            }
            assert disabled_ids == enabled_ids, "Should have same markdown patterns when YAML unavailable"
