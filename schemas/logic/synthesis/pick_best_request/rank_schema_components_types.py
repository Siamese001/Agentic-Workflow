"""Types and models for rank_schema_components."""

from enum import Enum

class RankDataComponentsPlanType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'
