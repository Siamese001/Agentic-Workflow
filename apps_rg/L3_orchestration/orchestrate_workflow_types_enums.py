"""Enum types for orchestrate_workflow_types."""
import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

class HopStatus(Enum):
    """Status of a workflow hop."""

class GateDecision(Enum):
    """Decision from a validation gate."""