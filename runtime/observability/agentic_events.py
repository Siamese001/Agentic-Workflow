from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SafetyEvent(BaseModel):
    """Observability event capturing safety-related activity.

    This is intentionally lightweight and does not depend on higher-level
    orchestration types; callers pass identifiers and structured payloads.
    """

    name: str = "safety_event"
    ts_ms: int
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    stage: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class DecisionEvent(BaseModel):
    """Event describing an applied safety / routing decision."""

    name: str = "decision_event"
    ts_ms: int
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    decision_type: str
    action: str
    reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CostEvent(BaseModel):
    """Event capturing per-call cost/latency for observability."""

    name: str = "cost_event"
    ts_ms: int
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    provider: str
    model_name: str
    estimated_cost: float
    latency_ms: int
    metadata: Dict[str, Any] = Field(default_factory=dict)



