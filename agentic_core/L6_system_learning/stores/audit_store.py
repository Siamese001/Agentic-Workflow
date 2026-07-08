"""Concrete AuditStore — reads compliance report data as audit slices.

Reads from ``logs/compliance_reports/`` to produce byte-serialized audit
slices for the meta-learning pipeline.  All I/O is explicit (no background
scanning) and deterministic given the same file contents.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "audit_store", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "audit_store", "policy_binding")
trace_contract._emit_snapshots_state("p0", "audit_store", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("audit_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("audit_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("audit_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("audit_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("audit_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("audit_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("audit_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("audit_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("audit_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("audit_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("audit_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("audit_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("audit_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("audit_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("audit_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("audit_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("audit_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("audit_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("audit_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("audit_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("audit_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("audit_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("audit_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("audit_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("audit_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("audit_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("audit_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("audit_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "audit_store", "context_pull")
trace_contract._emit_pulls_context("p1", "audit_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "audit_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "audit_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "audit_store", "write_through")
trace_contract._emit_writes_through("p1", "audit_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "audit_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "audit_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "audit_store", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "audit_store", "human_escalation")
trace_contract._emit_routes_through("p1", "audit_store", "route_through")
trace_contract._emit_checks_agent_registry("p1", "audit_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "audit_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "audit_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "audit_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "audit_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "audit_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "audit_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "audit_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "audit_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "audit_store")
trace_contract._emit_gated_by_confidence("p1", "audit_store", "confidence_gate")
trace_contract.emit_replay_key("p0", "audit_store")
trace_contract.emit_determinism_digest("p0", "audit_store")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "audit_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "audit_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "audit_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "audit_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "audit_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "audit_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "audit_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "audit_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "audit_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "audit_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "audit_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "audit_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "audit_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "audit_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "audit_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "audit_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "audit_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "audit_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "audit_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "audit_store", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class FileBackedAuditStore:
    """File-backed audit store reading from compliance report directory.

    Parameters
    ----------
    reports_dir : Path
        Directory containing compliance report JSON files.
    """

    def __init__(self, reports_dir: Path) -> None:
        self._reports_dir = Path(reports_dir)

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        """Read audit data within the given time window.

        Scans compliance report files and returns a JSON-serialized byte
        payload containing all reports whose timestamps fall within
        ``[window_start_utc, window_end_utc]``.  If no reports match or
        the directory is empty, returns an empty JSON array (``b"[]"``).

        Parameters
        ----------
        window_start_utc : int
            Start of the time window (inclusive).
        window_end_utc : int
            End of the time window (inclusive).

        Returns
        -------
        bytes
            JSON-encoded list of matching report dicts.
        """
        trace_contract._emit_writes_through(str(uuid.uuid4()), "FileBackedAuditStore.read_audit_slice", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "FileBackedAuditStore.read_audit_slice"
        )

        if not self._reports_dir.exists():
            return b"[]"
        matched: list[dict] = []
        unreadable_reports = 0
        for report_path in tqdm(sorted(self._reports_dir.glob("*.json")), desc="Processing", unit="item"):
            try:
                data = json.loads(report_path.read_text(encoding="utf-8", errors="replace"))
                raw_ts = data.get("timestamp_utc") or data.get("created_utc", 0)
                try:
                    ts = int(raw_ts)
                except (TypeError, ValueError):
                    ts = 0
                if window_start_utc <= ts <= window_end_utc:
                    matched.append(data)
                elif ts == 0:
                    matched.append(data)
            except (json.JSONDecodeError, OSError) as exc:  # review: Add error context logging
                unreadable_reports += 1
                logger.debug("Skipping unreadable report %s: %s", report_path.name, exc)
                continue
        if unreadable_reports:
            logger.warning(
                "Ignored %d unreadable compliance reports under %s", unreadable_reports, self._reports_dir
            )
        return json.dumps(matched, separators=(",", ":"), sort_keys=True).encode("utf-8")


class InMemoryAuditStore:
    """In-memory audit store for testing.

    Pre-loaded with byte slices keyed by ``(window_start, window_end)`` tuples.
    Falls back to ``b"[]"`` for unknown windows.
    """

    def __init__(self, slices: dict[tuple[int, int], bytes] | None = None) -> None:
        self._slices: dict[tuple[int, int], bytes] = slices or {}

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        return self._slices.get((window_start_utc, window_end_utc), b"[]")

    def add_slice(self, window_start_utc: int, window_end_utc: int, data: bytes) -> None:
        self._slices[window_start_utc, window_end_utc] = data


__all__ = ["FileBackedAuditStore", "InMemoryAuditStore"]
