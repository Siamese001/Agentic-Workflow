"""
Model routing data structures for résumé processing workflows.

Defines lightweight model selection and routing context for optimal résumé improvement performance.
"""

from dataclasses import dataclass
from typing import Optional

from core.models.models import ExecutionProfile


@dataclass
class ModelChoice:
    """
    Represents model selection choice for résumé processing workflows.

    Enables lightweight provider-agnostic model routing for comprehensive résumé enhancement.
    """

    provider: str
    model_name: str
    cost_tier: str  # e.g. "low", "medium", "high"
    estimated_cost: float
    latency_ms: int


@dataclass
class RoutingContext:
    """
    Provides routing context for résumé processing model selection.

    Ensures optimal model choice based on agent and task requirements for résumé improvement.
    """

    agent_id: str
    task_type: str
    execution_profile: Optional[ExecutionProfile] = None



