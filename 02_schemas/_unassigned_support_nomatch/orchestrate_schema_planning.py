"""
Schema definitions for orchestration-level schema planning.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class OrchestrationMode(Enum):
    """Orchestration execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINED = "pipelined"
    CONDITIONAL = "conditional"


class ResourceType(Enum):
    """Resource types for orchestration."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"


@dataclass
class OrchestrationStep:
    """Schema for individual orchestration step."""
    step_id: str
    step_type: str
    dependencies: List[str]
    resources_required: Dict[ResourceType, int]
    timeout_seconds: int


@dataclass
class OrchestrationPlan:
    """Schema for complete orchestration plan."""
    plan_id: str
    mode: OrchestrationMode
    steps: List[OrchestrationStep]
    total_resources: Dict[ResourceType, int]
    estimated_duration_seconds: int


@dataclass
class OrchestrationRequest:
    """Schema for orchestration planning request."""
    schema_ids: List[str]
    priority: str
    constraints: Optional[Dict[str, Any]] = None
    optimization_target: Optional[str] = None