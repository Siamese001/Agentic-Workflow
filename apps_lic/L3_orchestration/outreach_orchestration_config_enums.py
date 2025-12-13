"""Enum types for outreach_orchestration_config."""

from enum import Enum

class Route(str, Enum):
    """Message delivery routes."""
    INMAIL = 'INMAIL'
    CONNECTION_REQ = 'CONNECTION_REQ'
    EMAIL = 'EMAIL'
    FOLLOW_UP = 'FOLLOW_UP'
    SHORT_NEW = 'SHORT_NEW'
    LONG_NEW = 'LONG_NEW'

class Archetype(str, Enum):
    """Recipient archetypes for personalization."""
    C_LEVEL = 'C_LEVEL'
    EXECUTIVE = 'EXECUTIVE'
    SENIOR_TA = 'SENIOR_TA'
    RECRUITER = 'RECRUITER'

class ValidationSeverity(str, Enum):
    """Validation result severity levels."""
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    INFO = 'INFO'

