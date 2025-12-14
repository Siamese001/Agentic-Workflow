"""Enum types for agent_registry."""
import logging
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Standard agent capabilities."""

class AgentStatus(Enum):
    """Agent operational status."""