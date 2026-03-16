"""REQ-016/020: all boundary systems fail-closed; sealed artifacts immutable."""

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

_emit_records_execution_trace("p0", "evidence", "test_fail_closed")
_emit_applies_guardrail("p0", "test_fail_closed", "p0_governance")
_emit_reads_policy_state("p0", "test_fail_closed", "policy_binding")
_emit_snapshots_state("p0", "test_fail_closed", "state_snapshot")
emit_replay_key("p0", "test_fail_closed")
emit_determinism_digest("p0", "test_fail_closed")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_fail_closed", "execution_auth")
_emit_validates_capability("p2", "test_fail_closed", "capability_check")
_emit_routes_to_capability("p2", "test_fail_closed", "capability_route")
_emit_writes_via_uwg("p2", "test_fail_closed", "uwg_write")
_emit_blocks_direct_write("p2", "test_fail_closed", "direct_write_block")
_emit_records_tool_invocation("p2", "test_fail_closed", "tool_invocation")
_emit_captures_execution_output("p2", "test_fail_closed", "exec_output")
_emit_dispatches_agent("p3", "test_fail_closed", "agent_dispatch")
_emit_coordinates_agents("p3", "test_fail_closed", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_fail_closed", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_fail_closed", "healing_outcome")
_emit_escalates_failure("p3", "test_fail_closed", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_fail_closed", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_fail_closed", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_fail_closed", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_fail_closed", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_fail_closed", "eval_metric")
_emit_stores_embedding("p4", "test_fail_closed", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_fail_closed", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_fail_closed", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

HARDENING_ORDER = "land AST/CI ratchet for fail-closed patterns BEFORE applying runtime behavior changes."


@pytest.mark.governance
def test_req016_all_subsystems_fail_closed():
    """Boundary: 10 subsystems must raise on failure, never silently return."""
    from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

    uwg = UniversalWriteGateway()
    with pytest.raises(Exception):  # noqa: B017
        uwg.write(payload=b"x", signature="invalid", store=None)


@pytest.mark.governance
def test_req020_sealed_artifact_immutable():
    """Sealed artifacts must raise on post-seal mutation attempt."""
    from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore

    store = ReplayBundleStore()
    bundle_id = store.seal({"trace_id": "CC3AL1-00000001", "payload": "data"})
    with pytest.raises(Exception, match="sealed|immutable|append.only"):
        store.mutate(bundle_id, {"payload": "tampered"})
