"""ADG-driven tests for apps_lic/tools/validation_tools.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_validation_tools_adg")
_emit_applies_guardrail("p0", "test_validation_tools_adg", "p0_governance")
_emit_snapshots_state("p0", "test_validation_tools_adg", "state_snapshot")
emit_replay_key("p0", "test_validation_tools_adg")
emit_determinism_digest("p0", "test_validation_tools_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_validation_tools_adg", "execution_auth")
_emit_validates_capability("p2", "test_validation_tools_adg", "capability_check")
_emit_routes_to_capability("p2", "test_validation_tools_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_validation_tools_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_validation_tools_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_validation_tools_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_validation_tools_adg", "exec_output")
_emit_dispatches_agent("p3", "test_validation_tools_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_validation_tools_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_validation_tools_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_validation_tools_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_validation_tools_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_validation_tools_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_validation_tools_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_validation_tools_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_validation_tools_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_validation_tools_adg", "eval_metric")
_emit_stores_embedding("p4", "test_validation_tools_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_validation_tools_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_validation_tools_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from apps_lic.tools.validation_tools import ValidationResult, validate_schema_policy


class TestValidationResult:
    def test_creates_with_defaults(self):
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_add_error_marks_invalid(self):
        result = ValidationResult()
        result.add_error("field missing")
        assert result.is_valid is False
        assert "field missing" in result.errors

    def test_add_warning_does_not_invalidate(self):
        result = ValidationResult()
        result.add_warning("minor issue")
        assert result.is_valid is True
        assert "minor issue" in result.warnings

    def test_merge_propagates_errors(self):
        r1 = ValidationResult()
        r2 = ValidationResult()
        r2.add_error("err")
        r1.merge(r2)
        assert r1.is_valid is False
        assert "err" in r1.errors


class TestValidateSchemaPolicy:
    def test_returns_validation_result(self):
        result = validate_schema_policy({"key": "value"})
        assert isinstance(result, ValidationResult)

    def test_empty_data(self):
        result = validate_schema_policy({})
        assert isinstance(result, ValidationResult)
