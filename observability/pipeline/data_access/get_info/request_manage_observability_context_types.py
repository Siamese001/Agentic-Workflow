"""Types and models for request_manage_observability_context."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class FormatObservabilityContextPlanType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'
