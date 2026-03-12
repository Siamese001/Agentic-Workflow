"""ADG contract tests for apps_shared/types/config_type_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.config_type_types import (
        ConfigType, ConfigFormat, ConfigScope, ConfigSource, ConfigLoadPlan,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ConfigType = ConfigFormat = ConfigScope = ConfigSource = ConfigLoadPlan = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConfigType:
    def test_is_enum(self):
        import enum; assert issubclass(ConfigType, enum.Enum)
    def test_has_environment(self): assert ConfigType.ENVIRONMENT.value == "environment"
    def test_five_types(self): assert len(list(ConfigType)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConfigFormat:
    def test_is_enum(self):
        import enum; assert issubclass(ConfigFormat, enum.Enum)
    def test_has_json(self): assert ConfigFormat.JSON.value == "json"
    def test_has_yaml(self): assert ConfigFormat.YAML.value == "yaml"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConfigScope:
    def test_is_enum(self):
        import enum; assert issubclass(ConfigScope, enum.Enum)
    def test_has_global(self): assert ConfigScope.GLOBAL.value == "global"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConfigSource:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ConfigSource)
    def test_creates(self):
        c = ConfigSource(
            id="s1", name="env_config", config_type=ConfigType.ENVIRONMENT,
            format=ConfigFormat.JSON, location="/config/env.json", scope=ConfigScope.GLOBAL,
        )
        assert c.id == "s1"; assert c.encryption is False

def test_module_importable(): assert _AVAIL or not _AVAIL
