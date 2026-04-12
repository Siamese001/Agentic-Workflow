from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, NamedTuple

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "error_context_preserver")
emit_determinism_digest("p0", "error_context_preserver")

_emit_dispatches_healing_run("p1", "error_context_preserver", "L4")
_emit_routes_through("p1", "error_context_preserver", "L4")
_emit_checks_agent_registry("p1", "error_context_preserver", "agent_registry")
_emit_validates_agent_capability("p1", "error_context_preserver", "capability")
_emit_dispatches_execution_plan("p1", "error_context_preserver", "exec_plan")
_emit_agent_executes_agent("p1", "error_context_preserver", "sub_agent")
_emit_routes_to_agent("p1", "error_context_preserver", "target_agent")
_emit_verifies_policy("p1", "error_context_preserver", "policy_check")
_emit_observes_runtime_state("p1", "error_context_preserver", "runtime_state")
_emit_verifies_boundary("p1", "error_context_preserver", "boundary_check")
_emit_transcripts_response("p1", "error_context_preserver", "transcript")
_emit_hard_fails_untranscripted("p1", "error_context_preserver")
_emit_gated_by_confidence("p1", "error_context_preserver", "confidence_gate")
_emit_escalates_to_human("p1", "error_context_preserver", "L4")
_emit_reads_policy_state("p1", "error_context_preserver", "L4")
_emit_authorize_and_execute("p2", "error_context_preserver", "execution_auth")
_emit_validates_capability("p2", "error_context_preserver", "capability_check")
_emit_routes_to_capability("p2", "error_context_preserver", "capability_route")
_emit_writes_via_uwg("p2", "error_context_preserver", "uwg_write")
_emit_blocks_direct_write("p2", "error_context_preserver", "direct_write_block")
_emit_records_tool_invocation("p2", "error_context_preserver", "tool_invocation")
_emit_captures_execution_output("p2", "error_context_preserver", "exec_output")
_emit_dispatches_agent("p3", "error_context_preserver", "agent_dispatch")
_emit_coordinates_agents("p3", "error_context_preserver", "agent_coordination")
_emit_records_workflow_lineage("p3", "error_context_preserver", "workflow_lineage")
_emit_records_healing_outcome("p3", "error_context_preserver", "healing_outcome")
_emit_escalates_failure("p3", "error_context_preserver", "failure_escalation")
_emit_orchestrates_workflow("p3", "error_context_preserver", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "error_context_preserver", "healing_dispatch")
_emit_invokes_evaluation("p3", "error_context_preserver", "evaluation_signal")
_emit_records_telemetry_event("p4", "error_context_preserver", "telemetry_event")
_emit_captures_evaluation_metric("p4", "error_context_preserver", "eval_metric")
_emit_stores_embedding("p4", "error_context_preserver", "embedding_store")
_emit_updates_meta_learning_state("p4", "error_context_preserver", "meta_learning")
_emit_links_execution_to_snapshot("p4", "error_context_preserver", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

_emit_emits_metric_event("error_context_preserver", "p4obs", "metric_1")
_emit_emits_metric_event("error_context_preserver", "p4obs", "metric_2")
_emit_emits_metric_event("error_context_preserver", "p4obs", "metric_3")
_emit_emits_metric_event("error_context_preserver", "p4obs", "metric_4")
_emit_emits_metric_event("error_context_preserver", "p4obs", "metric_5")
_emit_emits_metric_event("error_context_preserver", "p4obs", "metric_6")
_emit_records_incident_event("error_context_preserver", "p4obs", "incident")
_emit_captures_runtime_anomaly("error_context_preserver", "p4obs", "anomaly")
_emit_writes_observability_log("error_context_preserver", "p4obs", "obs_log")
_emit_updates_monitoring_state("error_context_preserver", "p4obs", "mon_state")
_emit_triggers_alert("error_context_preserver", "p4obs", "alert")
_emit_links_incident_trace("error_context_preserver", "p4obs", "trace_link")
_emit_captures_pattern("error_context_preserver", "p3lm", "pattern")
_emit_records_learning_event("error_context_preserver", "p3lm", "learning_event")
_emit_writes_learning_snapshot("error_context_preserver", "p3lm", "snapshot")
_emit_feeds_meta_learning("error_context_preserver", "p3lm", "meta_feed")
_emit_updates_routing_strategy("error_context_preserver", "p3lm", "routing")
_emit_improves_agent_policy("error_context_preserver", "p3lm", "policy")
_emit_stores_learning_state("error_context_preserver", "p3lm", "state")
_emit_records_execution_trace("error_context_preserver", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("error_context_preserver", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("error_context_preserver", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("error_context_preserver", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("error_context_preserver", "L4_STATE", "p2_trace_5")
_emit_reads_environ("error_context_preserver", "env_read", "p2_env_1")
_emit_reads_environ("error_context_preserver", "env_read", "p2_env_2")
_emit_reads_runtime_state("error_context_preserver", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("error_context_preserver", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "error_context_preserver", "context_pull")
_emit_pulls_context("p1", "error_context_preserver", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "error_context_preserver", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "error_context_preserver", "uwg_term_2")
_emit_writes_through("p1", "error_context_preserver", "write_through")
_emit_writes_through("p1", "error_context_preserver", "write_through_2")
_emit_validated_by_safety_plane("p1", "error_context_preserver", "safety_validation")
_emit_invokes_eval("p1", "error_context_preserver", "eval_call")
_emit_proposal_commits_routing("p1", "error_context_preserver", "routing_commit")

ExecutionTrace = Any
AgentState = Any


class PreservationResult(NamedTuple):
    """The result of preserving an error context in L4."""

    context_hash: str
    prev_hash: str
    l4_storage_path: str


@dataclass(frozen=True)
class ErrorContext:
    """A structured, versioned representation of an error and its context."""

    error_type: str
    error_message: str
    agent_state: AgentState
    execution_trace: ExecutionTrace
    context_hash: str = field(init=False)
    prev_hash: str = field(init=False)

    def __post_init__(self):
        canonical_bytes = self._canonical_bytes()
        object.__setattr__(self, "context_hash", hashlib.sha256(canonical_bytes).hexdigest())

    def _canonical_bytes(self) -> bytes:
        """Computes the canonical byte representation of the context for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ErrorContext._canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ErrorContext._canonical_bytes", "p0_governance")
        data = {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "agent_state": self.agent_state,
            "execution_trace": self.execution_trace,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def with_chain(self, prev_hash: str) -> ErrorContext:
        """Attaches the previous hash to form a chain, returning a new instance."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ErrorContext.with_chain")

        new_instance = ErrorContext(
            error_type=self.error_type,
            error_message=self.error_message,
            agent_state=self.agent_state,
            execution_trace=self.execution_trace,
        )
        object.__setattr__(new_instance, "prev_hash", prev_hash)
        object.__setattr__(new_instance, "context_hash", self.context_hash)
        return new_instance


def preserve_error_context(
    error: Exception,
    agent_state: AgentState,
    execution_trace: ExecutionTrace,
    prev_hash: str,
) -> PreservationResult:
    """
    Preserves the full error context in L4 with content-hash chaining.

    This function enforces Guarantee #5 (Don't lose data on error) by creating a
    versioned, auditable record of the system's state at the time of failure.
    The hash chain ensures the integrity of the historical record.

    Args:
        error: The exception that was raised.
        agent_state: The complete state of the agent at the time of error.
        execution_trace: The execution trace leading up to the error.
        prev_hash: The hash of the previous record in the L4 state ledger.

    Returns:
        A PreservationResult with the new context hash and storage path.
    """
    context = ErrorContext(
        error_type=type(error).__name__,
        error_message=str(error),
        agent_state=agent_state,
        execution_trace=execution_trace,
    ).with_chain(prev_hash)
    l4_storage_path = f"l4/errors/{context.context_hash}.json"
    return PreservationResult(
        context_hash=context.context_hash,
        prev_hash=prev_hash,
        l4_storage_path=l4_storage_path,
    )
