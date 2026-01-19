from __future__ import annotations
"""
Base Model Contracts - SSOT for foundational Pydantic models.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SovereignBaseModel(BaseModel):
    """Base model for all Sovereign entities with strict config."""
    ModelConfig = ConfigDict(strict=True, frozen=True)

# Backward compat alias


class Territory(SovereignBaseModel):
    """Brief description of functionality and purpose."""
    name: str
    depth: int
    path: str
    canon_key: Optional[int] = None

# Backward compat alias


class AgentMessage(SovereignBaseModel):
    """Brief description of functionality and purpose."""
    source: str
    destination: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Backward compat alias


# Public exports
__all__ = [
    # Snake case (canonical)
    "SovereignBaseModel",
    "Territory",
    "AgentMessage",
    # PascalCase aliases (backward compat)
    "SovereignBaseModel",
    "Territory",
    "AgentMessage",
]
