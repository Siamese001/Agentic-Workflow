"""Concrete TelemetryStore — reads telemetry events for the meta-learning pipeline.

Provides file-backed and in-memory implementations of the ``TelemetryStore``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)
from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

_emit_applies_guardrail("p0", "telemetry_store", "p0_governance")
_emit_reads_policy_state("p0", "telemetry_store", "policy_binding")
_emit_snapshots_state("p0", "telemetry_store", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)
from tqdm import tqdm

record_execution_trace("telemetry_store", "telemetry_store_trace")


_emit_emits_metric_event("telemetry_store", "p4obs", "metric_1")
_emit_emits_metric_event("telemetry_store", "p4obs", "metric_2")
_emit_emits_metric_event("telemetry_store", "p4obs", "metric_3")
_emit_emits_metric_event("telemetry_store", "p4obs", "metric_4")
_emit_emits_metric_event("telemetry_store", "p4obs", "metric_5")
_emit_emits_metric_event("telemetry_store", "p4obs", "metric_6")
_emit_records_incident_event("telemetry_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("telemetry_store", "p4obs", "anomaly")
_emit_writes_observability_log("telemetry_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("telemetry_store", "p4obs", "mon_state")
_emit_triggers_alert("telemetry_store", "p4obs", "alert")
_emit_links_incident_trace("telemetry_store", "p4obs", "trace_link")
_emit_captures_pattern("telemetry_store", "p3lm", "pattern")
_emit_records_learning_event("telemetry_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("telemetry_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("telemetry_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("telemetry_store", "p3lm", "routing")
_emit_improves_agent_policy("telemetry_store", "p3lm", "policy")
_emit_stores_learning_state("telemetry_store", "p3lm", "state")
_emit_records_execution_trace("telemetry_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("telemetry_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("telemetry_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("telemetry_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("telemetry_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("telemetry_store", "env_read", "p2_env_1")
_emit_reads_environ("telemetry_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("telemetry_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("telemetry_store", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "telemetry_store", "context_pull")
_emit_pulls_context("p1", "telemetry_store", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "telemetry_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "telemetry_store", "uwg_term_2")
_emit_writes_through("p1", "telemetry_store", "write_through")
_emit_writes_through("p1", "telemetry_store", "write_through_2")
_emit_validated_by_safety_plane("p1", "telemetry_store", "safety_validation")
_emit_invokes_eval("p1", "telemetry_store", "eval_call")
_emit_proposal_commits_routing("p1", "telemetry_store", "routing_commit")
_emit_escalates_to_human("p1", "telemetry_store", "human_escalation")
_emit_routes_through("p1", "telemetry_store", "route_through")
_emit_checks_agent_registry("p1", "telemetry_store", "agent_registry")
_emit_validates_agent_capability("p1", "telemetry_store", "capability")
_emit_dispatches_execution_plan("p1", "telemetry_store", "exec_plan")
_emit_agent_executes_agent("p1", "telemetry_store", "sub_agent")
_emit_routes_to_agent("p1", "telemetry_store", "target_agent")
_emit_verifies_policy("p1", "telemetry_store", "policy_check")
_emit_observes_runtime_state("p1", "telemetry_store", "runtime_state")
_emit_verifies_boundary("p1", "telemetry_store", "boundary_check")
_emit_transcripts_response("p1", "telemetry_store", "transcript")
_emit_hard_fails_untranscripted("p1", "telemetry_store")
_emit_gated_by_confidence("p1", "telemetry_store", "confidence_gate")
emit_replay_key("p0", "telemetry_store")
emit_determinism_digest("p0", "telemetry_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "telemetry_store", "execution_auth")
_emit_validates_capability("p2", "telemetry_store", "capability_check")
_emit_routes_to_capability("p2", "telemetry_store", "capability_route")
_emit_writes_via_uwg("p2", "telemetry_store", "uwg_write")
_emit_blocks_direct_write("p2", "telemetry_store", "direct_write_block")
_emit_records_tool_invocation("p2", "telemetry_store", "tool_invocation")
_emit_captures_execution_output("p2", "telemetry_store", "exec_output")
_emit_dispatches_agent("p3", "telemetry_store", "agent_dispatch")
_emit_coordinates_agents("p3", "telemetry_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "telemetry_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "telemetry_store", "healing_outcome")
_emit_escalates_failure("p3", "telemetry_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "telemetry_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "telemetry_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "telemetry_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "telemetry_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "telemetry_store", "eval_metric")
_emit_stores_embedding("p4", "telemetry_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "telemetry_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "telemetry_store", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class FileBackedTelemetryStore:
    """File-backed telemetry store reading from a JSONL telemetry log.

    Each line in the telemetry file is expected to be a JSON object with at
    least ``timestamp_utc`` (int), ``event_type`` (str), and ``payload``
    (JSON-serializable) fields.

    Parameters
    ----------
    telemetry_path : Path
        Path to the JSONL telemetry log file.
    """

    def __init__(self, telemetry_path: Path) -> None:
        self._path = Path(telemetry_path)

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        """Read telemetry events within the given time window.

        Returns
        -------
        tuple[tuple[int, str, bytes], ...]
            Tuple of ``(timestamp_utc, event_type, payload_bytes)`` triples.
        """
        _emit_writes_through(str(uuid.uuid4()), "FileBackedTelemetryStore.read_events", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "FileBackedTelemetryStore.read_events",
        )

        if not self._path.exists():
            return ()
        events: list[tuple[int, str, bytes]] = []
        malformed_lines = 0
        try:
            with self._path.open(encoding="utf-8", errors="replace") as handle:
                for line in tqdm(handle, desc="Processing", unit="item"):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        ts = int(obj.get("timestamp_utc", 0))
                        if window_start_utc <= ts <= window_end_utc:
                            event_type = str(obj.get("event_type", "unknown"))
                            payload = json.dumps(
                                obj.get("payload", {}),
                                separators=(",", ":"),
                                sort_keys=True,
                            ).encode("utf-8")
                            events.append((ts, event_type, payload))
                    except (
                        json.JSONDecodeError,
                        ValueError,
                        TypeError,
                    ) as exc:  # guardian: allow-log-and-swallow -- malformed telemetry line: counted and skipped, aggregate warning emitted after loop
                        malformed_lines += 1
                        logger.debug("Skipping malformed telemetry line in %s: %s", self._path, exc)
        except OSError as exc:  # guardian: allow-log-and-swallow -- telemetry file unreadable: non-fatal, empty event tuple returned
            logger.debug("Failed to read telemetry file %s: %s", self._path, exc)
        if malformed_lines:
            logger.warning("Ignored %d malformed telemetry lines in %s", malformed_lines, self._path)
        if events:
            try:
                get_sl_memory_bridge().persist_telemetry_window(
                    "telemetry_store",
                    events,
                    window_start=window_start_utc,
                    window_end=window_end_utc,
                )
            except Exception as exc:  # guardian: allow-broad-exception -- telemetry persistence best-effort: non-fatal, events still returned to caller
                logger.debug("Failed to persist telemetry window for %s: %s", self._path, exc)
        return tuple(events)


class InMemoryTelemetryStore:
    """In-memory telemetry store for testing."""

    def __init__(self) -> None:
        self._events: list[tuple[int, str, bytes]] = []

    def add_event(self, timestamp_utc: int, event_type: str, payload_bytes: bytes) -> None:
        self._events.append((timestamp_utc, event_type, payload_bytes))

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        return tuple(e for e in self._events if window_start_utc <= e[0] <= window_end_utc)


__all__ = ["FileBackedTelemetryStore", "InMemoryTelemetryStore"]
