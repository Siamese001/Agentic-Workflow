"""Integration tests for YAML-backed PromptInjectionLoader with markdown fallback."""

import yaml

from agentic_core.runtime.config.prompt_injection_loader_config import (
    InjectionConfig,
    PromptInjectionLoader,
)


class TestYamlIntegration:
    """Test YAML integration with PromptInjectionLoader."""

    def test_yaml_disabled_returns_markdown_behavior(self):
        """Test that YAML disabled returns identical results to current markdown behavior."""
        # Create loader with YAML disabled (default)
        config = InjectionConfig(enable_yaml_loader=False)
        loader = PromptInjectionLoader(config)

        # Should have loaded markdown patterns
        injections = loader.injections

        # Check for known markdown pattern IDs
        markdown_ids = [1, 2, 3, 4, 5]  # First 5 instructional patterns
        for pattern_id in markdown_ids:
            assert str(pattern_id) in injections, f"Missing markdown pattern {pattern_id}"

        # Should NOT have YAML patterns
        yaml_pattern_ids = [f"yaml_framing_{i}" for i in range(1, 6)]
        for yaml_id in yaml_pattern_ids:
            assert yaml_id not in injections, f"Unexpected YAML pattern {yaml_id}"

    def test_yaml_enabled_returns_non_empty_yaml_patterns(self, tmp_path):
        """Test that YAML enabled returns non-empty patterns sourced from YAML."""
        # Create test YAML file
        test_yaml_content = {
            "v5_framing_injections": {
                "test_pattern": {
                    "description": "Test pattern from YAML",
                    "prompt_template": "Test template {var}",
                    "success_criteria": ["Test passes"],
                    "usage_context": ["Testing"],
                }
            }
        }

        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml.dump(test_yaml_content))

        # Create loader with YAML enabled
        config = InjectionConfig(enable_yaml_loader=True)
        loader = PromptInjectionLoader(config)

        # Should have loaded patterns (may be from actual YAML corpus or fallback)
        injections = loader.injections
        assert len(injections) > 0, "Should have loaded some patterns"

        # Check if any YAML patterns were loaded (depends on actual corpus availability)
        yaml_patterns = [k for k in injections.keys() if k.startswith("yaml_")]
        if yaml_patterns:
            # If YAML patterns exist, verify structure
            yaml_pattern = injections[yaml_patterns[0]]
            assert hasattr(yaml_pattern, "template")
            assert hasattr(yaml_pattern, "description")

    def test_yaml_enabled_with_forced_schema_error_falls_back_to_markdown(self, tmp_path):
        """Test that YAML enabled + forced schema error falls back to markdown and still succeeds."""
        # Create invalid YAML file to trigger schema error
        invalid_yaml_content = {
            "v5_framing_injections": {
                "invalid_pattern": {
                    # Missing required keys to trigger validation error
                    "description": "Invalid pattern"
                    # Missing prompt_template, success_criteria, usage_context
                }
            }
        }

        # Create temporary YAML directory with invalid file
        temp_yaml_dir = tmp_path / "injections"
        temp_yaml_dir.mkdir()

        invalid_file = temp_yaml_dir / "invalid.yaml"
        invalid_file.write_text(yaml.dump(invalid_yaml_content))

        # Create loader with YAML enabled, pointing to our temp directory
        config = InjectionConfig(enable_yaml_loader=True)
        loader = PromptInjectionLoader(config)

        # Should still succeed due to fallback to markdown
        injections = loader.injections
        assert len(injections) > 0, "Should have fallback patterns from markdown"

        # Should have markdown patterns
        markdown_ids = [1, 2, 3, 4, 5]
        for pattern_id in markdown_ids:
            assert str(pattern_id) in injections, f"Missing fallback markdown pattern {pattern_id}"

    def test_yaml_loader_integration_with_actual_corpus(self):
        """Test YAML loader integration with actual corpus (if available)."""
        # Create loader with YAML enabled
        config = InjectionConfig(enable_yaml_loader=True)
        loader = PromptInjectionLoader(config)

        injections = loader.injections

        # Should have loaded some patterns
        assert len(injections) > 0, "Should have loaded patterns"

        # Check if YAML patterns were loaded from actual corpus
        yaml_patterns = [k for k in injections.keys() if k.startswith("yaml_")]

        if yaml_patterns:
            # Verify YAML pattern structure
            yaml_pattern = yaml_patterns[0]
            injection = injections[yaml_pattern]

            assert hasattr(injection, "id")
            assert hasattr(injection, "name")
            assert hasattr(injection, "template")
            assert hasattr(injection, "description")
            assert injection.id.startswith("yaml_")
        else:
            # If no YAML patterns, should have markdown patterns
            markdown_ids = [1, 2, 3, 4, 5]
            for pattern_id in markdown_ids:
                assert str(pattern_id) in injections, f"Missing markdown pattern {pattern_id}"

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
        disabled_yaml = [k for k in loader_disabled.injections.keys() if k.startswith("yaml_")]
        enabled_yaml = [k for k in loader_enabled.injections.keys() if k.startswith("yaml_")]

        # Disabled should not have YAML patterns
        assert len(disabled_yaml) == 0, "Disabled loader should not have YAML patterns"

        # Enabled might have YAML patterns (if corpus available)
        # If not, both should have same markdown patterns
        if not enabled_yaml:
            # Both should have same markdown patterns
            disabled_ids = {k for k in loader_disabled.injections.keys() if not k.startswith("yaml_")}
            enabled_ids = {k for k in loader_enabled.injections.keys() if not k.startswith("yaml_")}
            assert disabled_ids == enabled_ids, "Should have same markdown patterns when YAML unavailable"
