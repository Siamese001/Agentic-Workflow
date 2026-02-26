"""
Reasoning Configuration Toggles for RG Sovereign Architecture — DEFAULTS ONLY.

These are static fallback defaults used when no L0-stamped
ReasoningIntensityProfile is available (e.g. unit tests, offline mode).

GOVERNANCE: Runtime reasoning intensity is governed by the
ReasoningIntensityProfile stamped by L0 ReasoningPolicyEngine and
injected via SignedExecutionEnvelope. Do NOT add environment-based
overrides or a get_toggles() factory here.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ReasoningToggles(BaseModel):
    """
    Static fallback defaults for enabling/disabling advanced reasoning features.
    Enforces strict safety bounds to prevent infinite loops or token exhaustion.

    NOTE: At runtime these values are OVERRIDDEN by the L0-stamped
    ReasoningIntensityProfile.  This class is defaults-only.
    """

    # Core Toggles
    use_cot: bool = Field(default=True, description="Enable Chain-of-Thought reasoning.")
    use_reflexion: bool = Field(default=False, description="Enable self-correction loops.")
    strict_mode: bool = Field(default=True, description="Fail on minor validation errors.")
    use_persistent_tracing: bool = Field(default=True, description="Enable persistent trace storage.")
    use_cyclic_validation: bool = Field(default=True, description="Enable cyclic retry validation.")

    # Tree of Thought Parameters
    tot_branches: int = Field(default=2, description="Number of alternative reasoning paths.")
    min_tot_depth: int = Field(default=1, description="Minimum depth for tree exploration.")

    # Sampling Parameters
    temperature_cap: float = Field(default=0.5, description="Maximum temperature.")

    @field_validator("tot_branches")
    @classmethod
    def validate_branches(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError(f"tot_branches must be between 1 and 5. Got {v}.")
        return v


DEFAULT_TOGGLES = ReasoningToggles()
