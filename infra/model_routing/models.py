from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.models.models import ExecutionProfile


@dataclass
class ModelChoice:
    """Concrete model selection for a given call.

    This is intentionally lightweight and provider-agnostic; it does not
    import provider SDKs or perform any I/O.
    """

    provider: str
    model_name: str
    cost_tier: str  # e.g. "low", "medium", "high"
    estimated_cost: float
    latency_ms: int


@dataclass
class RoutingContext:
    """Context used by dynamic model routing.

    This mirrors the minimal fields we need from the agent stack without
    importing core orchestration modules.
    """

    agent_id: str
    task_type: str
    execution_profile: Optional[ExecutionProfile] = None



