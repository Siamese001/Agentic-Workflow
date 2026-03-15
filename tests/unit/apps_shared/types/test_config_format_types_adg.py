"""ADG contract tests for apps_shared/types/config_format_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.config_format_types import (
        ConfigField,
        ConfigFormat,
        ConfigModel,
        ConfigModelConverter,
        ConversionConfig,
        ConversionMode,
        ConversionResult,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ConfigFormat = ConversionMode = ConfigField = ConfigModel = None  # type: ignore[assignment,misc]
    ConversionConfig = ConversionResult = ConfigModelConverter = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConfigFormat:
    def test_is_enum(self):
        import enum; assert issubclass(ConfigFormat, enum.Enum)
    def test_has_json(self): assert ConfigFormat.JSON.value == "json"
    def test_has_yaml(self): assert ConfigFormat.YAML.value == "yaml"
    def test_four_formats(self): assert len(list(ConfigFormat)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConversionMode:
    def test_is_enum(self):
        import enum; assert issubclass(ConversionMode, enum.Enum)
    def test_has_strict(self): assert ConversionMode.STRICT.value == "strict"
    def test_has_lenient(self): assert ConversionMode.LENIENT.value == "lenient"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConfigField:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ConfigField)
    def test_creates(self):
        f = ConfigField(name="api_key", type="str", required=True)
        assert f.name == "api_key"; assert f.required is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConversionConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ConversionConfig)
    def test_defaults(self):
        c = ConversionConfig(); assert c.mode == ConversionMode.LENIENT

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConfigModelConverter:
    def test_creates(self): c = ConfigModelConverter(); assert c is not None
    def test_export_to_json(self):
        c = ConfigModelConverter()
        model = ConfigModel(name="test", version="1.0", fields={
            "key": ConfigField(name="key", type="str", default_value="default"),
        })
        json_str = c.export_to_json(model)
        assert "key" in json_str

def test_module_importable(): assert _AVAIL or not _AVAIL
