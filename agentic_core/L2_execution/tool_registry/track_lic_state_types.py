"""Types and models for track_lic_state."""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


@dataclass
# NAMING FIXED: StateCheckpoint → state_checkpoint
class state_checkpoint:
    """Checkpoint for a HOP state."""

    _hop_id: str
    _mission_id: str
    _timestamp: str
    _checksum: str
    _filepath: str


@dataclass
# NAMING FIXED: StateValidationResult → state_validation_result
class state_validation_result:
    """Result of state validation."""

    _is_valid: bool
    _errors: List[str] = field(default_factory=list)
    _warnings: List[str] = field(default_factory=list)
