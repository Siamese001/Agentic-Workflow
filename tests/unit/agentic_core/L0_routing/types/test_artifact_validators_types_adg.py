"""ADG contract tests for L0_routing/types/artifact_validators_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_artifact_validators_types_adg")
_emit_applies_guardrail("p0", "test_artifact_validators_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_artifact_validators_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_artifact_validators_types_adg", "state_snapshot")
emit_replay_key("p0", "test_artifact_validators_types_adg")
emit_determinism_digest("p0", "test_artifact_validators_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_artifact_validators_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_artifact_validators_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_artifact_validators_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_artifact_validators_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_artifact_validators_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_artifact_validators_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_artifact_validators_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_artifact_validators_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_artifact_validators_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_artifact_validators_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_artifact_validators_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_artifact_validators_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_artifact_validators_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_artifact_validators_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_artifact_validators_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_artifact_validators_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_artifact_validators_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_artifact_validators_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_artifact_validators_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_artifact_validators_types_adg", "exec_snapshot_link")
pytestmark = pytest.mark.unit
from agentic_core.L0_routing.types.artifact_validators_types import (
    validate_healing_plan,
    validate_incident_artifact,
    validate_result_artifact,
)


class TestValidateResultArtifact:
    def test_valid_dict(self):
        d = {"trace_id": "t1", "execution_outcome": "ok", "final_state_hash": "h1", "artifact_class": "ac"}
        r = validate_result_artifact(d); assert r["trace_id"] == "t1"
    def test_missing_field_raises(self):
        with pytest.raises(ValueError): validate_result_artifact({"trace_id": "t1"})
    def test_emitting_layer_defaults(self):
        d = {"trace_id": "t1", "execution_outcome": "ok", "final_state_hash": "h1", "artifact_class": "ac"}
        r = validate_result_artifact(d); assert r["emitting_layer"] == "L2"
    def test_unsupported_type_raises(self):
        with pytest.raises(TypeError): validate_result_artifact("not_a_dict")  # type: ignore[arg-type]

class TestValidateHealingPlan:
    def test_valid_dict(self):
        d = {"trace_id": "t1", "plan_id": "p1", "policy_liaison_node": "pln",
             "manifests": ["m1"], "semantic_clock_tick": 1}
        r = validate_healing_plan(d); assert r["plan_id"] == "p1"
    def test_missing_field_raises(self):
        with pytest.raises(ValueError): validate_healing_plan({"trace_id": "t1"})

class TestValidateIncidentArtifact:
    def test_valid_dict(self):
        d = {"trace_id": "t1", "incident_id": "i1", "correlation_hash": "ch",
             "severity_enum": "high", "telemetry_events": ["e1"]}
        r = validate_incident_artifact(d); assert r["incident_id"] == "i1"
