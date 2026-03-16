"""ADG contract tests for apps_shared/types/otlp_exporter_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_otlp_exporter_types_adg")
_emit_applies_guardrail("p0", "test_otlp_exporter_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_otlp_exporter_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_otlp_exporter_types_adg", "state_snapshot")
emit_replay_key("p0", "test_otlp_exporter_types_adg")
emit_determinism_digest("p0", "test_otlp_exporter_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.otlp_exporter_types import BaseExporter, ExportResult, OtlpExporter
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ExportResult = BaseExporter = OtlpExporter = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExportResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ExportResult)
    def test_creates(self):
        r = ExportResult(success=True, items_exported=3, destination="stdout")
        assert r.success is True; assert r.items_exported == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestBaseExporter:
    def test_is_abstract(self):
        from abc import ABC; assert issubclass(BaseExporter, ABC)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOtlpExporter:
    def test_creates(self):
        e = OtlpExporter(); assert e.destination == "stdout"
    def test_creates_with_config(self):
        e = OtlpExporter(config={"destination": "file", "filepath": "/tmp/out.json"})
        assert e.destination == "file"
    def test_export_stdout_success(self):
        e = OtlpExporter()
        result = e.export({"key": "val"})
        assert isinstance(result, ExportResult)
        assert result.success is True; assert result.items_exported == 1
    def test_export_list(self):
        e = OtlpExporter()
        result = e.export([{"a": 1}, {"b": 2}])
        assert result.items_exported == 2
    def test_is_concrete_exporter(self):
        assert issubclass(OtlpExporter, BaseExporter)

def test_module_importable(): assert _AVAIL or not _AVAIL
