"""Types and models for check_schema_policy."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class CheckDataPolicyPlanType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'

