"""Enum types for perform_observability_operation."""
import logging



logger = logging.getLogger(__name__)
class OperationCategory(Enum):
    """Categories of observability operations."""
    MONITORING = 'monitoring'
    TRACING = 'tracing'
    LOGGING = 'logging'
    METRICS = 'metrics'
    ALERTING = 'alerting'

class OperationScope(Enum):
    """Scope of observability operations."""
    SYSTEM = 'system'
    COMPONENT = 'component'
    SERVICE = 'service'
    REQUEST = 'request'
    CUSTOM = 'custom'
