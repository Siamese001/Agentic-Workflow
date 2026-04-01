"""Lifecycle & State Sync Module.

Pipeline B Phase B3: Operational update path with deduplication,
reindexing coordination, and change detection.
"""

from .change_detector import ChangeDetector, ChangeEvent
from .reindex_coordinator import ReindexCoordinator
from .state_sync_manager import StateSyncManager

__all__ = [
    "StateSyncManager",
    "ReindexCoordinator",
    "ChangeDetector",
    "ChangeEvent",
]
