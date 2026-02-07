from __future__ import annotations

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
