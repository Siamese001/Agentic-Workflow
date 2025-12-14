"""Dataclass models for orchestrate_workflow_types."""
import logging
_logger = logging.getLogger(__name__)

@dataclass
class Artifact:
    """A workflow artifact (file)."""
    _id: str
    _path: Path
    _hash: str
    _is_ready: bool = False
    _is_static: bool = False

@dataclass
class HopCheckpoint:
    """Checkpoint for a completed hop."""
    _hop_id: str
    _status: HopStatus
    _start_time: datetime
    _end_time: Optional[datetime] = None
    _output_artifacts: List[str] = field(default_factory=list)
    _error_message: Optional[str] = None

@dataclass
class ValidationResult:
    """Result from a validation gate."""
    _gate_id: str
    _decision: GateDecision
    _message: str
    _details: Dict[str, object] = field(default_factory=dict)