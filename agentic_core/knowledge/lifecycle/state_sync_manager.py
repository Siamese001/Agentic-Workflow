"""State Sync Manager.

Monitors source files, detects changes, and triggers reindexing workflows.
Implements deduplication using checksums and version comparison.
"""

import hashlib
import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Callable

from agentic_core.knowledge.canonical.canonical_store import CanonicalStore
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class SyncStatus:
    """Status of a file in the sync system."""
    file_path: str
    last_checksum: str
    last_modified: float
    last_synced: float | None = None
    sync_count: int = 0
    error_count: int = 0
    is_stale: bool = False


@dataclass
class SyncResult:
    """Result of a sync operation."""
    file_path: str
    action: str  # 'created', 'updated', 'deleted', 'unchanged', 'error'
    unit_id: str | None = None
    previous_unit_id: str | None = None
    timestamp: float = field(default_factory=time.time)
    error_message: str | None = None


class StateSyncManager:
    """Manages synchronization between source files and canonical units.

    The StateSyncManager monitors source files for changes, detects
    modifications using checksums, and coordinates reindexing workflows.
    It maintains the operational update path for the ingestion pipeline.
    """

    def __init__(
        self,
        canonical_store: CanonicalStore | None = None,
        check_interval: float = 60.0,  # seconds
        enable_auto_sync: bool = False,
    ):
        """Initialize the state sync manager.

        Args:
            canonical_store: Store for canonical units
            check_interval: How often to check for changes (seconds)
            enable_auto_sync: Whether to enable automatic sync
        """
        self.store = canonical_store or CanonicalStore()
        self.check_interval = check_interval
        self.enable_auto_sync = enable_auto_sync

        # Track sync status for all monitored files
        self._sync_status: dict[str, SyncStatus] = {}
        self._status_lock = Lock()

        # Callbacks for sync events
        self._on_sync_callbacks: list[Callable[[SyncResult], None]] = []
        self._on_error_callbacks: list[Callable[[str, Exception], None]] = []

        # Background monitoring
        self._monitoring = False
        self._monitor_thread: threading.Thread | None = None

        log.info(f"StateSyncManager initialized (auto_sync={enable_auto_sync})")

    def register_file(self, file_path: str | Path) -> SyncStatus:
        """Register a file for monitoring.

        Args:
            file_path: Path to the file to monitor

        Returns:
            SyncStatus for the registered file
        """
        path_str = str(file_path)

        with self._status_lock:
            if path_str in self._sync_status:
                return self._sync_status[path_str]

            # Calculate initial checksum
            checksum = self._calculate_checksum(file_path) if Path(file_path).exists() else ""
            mtime = Path(file_path).stat().st_mtime if Path(file_path).exists() else 0.0

            status = SyncStatus(
                file_path=path_str,
                last_checksum=checksum,
                last_modified=mtime,
            )
            self._sync_status[path_str] = status

            log.debug(f"Registered file for sync: {path_str}")
            return status

    def unregister_file(self, file_path: str | Path) -> bool:
        """Unregister a file from monitoring.

        Args:
            file_path: Path to the file to unregister

        Returns:
            True if unregistered, False if not found
        """
        path_str = str(file_path)

        with self._status_lock:
            if path_str in self._sync_status:
                del self._sync_status[path_str]
                log.debug(f"Unregistered file from sync: {path_str}")
                return True
            return False

    def check_for_changes(self, file_path: str | Path) -> SyncResult | None:
        """Check if a file has changed and sync if needed.

        Args:
            file_path: Path to check

        Returns:
            SyncResult if changes detected, None if unchanged or error
        """
        path_str = str(file_path)
        path = Path(file_path)

        trace_id = f"check_{hashlib.sha256(path_str.encode()).hexdigest()[:8]}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L4_STATE, "StateSyncManager.check_for_changes"
        )

        try:
            # Get current status
            with self._status_lock:
                status = self._sync_status.get(path_str)
                if not status:
                    status = self.register_file(file_path)

            # Check if file exists
            if not path.exists():
                # File was deleted
                if status.last_checksum:  # Was previously tracked
                    result = SyncResult(
                        file_path=path_str,
                        action='deleted',
                    )
                    self._handle_sync_result(result)
                    return result
                return None

            # Get current state
            current_mtime = path.stat().st_mtime
            current_checksum = self._calculate_checksum(path)

            # Check for changes
            if current_checksum == status.last_checksum:
                # No change
                return None

            # Determine action type
            if not status.last_checksum:
                action = 'created'
            else:
                action = 'updated'

            # Find existing unit
            existing_units = self.store.find_by_checksum(status.last_checksum)
            previous_unit_id = existing_units[0].identifier.unit_id if existing_units else None

            # Update status
            with self._status_lock:
                status.last_checksum = current_checksum
                status.last_modified = current_mtime
                status.last_synced = time.time()
                status.sync_count += 1
                status.is_stale = False

            result = SyncResult(
                file_path=path_str,
                action=action,
                previous_unit_id=previous_unit_id,
            )

            self._handle_sync_result(result)

            _emit_records_telemetry_event(
                "state_sync",
                f"file_{action}_{path.name}"
            )

            return result

        except Exception as e:
            log.error(f"Error checking file {path_str}: {e}")
            self._handle_error(path_str, e)
            return SyncResult(
                file_path=path_str,
                action='error',
                error_message=str(e),
            )

    def sync_all(self) -> list[SyncResult]:
        """Check all registered files for changes.

        Returns:
            List of SyncResult for all changes detected
        """
        trace_id = f"sync_all_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L4_STATE, "StateSyncManager.sync_all"
        )

        results = []

        with self._status_lock:
            files = list(self._sync_status.keys())

        for file_path in files:
            result = self.check_for_changes(file_path)
            if result:
                results.append(result)

        log.info(f"Synced {len(results)} changed files out of {len(files)} monitored")
        return results

    def mark_stale(self, file_path: str | Path) -> bool:
        """Mark a file as stale (needs reindexing).

        Args:
            file_path: Path to mark as stale

        Returns:
            True if marked, False if not found
        """
        path_str = str(file_path)

        with self._status_lock:
            if path_str in self._sync_status:
                self._sync_status[path_str].is_stale = True
                log.debug(f"Marked file as stale: {path_str}")
                return True
            return False

    def get_stale_files(self) -> list[str]:
        """Get list of files marked as stale.

        Returns:
            List of file paths marked stale
        """
        with self._status_lock:
            return [
                path for path, status in self._sync_status.items()
                if status.is_stale
            ]

    def get_sync_stats(self) -> dict[str, int]:
        """Get synchronization statistics.

        Returns:
            Dictionary with sync statistics
        """
        with self._status_lock:
            total = len(self._sync_status)
            synced = sum(1 for s in self._sync_status.values() if s.last_synced)
            stale = sum(1 for s in self._sync_status.values() if s.is_stale)
            errors = sum(s.error_count for s in self._sync_status.values())

        return {
            'total_monitored': total,
            'synced_at_least_once': synced,
            'stale_files': stale,
            'total_errors': errors,
        }

    def on_sync(self, callback: Callable[[SyncResult], None]) -> None:
        """Register a callback for sync events.

        Args:
            callback: Function to call when sync completes
        """
        self._on_sync_callbacks.append(callback)

    def on_error(self, callback: Callable[[str, Exception], None]) -> None:
        """Register a callback for error events.

        Args:
            callback: Function to call when errors occur
        """
        self._on_error_callbacks.append(callback)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _handle_sync_result(self, result: SyncResult) -> None:
        """Handle a sync result by notifying callbacks."""
        for callback in self._on_sync_callbacks:
            try:
                callback(result)
            except Exception as e:
                log.warning(f"Sync callback error: {e}")

    def _handle_error(self, file_path: str, error: Exception) -> None:
        """Handle an error by notifying callbacks."""
        # Update error count
        with self._status_lock:
            if file_path in self._sync_status:
                self._sync_status[file_path].error_count += 1

        for callback in self._on_error_callbacks:
            try:
                callback(file_path, error)
            except Exception as e:
                log.warning(f"Error callback error: {e}")


# Global instance
_global_sync_manager: StateSyncManager | None = None


def get_state_sync_manager() -> StateSyncManager:
    """Get or create the global state sync manager."""
    global _global_sync_manager
    if _global_sync_manager is None:
        _global_sync_manager = StateSyncManager()
    return _global_sync_manager
