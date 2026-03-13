from __future__ import annotations

"Enum types for orchestrate_workflow_types."
import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class HopStatus(Enum):
    """Status of a workflow hop."""


class GateDecision(Enum):
    """Decision from a validation gate."""
