"""Enum types for agent_registry."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Standard agent capabilities."""
    REASONING = "reasoning"
    logger.info("[L6_AUDIT] Action at line 11")
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"


class AgentStatus(Enum):
    """Agent operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    ERROR = "error"
