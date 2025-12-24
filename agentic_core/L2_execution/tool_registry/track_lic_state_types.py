"""Types and models for track_lic_state."""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field


import logging

_logger = logging.getLogger(__name__)


@dataclass
class StateCheckpoint:
    """Checkpoint for a HOP state."""

    _hop_id: str
    _mission_id: str
    _timestamp: str
    _checksum: str
    _filepath: str


@dataclass
class StateValidationResult:
    """Result of state validation."""

    _is_valid: bool
    _errors: List[str] = field(default_factory=list)
    _warnings: List[str] = field(default_factory=list)
