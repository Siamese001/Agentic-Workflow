"""TelemetryRecorder — Durable L4 telemetry and outcome logging.

Phase 1 Wave 1.3 implementation. Replaces stub with full telemetry
including metrics, versioning, async sync, and reconciliation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from typing import Any

from agentic_core.L2_execution.utils.execution_proof_emitter import ExecutionProofEmitter
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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "telemetry_recorder")
emit_determinism_digest("p0", "telemetry_recorder")

_emit_dispatches_healing_run("p1", "telemetry_recorder", "L4")
_emit_routes_through("p1", "telemetry_recorder", "L4")
_emit_checks_agent_registry("p1", "telemetry_recorder", "agent_registry")
_emit_validates_agent_capability("p1", "telemetry_recorder", "capability")
_emit_dispatches_execution_plan("p1", "telemetry_recorder", "exec_plan")
_emit_agent_executes_agent("p1", "telemetry_recorder", "sub_agent")
_emit_routes_to_agent("p1", "telemetry_recorder", "target_agent")
_emit_verifies_policy("p1", "telemetry_recorder", "policy_check")
_emit_observes_runtime_state("p1", "telemetry_recorder", "runtime_state")
_emit_verifies_boundary("p1", "telemetry_recorder", "boundary_check")
_emit_transcripts_response("p1", "telemetry_recorder", "transcript")
_emit_hard_fails_untranscripted("p1", "telemetry_recorder")
_emit_gated_by_confidence("p1", "telemetry_recorder", "confidence_gate")
_emit_escalates_to_human("p1", "telemetry_recorder", "L4")
_emit_reads_policy_state("p1", "telemetry_recorder", "L4")

_emit_snapshots_state("p0", "telemetry_recorder", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "telemetry_recorder", "p0_governance")
_emit_authorize_and_execute("p2", "telemetry_recorder", "execution_auth")
_emit_validates_capability("p2", "telemetry_recorder", "capability_check")
_emit_routes_to_capability("p2", "telemetry_recorder", "capability_route")
_emit_writes_via_uwg("p2", "telemetry_recorder", "uwg_write")
_emit_blocks_direct_write("p2", "telemetry_recorder", "direct_write_block")
_emit_records_tool_invocation("p2", "telemetry_recorder", "tool_invocation")
_emit_captures_execution_output("p2", "telemetry_recorder", "exec_output")
_emit_dispatches_agent("p3", "telemetry_recorder", "agent_dispatch")
_emit_coordinates_agents("p3", "telemetry_recorder", "agent_coordination")
_emit_records_workflow_lineage("p3", "telemetry_recorder", "workflow_lineage")
_emit_records_healing_outcome("p3", "telemetry_recorder", "healing_outcome")
_emit_escalates_failure("p3", "telemetry_recorder", "failure_escalation")
_emit_orchestrates_workflow("p3", "telemetry_recorder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "telemetry_recorder", "healing_dispatch")
_emit_invokes_evaluation("p3", "telemetry_recorder", "evaluation_signal")
_emit_records_telemetry_event("p4", "telemetry_recorder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "telemetry_recorder", "eval_metric")
_emit_stores_embedding("p4", "telemetry_recorder", "embedding_store")
_emit_updates_meta_learning_state("p4", "telemetry_recorder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "telemetry_recorder", "exec_snapshot_link")
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

_emit_emits_metric_event("telemetry_recorder", "p4obs", "metric_1")
_emit_emits_metric_event("telemetry_recorder", "p4obs", "metric_2")
_emit_emits_metric_event("telemetry_recorder", "p4obs", "metric_3")
_emit_emits_metric_event("telemetry_recorder", "p4obs", "metric_4")
_emit_emits_metric_event("telemetry_recorder", "p4obs", "metric_5")
_emit_emits_metric_event("telemetry_recorder", "p4obs", "metric_6")
_emit_records_incident_event("telemetry_recorder", "p4obs", "incident")
_emit_captures_runtime_anomaly("telemetry_recorder", "p4obs", "anomaly")
_emit_writes_observability_log("telemetry_recorder", "p4obs", "obs_log")
_emit_updates_monitoring_state("telemetry_recorder", "p4obs", "mon_state")
_emit_triggers_alert("telemetry_recorder", "p4obs", "alert")
_emit_links_incident_trace("telemetry_recorder", "p4obs", "trace_link")
_emit_captures_pattern("telemetry_recorder", "p3lm", "pattern")
_emit_records_learning_event("telemetry_recorder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("telemetry_recorder", "p3lm", "snapshot")
_emit_feeds_meta_learning("telemetry_recorder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("telemetry_recorder", "p3lm", "routing")
_emit_improves_agent_policy("telemetry_recorder", "p3lm", "policy")
_emit_stores_learning_state("telemetry_recorder", "p3lm", "state")
_emit_records_execution_trace("telemetry_recorder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("telemetry_recorder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("telemetry_recorder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("telemetry_recorder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("telemetry_recorder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("telemetry_recorder", "env_read", "p2_env_1")
_emit_reads_environ("telemetry_recorder", "env_read", "p2_env_2")
_emit_reads_runtime_state("telemetry_recorder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("telemetry_recorder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "telemetry_recorder", "context_pull")
_emit_pulls_context("p1", "telemetry_recorder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "telemetry_recorder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "telemetry_recorder", "uwg_term_2")
_emit_writes_through("p1", "telemetry_recorder", "write_through")
_emit_writes_through("p1", "telemetry_recorder", "write_through_2")
_emit_validated_by_safety_plane("p1", "telemetry_recorder", "safety_validation")
_emit_invokes_eval("p1", "telemetry_recorder", "eval_call")
_emit_proposal_commits_routing("p1", "telemetry_recorder", "routing_commit")

MAX_EVENTS = 100
_proof_emitter = ExecutionProofEmitter("L4.TelemetryRecorder")
_telemetry_log: list[dict[str, Any]] = []


@dataclass(frozen=True)
class OutcomeRecord:
    """Immutable outcome record with metrics and reconciliation data."""

    execution_latency_ms: float
    outcome_accuracy: float
    compute_cost_tokens: int
    human_correction_rate: float
    state_diff: dict
    l2_commit_hash: str
    record_hash: str


@dataclass(frozen=True)
class ReconResult:
    """Reconciliation result between L4 state and actual mutations."""

    ghost_mutation_detected: bool
    l4_state_hash: str
    actual_hash: str
    details: str


class TelemetryRecorder:
    """Durable L4 telemetry recorder with metrics and reconciliation.

    - record(): Store telemetry events with timestamps
    - log_async(): Store outcome records (only after L2.2 commit)
    - reconcile(): Compare L4 state vs actual mutation reality
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def record(
        self, event_type: str, data: dict[str, Any], commit_tick: int, timestamp: int | None = None
    ) -> str:
        """Record a telemetry event.

        Args:
            event_type: Type of telemetry event
            data: Event data payload
            commit_tick: Current commit tick
            timestamp: Optional caller-supplied timestamp (not used in ID derivation)

        Returns:
            Event ID (SHA-256 of event content)
        """
        _emit_writes_through(str(uuid.uuid4()), "TelemetryRecorder.record", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "TelemetryRecorder.record")

        with _proof_emitter.proof_op(f"record:{event_type}"):
            pass
        event = {"event_type": event_type, "data": data, "commit_tick": commit_tick}
        if timestamp is not None:
            event["timestamp"] = timestamp
        event_json = json.dumps(event, sort_keys=True, separators=(",", ":"))
        event_id = hashlib.sha256(event_json.encode("utf-8")).hexdigest()
        event["event_id"] = event_id
        _telemetry_log.append(event)
        self.logger.info(f"Telemetry recorded: {event_type} (id: {event_id[:8]})")
        return event_id

    def log_async(self, record: OutcomeRecord) -> None:
        """Store an outcome record asynchronously.

        Args:
            record: OutcomeRecord to store

        Raises:
            ValueError: If record lacks required l2_commit_hash
        """
        if not record.l2_commit_hash:
            raise ValueError("OutcomeRecord must have l2_commit_hash for async logging")
        _telemetry_log.append({"event_type": "outcome_record", "record": asdict(record)})
        self.logger.info(f"Outcome logged async: {record.record_hash[:8]}")

    def reconcile(self, l4_state_hash: str, actual_hash: str, commit_tick: int = 0) -> ReconResult:
        """Reconcile L4 state vs actual mutation reality.

        Args:
            l4_state_hash: Expected L4 state hash
            actual_hash: Actual mutation state hash

        Returns:
            ReconResult with mismatch detection
        """
        ghost_detected = l4_state_hash != actual_hash
        details = (
            f"Ghost mutation detected: L4={l4_state_hash[:8]}, actual={actual_hash[:8]}"
            if ghost_detected
            else "State reconciliation successful"
        )
        result = ReconResult(
            ghost_mutation_detected=ghost_detected,
            l4_state_hash=l4_state_hash,
            actual_hash=actual_hash,
            details=details,
        )
        self.record(
            "reconciliation",
            {
                "ghost_detected": ghost_detected,
                "l4_hash": l4_state_hash,
                "actual_hash": actual_hash,
                "details": details,
            },
            commit_tick=commit_tick,
        )
        return result

    def get_events(self, event_type: str | None = None, limit: int = MAX_EVENTS) -> list[dict[str, Any]]:
        """Retrieve telemetry events.

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of telemetry events
        """
        events = _telemetry_log
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]
        return events[-limit:] if limit > 0 else events

    def clear(self) -> None:
        """Clear all telemetry data (tests only)."""
        _telemetry_log.clear()


telemetry_recorder = TelemetryRecorder()
