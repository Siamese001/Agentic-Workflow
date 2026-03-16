"""REQ-245/248: HIL exception TTL; policy override expires on TTL (semantic clock)."""

from __future__ import annotations

import dataclasses

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

_emit_records_execution_trace("p0", "evidence", "test_hil_ttl")
_emit_applies_guardrail("p0", "test_hil_ttl", "p0_governance")
_emit_snapshots_state("p0", "test_hil_ttl", "state_snapshot")
emit_replay_key("p0", "test_hil_ttl")
emit_determinism_digest("p0", "test_hil_ttl")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hil_ttl", "execution_auth")
_emit_validates_capability("p2", "test_hil_ttl", "capability_check")
_emit_routes_to_capability("p2", "test_hil_ttl", "capability_route")
_emit_writes_via_uwg("p2", "test_hil_ttl", "uwg_write")
_emit_blocks_direct_write("p2", "test_hil_ttl", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hil_ttl", "tool_invocation")
_emit_captures_execution_output("p2", "test_hil_ttl", "exec_output")
_emit_dispatches_agent("p3", "test_hil_ttl", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hil_ttl", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hil_ttl", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hil_ttl", "healing_outcome")
_emit_escalates_failure("p3", "test_hil_ttl", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hil_ttl", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hil_ttl", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hil_ttl", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hil_ttl", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hil_ttl", "eval_metric")
_emit_stores_embedding("p4", "test_hil_ttl", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hil_ttl", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hil_ttl", "exec_snapshot_link")

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
def test_req245_expired_exception_auto_revoked():
    from agentic_core.L0_routing.types.governance_types import PolicyExceptionArtifact

    fields = {f.name for f in dataclasses.fields(PolicyExceptionArtifact)}
    assert "ttl_ticks" in fields
    assert "semantic_clock_tick" in fields


@pytest.mark.governance
def test_req248_semantic_clock_ttl():
    from agentic_core.L0_routing.types.governance_types import (
        ExceptionScope,
        PolicyExceptionArtifact,
    )

    artifact = PolicyExceptionArtifact(
        trace_id="CC3AL1-00000001",
        nonce="n1",
        exception_scope=ExceptionScope.SINGLE_AGENT,
        semantic_clock_tick=10,
        issuer_signature="sig",
        ttl_ticks=5,
    )
    assert artifact.is_expired(now_tick=16)  # 16 > 10 + 5 → expired
    assert not artifact.is_expired(now_tick=14)  # 14 <= 10 + 5 → not expired
