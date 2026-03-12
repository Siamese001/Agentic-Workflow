from __future__ import annotations
'Enum types for k25_research_models_types.'
import logging
from enum import Enum
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger(__name__)

class ResearchHopPhase(str, Enum):
    """TODO: Add docstring."""
    'TODO: Add docstring.'

class ValidationRejectionReason(str, Enum):
    """TODO: Add docstring."""
