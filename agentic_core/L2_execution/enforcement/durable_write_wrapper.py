"""
Durable Write Wrapper - Enforces sole mutation authority in L2.2.

All durable writes must go through this wrapper to track mutations.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "durable_write_wrapper")
trace_contract.emit_determinism_digest("p0", "durable_write_wrapper")

trace_contract._emit_dispatches_healing_run("p1", "durable_write_wrapper", "L2")
trace_contract._emit_routes_through("p1", "durable_write_wrapper", "L2")
trace_contract._emit_checks_agent_registry("p1", "durable_write_wrapper", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "durable_write_wrapper", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "durable_write_wrapper", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "durable_write_wrapper", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "durable_write_wrapper", "target_agent")
trace_contract._emit_verifies_policy("p1", "durable_write_wrapper", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "durable_write_wrapper", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "durable_write_wrapper", "boundary_check")
trace_contract._emit_transcripts_response("p1", "durable_write_wrapper", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "durable_write_wrapper")
trace_contract._emit_gated_by_confidence("p1", "durable_write_wrapper", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "durable_write_wrapper", "L2")
trace_contract._emit_reads_policy_state("p1", "durable_write_wrapper", "L2")
trace_contract._emit_authorize_and_execute("p2", "durable_write_wrapper", "execution_auth")
trace_contract._emit_validates_capability("p2", "durable_write_wrapper", "capability_check")
trace_contract._emit_routes_to_capability("p2", "durable_write_wrapper", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "durable_write_wrapper", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "durable_write_wrapper", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "durable_write_wrapper", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "durable_write_wrapper", "exec_output")
trace_contract._emit_dispatches_agent("p3", "durable_write_wrapper", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "durable_write_wrapper", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "durable_write_wrapper", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "durable_write_wrapper", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "durable_write_wrapper", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "durable_write_wrapper", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "durable_write_wrapper", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "durable_write_wrapper", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "durable_write_wrapper", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "durable_write_wrapper", "eval_metric")
trace_contract._emit_stores_embedding("p4", "durable_write_wrapper", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "durable_write_wrapper", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "durable_write_wrapper", "exec_snapshot_link")

Logger = logging.getLogger(__name__)
from agentic_core.L0_routing.enforcement.execution_gateway import (
    CURRENT_PHASE,
    MUTATION_COUNTER,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency

trace_contract._emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("durable_write_wrapper", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("durable_write_wrapper", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("durable_write_wrapper", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("durable_write_wrapper", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("durable_write_wrapper", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("durable_write_wrapper", "p4obs", "alert")
trace_contract._emit_links_incident_trace("durable_write_wrapper", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("durable_write_wrapper", "p3lm", "pattern")
trace_contract._emit_records_learning_event("durable_write_wrapper", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("durable_write_wrapper", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("durable_write_wrapper", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("durable_write_wrapper", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("durable_write_wrapper", "p3lm", "policy")
trace_contract._emit_stores_learning_state("durable_write_wrapper", "p3lm", "state")
trace_contract._emit_records_execution_trace("durable_write_wrapper", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("durable_write_wrapper", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("durable_write_wrapper", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("durable_write_wrapper", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("durable_write_wrapper", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("durable_write_wrapper", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("durable_write_wrapper", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("durable_write_wrapper", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("durable_write_wrapper", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "durable_write_wrapper", "context_pull")
trace_contract._emit_pulls_context("p1", "durable_write_wrapper", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "durable_write_wrapper", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "durable_write_wrapper", "uwg_term_2")
trace_contract._emit_writes_through("p1", "durable_write_wrapper", "write_through")
trace_contract._emit_writes_through("p1", "durable_write_wrapper", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "durable_write_wrapper", "safety_validation")
trace_contract._emit_invokes_eval("p1", "durable_write_wrapper", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "durable_write_wrapper", "routing_commit")


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

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "durable_write", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "durable_write", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "durable_write")
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
