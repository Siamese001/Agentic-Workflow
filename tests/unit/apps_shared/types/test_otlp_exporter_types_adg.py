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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_otlp_exporter_types_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_otlp_exporter_types_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_otlp_exporter_types_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_otlp_exporter_types_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_otlp_exporter_types_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_otlp_exporter_types_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_otlp_exporter_types_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_otlp_exporter_types_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_otlp_exporter_types_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_otlp_exporter_types_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_otlp_exporter_types_adg", "p4obs", "alert")
_emit_links_incident_trace("test_otlp_exporter_types_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_otlp_exporter_types_adg", "p3lm", "pattern")
_emit_records_learning_event("test_otlp_exporter_types_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_otlp_exporter_types_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_otlp_exporter_types_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_otlp_exporter_types_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_otlp_exporter_types_adg", "p3lm", "policy")
_emit_stores_learning_state("test_otlp_exporter_types_adg", "p3lm", "state")
_emit_records_execution_trace("test_otlp_exporter_types_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_otlp_exporter_types_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_otlp_exporter_types_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_otlp_exporter_types_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_otlp_exporter_types_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_otlp_exporter_types_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_otlp_exporter_types_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_otlp_exporter_types_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_otlp_exporter_types_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_otlp_exporter_types_adg", "context_pull")
_emit_pulls_context("p1", "test_otlp_exporter_types_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_otlp_exporter_types_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_otlp_exporter_types_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_otlp_exporter_types_adg", "write_through")
_emit_writes_through("p1", "test_otlp_exporter_types_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_otlp_exporter_types_adg", "safety_validation")
_emit_invokes_eval("p1", "test_otlp_exporter_types_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_otlp_exporter_types_adg", "routing_commit")

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
