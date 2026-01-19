from __future__ import annotations
"""Enum types for outreach_orchestration_config."""
import logging
from enum import Enum, auto

_logger = logging.getLogger(__name__)


# NAMING FIXED: Route → Route
class Route(str, Enum):
    """Message delivery routes."""


# NAMING FIXED: Archetype → Archetype
class Archetype(str, Enum):
    """Recipient archetypes for personalization."""


# NAMING FIXED: ValidationSeverity → ValidationSeverity
class ValidationSeverity(str, Enum):
    """Validation result Severity levels."""