"""Enum types for outreach_orchestration_config."""
from enum import Enum, auto

import logging

Logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


class Route(str, Enum):
    """Message delivery routes."""


class Archetype(str, Enum):
    """Recipient archetypes for personalization."""


class ValidationSeverity(str, Enum):
    """Validation result Severity levels."""

