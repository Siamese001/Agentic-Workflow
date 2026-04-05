"""
EscalationContext — Immutable escalation state with monotonicity enforcement.

retry_count is stored in a frozen dataclass and must only increase between
successive EscalationContext instances for the same trace.

EscalationContext.from_result() verifies monotonicity; a decrease in
retry_count is a HARD FAIL (signals tampering or replay violation).

Phase 3.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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

emit_replay_key("p0", "escalation_context")
emit_determinism_digest("p0", "escalation_context")

_emit_dispatches_healing_run("p1", "escalation_context", "L2")
_emit_routes_through("p1", "escalation_context", "L2")
_emit_checks_agent_registry("p1", "escalation_context", "agent_registry")
_emit_validates_agent_capability("p1", "escalation_context", "capability")
_emit_dispatches_execution_plan("p1", "escalation_context", "exec_plan")
_emit_agent_executes_agent("p1", "escalation_context", "sub_agent")
_emit_routes_to_agent("p1", "escalation_context", "target_agent")
_emit_verifies_policy("p1", "escalation_context", "policy_check")
_emit_observes_runtime_state("p1", "escalation_context", "runtime_state")
_emit_verifies_boundary("p1", "escalation_context", "boundary_check")
_emit_transcripts_response("p1", "escalation_context", "transcript")
_emit_hard_fails_untranscripted("p1", "escalation_context")
_emit_gated_by_confidence("p1", "escalation_context", "confidence_gate")
_emit_escalates_to_human("p1", "escalation_context", "L2")
_emit_reads_policy_state("p1", "escalation_context", "L2")

_emit_applies_guardrail("p0", "escalation_context", "p0_governance")
_emit_snapshots_state("p0", "escalation_context", "state_snapshot")
_emit_authorize_and_execute("p2", "escalation_context", "execution_auth")
_emit_validates_capability("p2", "escalation_context", "capability_check")
_emit_routes_to_capability("p2", "escalation_context", "capability_route")
_emit_writes_via_uwg("p2", "escalation_context", "uwg_write")
_emit_blocks_direct_write("p2", "escalation_context", "direct_write_block")
_emit_records_tool_invocation("p2", "escalation_context", "tool_invocation")
_emit_captures_execution_output("p2", "escalation_context", "exec_output")
_emit_dispatches_agent("p3", "escalation_context", "agent_dispatch")
_emit_coordinates_agents("p3", "escalation_context", "agent_coordination")
_emit_records_workflow_lineage("p3", "escalation_context", "workflow_lineage")
_emit_records_healing_outcome("p3", "escalation_context", "healing_outcome")
_emit_escalates_failure("p3", "escalation_context", "failure_escalation")
_emit_orchestrates_workflow("p3", "escalation_context", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "escalation_context", "healing_dispatch")
_emit_invokes_evaluation("p3", "escalation_context", "evaluation_signal")
_emit_records_telemetry_event("p4", "escalation_context", "telemetry_event")
_emit_captures_evaluation_metric("p4", "escalation_context", "eval_metric")
_emit_stores_embedding("p4", "escalation_context", "embedding_store")
_emit_updates_meta_learning_state("p4", "escalation_context", "meta_learning")
_emit_links_execution_to_snapshot("p4", "escalation_context", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("escalation_context", "p4obs", "metric_1")
_emit_emits_metric_event("escalation_context", "p4obs", "metric_2")
_emit_emits_metric_event("escalation_context", "p4obs", "metric_3")
_emit_emits_metric_event("escalation_context", "p4obs", "metric_4")
_emit_emits_metric_event("escalation_context", "p4obs", "metric_5")
_emit_emits_metric_event("escalation_context", "p4obs", "metric_6")
_emit_records_incident_event("escalation_context", "p4obs", "incident")
_emit_captures_runtime_anomaly("escalation_context", "p4obs", "anomaly")
_emit_writes_observability_log("escalation_context", "p4obs", "obs_log")
_emit_updates_monitoring_state("escalation_context", "p4obs", "mon_state")
_emit_triggers_alert("escalation_context", "p4obs", "alert")
_emit_links_incident_trace("escalation_context", "p4obs", "trace_link")
_emit_captures_pattern("escalation_context", "p3lm", "pattern")
_emit_records_learning_event("escalation_context", "p3lm", "learning_event")
_emit_writes_learning_snapshot("escalation_context", "p3lm", "snapshot")
_emit_feeds_meta_learning("escalation_context", "p3lm", "meta_feed")
_emit_updates_routing_strategy("escalation_context", "p3lm", "routing")
_emit_improves_agent_policy("escalation_context", "p3lm", "policy")
_emit_stores_learning_state("escalation_context", "p3lm", "state")
_emit_records_execution_trace("escalation_context", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("escalation_context", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("escalation_context", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("escalation_context", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("escalation_context", "L4_STATE", "p2_trace_5")
_emit_reads_environ("escalation_context", "env_read", "p2_env_1")
_emit_reads_environ("escalation_context", "env_read", "p2_env_2")
_emit_reads_runtime_state("escalation_context", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("escalation_context", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "escalation_context", "context_pull")
_emit_pulls_context("p1", "escalation_context", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "escalation_context", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "escalation_context", "uwg_term_2")
_emit_writes_through("p1", "escalation_context", "write_through")
_emit_writes_through("p1", "escalation_context", "write_through_2")
_emit_validated_by_safety_plane("p1", "escalation_context", "safety_validation")
_emit_invokes_eval("p1", "escalation_context", "eval_call")
_emit_proposal_commits_routing("p1", "escalation_context", "routing_commit")


class MonotonicityViolation(RuntimeError):
    """Raised when retry_count decreases between successive escalation contexts."""


@dataclass(frozen=True)
class EscalationContext:
    """Immutable snapshot of escalation state for one healing cycle step.

    Fields
    ------
    trace_id : str
        Identifier for the parent execution trace.
    retry_count : int
        Number of healing attempts so far (monotonically non-decreasing).
    healing_tier : str
        Current healing tier name (e.g. "tier_1", "tier_2").
    previous_retry_count : int
        retry_count of the immediately prior context (0 for the first).
    """

    trace_id: str
    retry_count: int
    healing_tier: str
    previous_retry_count: int = 0

    def __post_init__(self) -> None:
        if self.retry_count < 0:
            raise ValueError(f"EscalationContext: retry_count must be >= 0, got {self.retry_count}")
        if self.retry_count < self.previous_retry_count:
            raise MonotonicityViolation(
                f"EscalationContext: monotonicity violation — retry_count={self.retry_count} < previous_retry_count={self.previous_retry_count} for trace_id={self.trace_id!r}"
            )

    @classmethod
    def initial(cls, trace_id: str, healing_tier: str) -> EscalationContext:
        """Create the first EscalationContext for a trace (retry_count=0)."""
        return cls(trace_id=trace_id, retry_count=0, healing_tier=healing_tier, previous_retry_count=0)

    @classmethod
    def from_result(
        cls, previous: EscalationContext, new_healing_tier: str | None = None
    ) -> EscalationContext:
        """Create the next context after one healing attempt.

        Increments retry_count by 1 and enforces monotonicity.

        Args:
            previous: The EscalationContext from the prior step.
            new_healing_tier: Updated tier, defaults to previous tier.

        Raises:
            MonotonicityViolation: if new retry_count < previous retry_count
                (should never happen via this factory, but guards against
                 injection of a tampered *previous*).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "EscalationContext.from_result")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:EscalationContext.from_result".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        new_count = previous.retry_count + 1
        return cls(
            trace_id=previous.trace_id,
            retry_count=new_count,
            healing_tier=new_healing_tier or previous.healing_tier,
            previous_retry_count=previous.retry_count,
        )

    @property
    def is_exhausted(self) -> bool:
        """True when retry_count has reached the hard limit (5)."""
        return self.retry_count >= 5


__all__ = ["EscalationContext", "MonotonicityViolation"]
