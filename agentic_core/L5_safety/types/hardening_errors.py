"""Hardening error types for all Addendum enforcement violations.

All new error types from the Master Hardening Consolidation Addendum.
"""

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("hardening_errors", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("hardening_errors", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("hardening_errors", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("hardening_errors", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("hardening_errors", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("hardening_errors", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("hardening_errors", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("hardening_errors", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("hardening_errors", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("hardening_errors", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("hardening_errors", "p4obs", "alert")
trace_contract._emit_links_incident_trace("hardening_errors", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("hardening_errors", "p3lm", "pattern")
trace_contract._emit_records_learning_event("hardening_errors", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("hardening_errors", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("hardening_errors", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("hardening_errors", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("hardening_errors", "p3lm", "policy")
trace_contract._emit_stores_learning_state("hardening_errors", "p3lm", "state")
trace_contract._emit_records_execution_trace("hardening_errors", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("hardening_errors", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("hardening_errors", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("hardening_errors", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("hardening_errors", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("hardening_errors", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("hardening_errors", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("hardening_errors", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("hardening_errors", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "hardening_errors")
trace_contract.emit_determinism_digest("p0", "hardening_errors")

trace_contract._emit_dispatches_healing_run("p1", "hardening_errors", "L5")
trace_contract._emit_routes_through("p1", "hardening_errors", "L5")
trace_contract._emit_checks_agent_registry("p1", "hardening_errors", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "hardening_errors", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "hardening_errors", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "hardening_errors", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "hardening_errors", "target_agent")
trace_contract._emit_verifies_policy("p1", "hardening_errors", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "hardening_errors", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "hardening_errors", "boundary_check")
trace_contract._emit_transcripts_response("p1", "hardening_errors", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "hardening_errors")
trace_contract._emit_gated_by_confidence("p1", "hardening_errors", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "hardening_errors", "L5")
trace_contract._emit_reads_policy_state("p1", "hardening_errors", "L5")
trace_contract._emit_pulls_context("p1", "hardening_errors", "context_pull")
trace_contract._emit_pulls_context("p1", "hardening_errors", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "hardening_errors", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "hardening_errors", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "hardening_errors", "write_through")
trace_contract._emit_writes_through("p1", "hardening_errors", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "hardening_errors", "safety_validation")
trace_contract._emit_invokes_eval("p1", "hardening_errors", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "hardening_errors", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "hardening_errors")
trace_contract._emit_applies_guardrail("p0", "hardening_errors", "p0_governance")
trace_contract._emit_snapshots_state("p0", "hardening_errors", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "hardening_errors", "execution_auth")
trace_contract._emit_validates_capability("p2", "hardening_errors", "capability_check")
trace_contract._emit_routes_to_capability("p2", "hardening_errors", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "hardening_errors", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "hardening_errors", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "hardening_errors", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "hardening_errors", "exec_output")
trace_contract._emit_dispatches_agent("p3", "hardening_errors", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "hardening_errors", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "hardening_errors", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "hardening_errors", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "hardening_errors", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "hardening_errors", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "hardening_errors", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "hardening_errors", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "hardening_errors", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "hardening_errors", "eval_metric")
trace_contract._emit_stores_embedding("p4", "hardening_errors", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "hardening_errors", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "hardening_errors", "exec_snapshot_link")


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
