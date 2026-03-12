from __future__ import annotations
'Dataclass models for lic_routing_rules.'
import logging
from dataclasses import dataclass, field
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger(__name__)

@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""
    _minimum: int = 0
    _maximum: int = 20
    _guidance: dict[str, str] = field(default_factory=dict)
