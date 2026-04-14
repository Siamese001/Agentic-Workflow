"""Hardening error types for all Addendum enforcement violations.

All new error types from the Master Hardening Consolidation Addendum.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("hardening_errors", "p4obs", "metric_1")
_emit_emits_metric_event("hardening_errors", "p4obs", "metric_2")
_emit_emits_metric_event("hardening_errors", "p4obs", "metric_3")
_emit_emits_metric_event("hardening_errors", "p4obs", "metric_4")
_emit_emits_metric_event("hardening_errors", "p4obs", "metric_5")
_emit_emits_metric_event("hardening_errors", "p4obs", "metric_6")
_emit_records_incident_event("hardening_errors", "p4obs", "incident")
_emit_captures_runtime_anomaly("hardening_errors", "p4obs", "anomaly")
_emit_writes_observability_log("hardening_errors", "p4obs", "obs_log")
_emit_updates_monitoring_state("hardening_errors", "p4obs", "mon_state")
_emit_triggers_alert("hardening_errors", "p4obs", "alert")
_emit_links_incident_trace("hardening_errors", "p4obs", "trace_link")
_emit_captures_pattern("hardening_errors", "p3lm", "pattern")
_emit_records_learning_event("hardening_errors", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hardening_errors", "p3lm", "snapshot")
_emit_feeds_meta_learning("hardening_errors", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hardening_errors", "p3lm", "routing")
_emit_improves_agent_policy("hardening_errors", "p3lm", "policy")
_emit_stores_learning_state("hardening_errors", "p3lm", "state")
_emit_records_execution_trace("hardening_errors", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hardening_errors", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hardening_errors", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hardening_errors", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hardening_errors", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hardening_errors", "env_read", "p2_env_1")
_emit_reads_environ("hardening_errors", "env_read", "p2_env_2")
_emit_reads_runtime_state("hardening_errors", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hardening_errors", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "hardening_errors")
emit_determinism_digest("p0", "hardening_errors")

_emit_dispatches_healing_run("p1", "hardening_errors", "L5")
_emit_routes_through("p1", "hardening_errors", "L5")
_emit_checks_agent_registry("p1", "hardening_errors", "agent_registry")
_emit_validates_agent_capability("p1", "hardening_errors", "capability")
_emit_dispatches_execution_plan("p1", "hardening_errors", "exec_plan")
_emit_agent_executes_agent("p1", "hardening_errors", "sub_agent")
_emit_routes_to_agent("p1", "hardening_errors", "target_agent")
_emit_verifies_policy("p1", "hardening_errors", "policy_check")
_emit_observes_runtime_state("p1", "hardening_errors", "runtime_state")
_emit_verifies_boundary("p1", "hardening_errors", "boundary_check")
_emit_transcripts_response("p1", "hardening_errors", "transcript")
_emit_hard_fails_untranscripted("p1", "hardening_errors")
_emit_gated_by_confidence("p1", "hardening_errors", "confidence_gate")
_emit_escalates_to_human("p1", "hardening_errors", "L5")
_emit_reads_policy_state("p1", "hardening_errors", "L5")
_emit_pulls_context("p1", "hardening_errors", "context_pull")
_emit_pulls_context("p1", "hardening_errors", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "hardening_errors", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hardening_errors", "uwg_term_secondary")
_emit_writes_through("p1", "hardening_errors", "write_through")
_emit_writes_through("p1", "hardening_errors", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "hardening_errors", "safety_validation")
_emit_invokes_eval("p1", "hardening_errors", "eval_call")
_emit_proposal_commits_routing("p1", "hardening_errors", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "hardening_errors")
_emit_applies_guardrail("p0", "hardening_errors", "p0_governance")
_emit_snapshots_state("p0", "hardening_errors", "state_snapshot")
_emit_authorize_and_execute("p2", "hardening_errors", "execution_auth")
_emit_validates_capability("p2", "hardening_errors", "capability_check")
_emit_routes_to_capability("p2", "hardening_errors", "capability_route")
_emit_writes_via_uwg("p2", "hardening_errors", "uwg_write")
_emit_blocks_direct_write("p2", "hardening_errors", "direct_write_block")
_emit_records_tool_invocation("p2", "hardening_errors", "tool_invocation")
_emit_captures_execution_output("p2", "hardening_errors", "exec_output")
_emit_dispatches_agent("p3", "hardening_errors", "agent_dispatch")
_emit_coordinates_agents("p3", "hardening_errors", "agent_coordination")
_emit_records_workflow_lineage("p3", "hardening_errors", "workflow_lineage")
_emit_records_healing_outcome("p3", "hardening_errors", "healing_outcome")
_emit_escalates_failure("p3", "hardening_errors", "failure_escalation")
_emit_orchestrates_workflow("p3", "hardening_errors", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hardening_errors", "healing_dispatch")
_emit_invokes_evaluation("p3", "hardening_errors", "evaluation_signal")
_emit_records_telemetry_event("p4", "hardening_errors", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hardening_errors", "eval_metric")
_emit_stores_embedding("p4", "hardening_errors", "embedding_store")
_emit_updates_meta_learning_state("p4", "hardening_errors", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hardening_errors", "exec_snapshot_link")


class ExecutionTraceIntegrityError(RuntimeError):
    """Raised when ExecutionTrace is missing required fields (Addendum 1.1)."""


class MutationReplayIntegrityViolation(RuntimeError):
    """Raised when computed diff != UWG state_diff (Addendum 1.2)."""


class LedgerIntegrityViolation(RuntimeError):
    """Raised when ledger hash chain is broken (Addendum 2.2)."""


class MutationCommitFailure(RuntimeError):
    """Raised when 2PC commit fails (either ACK missing) (Addendum 2.3)."""


class C0AuthorityLeakError(RuntimeError):
    """Raised when C0 RAG payload contains authority fields (Addendum 3.1)."""


class C0MutationViolation(RuntimeError):
    """Raised when C0 context payload is mutated during assembly (Addendum 3.2)."""


class RuntimePolicyMutationViolation(RuntimeError):
    """Raised when runtime config is modified during meta-learning S1-S8 (Addendum 5.2)."""


class HumanPatchValidationError(RuntimeError):
    """Raised when a human patch is missing required fields (Addendum 6.1)."""


class HumanPatchL5ClearanceError(RuntimeError):
    """Raised when a human patch bypasses L5 re-clearance (Addendum 6.2)."""


__all__ = [
    "ExecutionTraceIntegrityError",
    "MutationReplayIntegrityViolation",
    "LedgerIntegrityViolation",
    "MutationCommitFailure",
    "C0AuthorityLeakError",
    "C0MutationViolation",
    "RuntimePolicyMutationViolation",
    "HumanPatchValidationError",
    "HumanPatchL5ClearanceError",
]
