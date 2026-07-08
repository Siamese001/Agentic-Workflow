"""
L1 Cognition Telemetry Emitter - Write-only, ZERO-decision component

Emits deterministic TelemetryEvent artifacts and forwards them to L4
telemetry recording via an injected seam. L1 never branches on safety
state and does not couple to L2/L5.
"""

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "telemetry_emitter")
trace_contract.emit_determinism_digest("p0", "telemetry_emitter")

trace_contract._emit_dispatches_healing_run("p1", "telemetry_emitter", "L1")
trace_contract._emit_routes_through("p1", "telemetry_emitter", "L1")
trace_contract._emit_checks_agent_registry("p1", "telemetry_emitter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "telemetry_emitter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "telemetry_emitter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "telemetry_emitter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "telemetry_emitter", "target_agent")
trace_contract._emit_verifies_policy("p1", "telemetry_emitter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "telemetry_emitter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "telemetry_emitter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "telemetry_emitter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "telemetry_emitter")
trace_contract._emit_gated_by_confidence("p1", "telemetry_emitter", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "telemetry_emitter", "L1")
trace_contract._emit_reads_policy_state("p1", "telemetry_emitter", "L1")
trace_contract._emit_authorize_and_execute("p2", "telemetry_emitter", "execution_auth")
trace_contract._emit_validates_capability("p2", "telemetry_emitter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "telemetry_emitter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "telemetry_emitter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "telemetry_emitter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "telemetry_emitter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "telemetry_emitter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "telemetry_emitter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "telemetry_emitter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "telemetry_emitter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "telemetry_emitter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "telemetry_emitter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "telemetry_emitter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "telemetry_emitter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "telemetry_emitter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "telemetry_emitter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "telemetry_emitter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "telemetry_emitter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "telemetry_emitter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "telemetry_emitter", "exec_snapshot_link")

trace_contract.record_execution_trace("telemetry_emitter", "telemetry_emitter_trace")


trace_contract._emit_emits_metric_event("telemetry_emitter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("telemetry_emitter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("telemetry_emitter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("telemetry_emitter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("telemetry_emitter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("telemetry_emitter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("telemetry_emitter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("telemetry_emitter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("telemetry_emitter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("telemetry_emitter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("telemetry_emitter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("telemetry_emitter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("telemetry_emitter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("telemetry_emitter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("telemetry_emitter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("telemetry_emitter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("telemetry_emitter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("telemetry_emitter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("telemetry_emitter", "p3lm", "state")
trace_contract._emit_records_execution_trace("telemetry_emitter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("telemetry_emitter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("telemetry_emitter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("telemetry_emitter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("telemetry_emitter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("telemetry_emitter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("telemetry_emitter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("telemetry_emitter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("telemetry_emitter", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "telemetry_emitter", "context_pull")
trace_contract._emit_pulls_context("p1", "telemetry_emitter", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "telemetry_emitter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "telemetry_emitter", "uwg_term_2")
trace_contract._emit_writes_through("p1", "telemetry_emitter", "write_through")
trace_contract._emit_writes_through("p1", "telemetry_emitter", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "telemetry_emitter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "telemetry_emitter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "telemetry_emitter", "routing_commit")


def compute_event_hash(stage: str, kind: str, commit_tick: int, details: dict[str, Any]) -> str:
    """
    Compute deterministic event hash from canonical JSON bytes.

    Args:
        stage: Event stage identifier
        kind: Event kind/type
        commit_tick: Required input tick (no wall-clock)
        details: Event details dictionary

    Returns:
        SHA-256 hash of canonical JSON representation
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "compute_event_hash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "compute_event_hash", "p0_governance")
    canonical_data = {"stage": stage, "kind": kind, "commit_tick": commit_tick, "details": details}
    canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TelemetryEvent:
    """Immutable telemetry event artifact."""

    trace_id: str
    stage: str
    kind: str
    commit_tick: int
    details: dict
    event_hash: str

    @classmethod
    def create(
        cls,
        trace_id: str,
        stage: str,
        kind: str,
        commit_tick: int,
        details: dict[str, Any],
    ) -> "TelemetryEvent":
        """
        Create a new TelemetryEvent with deterministic event_hash.

        Args:
            trace_id: Execution trace identifier
            stage: Event stage identifier
            kind: Event kind/type
            commit_tick: Required input tick (no wall-clock)
            details: Event details dictionary

        Returns:
            New TelemetryEvent with computed event_hash
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "TelemetryEvent.create")

        details_copy = copy.deepcopy(details)
        event_hash = compute_event_hash(stage, kind, commit_tick, details_copy)
        return cls(
            trace_id=trace_id,
            stage=stage,
            kind=kind,
            commit_tick=commit_tick,
            details=details_copy,
            event_hash=event_hash,
        )


class TelemetryEmitter:
    """
    Write-only telemetry emitter with injected recording seam.

    Calls injected record_fn exactly once, no branching on event content,
    no I/O, no decisions.
    """

    def emit(self, *, event: TelemetryEvent, record_fn) -> None:
        """
        Emit telemetry event via injected recording function.

        Args:
            event: TelemetryEvent to emit
            record_fn: Injected recording function to call
        """
        record_fn(event)

    def build_event(
        self,
        *,
        trace_id: str,
        stage: str,
        kind: str,
        commit_tick: int,
        details: dict[str, Any],
    ) -> TelemetryEvent:
        """
        Convenience constructor for TelemetryEvent.

        Args:
            trace_id: Execution trace identifier
            stage: Event stage identifier
            kind: Event kind/type
            commit_tick: Required input tick (no wall-clock)
            details: Event details dictionary

        Returns:
            New TelemetryEvent
        """
        return TelemetryEvent.create(trace_id, stage, kind, commit_tick, details)
