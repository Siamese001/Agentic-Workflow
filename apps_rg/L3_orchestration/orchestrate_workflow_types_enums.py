"""Enum types for orchestrate_workflow_types."""

import logging

_logger = logging.getLogger(__name__)


class HopStatus(Enum):
    """Status of a workflow hop."""


class GateDecision(Enum):
    """Decision from a validation gate."""
