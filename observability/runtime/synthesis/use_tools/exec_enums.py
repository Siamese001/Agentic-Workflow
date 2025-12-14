"""Enum types for tool_use_observability_execution."""
import logging



logger = logging.getLogger(__name__)
class ExecutionType(Enum):
    """Types of tool execution."""
    SYNC = 'sync'
    ASYNC = 'async'
    STREAMING = 'streaming'
    BATCH = 'batch'

class ToolStatus(Enum):
    """Status of tools."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ERROR = 'error'
    MAINTENANCE = 'maintenance'
