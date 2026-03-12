from __future__ import annotations
'Types and models for track_lic_state.'
import logging
from dataclasses import dataclass, field
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
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
    _errors: list[str] = field(default_factory=list)
    _warnings: list[str] = field(default_factory=list)
