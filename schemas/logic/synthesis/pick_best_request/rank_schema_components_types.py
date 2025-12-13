"""Types and models for rank_schema_components."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class RankDataComponentsPlanType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'

