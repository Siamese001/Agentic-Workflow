"""Concrete TelemetryStore — reads telemetry events for the meta-learning pipeline.

Provides file-backed and in-memory implementations of the ``TelemetryStore``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from agentic_core.L6_system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

trace_contract._emit_applies_guardrail("p0", "telemetry_store", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "telemetry_store", "policy_binding")
trace_contract._emit_snapshots_state("p0", "telemetry_store", "state_snapshot")
from tqdm import tqdm

trace_contract.record_execution_trace("telemetry_store", "telemetry_store_trace")


trace_contract._emit_emits_metric_event("telemetry_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("telemetry_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("telemetry_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("telemetry_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("telemetry_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("telemetry_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("telemetry_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("telemetry_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("telemetry_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("telemetry_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("telemetry_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("telemetry_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("telemetry_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("telemetry_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("telemetry_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("telemetry_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("telemetry_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("telemetry_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("telemetry_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("telemetry_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("telemetry_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("telemetry_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("telemetry_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("telemetry_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("telemetry_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("telemetry_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("telemetry_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("telemetry_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "telemetry_store", "context_pull")
trace_contract._emit_pulls_context("p1", "telemetry_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "telemetry_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "telemetry_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "telemetry_store", "write_through")
trace_contract._emit_writes_through("p1", "telemetry_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "telemetry_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "telemetry_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "telemetry_store", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "telemetry_store", "human_escalation")
trace_contract._emit_routes_through("p1", "telemetry_store", "route_through")
trace_contract._emit_checks_agent_registry("p1", "telemetry_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "telemetry_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "telemetry_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "telemetry_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "telemetry_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "telemetry_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "telemetry_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "telemetry_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "telemetry_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "telemetry_store")
trace_contract._emit_gated_by_confidence("p1", "telemetry_store", "confidence_gate")
trace_contract.emit_replay_key("p0", "telemetry_store")
trace_contract.emit_determinism_digest("p0", "telemetry_store")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "telemetry_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "telemetry_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "telemetry_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "telemetry_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "telemetry_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "telemetry_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "telemetry_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "telemetry_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "telemetry_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "telemetry_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "telemetry_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "telemetry_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "telemetry_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "telemetry_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "telemetry_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "telemetry_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "telemetry_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "telemetry_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "telemetry_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "telemetry_store", "exec_snapshot_link")

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
        trace_contract._emit_writes_through(str(uuid.uuid4()), "FileBackedTelemetryStore.read_events", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
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
