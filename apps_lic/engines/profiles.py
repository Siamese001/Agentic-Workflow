from __future__ import annotations

"""
System Profiles Schemas
=======================
Defines safety and budget profiles for system execution.
"""

from pydantic import BaseModel, Field


class SafetyProfile(BaseModel):
    """Safety configuration profile used by execution profiles."""
    safety_tier: str = Field(default="standard", description="standard | strict | relaxed | debug")
    pii_detection_enabled: bool = True
    policy_engine_enabled: bool = True

class BudgetProfile(BaseModel):
    """High-level budget profile for cost and latency envelopes."""
    max_cost_usd: float = Field(default=0.10, ge=0.0)
    max_latency_ms: int = Field(default=3000, ge=0)
