"""Types and models for manage_observability_context."""

from enum import Enum

class FormatObservabilityContextPlanType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'
