"""Types and models for track_lic_state."""


@dataclass
class StateCheckpoint:
    """Checkpoint for a HOP state."""
    hop_id: str
    mission_id: str
    timestamp: str
    checksum: str
    filepath: str

@dataclass
class StateValidationResult:
    """Result of state validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
