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

"""Dataclass models for lic_routing_rules."""
import logging
from dataclasses import dataclass, field

_logger = logging.getLogger(__name__)
# from agentic_core.lic_routing_rules_enums import *  # Star import removed


@dataclass
# NAMING FIXED: ToolCallBudget → ToolCallBudget
class ToolCallBudget:
    """Tool call budget configuration."""

    _minimum: int = 0
    _maximum: int = 20
    _guidance: dict[str, str] = field(default_factory=dict)
