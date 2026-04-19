"""Change Detector.

Monitors file system for changes and propagates change events
to trigger reindexing workflows.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Callable

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    Observer = None
    FileSystemEventHandler = object

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class ChangeType(Enum):
    """Type of file system change."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class ChangeEvent:
    """A file system change event."""

    file_path: str
    change_type: ChangeType
    timestamp: float = field(default_factory=time.time)
    is_directory: bool = False
    src_path: str | None = None  # For move events

    def __str__(self) -> str:
        return f"{self.change_type.value}: {self.file_path}"


class ChangeHandler(FileSystemEventHandler if HAS_WATCHDOG else object):
    """Handler for file system change events."""

    def __init__(self, callback: Callable[[ChangeEvent], None]):
        """Initialize the change handler.

        Args:
            callback: Function to call when change detected
        """
        self.callback = callback
        super().__init__()

    def on_modified(self, event):
        """Handle file modification."""
        if not event.is_directory:
            self._emit_event(event.src_path, ChangeType.MODIFIED)

    def on_created(self, event):
        """Handle file creation."""
        if not event.is_directory:
            self._emit_event(event.src_path, ChangeType.CREATED)

    def on_deleted(self, event):
        """Handle file deletion."""
        if not event.is_directory:
            self._emit_event(event.src_path, ChangeType.DELETED)

    def on_moved(self, event):
        """Handle file move."""
        if not event.is_directory:
            self._emit_event(
                event.dest_path,
                ChangeType.MOVED,
                src_path=event.src_path,
            )

    def _emit_event(self, file_path: str, change_type: ChangeType, src_path: str | None = None):
        """Emit a change event."""
        event = ChangeEvent(
            file_path=file_path,
            change_type=change_type,
            src_path=src_path,
        )
        try:
            self.callback(event)
        except (AttributeError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-log-and-swallow -- watchdog callback isolation: non-fatal, watcher continues
            log.error(f"Error in change callback: {e}")


class ChangeDetector:
    """Detects file system changes and triggers reindexing.

    The ChangeDetector monitors directories for file changes and
    propagates change events to trigger reindexing workflows.
    """

    def __init__(self, use_watchdog: bool = True):
        """Initialize the change detector.

        Args:
            use_watchdog: Whether to use watchdog for real-time monitoring
        """
        self.use_watchdog = use_watchdog and HAS_WATCHDOG

        # Monitored paths
        self._monitored_paths: set[str] = set()
        self._paths_lock = Lock()

        # Callbacks
        self._on_change_callbacks: list[Callable[[ChangeEvent], None]] = []

        # Watchdog observer
        self._observer: Observer | None = None
        self._handlers: dict[str, ChangeHandler] = {}

        if self.use_watchdog:
            self._observer = Observer()

        log.info(f"ChangeDetector initialized (watchdog={self.use_watchdog})")

    def monitor_path(self, path: str | Path, recursive: bool = True) -> bool:
        """Start monitoring a path for changes.

        Args:
            path: Directory or file to monitor
            recursive: Whether to monitor subdirectories

        Returns:
            True if monitoring started, False otherwise
        """
        path_str = str(path)
        path_obj = Path(path)

        if not path_obj.exists():
            log.warning(f"Cannot monitor non-existent path: {path_str}")
            return False

        with self._paths_lock:
            if path_str in self._monitored_paths:
                return True

            self._monitored_paths.add(path_str)

        if self.use_watchdog and self._observer:
            handler = ChangeHandler(self._handle_change)
            self._handlers[path_str] = handler

            try:
                self._observer.schedule(handler, path_str, recursive=recursive)
                if not self._observer.is_alive():
                    self._observer.start()

                log.info(f"Started monitoring {path_str} (recursive={recursive})")
                return True
            except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
                log.error(f"Error starting monitoring for {path_str}: {e}")
                with self._paths_lock:
                    self._monitored_paths.discard(path_str)
                return False
        else:
            log.info(f"Registered path for polling: {path_str}")
            return True

    def stop_monitoring(self, path: str | Path) -> bool:
        """Stop monitoring a path.

        Args:
            path: Directory or file to stop monitoring

        Returns:
            True if stopped, False if not monitored
        """
        path_str = str(path)

        with self._paths_lock:
            if path_str not in self._monitored_paths:
                return False

            self._monitored_paths.discard(path_str)

        if self.use_watchdog and path_str in self._handlers:
            # Note: watchdog doesn't support unscheduling directly
            # We just remove from our tracking
            del self._handlers[path_str]

        log.info(f"Stopped monitoring {path_str}")
        return True

    def on_change(self, callback: Callable[[ChangeEvent], None]) -> None:
        """Register a callback for change events.

        Args:
            callback: Function to call when change detected
        """
        self._on_change_callbacks.append(callback)

    def get_monitored_paths(self) -> list[str]:
        """Get list of monitored paths.

        Returns:
            List of monitored path strings
        """
        with self._paths_lock:
            return list(self._monitored_paths)

    def stop_all(self) -> None:
        """Stop all monitoring."""
        if self._observer and self._observer.is_alive():
            self._observer.stop()
            self._observer.join()

        with self._paths_lock:
            self._monitored_paths.clear()

        self._handlers.clear()

        log.info("Stopped all monitoring")

    def _handle_change(self, event: ChangeEvent) -> None:
        """Handle a change event."""
        trace_id = f"change_{event.change_type.value}_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L4_STATE,
            "ChangeDetector._handle_change",
        )

        _emit_records_telemetry_event(
            "file_change",
            f"{event.change_type.value}_{Path(event.file_path).name}",
        )

        # Notify all callbacks
        for callback in self._on_change_callbacks:
            try:
                callback(event)
            except (AttributeError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-log-and-swallow -- change callback isolation: non-fatal, other callbacks continue
                log.error(f"Error in change callback: {e}")


# Global instance
_global_detector: ChangeDetector | None = None


def get_change_detector() -> ChangeDetector:
    """Get or create the global change detector."""
    global _global_detector
    if _global_detector is None:
        _global_detector = ChangeDetector()
    return _global_detector
