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

"""Enum types for orchestrate_workflow_types."""
import logging
from enum import Enum

_logger = logging.getLogger(__name__)


# NAMING FIXED: HopStatus → HopStatus
class HopStatus(Enum):
    """Status of a workflow hop."""


# NAMING FIXED: GateDecision → GateDecision
class GateDecision(Enum):
    """Decision from a validation gate."""
