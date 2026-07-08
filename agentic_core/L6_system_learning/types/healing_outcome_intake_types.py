"""Healing Outcome Intake Types - Immutable contract for meta-learning intake."""

import json
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "healing_outcome_intake_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "healing_outcome_intake_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "healing_outcome_intake_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "healing_outcome_intake_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "healing_outcome_intake_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "healing_outcome_intake_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "healing_outcome_intake_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "healing_outcome_intake_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "healing_outcome_intake_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "healing_outcome_intake_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "healing_outcome_intake_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "healing_outcome_intake_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "healing_outcome_intake_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "healing_outcome_intake_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "healing_outcome_intake_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "healing_outcome_intake_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "healing_outcome_intake_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "healing_outcome_intake_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "healing_outcome_intake_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "healing_outcome_intake_types", "exec_snapshot_link")
from .healing_outcome_types import HealingOutcomeProposal, HealingOutcomeStats

trace_contract._emit_applies_guardrail("p0", "healing_outcome_intake_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "healing_outcome_intake_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "healing_outcome_intake_types", "state_snapshot")

trace_contract._emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("healing_outcome_intake_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("healing_outcome_intake_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("healing_outcome_intake_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("healing_outcome_intake_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("healing_outcome_intake_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("healing_outcome_intake_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("healing_outcome_intake_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("healing_outcome_intake_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("healing_outcome_intake_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("healing_outcome_intake_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("healing_outcome_intake_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("healing_outcome_intake_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("healing_outcome_intake_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("healing_outcome_intake_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("healing_outcome_intake_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("healing_outcome_intake_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("healing_outcome_intake_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("healing_outcome_intake_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("healing_outcome_intake_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("healing_outcome_intake_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("healing_outcome_intake_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("healing_outcome_intake_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "healing_outcome_intake_types", "context_pull")
trace_contract._emit_pulls_context("p1", "healing_outcome_intake_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_outcome_intake_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_outcome_intake_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "healing_outcome_intake_types", "write_through")
trace_contract._emit_writes_through("p1", "healing_outcome_intake_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "healing_outcome_intake_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "healing_outcome_intake_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "healing_outcome_intake_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "healing_outcome_intake_types", "human_escalation")
trace_contract._emit_routes_through("p1", "healing_outcome_intake_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "healing_outcome_intake_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "healing_outcome_intake_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "healing_outcome_intake_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "healing_outcome_intake_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "healing_outcome_intake_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "healing_outcome_intake_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "healing_outcome_intake_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "healing_outcome_intake_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "healing_outcome_intake_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "healing_outcome_intake_types")
trace_contract._emit_gated_by_confidence("p1", "healing_outcome_intake_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "healing_outcome_intake_types")
trace_contract.emit_determinism_digest("p0", "healing_outcome_intake_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class HealingOutcomeIntakeRecord:
    """Immutable record for healing outcome intake into meta-learning pipeline.

    This is a persist-only artifact - no configuration or routing mutations.
    The snapshot is stored deterministically as a sorted tuple.
    """

    schema_version: int
    created_utc: int
    window_size: int
    snapshot: tuple[HealingOutcomeStats, ...]
    proposal: HealingOutcomeProposal
    source: str
    run_id: str | None = None
    trace_id: str | None = None

    def __post_init__(self) -> None:
        """Validate invariants."""
        if self.schema_version < 1:
            raise ValueError("schema_version must be >= 1")
        if self.window_size <= 0:
            raise ValueError("window_size must be positive")
        if not self.snapshot:
            raise ValueError("snapshot cannot be empty")
        if list(self.snapshot) != sorted(self.snapshot, key=lambda s: (s.healer_id, s.tier, s.failure_type)):
            raise ValueError("snapshot must be sorted by (healer_id, tier, failure_type)")

    def canonical_bytes(self) -> bytes:
        """Deterministic canonical byte representation for content-addressed identity.

        Used by FileBackedVersionStore for SHA-256 dedup: identical semantic
        records (same schema_version, snapshot, source) produce identical bytes.
        Non-semantic fields (run_id, trace_id) are excluded from the hash
        so that re-runs of the same data do not create duplicate entries.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HealingOutcomeIntakeRecord.canonical_bytes"
        )

        payload = {
            "schema_version": self.schema_version,
            "created_utc": self.created_utc,
            "window_size": self.window_size,
            "source": self.source,
            "snapshot": [
                {
                    "healer_id": s.healer_id,
                    "tier": s.tier,
                    "failure_type": s.failure_type,
                    "total_count": s.total_count,
                    "success_count": s.success_count,
                    "failure_count": s.failure_count,
                }
                for s in self.snapshot
            ],
        }
        return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
