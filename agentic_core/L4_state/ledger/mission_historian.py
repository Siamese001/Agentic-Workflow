from __future__ import annotations

"""
MissionHistorian - L4 State Framework Agent
Tracks mission execution history and audit trails.
"""
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

Logger: Any = logging.getLogger(__name__)

class MissionHistorian:
    """
    L4 State: Mission History Tracking
    Records all mission actions, decisions, and outcomes for audit trails.
    """

    def __init__(self, log_path: Path=None):
        """
        Initialize the MissionHistorian.

        Args:
            log_path: Path to the audit log CSV file
        """
        self.log_path = log_path or Path('mission_audit.csv')
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'file', 'action', 'source', 'destination', 'reason'])

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
        try:
            with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
                writer: Any = csv.writer(f)
                writer.writerow([datetime.now().isoformat(), file_name, action, source, destination, reason])
            Logger.debug(f'[MissionHistorian] Recorded: {action} on {file_name}')
        except Exception as e:
            Logger.error(f'[MissionHistorian] Failed to record action: {e}')

    def get_history(self, file_name: str | None=None) -> list:
        """
        Retrieve mission history.

        Args:
            file_name: Optional filter by file name

        Returns:
            List of history records
        """
        if not self.log_path.exists():
            return []
        history: Any = []
        try:
            with open(self.log_path, newline='', encoding='utf-8') as f:
                reader: Any = csv.DictReader(f)
                for row in reader:
                    if file_name is None or row.get('file') == file_name:
                        history.append(row)
        except Exception as e:
            Logger.error(f'[MissionHistorian] Failed to read history: {e}')
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
            action: Any = record.get('action', 'unknown')
            actions[action] = actions.get(action, 0) + 1
        return {'total_records': len(history), 'actions': actions, 'log_path': str(self.log_path)}
