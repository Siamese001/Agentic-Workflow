from __future__ import annotations

"""Enum types for AgentRegistry."""
import logging
from enum import Enum
from typing import Any

_logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Standard agent capabilities."""

    REASONING: Any = "reasoning"
    PLANNING: Any = "planning"
    EXECUTION: Any = "execution"
    MONITORING: Any = "monitoring"


class AgentStatus(Enum):
    """Agent operational status."""

    ACTIVE: Any = "active"
    INACTIVE: Any = "inactive"
    BUSY: Any = "busy"
    ERROR: Any = "error"
