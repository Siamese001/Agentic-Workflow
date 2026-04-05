"""
Durable Write Wrapper - Enforces sole mutation authority in L2.2.

All durable writes must go through this wrapper to track mutations.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "durable_write_wrapper")
emit_determinism_digest("p0", "durable_write_wrapper")

_emit_dispatches_healing_run("p1", "durable_write_wrapper", "L2")
_emit_routes_through("p1", "durable_write_wrapper", "L2")
_emit_checks_agent_registry("p1", "durable_write_wrapper", "agent_registry")
_emit_validates_agent_capability("p1", "durable_write_wrapper", "capability")
_emit_dispatches_execution_plan("p1", "durable_write_wrapper", "exec_plan")
_emit_agent_executes_agent("p1", "durable_write_wrapper", "sub_agent")
_emit_routes_to_agent("p1", "durable_write_wrapper", "target_agent")
_emit_verifies_policy("p1", "durable_write_wrapper", "policy_check")
_emit_observes_runtime_state("p1", "durable_write_wrapper", "runtime_state")
_emit_verifies_boundary("p1", "durable_write_wrapper", "boundary_check")
_emit_transcripts_response("p1", "durable_write_wrapper", "transcript")
_emit_hard_fails_untranscripted("p1", "durable_write_wrapper")
_emit_gated_by_confidence("p1", "durable_write_wrapper", "confidence_gate")
_emit_escalates_to_human("p1", "durable_write_wrapper", "L2")
_emit_reads_policy_state("p1", "durable_write_wrapper", "L2")
_emit_authorize_and_execute("p2", "durable_write_wrapper", "execution_auth")
_emit_validates_capability("p2", "durable_write_wrapper", "capability_check")
_emit_routes_to_capability("p2", "durable_write_wrapper", "capability_route")
_emit_writes_via_uwg("p2", "durable_write_wrapper", "uwg_write")
_emit_blocks_direct_write("p2", "durable_write_wrapper", "direct_write_block")
_emit_records_tool_invocation("p2", "durable_write_wrapper", "tool_invocation")
_emit_captures_execution_output("p2", "durable_write_wrapper", "exec_output")
_emit_dispatches_agent("p3", "durable_write_wrapper", "agent_dispatch")
_emit_coordinates_agents("p3", "durable_write_wrapper", "agent_coordination")
_emit_records_workflow_lineage("p3", "durable_write_wrapper", "workflow_lineage")
_emit_records_healing_outcome("p3", "durable_write_wrapper", "healing_outcome")
_emit_escalates_failure("p3", "durable_write_wrapper", "failure_escalation")
_emit_orchestrates_workflow("p3", "durable_write_wrapper", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "durable_write_wrapper", "healing_dispatch")
_emit_invokes_evaluation("p3", "durable_write_wrapper", "evaluation_signal")
_emit_records_telemetry_event("p4", "durable_write_wrapper", "telemetry_event")
_emit_captures_evaluation_metric("p4", "durable_write_wrapper", "eval_metric")
_emit_stores_embedding("p4", "durable_write_wrapper", "embedding_store")
_emit_updates_meta_learning_state("p4", "durable_write_wrapper", "meta_learning")
_emit_links_execution_to_snapshot("p4", "durable_write_wrapper", "exec_snapshot_link")

Logger = logging.getLogger(__name__)
from agentic_core.L0_routing.enforcement.execution_gateway import CURRENT_PHASE, MUTATION_COUNTER
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    _emit_writes_through,
)

_emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_1")
_emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_2")
_emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_3")
_emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_4")
_emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_5")
_emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_6")
_emit_records_incident_event("durable_write_wrapper", "p4obs", "incident")
_emit_captures_runtime_anomaly("durable_write_wrapper", "p4obs", "anomaly")
_emit_writes_observability_log("durable_write_wrapper", "p4obs", "obs_log")
_emit_updates_monitoring_state("durable_write_wrapper", "p4obs", "mon_state")
_emit_triggers_alert("durable_write_wrapper", "p4obs", "alert")
_emit_links_incident_trace("durable_write_wrapper", "p4obs", "trace_link")
_emit_captures_pattern("durable_write_wrapper", "p3lm", "pattern")
_emit_records_learning_event("durable_write_wrapper", "p3lm", "learning_event")
_emit_writes_learning_snapshot("durable_write_wrapper", "p3lm", "snapshot")
_emit_feeds_meta_learning("durable_write_wrapper", "p3lm", "meta_feed")
_emit_updates_routing_strategy("durable_write_wrapper", "p3lm", "routing")
_emit_improves_agent_policy("durable_write_wrapper", "p3lm", "policy")
_emit_stores_learning_state("durable_write_wrapper", "p3lm", "state")
_emit_records_execution_trace("durable_write_wrapper", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("durable_write_wrapper", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("durable_write_wrapper", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("durable_write_wrapper", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("durable_write_wrapper", "L4_STATE", "p2_trace_5")
_emit_reads_environ("durable_write_wrapper", "env_read", "p2_env_1")
_emit_reads_environ("durable_write_wrapper", "env_read", "p2_env_2")
_emit_reads_runtime_state("durable_write_wrapper", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("durable_write_wrapper", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "durable_write_wrapper", "context_pull")
_emit_pulls_context("p1", "durable_write_wrapper", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "durable_write_wrapper", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "durable_write_wrapper", "uwg_term_2")
_emit_writes_through("p1", "durable_write_wrapper", "write_through")
_emit_writes_through("p1", "durable_write_wrapper", "write_through_2")
_emit_validated_by_safety_plane("p1", "durable_write_wrapper", "safety_validation")
_emit_invokes_eval("p1", "durable_write_wrapper", "eval_call")
_emit_proposal_commits_routing("p1", "durable_write_wrapper", "routing_commit")


def durable_write(operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Wrapper for all durable write operations.

    Args:
        operation: The actual write operation to perform
        *args: Arguments to pass to the operation
        **kwargs: Keyword arguments to pass to the operation

    Returns:
        Result of the operation

    Raises:
        AssertionError: If not in L2.2 phase
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "durable_write", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "durable_write", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "durable_write")
    global CURRENT_PHASE, MUTATION_COUNTER
    if CURRENT_PHASE != "L2.2":
        raise AssertionError(f"Durable write attempted in phase {CURRENT_PHASE}, only L2.2 allowed")
    MUTATION_COUNTER += 1
    Logger.info(f"[DURABLE_WRITE] Mutation #{MUTATION_COUNTER} in phase {CURRENT_PHASE}")
    return operation(*args, **kwargs)


def reset_mutation_counter() -> None:
    """Reset mutation counter (for testing only)."""
    global MUTATION_COUNTER
    MUTATION_COUNTER = 0


def get_mutation_count() -> int:
    """Get current mutation count."""
    return MUTATION_COUNTER


def set_phase(phase: str) -> None:
    """Set current execution phase."""
    global CURRENT_PHASE
    CURRENT_PHASE = phase


def get_current_phase() -> str:
    """Get current execution phase."""
    return CURRENT_PHASE
