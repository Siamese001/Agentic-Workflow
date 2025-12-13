"""Types and models for workflow_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class HopStatus(Enum):
    """Status of a workflow hop/step."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()

class GateDecision(Enum):
    """Decision from a workflow gate."""
    PROCEED = auto()
    BLOCK = auto()
    RETRY = auto()
    ESCALATE = auto()

class BulletProvenance(Enum):
    """Source of a bullet point."""
    Verbatim = 'verbatim'
    Enhanced = 'enhanced'
    Generated = 'generated'

@dataclass
class HopCheckpoint:
    """Checkpoint data for a workflow hop."""
    hop_id: str
    status: HopStatus
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output: Optional[Dict[str, object]] = None

@dataclass
class RetrievalSource:
    """Metadata about a data retrieval source."""
    id: str
    type: str
    confidence: float = 0.0
    status: str = 'UNKNOWN'
    specific_source: Optional[str] = None

