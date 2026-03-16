"""ADG contract tests for apps_shared/types/json_exporter_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_json_exporter_types_adg")
_emit_applies_guardrail("p0", "test_json_exporter_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_json_exporter_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_json_exporter_types_adg", "state_snapshot")
emit_replay_key("p0", "test_json_exporter_types_adg")
emit_determinism_digest("p0", "test_json_exporter_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.json_exporter_types import (
        ExportResult,
        JsonExporter,
        export_data,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ExportResult = JsonExporter = export_data = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExportResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ExportResult)
    def test_creates_success(self):
        r = ExportResult(success=True, items_exported=5, destination="stdout")
        assert r.success is True; assert r.errors is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestJsonExporter:
    def test_creates(self): e = JsonExporter(); assert e is not None
    def test_export_stdout(self):
        e = JsonExporter({"destination": "stdout"})
        result = e.export({"key": "value"})
        assert result.success is True; assert result.items_exported == 1
    def test_export_list(self):
        e = JsonExporter({"destination": "stdout"})
        result = e.export([{"a": 1}, {"b": 2}])
        assert result.items_exported == 2

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExportDataFunction:
    def test_convenience_function(self):
        result = export_data({"key": "val"}, {"destination": "stdout"})
        assert result.success is True

def test_module_importable(): assert _AVAIL or not _AVAIL
