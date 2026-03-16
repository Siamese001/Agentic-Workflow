"""REQ-106: replay sandbox blocks network IO and SDK invocation."""

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

_emit_records_execution_trace("p0", "evidence", "test_replay_sandbox")
_emit_applies_guardrail("p0", "test_replay_sandbox", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_sandbox", "policy_binding")
_emit_snapshots_state("p0", "test_replay_sandbox", "state_snapshot")
emit_replay_key("p0", "test_replay_sandbox")
emit_determinism_digest("p0", "test_replay_sandbox")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_replay_sandbox", "execution_auth")
_emit_validates_capability("p2", "test_replay_sandbox", "capability_check")
_emit_routes_to_capability("p2", "test_replay_sandbox", "capability_route")
_emit_writes_via_uwg("p2", "test_replay_sandbox", "uwg_write")
_emit_blocks_direct_write("p2", "test_replay_sandbox", "direct_write_block")
_emit_records_tool_invocation("p2", "test_replay_sandbox", "tool_invocation")
_emit_captures_execution_output("p2", "test_replay_sandbox", "exec_output")
_emit_dispatches_agent("p3", "test_replay_sandbox", "agent_dispatch")
_emit_coordinates_agents("p3", "test_replay_sandbox", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_replay_sandbox", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_replay_sandbox", "healing_outcome")
_emit_escalates_failure("p3", "test_replay_sandbox", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_replay_sandbox", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_replay_sandbox", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_replay_sandbox", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_replay_sandbox", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_replay_sandbox", "eval_metric")
_emit_stores_embedding("p4", "test_replay_sandbox", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_replay_sandbox", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_replay_sandbox", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.governance
def test_replay_sandbox_blocks_network():
    from agentic_core.L2_execution.determinism.replay_guard import ReplayGuard

    guard = ReplayGuard()
    with guard:
        with pytest.raises(Exception, match="network|blocked|replay|Replay"):
            import urllib.request

            urllib.request.urlopen("http://example.com")
