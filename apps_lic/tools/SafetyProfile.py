"""
System Profiles Schemas
=======================
Defines safety and budget profiles for system execution.
"""

import os

from pydantic import BaseModel, Field


class SafetyProfile(BaseModel):
    """Safety configuration profile used by execution profiles."""

    safety_tier: str = Field(default="standard", description="standard | strict | relaxed | debug")
    pii_detection_enabled: bool = True
    policy_engine_enabled: bool = True


class BudgetProfile(BaseModel):
    """[HARDENED] Environment-aware high-level budget profile for cost and latency envelopes."""

    max_cost_usd: float = Field(
        default_factory=lambda: float(os.getenv("BUDGET_MAX_COST_USD", "0.10")),
        ge=0.0,
    )
    max_latency_ms: int = Field(default_factory=lambda: int(os.getenv("BUDGET_MAX_LATENCY_MS", "3000")), ge=0)
