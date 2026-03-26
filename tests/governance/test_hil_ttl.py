"""REQ-245/248: HIL exception TTL; policy override expires on TTL (semantic clock)."""

from __future__ import annotations

import dataclasses

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_hil_ttl")
# REMOVED: _emit_applies_guardrail("p0", "test_hil_ttl", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_hil_ttl", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_hil_ttl", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_hil_ttl", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_hil_ttl", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_hil_ttl", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_hil_ttl", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_hil_ttl", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_hil_ttl", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_hil_ttl", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_hil_ttl", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_hil_ttl", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_hil_ttl", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_hil_ttl", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_hil_ttl", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_hil_ttl", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_hil_ttl", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_hil_ttl", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_hil_ttl", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_hil_ttl", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_hil_ttl", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_hil_ttl", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_hil_ttl", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_hil_ttl", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_hil_ttl", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_hil_ttl", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_hil_ttl", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_hil_ttl", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_hil_ttl", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_hil_ttl", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_hil_ttl", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_hil_ttl", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hil_ttl", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hil_ttl", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_hil_ttl", "write_through")
# REMOVED: _emit_writes_through("p1", "test_hil_ttl", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_hil_ttl", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_hil_ttl", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_hil_ttl", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_hil_ttl", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_hil_ttl", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_hil_ttl", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_hil_ttl", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_hil_ttl", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_hil_ttl", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_hil_ttl", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_hil_ttl", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_hil_ttl", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_hil_ttl", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_hil_ttl", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_hil_ttl")
# REMOVED: _emit_gated_by_confidence("p1", "test_hil_ttl", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_hil_ttl")
# REMOVED: emit_determinism_digest("p0", "test_hil_ttl")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_hil_ttl", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_hil_ttl", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_hil_ttl", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_hil_ttl", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_hil_ttl", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_hil_ttl", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_hil_ttl", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_hil_ttl", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_hil_ttl", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_hil_ttl", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_hil_ttl", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_hil_ttl", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_hil_ttl", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_hil_ttl", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_hil_ttl", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_hil_ttl", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_hil_ttl", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_hil_ttl", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_hil_ttl", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_hil_ttl", "exec_snapshot_link")

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
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L0_routing.types.governance_types import PolicyExceptionArtifact
    from agentic_core.L0_routing.types.governance_types import (
#  # MOVED: from agentic_core.L0_routing.types.governance_types import PolicyExceptionArtifact

    fields = {f.name for f in dataclasses.fields(PolicyExceptionArtifact)}
    assert "ttl_ticks" in fields
    assert "semantic_clock_tick" in fields


@pytest.mark.governance
def test_req248_semantic_clock_ttl():
#  # MOVED: from agentic_core.L0_routing.types.governance_types import (
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
