from __future__ import annotations
'Enum types for orchestrate_workflow_types.'
import logging
from enum import Enum
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger(__name__)

class HopStatus(Enum):
    """Status of a workflow hop."""

class GateDecision(Enum):
    """Decision from a validation gate."""
