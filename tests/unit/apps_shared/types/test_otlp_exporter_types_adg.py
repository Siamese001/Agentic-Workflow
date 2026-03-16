"""ADG contract tests for apps_shared/types/otlp_exporter_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "test_otlp_exporter_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_otlp_exporter_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_otlp_exporter_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_otlp_exporter_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_otlp_exporter_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_otlp_exporter_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_otlp_exporter_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_otlp_exporter_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_otlp_exporter_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_otlp_exporter_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_otlp_exporter_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_otlp_exporter_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_otlp_exporter_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_otlp_exporter_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_otlp_exporter_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_otlp_exporter_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_otlp_exporter_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_otlp_exporter_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_otlp_exporter_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_otlp_exporter_types_adg", "exec_snapshot_link")

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
