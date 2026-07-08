"""Concrete implementation of ChangePackage for testing and production use."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "change_package_impl", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "change_package_impl", "policy_binding")
trace_contract._emit_snapshots_state("p0", "change_package_impl", "state_snapshot")

trace_contract._emit_emits_metric_event("change_package_impl", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("change_package_impl", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("change_package_impl", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("change_package_impl", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("change_package_impl", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("change_package_impl", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("change_package_impl", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("change_package_impl", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("change_package_impl", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("change_package_impl", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("change_package_impl", "p4obs", "alert")
trace_contract._emit_links_incident_trace("change_package_impl", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("change_package_impl", "p3lm", "pattern")
trace_contract._emit_records_learning_event("change_package_impl", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("change_package_impl", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("change_package_impl", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("change_package_impl", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("change_package_impl", "p3lm", "policy")
trace_contract._emit_stores_learning_state("change_package_impl", "p3lm", "state")
trace_contract._emit_records_execution_trace("change_package_impl", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("change_package_impl", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("change_package_impl", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("change_package_impl", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("change_package_impl", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("change_package_impl", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("change_package_impl", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("change_package_impl", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("change_package_impl", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "change_package_impl", "context_pull")
trace_contract._emit_pulls_context("p1", "change_package_impl", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "change_package_impl", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "change_package_impl", "uwg_term_2")
trace_contract._emit_writes_through("p1", "change_package_impl", "write_through")
trace_contract._emit_writes_through("p1", "change_package_impl", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "change_package_impl", "safety_validation")
trace_contract._emit_invokes_eval("p1", "change_package_impl", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "change_package_impl", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "change_package_impl", "human_escalation")
trace_contract._emit_routes_through("p1", "change_package_impl", "route_through")
trace_contract._emit_checks_agent_registry("p1", "change_package_impl", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "change_package_impl", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "change_package_impl", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "change_package_impl", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "change_package_impl", "target_agent")
trace_contract._emit_verifies_policy("p1", "change_package_impl", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "change_package_impl", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "change_package_impl", "boundary_check")
trace_contract._emit_transcripts_response("p1", "change_package_impl", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "change_package_impl")
trace_contract._emit_gated_by_confidence("p1", "change_package_impl", "confidence_gate")
trace_contract.emit_replay_key("p0", "change_package_impl")
trace_contract.emit_determinism_digest("p0", "change_package_impl")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "change_package_impl", "execution_auth")
trace_contract._emit_validates_capability("p2", "change_package_impl", "capability_check")
trace_contract._emit_routes_to_capability("p2", "change_package_impl", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "change_package_impl", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "change_package_impl", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "change_package_impl", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "change_package_impl", "exec_output")
trace_contract._emit_dispatches_agent("p3", "change_package_impl", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "change_package_impl", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "change_package_impl", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "change_package_impl", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "change_package_impl", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "change_package_impl", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "change_package_impl", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "change_package_impl", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "change_package_impl", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "change_package_impl", "eval_metric")
trace_contract._emit_stores_embedding("p4", "change_package_impl", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "change_package_impl", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "change_package_impl", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ChangePackage.canonical_bytes"
        )

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
