"""Types and models for request_orchestrate_observability_planning."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class OrchestrateObservabilityPlanningOrchestratorType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'
