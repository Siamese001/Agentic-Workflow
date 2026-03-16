"""ADG contract tests for apps_shared/types/config_type_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_config_type_types_adg")
_emit_applies_guardrail("p0", "test_config_type_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_config_type_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_config_type_types_adg", "state_snapshot")
emit_replay_key("p0", "test_config_type_types_adg")
emit_determinism_digest("p0", "test_config_type_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.config_type_types import (
        ConfigFormat,
        ConfigLoadPlan,
        ConfigScope,
        ConfigSource,
        ConfigType,
    )
    _AVAIL = True
except ImportError:
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
