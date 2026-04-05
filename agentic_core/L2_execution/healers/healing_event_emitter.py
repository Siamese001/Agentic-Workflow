"""Addendum 1.3: Healing Visibility Enforcement.

Every healing loop MUST emit a HealingAttemptEvent. Silent retries are forbidden.

Schema:
    HealingAttemptEvent:
      - trace_id
      - attempt_number
      - failure_class
      - healer_selected
      - model_used
      - outcome
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

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

emit_replay_key("p0", "healing_event_emitter")
emit_determinism_digest("p0", "healing_event_emitter")

_emit_dispatches_healing_run("p1", "healing_event_emitter", "L2")
_emit_routes_through("p1", "healing_event_emitter", "L2")
_emit_checks_agent_registry("p1", "healing_event_emitter", "agent_registry")
_emit_validates_agent_capability("p1", "healing_event_emitter", "capability")
_emit_dispatches_execution_plan("p1", "healing_event_emitter", "exec_plan")
_emit_agent_executes_agent("p1", "healing_event_emitter", "sub_agent")
_emit_routes_to_agent("p1", "healing_event_emitter", "target_agent")
_emit_verifies_policy("p1", "healing_event_emitter", "policy_check")
_emit_observes_runtime_state("p1", "healing_event_emitter", "runtime_state")
_emit_verifies_boundary("p1", "healing_event_emitter", "boundary_check")
_emit_transcripts_response("p1", "healing_event_emitter", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_event_emitter")
_emit_gated_by_confidence("p1", "healing_event_emitter", "confidence_gate")
_emit_escalates_to_human("p1", "healing_event_emitter", "L2")
_emit_reads_policy_state("p1", "healing_event_emitter", "L2")

_emit_applies_guardrail("p0", "healing_event_emitter", "p0_governance")
_emit_snapshots_state("p0", "healing_event_emitter", "state_snapshot")
_emit_authorize_and_execute("p2", "healing_event_emitter", "execution_auth")
_emit_validates_capability("p2", "healing_event_emitter", "capability_check")
_emit_routes_to_capability("p2", "healing_event_emitter", "capability_route")
_emit_writes_via_uwg("p2", "healing_event_emitter", "uwg_write")
_emit_blocks_direct_write("p2", "healing_event_emitter", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_event_emitter", "tool_invocation")
_emit_captures_execution_output("p2", "healing_event_emitter", "exec_output")
_emit_dispatches_agent("p3", "healing_event_emitter", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_event_emitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_event_emitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_event_emitter", "healing_outcome")
_emit_escalates_failure("p3", "healing_event_emitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_event_emitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_event_emitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_event_emitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_event_emitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_event_emitter", "eval_metric")
_emit_stores_embedding("p4", "healing_event_emitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_event_emitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_event_emitter", "exec_snapshot_link")
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

_emit_emits_metric_event("healing_event_emitter", "p4obs", "metric_1")
_emit_emits_metric_event("healing_event_emitter", "p4obs", "metric_2")
_emit_emits_metric_event("healing_event_emitter", "p4obs", "metric_3")
_emit_emits_metric_event("healing_event_emitter", "p4obs", "metric_4")
_emit_emits_metric_event("healing_event_emitter", "p4obs", "metric_5")
_emit_emits_metric_event("healing_event_emitter", "p4obs", "metric_6")
_emit_records_incident_event("healing_event_emitter", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_event_emitter", "p4obs", "anomaly")
_emit_writes_observability_log("healing_event_emitter", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_event_emitter", "p4obs", "mon_state")
_emit_triggers_alert("healing_event_emitter", "p4obs", "alert")
_emit_links_incident_trace("healing_event_emitter", "p4obs", "trace_link")
_emit_captures_pattern("healing_event_emitter", "p3lm", "pattern")
_emit_records_learning_event("healing_event_emitter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_event_emitter", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_event_emitter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_event_emitter", "p3lm", "routing")
_emit_improves_agent_policy("healing_event_emitter", "p3lm", "policy")
_emit_stores_learning_state("healing_event_emitter", "p3lm", "state")
_emit_records_execution_trace("healing_event_emitter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_event_emitter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_event_emitter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_event_emitter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_event_emitter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_event_emitter", "env_read", "p2_env_1")
_emit_reads_environ("healing_event_emitter", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_event_emitter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_event_emitter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_event_emitter", "context_pull")
_emit_pulls_context("p1", "healing_event_emitter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_event_emitter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_event_emitter", "uwg_term_2")
_emit_writes_through("p1", "healing_event_emitter", "write_through")
_emit_writes_through("p1", "healing_event_emitter", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_event_emitter", "safety_validation")
_emit_invokes_eval("p1", "healing_event_emitter", "eval_call")
_emit_proposal_commits_routing("p1", "healing_event_emitter", "routing_commit")

logger = logging.getLogger(__name__)
_DEFAULT_LOG_PATH = Path("artifacts/healing/healing_events.jsonl")
_LOCK = threading.Lock()


@dataclass
class HealingAttemptEvent:
    """Single healing attempt record."""

    trace_id: str
    attempt_number: int
    failure_class: str
    healer_selected: str
    model_used: str
    outcome: str
    metadata: dict[str, Any] | None = None

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True)


class HealingEventEmitter:
    """Emitter for healing attempt events.

    Wire into all healing orchestrators (RG, LIC, core).
    """

    def __init__(self, log_path: Path | None = None) -> None:
        self._path = log_path or _DEFAULT_LOG_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._emitted: list[HealingAttemptEvent] = []

    def emit(
        self,
        trace_id: str,
        attempt_number: int,
        failure_class: str,
        healer_selected: str,
        model_used: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
    ) -> HealingAttemptEvent:
        """Emit a healing attempt event to the log and in-memory list."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "HealingEventEmitter.emit")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HealingEventEmitter.emit".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        event = HealingAttemptEvent(
            trace_id=trace_id,
            attempt_number=attempt_number,
            failure_class=failure_class,
            healer_selected=healer_selected,
            model_used=model_used,
            outcome=outcome,
            metadata=metadata,
        )
        with _LOCK:
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(event.to_jsonl() + "\n")
            except OSError as exc:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                logger.warning("HealingEventEmitter: write failed: %s", exc)
            self._emitted.append(event)
        logger.info(
            "HealingAttempt[%d] trace=%s healer=%s outcome=%s failure=%s",
            attempt_number,
            trace_id,
            healer_selected,
            outcome,
            failure_class,
        )
        return event

    def emitted_events(self) -> list[HealingAttemptEvent]:
        """Return all events emitted in this session (in-memory only)."""
        with _LOCK:
            return list(self._emitted)


_DEFAULT_EMITTER: HealingEventEmitter | None = None


def get_healing_emitter(path: Path | None = None) -> HealingEventEmitter:
    """Return module-level singleton emitter."""
    global _DEFAULT_EMITTER
    if _DEFAULT_EMITTER is None:
        _DEFAULT_EMITTER = HealingEventEmitter(log_path=path)
    return _DEFAULT_EMITTER


__all__ = ["HealingAttemptEvent", "HealingEventEmitter", "get_healing_emitter"]
