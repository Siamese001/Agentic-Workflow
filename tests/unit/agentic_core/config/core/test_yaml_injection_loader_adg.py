"""ADG-driven tests for agentic_core/config/core/yaml_injection_loader.py — fan_in=2.

Contract tests: YamlValidationError, YamlInjectionLoader init, constants, and basic API.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.config.core.yaml_injection_loader import (
    YamlInjectionLoader,
    YamlValidationError,
)


class TestYamlValidationError:
    def test_importable(self):
        assert callable(YamlValidationError)

    def test_missing_key_message(self):
        err = YamlValidationError(filename="test.yaml", missing_key="description")
        assert "description" in str(err)
        assert "test.yaml" in str(err)

    def test_parse_error_message(self):
        err = YamlValidationError(filename="bad.yaml", parse_error="unexpected token")
        assert "unexpected token" in str(err)
        assert "bad.yaml" in str(err)

    def test_no_detail_message(self):
        err = YamlValidationError(filename="x.yaml")
        assert "x.yaml" in str(err)

    def test_is_exception(self):
        assert issubclass(YamlValidationError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(YamlValidationError):
            raise YamlValidationError(filename="x.yaml", missing_key="key")


class TestYamlInjectionLoaderConstants:
    def test_required_keys_nonempty(self):
        assert len(YamlInjectionLoader.REQUIRED_KEYS) > 0

    def test_layer_mapping_nonempty(self):
        assert len(YamlInjectionLoader.LAYER_MAPPING) > 0

    def test_required_keys_is_set(self):
        assert isinstance(YamlInjectionLoader.REQUIRED_KEYS, set)

    def test_description_in_required_keys(self):
        assert "description" in YamlInjectionLoader.REQUIRED_KEYS

    def test_framing_in_layer_mapping(self):
        assert "framing" in YamlInjectionLoader.LAYER_MAPPING


class TestYamlInjectionLoaderInit:
    def test_creates_with_defaults(self):
        loader = YamlInjectionLoader()
        assert loader is not None

    def test_cache_starts_empty(self):
        loader = YamlInjectionLoader()
        assert loader._cache == {}

    def test_yaml_root_is_path(self):
        from pathlib import Path
        loader = YamlInjectionLoader()
        assert isinstance(loader.yaml_root, Path)

    def test_custom_yaml_root(self):
        from pathlib import Path
        loader = YamlInjectionLoader(yaml_root=Path("data"))
        assert loader.yaml_root == Path("data")


class TestYamlInjectionLoaderEnumerate:
    def test_enumerate_nonexistent_root_raises(self):
        from pathlib import Path
        loader = YamlInjectionLoader(yaml_root=Path("nonexistent_xyz_dir"))
        with pytest.raises(FileNotFoundError):
            loader.enumerate_yaml_files()

    def test_load_by_layer_unknown_returns_empty(self):
        from pathlib import Path
        loader = YamlInjectionLoader(yaml_root=Path("nonexistent_xyz_dir"))
        # load_by_layer on missing root should either raise or return empty list
        try:
            result = loader.load_by_layer("nonexistent_layer_xyz")
            assert isinstance(result, list)
        except (FileNotFoundError, KeyError):
            pass  # Both acceptable for missing root
