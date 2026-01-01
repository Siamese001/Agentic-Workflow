"""Enum types for outreach_orchestration_config."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: Route → route
class route(str, Enum):
    """Message delivery routes."""


# NAMING FIXED: Archetype → archetype
class archetype(str, Enum):
    """Recipient archetypes for personalization."""


# NAMING FIXED: ValidationSeverity → validation_severity
class validation_severity(str, Enum):
    """Validation result severity levels."""