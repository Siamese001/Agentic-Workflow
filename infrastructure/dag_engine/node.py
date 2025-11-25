from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DAGNode(BaseModel):
    """Agent-aware DAG node model used by Phase-1 substrate.

    This model is a higher-level, declarative view over the lower-level
    infra.dag_engine.models.Node dataclass. It is not yet wired directly
    into the executor but provides a typed contract for future routing
    and orchestration layers.
    """

    id: str
    type: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    agent_type: Optional[str] = None
    required_capabilities: List[str] = Field(default_factory=list)
    preferred_agent_ids: List[str] = Field(default_factory=list)



