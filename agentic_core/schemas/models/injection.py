from __future__ import annotations

"""
Prompt Injection & Governance Schemas
====================================
Defines schemas for dynamic prompt injection and safety scoping.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class InjectionType(str, Enum):
    """Types of prompt injections."""
    SYSTEM = "system"
    USER = "user"
    CONTEXT = "context"
    REASONING = "reasoning"
    TOOLING = "tooling"
    SAFETY = "safety"
    OUTPUT = "output"

class InjectionScope(BaseModel):
    """Scope defining where an injection should be applied."""
    hop_types: list[str] = Field(default_factory=list)
    stages: list[str] = Field(default_factory=list)
    contexts: dict[str, Any] = Field(default_factory=dict)

class InjectionPattern(BaseModel):
    """A single prompt injection pattern template."""
    id: str
    name: str
    type: InjectionType
    description: str
    template: str
    variables: list[str] = Field(default_factory=list)
    scope: InjectionScope = Field(default_factory=InjectionScope)
    priority: int = Field(default=0, ge=0, le=10)
    enabled: bool = True
