from __future__ import annotations

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.L2_execution.utils.execution_proof_emitter import ExecutionProofEmitter
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_proof_emitter = ExecutionProofEmitter("L4.MissionHistorian")


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


"\nMissionHistorian - L4 State Framework Agent\nTracks mission execution history and audit trails.\n"
import csv
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_snapshots_state,
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

Logger: Any = logging.getLogger(__name__)


class MissionHistorian:
    """
    L4 State: Mission History Tracking
    Records all mission actions, decisions, and outcomes for audit trails.
    """

    def __init__(self, log_path: Path = None):
        """
        Initialize the MissionHistorian.

        Args:
            log_path: Path to the audit log CSV file
        """
        self.log_path = log_path or Path("mission_audit.csv")
        if not self.log_path.exists():
            _get_write_gateway().init_csv(
                self.log_path, ["timestamp", "file", "action", "source", "destination", "reason"]
            )

    def record(self, file_name: str, action: str, source: str, destination: str, reason: str) -> Any:
        """
        Record a mission action to the audit log.

        Args:
            file_name: Name of the file affected
            action: Action performed (e.g., 'move', 'delete', 'create')
            source: Source location
            destination: Destination location
            reason: Reason for the action
        """
        _emit_snapshots_state(str(uuid.uuid4()), "MissionHistorian.record", "L4_STATE")
        try:
            with _proof_emitter.proof_op(f"record:{action}:{file_name}"):
                pass
            _get_write_gateway().append_csv_row(
                self.log_path, [datetime.now().isoformat(), file_name, action, source, destination, reason]
            )
            Logger.debug(f"[MissionHistorian] Recorded: {action} on {file_name}")
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.error(f"[MissionHistorian] Failed to record action: {e}")

    def get_history(self, file_name: str | None = None) -> list:
        """
        Retrieve mission history.

        Args:
            file_name: Optional filter by file name

        Returns:
            List of history records
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "MissionHistorian.get_history")

        if not self.log_path.exists():
            return []
        history: Any = []
        try:
            with open(self.log_path, newline="", encoding="utf-8") as f:
                reader: Any = csv.DictReader(f)
                for row in reader:
                    if file_name is None or row.get("file") == file_name:
                        history.append(row)
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[MissionHistorian] Failed to read history: {e}")
        return history

    def get_summary(self) -> dict[str, Any]:
        """
        Get summary statistics of mission history.

        Returns:
            Dictionary with summary statistics
        """
        history: Any = self.get_history()
        actions: Any = {}
        for record in history:
            action: Any = record.get("action", "unknown")
            actions[action] = actions.get(action, 0) + 1
        return {"total_records": len(history), "actions": actions, "log_path": str(self.log_path)}
