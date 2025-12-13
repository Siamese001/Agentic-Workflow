"""Types and models for request_coordinate_observability_queries."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class CoordinateObservabilityOperationsOrchestratorType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'
