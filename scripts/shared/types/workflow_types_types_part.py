"""Split module 1 for workflow_types_types."""
import logging



class CircuitState(Enum):
    """Circuit breaker states."""

class HopStatus(Enum):
    """Status of a workflow hop/step."""

class GateDecision(Enum):
    """Decision from a workflow gate."""

class BulletProvenance(Enum):
    """Source of a bullet point."""

@dataclass
class HopCheckpoint:
    """Checkpoint data for a workflow hop."""
    hop_id: str
    status: HopStatus
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output: Optional[Dict[str, object]] = None
