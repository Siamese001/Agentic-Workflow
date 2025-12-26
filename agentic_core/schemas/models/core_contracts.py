"""
Sovereign Schema SSOT
The absolute source of truth for Pydantic models and data contracts.
"""
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict

class SovereignBaseModel(BaseModel):
    """Base model for all Sovereign entities with strict config."""
    model_config = ConfigDict(strict=True, frozen=True)

class Territory(SovereignBaseModel):
    name: str
    depth: int
    path: str
    canon_key: Optional[int] = None

class AgentMessage(SovereignBaseModel):
    source: str
    destination: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
