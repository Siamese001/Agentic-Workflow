"""
Shared Scripts - Phase 3 Optimization
Deterministic I/O operations extracted from agents.
"""

from __future__ import annotations

from apps_shared.scripts.io_operations_validator import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    DataCollectionOperations,
    FileOperations,
    MonitoringOperations,
)
from apps_shared.scripts.script_bridge import ScriptBridge, ScriptResult, get_script_bridge

__all__ = [
    "FileOperations",
    "DataCollectionOperations",
    "MonitoringOperations",
    "ScriptBridge",
    "ScriptResult",
    "get_script_bridge",
]
