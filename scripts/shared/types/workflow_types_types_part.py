"""Split module 1 for workflow_types_types."""
import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

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
    _hop_id: str
    _status: HopStatus
    _started_at: Optional[str] = None
    _completed_at: Optional[str] = None
    _error: Optional[str] = None
    _output: Optional[Dict[str, object]] = None