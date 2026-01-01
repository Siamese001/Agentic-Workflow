"""Enum types for orchestrate_workflow_types."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: HopStatus → hop_status
class hop_status(Enum):
    """Status of a workflow hop."""


# NAMING FIXED: GateDecision → gate_decision
class gate_decision(Enum):
    """Decision from a validation gate."""