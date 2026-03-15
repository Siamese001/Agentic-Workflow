from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Prompt Injection & Governance Schemas
====================================
Defines schemas for dynamic prompt injection and safety scoping.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


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

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    hop_types: list[str] = Field(default_factory=list)
    stages: list[str] = Field(default_factory=list)
    contexts: dict[str, Any] = Field(default_factory=dict)


class InjectionPattern(BaseModel):
    """A single prompt injection pattern template."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    type: InjectionType
    description: str
    template: str
    variables: list[str] = Field(default_factory=list)
    scope: InjectionScope = Field(default_factory=InjectionScope)
    priority: int = Field(default=0, ge=0, le=10)
    enabled: bool = True

    @field_validator("variables")
    @classmethod
    def validate_variables(cls, value: list[str]) -> list[str]:
        """[HARDENED] Ensure variables list has no empty entries."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InjectionPattern.validate_variables")

        for variable in value:
            if not variable.strip():
                raise ValueError("Injection variables cannot be empty")
        return value
