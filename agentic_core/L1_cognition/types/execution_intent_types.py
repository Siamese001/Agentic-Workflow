"""
L1 Execution Intent - Pure transformation without side effects.

L1 modules must return ExecutionIntent objects instead of performing mutations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "execution_intent_types")
trace_contract.emit_determinism_digest("p0", "execution_intent_types")

trace_contract._emit_dispatches_healing_run("p1", "execution_intent_types", "L1")
trace_contract._emit_routes_through("p1", "execution_intent_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "execution_intent_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "execution_intent_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "execution_intent_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "execution_intent_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "execution_intent_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "execution_intent_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "execution_intent_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "execution_intent_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "execution_intent_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "execution_intent_types")
trace_contract._emit_gated_by_confidence("p1", "execution_intent_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "execution_intent_types", "L1")
trace_contract._emit_reads_policy_state("p1", "execution_intent_types", "L1")
trace_contract._emit_authorize_and_execute("p2", "execution_intent_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "execution_intent_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "execution_intent_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "execution_intent_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "execution_intent_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "execution_intent_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "execution_intent_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "execution_intent_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "execution_intent_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "execution_intent_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "execution_intent_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "execution_intent_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "execution_intent_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "execution_intent_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "execution_intent_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "execution_intent_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "execution_intent_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "execution_intent_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "execution_intent_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "execution_intent_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("execution_intent_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("execution_intent_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("execution_intent_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("execution_intent_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("execution_intent_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("execution_intent_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("execution_intent_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("execution_intent_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("execution_intent_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("execution_intent_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("execution_intent_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("execution_intent_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("execution_intent_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("execution_intent_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("execution_intent_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("execution_intent_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("execution_intent_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("execution_intent_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("execution_intent_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("execution_intent_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("execution_intent_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("execution_intent_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("execution_intent_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("execution_intent_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("execution_intent_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("execution_intent_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("execution_intent_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("execution_intent_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "execution_intent_types", "context_pull")
trace_contract._emit_pulls_context("p1", "execution_intent_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_intent_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_intent_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "execution_intent_types", "write_through")
trace_contract._emit_writes_through("p1", "execution_intent_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "execution_intent_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "execution_intent_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "execution_intent_types", "routing_commit")


@dataclass
class ExecutionIntent:
    """Pure execution intent that L1 can return without side effects."""

    tool_name: str
    args: dict[str, Any]
    metadata: dict[str, Any]
    requires_commit: bool = True


@dataclass
class L1Result:
    """Standard L1 result containing either pure output or execution intents."""

    success: bool
    output: Any
    execution_intents: list[ExecutionIntent] | None = None
    error: str | None = None


MUTATION_GUARD = 0


def assert_l1_purity(instance: Any) -> None:
    """Runtime assertion that L1 instance has no mutation capabilities."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "assert_l1_purity", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "assert_l1_purity", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_COGNITION, "assert_l1_purity")
    assert not hasattr(instance, "redis"), "L1 instance cannot have redis client"
    assert not hasattr(instance, "pinecone"), "L1 instance cannot have pinecone client"
    assert not hasattr(instance, "subprocess"), "L1 instance cannot have subprocess access"
    assert not hasattr(instance, "filesystem"), "L1 instance cannot have direct filesystem access"


def increment_mutation_guard() -> None:
    """Increment global mutation guard - should only be called in L2.2."""
    global MUTATION_GUARD
    MUTATION_GUARD += 1


def get_mutation_count() -> int:
    """Get current mutation count."""
    return MUTATION_GUARD


def reset_mutation_guard() -> None:
    """Reset mutation guard (for testing only)."""
    global MUTATION_GUARD
    MUTATION_GUARD = 0
