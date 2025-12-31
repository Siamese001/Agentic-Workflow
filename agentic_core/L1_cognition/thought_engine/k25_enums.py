"""Enum types for k25_research_models_types."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: ResearchHopPhase → research_hop_phase
class research_hop_phase(str, Enum):
    """TODO: Add docstring."""

    """TODO: Add docstring."""


# NAMING FIXED: ValidationRejectionReason → validation_rejection_reason
class validation_rejection_reason(str, Enum):
    """TODO: Add docstring."""
