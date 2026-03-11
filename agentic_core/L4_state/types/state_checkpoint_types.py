from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Types and models for track_lic_state."""
import logging
from dataclasses import dataclass, field

_logger = logging.getLogger(__name__)


@dataclass
# NAMING FIXED: StateCheckpoint → StateCheckpoint
class StateCheckpoint:
    """Checkpoint for a HOP state."""

    _hop_id: str
    _mission_id: str
    _timestamp: str
    _checksum: str
    _filepath: str


@dataclass
# NAMING FIXED: StateValidationResult → StateValidationResult
class StateValidationResult:
    """Result of state validation."""

    _is_valid: bool
    _errors: list[str] = field(default_factory=list)
    _warnings: list[str] = field(default_factory=list)
