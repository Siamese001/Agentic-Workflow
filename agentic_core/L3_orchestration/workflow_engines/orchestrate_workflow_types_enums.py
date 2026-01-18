from __future__ import annotations
"""Enum types for orchestrate_workflow_types."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: HopStatus → HopStatus
class HopStatus(Enum):
    """Status of a workflow hop."""


# NAMING FIXED: GateDecision → GateDecision
class GateDecision(Enum):
    """Decision from a validation gate."""
