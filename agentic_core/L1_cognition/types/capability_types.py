from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
