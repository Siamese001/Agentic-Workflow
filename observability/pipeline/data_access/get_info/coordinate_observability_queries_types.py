"""Types and models for coordinate_observability_queries."""

from enum import Enum
import logging


logger = logging.getLogger(__name__)
class CoordinateObservabilityOperationsOrchestratorType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'
