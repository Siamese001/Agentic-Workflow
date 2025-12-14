"""Enum types for orchestrate_workflow_types."""
import logging



logger = logging.getLogger(__name__)
class HopStatus(Enum):
    """Status of a workflow hop."""
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    SKIPPED = 'SKIPPED'

class GateDecision(Enum):
    """Decision from a validation gate."""
    PASS = 'PASS'
    FAIL = 'FAIL'
    WARN = 'WARN'
    SKIP = 'SKIP'
