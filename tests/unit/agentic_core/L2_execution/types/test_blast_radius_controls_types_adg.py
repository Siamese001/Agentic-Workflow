"""ADG-driven tests for L2_execution/types/blast_radius_controls_types.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_blast_radius_controls_types_adg")
_emit_applies_guardrail("p0", "test_blast_radius_controls_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_blast_radius_controls_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_blast_radius_controls_types_adg", "state_snapshot")
emit_replay_key("p0", "test_blast_radius_controls_types_adg")
emit_determinism_digest("p0", "test_blast_radius_controls_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_blast_radius_controls_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_blast_radius_controls_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_blast_radius_controls_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_blast_radius_controls_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_blast_radius_controls_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_blast_radius_controls_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_blast_radius_controls_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_blast_radius_controls_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_blast_radius_controls_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_blast_radius_controls_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_blast_radius_controls_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_blast_radius_controls_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_blast_radius_controls_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_blast_radius_controls_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_blast_radius_controls_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_blast_radius_controls_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_blast_radius_controls_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_blast_radius_controls_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_blast_radius_controls_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_blast_radius_controls_types_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.blast_radius_controls_types import (
    BlastRadiusControls,
    BlastRadiusExceeded,
)


class TestBlastRadiusExceeded:
    def test_is_runtime_error(self):
        assert issubclass(BlastRadiusExceeded, RuntimeError)

    def test_raises(self):
        with pytest.raises(BlastRadiusExceeded):
            raise BlastRadiusExceeded("exceeded max_compute_ms")


class TestBlastRadiusControls:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BlastRadiusControls)

    def test_is_frozen(self):
        ctrl = BlastRadiusControls(
            max_state_diff_bytes=1024,
            max_file_write_bytes=2048,
            max_compute_ms=5000,
        )
        with pytest.raises((AttributeError, TypeError)):
            ctrl.max_compute_ms = 9999

    def test_creates(self):
        ctrl = BlastRadiusControls(
            max_state_diff_bytes=1024,
            max_file_write_bytes=2048,
            max_compute_ms=5000,
        )
        assert ctrl.max_state_diff_bytes == 1024
        assert ctrl.max_compute_ms == 5000
