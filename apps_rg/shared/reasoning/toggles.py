"""
Reasoning Configuration Toggles for RG Sovereign Architecture.

Defines the bounds and safety switches for advanced reasoning capabilities
(CoT, ToT, Reflexion) within the agentic workflow.
Aligned with LIC ReasoningToggles pattern.

HARDENING: Adds get_toggles factory for environment switching.
"""

from __future__ import annotations

import os
from pydantic import BaseModel, Field, field_validator


class ReasoningToggles(BaseModel):
    """
    Configuration object for enabling/disabling advanced reasoning features.
    Enforces strict safety bounds to prevent infinite loops or token exhaustion.
    """

    # Core Toggles
    use_cot: bool = Field(default=True, description="Enable Chain-of-Thought reasoning.")
    use_reflexion: bool = Field(default=True, description="Enable self-correction loops.")
    strict_mode: bool = Field(default=True, description="Fail on minor validation errors.")

    # Tree of Thought Parameters
    tot_branches: int = Field(default=3, description="Number of alternative reasoning paths.")
    min_tot_depth: int = Field(default=2, description="Minimum depth for tree exploration.")

    # Sampling Parameters
    temperature_cap: float = Field(default=0.5, description="Maximum temperature.")

    @field_validator("tot_branches")
    @classmethod
    def validate_branches(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError(f"tot_branches must be between 1 and 5. Got {v}.")
        return v


def get_toggles(env: str = None) -> ReasoningToggles:
    """Factory to load toggles based on environment."""
    environment = env or os.getenv("RG_ENV", "prod")

    if environment == "dev":
        # Dev Mode: More expensive reasoning, loose constraints
        return ReasoningToggles(tot_branches=5, min_tot_depth=3, strict_mode=False)
    elif environment == "test":
        # Test Mode: Deterministic, fast
        return ReasoningToggles(use_cot=False, use_reflexion=False, tot_branches=1)

    # Prod Mode: Default
    return ReasoningToggles()
