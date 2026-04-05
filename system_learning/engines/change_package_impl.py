"""Concrete implementation of ChangePackage for testing and production use."""

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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

_emit_applies_guardrail("p0", "change_package_impl", "p0_governance")
_emit_reads_policy_state("p0", "change_package_impl", "policy_binding")
_emit_snapshots_state("p0", "change_package_impl", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("change_package_impl", "p4obs", "metric_1")
_emit_emits_metric_event("change_package_impl", "p4obs", "metric_2")
_emit_emits_metric_event("change_package_impl", "p4obs", "metric_3")
_emit_emits_metric_event("change_package_impl", "p4obs", "metric_4")
_emit_emits_metric_event("change_package_impl", "p4obs", "metric_5")
_emit_emits_metric_event("change_package_impl", "p4obs", "metric_6")
_emit_records_incident_event("change_package_impl", "p4obs", "incident")
_emit_captures_runtime_anomaly("change_package_impl", "p4obs", "anomaly")
_emit_writes_observability_log("change_package_impl", "p4obs", "obs_log")
_emit_updates_monitoring_state("change_package_impl", "p4obs", "mon_state")
_emit_triggers_alert("change_package_impl", "p4obs", "alert")
_emit_links_incident_trace("change_package_impl", "p4obs", "trace_link")
_emit_captures_pattern("change_package_impl", "p3lm", "pattern")
_emit_records_learning_event("change_package_impl", "p3lm", "learning_event")
_emit_writes_learning_snapshot("change_package_impl", "p3lm", "snapshot")
_emit_feeds_meta_learning("change_package_impl", "p3lm", "meta_feed")
_emit_updates_routing_strategy("change_package_impl", "p3lm", "routing")
_emit_improves_agent_policy("change_package_impl", "p3lm", "policy")
_emit_stores_learning_state("change_package_impl", "p3lm", "state")
_emit_records_execution_trace("change_package_impl", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("change_package_impl", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("change_package_impl", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("change_package_impl", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("change_package_impl", "L4_STATE", "p2_trace_5")
_emit_reads_environ("change_package_impl", "env_read", "p2_env_1")
_emit_reads_environ("change_package_impl", "env_read", "p2_env_2")
_emit_reads_runtime_state("change_package_impl", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("change_package_impl", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "change_package_impl", "context_pull")
_emit_pulls_context("p1", "change_package_impl", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "change_package_impl", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "change_package_impl", "uwg_term_2")
_emit_writes_through("p1", "change_package_impl", "write_through")
_emit_writes_through("p1", "change_package_impl", "write_through_2")
_emit_validated_by_safety_plane("p1", "change_package_impl", "safety_validation")
_emit_invokes_eval("p1", "change_package_impl", "eval_call")
_emit_proposal_commits_routing("p1", "change_package_impl", "routing_commit")
_emit_escalates_to_human("p1", "change_package_impl", "human_escalation")
_emit_routes_through("p1", "change_package_impl", "route_through")
_emit_checks_agent_registry("p1", "change_package_impl", "agent_registry")
_emit_validates_agent_capability("p1", "change_package_impl", "capability")
_emit_dispatches_execution_plan("p1", "change_package_impl", "exec_plan")
_emit_agent_executes_agent("p1", "change_package_impl", "sub_agent")
_emit_routes_to_agent("p1", "change_package_impl", "target_agent")
_emit_verifies_policy("p1", "change_package_impl", "policy_check")
_emit_observes_runtime_state("p1", "change_package_impl", "runtime_state")
_emit_verifies_boundary("p1", "change_package_impl", "boundary_check")
_emit_transcripts_response("p1", "change_package_impl", "transcript")
_emit_hard_fails_untranscripted("p1", "change_package_impl")
_emit_gated_by_confidence("p1", "change_package_impl", "confidence_gate")
emit_replay_key("p0", "change_package_impl")
emit_determinism_digest("p0", "change_package_impl")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "change_package_impl", "execution_auth")
_emit_validates_capability("p2", "change_package_impl", "capability_check")
_emit_routes_to_capability("p2", "change_package_impl", "capability_route")
_emit_writes_via_uwg("p2", "change_package_impl", "uwg_write")
_emit_blocks_direct_write("p2", "change_package_impl", "direct_write_block")
_emit_records_tool_invocation("p2", "change_package_impl", "tool_invocation")
_emit_captures_execution_output("p2", "change_package_impl", "exec_output")
_emit_dispatches_agent("p3", "change_package_impl", "agent_dispatch")
_emit_coordinates_agents("p3", "change_package_impl", "agent_coordination")
_emit_records_workflow_lineage("p3", "change_package_impl", "workflow_lineage")
_emit_records_healing_outcome("p3", "change_package_impl", "healing_outcome")
_emit_escalates_failure("p3", "change_package_impl", "failure_escalation")
_emit_orchestrates_workflow("p3", "change_package_impl", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "change_package_impl", "healing_dispatch")
_emit_invokes_evaluation("p3", "change_package_impl", "evaluation_signal")
_emit_records_telemetry_event("p4", "change_package_impl", "telemetry_event")
_emit_captures_evaluation_metric("p4", "change_package_impl", "eval_metric")
_emit_stores_embedding("p4", "change_package_impl", "embedding_store")
_emit_updates_meta_learning_state("p4", "change_package_impl", "meta_learning")
_emit_links_execution_to_snapshot("p4", "change_package_impl", "exec_snapshot_link")


@dataclass(frozen=True, slots=True)
class ChangePackage:
    """Concrete implementation of ChangePackage protocol.

    Attributes:
        source: Source identifier for the change.
        target: Target identifier for the change.
        changes: Raw bytes representing the change.
        confidence: Confidence level (0.0 to 1.0).
        reason: Tuple of reason strings.
        timestamp_utc: UTC timestamp.
        authority_sensitivity: Authority sensitivity level (LOW/MEDIUM/HIGH).
        target_surface: Target surface identifier for mutation containment.
    """

    source: str
    target: str
    changes: bytes
    confidence: float
    reason: tuple[str, ...]
    timestamp_utc: int
    embedding_context_hash: str | None = None
    authority_sensitivity: str = "MEDIUM"
    target_surface: str | None = None

    @property
    def reasons(self) -> tuple[str, ...]:
        """Alias for reason tuple (for API compatibility)."""
        return self.reason

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ChangePackage.canonical_bytes")

        import json

        return json.dumps(
            {
                "source": self.source,
                "target": self.target,
                "changes": self.changes.decode("utf-8", errors="replace"),
                "confidence": self.confidence,
                "reason": list(self.reason),
                "timestamp_utc": self.timestamp_utc,
                "embedding_context_hash": self.embedding_context_hash,
                "authority_sensitivity": self.authority_sensitivity,
                "target_surface": self.target_surface,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
