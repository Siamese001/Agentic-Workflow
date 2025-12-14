"""Enum types for use_observability_execution."""
import logging



logger = logging.getLogger(__name__)
class ExecutionStrategy(Enum):
    """Strategies for execution."""
    IMMEDIATE = 'immediate'
    QUEUED = 'queued'
    SCHEDULED = 'scheduled'
    CONDITIONAL = 'conditional'

class ExecutionPriority(Enum):
    """Priority levels for execution."""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    CRITICAL = 'critical'
