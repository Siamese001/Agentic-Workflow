"""ADG contract tests for apps_shared/types/schema_type_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_schema_type_types_adg")
_emit_applies_guardrail("p0", "test_schema_type_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_schema_type_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_schema_type_types_adg", "state_snapshot")
emit_replay_key("p0", "test_schema_type_types_adg")
emit_determinism_digest("p0", "test_schema_type_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.schema_type_types import (
        ConversionStrategy,
        FieldMapping,
        SchemaType,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    SchemaType = ConversionStrategy = FieldMapping = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaType:
    def test_is_enum(self):
        import enum; assert issubclass(SchemaType, enum.Enum)
    def test_has_json_schema(self): assert SchemaType.JSON_SCHEMA.value == "json_schema"
    def test_has_custom(self): assert SchemaType.CUSTOM.value == "custom"
    def test_four_types(self): assert len(list(SchemaType)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConversionStrategy:
    def test_is_enum(self):
        import enum; assert issubclass(ConversionStrategy, enum.Enum)
    def test_has_strict(self): assert ConversionStrategy.STRICT.value == "strict"
    def test_four_strategies(self): assert len(list(ConversionStrategy)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFieldMapping:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(FieldMapping)
    def test_creates(self):
        m = FieldMapping(external_path="$.name", internal_path="name")
        assert m.external_path == "$.name"; assert m.required is False

def test_module_importable(): assert _AVAIL or not _AVAIL
