"""Healing Outcome Intake Types - Immutable contract for meta-learning intake."""

import json
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

_emit_authorize_and_execute("p2", "healing_outcome_intake_types", "execution_auth")
_emit_validates_capability("p2", "healing_outcome_intake_types", "capability_check")
_emit_routes_to_capability("p2", "healing_outcome_intake_types", "capability_route")
_emit_writes_via_uwg("p2", "healing_outcome_intake_types", "uwg_write")
_emit_blocks_direct_write("p2", "healing_outcome_intake_types", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_outcome_intake_types", "tool_invocation")
_emit_captures_execution_output("p2", "healing_outcome_intake_types", "exec_output")
_emit_dispatches_agent("p3", "healing_outcome_intake_types", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_outcome_intake_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_outcome_intake_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_outcome_intake_types", "healing_outcome")
_emit_escalates_failure("p3", "healing_outcome_intake_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_outcome_intake_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_outcome_intake_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_outcome_intake_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_outcome_intake_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_outcome_intake_types", "eval_metric")
_emit_stores_embedding("p4", "healing_outcome_intake_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_outcome_intake_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_outcome_intake_types", "exec_snapshot_link")
from system_learning.types.healing_outcome_types import HealingOutcomeProposal, HealingOutcomeStats

_emit_applies_guardrail("p0", "healing_outcome_intake_types", "p0_governance")
_emit_reads_policy_state("p0", "healing_outcome_intake_types", "policy_binding")
_emit_snapshots_state("p0", "healing_outcome_intake_types", "state_snapshot")
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

_emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_1")
_emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_2")
_emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_3")
_emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_4")
_emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_5")
_emit_emits_metric_event("healing_outcome_intake_types", "p4obs", "metric_6")
_emit_records_incident_event("healing_outcome_intake_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_outcome_intake_types", "p4obs", "anomaly")
_emit_writes_observability_log("healing_outcome_intake_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_outcome_intake_types", "p4obs", "mon_state")
_emit_triggers_alert("healing_outcome_intake_types", "p4obs", "alert")
_emit_links_incident_trace("healing_outcome_intake_types", "p4obs", "trace_link")
_emit_captures_pattern("healing_outcome_intake_types", "p3lm", "pattern")
_emit_records_learning_event("healing_outcome_intake_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_outcome_intake_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_outcome_intake_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_outcome_intake_types", "p3lm", "routing")
_emit_improves_agent_policy("healing_outcome_intake_types", "p3lm", "policy")
_emit_stores_learning_state("healing_outcome_intake_types", "p3lm", "state")
_emit_records_execution_trace("healing_outcome_intake_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_outcome_intake_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_outcome_intake_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_outcome_intake_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_outcome_intake_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_outcome_intake_types", "env_read", "p2_env_1")
_emit_reads_environ("healing_outcome_intake_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_outcome_intake_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_outcome_intake_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_outcome_intake_types", "context_pull")
_emit_pulls_context("p1", "healing_outcome_intake_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_outcome_intake_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_outcome_intake_types", "uwg_term_2")
_emit_writes_through("p1", "healing_outcome_intake_types", "write_through")
_emit_writes_through("p1", "healing_outcome_intake_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_outcome_intake_types", "safety_validation")
_emit_invokes_eval("p1", "healing_outcome_intake_types", "eval_call")
_emit_proposal_commits_routing("p1", "healing_outcome_intake_types", "routing_commit")
_emit_escalates_to_human("p1", "healing_outcome_intake_types", "human_escalation")
_emit_routes_through("p1", "healing_outcome_intake_types", "route_through")
_emit_checks_agent_registry("p1", "healing_outcome_intake_types", "agent_registry")
_emit_validates_agent_capability("p1", "healing_outcome_intake_types", "capability")
_emit_dispatches_execution_plan("p1", "healing_outcome_intake_types", "exec_plan")
_emit_agent_executes_agent("p1", "healing_outcome_intake_types", "sub_agent")
_emit_routes_to_agent("p1", "healing_outcome_intake_types", "target_agent")
_emit_verifies_policy("p1", "healing_outcome_intake_types", "policy_check")
_emit_observes_runtime_state("p1", "healing_outcome_intake_types", "runtime_state")
_emit_verifies_boundary("p1", "healing_outcome_intake_types", "boundary_check")
_emit_transcripts_response("p1", "healing_outcome_intake_types", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_outcome_intake_types")
_emit_gated_by_confidence("p1", "healing_outcome_intake_types", "confidence_gate")
emit_replay_key("p0", "healing_outcome_intake_types")
emit_determinism_digest("p0", "healing_outcome_intake_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingOutcomeIntakeRecord.canonical_bytes")

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
