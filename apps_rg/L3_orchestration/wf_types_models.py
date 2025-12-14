"""Dataclass models for orchestrate_workflow_types."""
import logging


# from .orchestrate_workflow_types_enums import *  # Star import removed

@dataclass
class Artifact:
    """A workflow artifact (file)."""
    id: str
    path: Path
    hash: str
    is_ready: bool = False
    is_static: bool = False

@dataclass
class HopCheckpoint:
    """Checkpoint for a completed hop."""
    hop_id: str
    status: HopStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output_artifacts: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

@dataclass
class ValidationResult:
    """Result from a validation gate."""
    gate_id: str
    decision: GateDecision
    message: str
    details: Dict[str, object] = field(default_factory=dict)
