"""Hardening error types for all Addendum enforcement violations.

All new error types from the Master Hardening Consolidation Addendum.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "hardening_errors")
emit_determinism_digest("p0", "hardening_errors")

_emit_dispatches_healing_run("p1", "hardening_errors", "L5")
_emit_routes_through("p1", "hardening_errors", "L5")
_emit_escalates_to_human("p1", "hardening_errors", "L5")
_emit_reads_policy_state("p1", "hardening_errors", "L5")

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
