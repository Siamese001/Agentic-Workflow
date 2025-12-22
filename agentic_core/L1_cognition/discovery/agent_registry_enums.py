"""Enum types for agent_registry."""
from enum import Enum, auto


import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Standard agent capabilities."""
    REASONING = "reasoning"
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"


class AgentStatus(Enum):
    """Agent operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    ERROR = "error"
