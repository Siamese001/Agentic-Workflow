from __future__ import annotations

"""
Core Contracts - Pydantic models for sovereign system contracts.
SSOT for retry policies, hop specifications, and registry.
"""
from typing import Any

from pydantic import BaseModel, Field


class RetryPolicy(BaseModel):
    """Retry policy for agent operations."""
    max_retries: int = Field(default=3, ge=0, le=10)
    backoff_base: float = Field(default=0.5, ge=0.1, le=5.0)
    backoff_max: float = Field(default=30.0, ge=1.0, le=300.0)
    retry_on: list[str] = Field(default_factory=lambda: ["timeout", "rate_limit"])


class HopSpec(BaseModel):
    """Specification for a HOP (Handoff Operation Protocol) stage."""
    hop_id: str
    name: str
    description: str = ""
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    retry_policy: RetryPolicy | None = None
    dependencies: list[str] = Field(default_factory=list)


class AgentContract(BaseModel):
    """Contract specification for an agent."""
    name: str
    layer: str
    capabilities: list[str] = Field(default_factory=list)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)


# Registry of all core contracts
CORE_CONTRACTS_REGISTRY: dict[str, Any] = {
    "RetryPolicy": RetryPolicy,
    "HopSpec": HopSpec,
    "AgentContract": AgentContract,
}


__all__ = [
    "RetryPolicy",
    "HopSpec",
    "AgentContract",
    "CORE_CONTRACTS_REGISTRY",
]
