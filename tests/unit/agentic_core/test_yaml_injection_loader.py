"""Tests for YAML Injection Loader - Deterministic behavior and validation."""

from pathlib import Path

import pytest
import yaml

from agentic_core.config.core.injection_layer_config import InjectionLayer
from agentic_core.config.core.yaml_injection_loader import (
    YamlInjectionLoader,
    YamlValidationError,
    clear_yaml_cache,
    get_yaml_loader,
)


class TestYamlInjectionLoader:
    """Test deterministic YAML loading and validation."""

    def test_enumeration_order_is_stable(self, tmp_path):
        """Test that enumeration order is stable across runs."""
        # Create test YAML files in non-alphabetical order
        test_files = [
            ("z_framing.yaml", {"v5_framing_injections": {}}),
            ("a_safety.yaml", {"v5_safety_injections": {}}),
            ("m_reasoning.yaml", {"v5_reasoning_injections": {}}),
        ]

        for filename, content in test_files:
            (tmp_path / filename).write_text(yaml.dump(content))

        loader = YamlInjectionLoader(tmp_path)
        files1 = loader.enumerate_yaml_files()
        files2 = loader.enumerate_yaml_files()

        # Should be identical and sorted
        assert files1 == files2
        assert [f.name for f in files1] == ["a_safety.yaml", "m_reasoning.yaml", "z_framing.yaml"]

    def test_missing_required_keys_is_handled_gracefully(self, tmp_path):
        """Test that missing required keys are handled gracefully by skipping patterns."""
        # Create YAML file missing required keys
        invalid_content = {
            "v5_framing_injections": {
                "test_pattern": {
                    "description": "Test pattern",
                    # Missing prompt_template, success_criteria, usage_context
                }
            }
        }

        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text(yaml.dump(invalid_content))

        loader = YamlInjectionLoader(tmp_path)

        # Should not raise an error, but should skip the invalid pattern
        patterns = loader.load_all_patterns()

        # Should have empty patterns for framing layer since the only pattern was invalid
        framing_patterns = patterns.get("framing", [])
        assert len(framing_patterns) == 0, "Invalid pattern should be skipped"

        # Should still have other layers initialized as empty lists
        assert "framing" in patterns
        assert "safety" in patterns

    def test_yaml_parse_failure_includes_filename(self, tmp_path):
        """Test that YAML parse failure includes filename and doesn't crash unrelated loads."""
        # Create invalid YAML file
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: [")

        # Create valid YAML file
        valid_content = {
            "v5_framing_injections": {
                "test_pattern": {
                    "description": "Test pattern",
                    "prompt_template": "Test template {var}",
                    "success_criteria": ["Test passes"],
                    "usage_context": ["Testing"],
                }
            }
        }
        valid_yaml = tmp_path / "valid.yaml"
        valid_yaml.write_text(yaml.dump(valid_content))

        loader = YamlInjectionLoader(tmp_path)

        with pytest.raises(YamlValidationError) as exc_info:
            loader.load_all_patterns()

        error = exc_info.value
        assert error.filename == str(invalid_yaml)
        assert "parse error" in str(error).lower()
        assert "yaml" in str(error).lower()

    def test_deterministic_pattern_ordering(self, tmp_path):
        """Test that patterns are returned in deterministic order."""
        content = {
            "v5_framing_injections": {
                "zebra_pattern": {
                    "description": "Zebra pattern",
                    "prompt_template": "Zebra template {var}",
                    "success_criteria": ["Zebra passes"],
                    "usage_context": ["Testing"],
                },
                "alpha_pattern": {
                    "description": "Alpha pattern",
                    "prompt_template": "Alpha template {var}",
                    "success_criteria": ["Alpha passes"],
                    "usage_context": ["Testing"],
                },
                "beta_pattern": {
                    "description": "Beta pattern",
                    "prompt_template": "Beta template {var}",
                    "success_criteria": ["Beta passes"],
                    "usage_context": ["Testing"],
                },
            }
        }

        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml.dump(content))

        loader = YamlInjectionLoader(tmp_path)
        patterns = loader.load_all_patterns()

        # Patterns should be sorted alphabetically by name for deterministic IDs
        framing_patterns = patterns["framing"]
        assert len(framing_patterns) == 3
        assert framing_patterns[0].name == "alpha_pattern"  # ID 1 (alphabetical)
        assert framing_patterns[1].name == "beta_pattern"  # ID 2
        assert framing_patterns[2].name == "zebra_pattern"  # ID 3

    def test_load_by_layer_filters_correctly(self, tmp_path):
        """Test that load_by_layer returns only patterns for specified layer."""
        # Create files for different layers
        framing_content = {
            "v5_framing_injections": {
                "framing_pattern": {
                    "description": "Framing pattern",
                    "prompt_template": "Framing template {var}",
                    "success_criteria": ["Framing passes"],
                    "usage_context": ["Testing"],
                }
            }
        }

        safety_content = {
            "v5_safety_injections": {
                "safety_pattern": {
                    "description": "Safety pattern",
                    "prompt_template": "Safety template {var}",
                    "success_criteria": ["Safety passes"],
                    "usage_context": ["Testing"],
                }
            }
        }

        # Create directory structure
        framing_dir = tmp_path / "modular" / "framing"
        safety_dir = tmp_path / "modular" / "safety"
        framing_dir.mkdir(parents=True)
        safety_dir.mkdir(parents=True)

        (framing_dir / "v5_framing_injections.yaml").write_text(yaml.dump(framing_content))
        (safety_dir / "v5_safety_injections.yaml").write_text(yaml.dump(safety_content))

        loader = YamlInjectionLoader(tmp_path)

        framing_patterns = loader.load_by_layer(InjectionLayer.FRAMING)
        safety_patterns = loader.load_by_layer(InjectionLayer.SAFETY)

        assert len(framing_patterns) == 1
        assert framing_patterns[0].name == "framing_pattern"
        assert framing_patterns[0].layer == InjectionLayer.FRAMING

        assert len(safety_patterns) == 1
        assert safety_patterns[0].name == "safety_pattern"
        assert safety_patterns[0].layer == InjectionLayer.SAFETY

    def test_layer_determination_from_path(self, tmp_path):
        """Test layer determination from file paths."""
        test_cases = [
            ("modular/framing/v5_framing_injections.yaml", InjectionLayer.FRAMING),
            ("modular/safety/v5_safety_injections.yaml", InjectionLayer.SAFETY),
            ("modular/reasoning/v5_reasoning_injections.yaml", InjectionLayer.REASONING),
            ("modular/tool_use/v5_tooling_injections.yaml", InjectionLayer.TOOLING),
            ("modular/output_governance/v5_output_injections.yaml", InjectionLayer.OUTPUT),
            ("modular/context_engineering/v5_context_injections.yaml", InjectionLayer.CONTEXT),
        ]

        for relative_path, expected_layer in test_cases:
            yaml_file = tmp_path / relative_path
            yaml_file.parent.mkdir(parents=True, exist_ok=True)

            content = {
                f"v5_{expected_layer.value}_injections": {
                    "test_pattern": {
                        "description": "Test",
                        "prompt_template": "Test {var}",
                        "success_criteria": ["Test passes"],
                        "usage_context": ["Testing"],
                    }
                }
            }

            yaml_file.write_text(yaml.dump(content))

            loader = YamlInjectionLoader(tmp_path)
            patterns = loader.load_by_layer(expected_layer)

            assert len(patterns) == 1
            assert patterns[0].layer == expected_layer

    def test_enabled_flag_defaults_to_true(self, tmp_path):
        """Test that enabled flag defaults to True when not specified."""
        content = {
            "v5_framing_injections": {
                "pattern_without_enabled": {
                    "description": "Test pattern",
                    "prompt_template": "Test template {var}",
                    "success_criteria": ["Test passes"],
                    "usage_context": ["Testing"],
                },
                "pattern_disabled": {
                    "description": "Disabled pattern",
                    "prompt_template": "Disabled template {var}",
                    "success_criteria": ["Disabled passes"],
                    "usage_context": ["Testing"],
                    "enabled": False,
                },
            }
        }

        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml.dump(content))

        loader = YamlInjectionLoader(tmp_path)
        patterns = loader.load_all_patterns()["framing"]

        assert len(patterns) == 2
        # Patterns are sorted alphabetically, so pattern_disabled comes first
        assert patterns[0].enabled is False  # Explicitly disabled
        assert patterns[1].enabled is True  # Default

    def test_global_loader_caching(self, tmp_path):
        """Test that global loader provides caching behavior."""
        clear_yaml_cache()

        # First call should create new instance
        loader1 = get_yaml_loader(tmp_path)

        # Second call should return same instance
        loader2 = get_yaml_loader()

        assert loader1 is loader2

        # Clear cache and create new instance
        clear_yaml_cache()
        loader3 = get_yaml_loader()

        assert loader1 is not loader3

    def test_nonexistent_yaml_root_raises_file_not_found(self):
        """Test that nonexistent YAML root raises FileNotFoundError."""
        # Use a clearly nonexistent path
        nonexistent_path = Path("C:/definitely_nonexistent_path_12345")
        loader = YamlInjectionLoader(nonexistent_path)

        # The error is raised when we try to enumerate files, not in __init__
        with pytest.raises(FileNotFoundError):
            loader.enumerate_yaml_files()
