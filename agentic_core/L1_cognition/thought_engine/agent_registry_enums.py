"""Enum types for agent_registry."""
import logging
from enum import Enum, auto
from typing import Any
_logger = logging.getLogger(__name__)

class agent_capability(Enum):
    """Standard agent capabilities."""
    REASONING: Any = 'reasoning'
    PLANNING: Any = 'planning'
    EXECUTION: Any = 'execution'
    MONITORING: Any = 'monitoring'

class agent_status(Enum):
    """Agent operational status."""
    ACTIVE: Any = 'active'
    INACTIVE: Any = 'inactive'
    BUSY: Any = 'busy'
    ERROR: Any = 'error'