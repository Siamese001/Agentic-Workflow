"""
Base Model Contracts - SSOT for foundational Pydantic models.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class sovereign_base_model(BaseModel):
    """Base model for all Sovereign entities with strict config."""
    model_config = ConfigDict(strict=True, frozen=True)

# Backward compat alias
SovereignBaseModel = sovereign_base_model


class territory(sovereign_base_model):
    """Brief description of functionality and purpose."""
    name: str
    depth: int
    path: str
    canon_key: Optional[int] = None

# Backward compat alias
Territory = territory


class agent_message(sovereign_base_model):
    """Brief description of functionality and purpose."""
    source: str
    destination: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Backward compat alias
AgentMessage = agent_message


# Public exports
__all__ = [
    # Snake case (canonical)
    "sovereign_base_model",
    "territory",
    "agent_message",
    # PascalCase aliases (backward compat)
    "SovereignBaseModel",
    "Territory",
    "AgentMessage",
]
