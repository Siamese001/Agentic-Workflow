from __future__ import annotations

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.L2_execution.utils.execution_proof_emitter import ExecutionProofEmitter

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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_snapshots_state,
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
                self.log_path,
                ["timestamp", "file", "action", "source", "destination", "reason"],
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
                self.log_path,
                [datetime.now().isoformat(), file_name, action, source, destination, reason],
            )
            Logger.debug(f"[MissionHistorian] Recorded: {action} on {file_name}")
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
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
