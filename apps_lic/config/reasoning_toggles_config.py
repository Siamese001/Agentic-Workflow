"""
Reasoning configuration Toggles — DEFAULTS ONLY.

These are static fallback defaults used when no L0-stamped
ReasoningIntensityProfile is available (e.g. unit tests, offline mode).

GOVERNANCE: Runtime reasoning intensity is governed by the
ReasoningIntensityProfile stamped by L0 ReasoningPolicyEngine and
injected into HOPPipelineExecutor via SignedExecutionEnvelope.
Do NOT add environment-based overrides here.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ReasoningToggles(BaseModel):
    """
    Static fallback defaults for reasoning feature configuration.
    Enforces strict safety bounds to prevent infinite loops or token exhaustion.

    NOTE: At runtime these values are OVERRIDDEN by the L0-stamped
    ReasoningIntensityProfile.  This class is defaults-only.
    """

    # Core Toggles
    use_cot: bool = Field(default=True, description="Enable Chain-of-Thought reasoning.")
    use_reflexion: bool = Field(default=False, description="Enable self-correction loops.")

    # Tree of Thought Parameters
    tot_branches: int = Field(default=2, description="Number of alternative reasoning paths.")
    min_tot_depth: int = Field(default=1, description="Minimum depth for tree exploration.")

    # Sampling Parameters
    self_consistency_samples: int = Field(default=3, description="Number of samples for majority voting.")
    temperature_cap: float = Field(default=0.5, description="Maximum temperature for reasoning steps.")

    @field_validator("tot_branches")
    @classmethod
    def validate_branches(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError(f"tot_branches must be between 1 and 5. Got {v}.")
        return v

    @field_validator("min_tot_depth")
    @classmethod
    def validate_depth(cls, v: int) -> int:
        if not 1 <= v <= 3:
            raise ValueError(f"min_tot_depth must be between 1 and 3. Got {v}.")
        return v

    @field_validator("temperature_cap")
    @classmethod
    def validate_temp(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"temperature_cap must be between 0.0 and 1.0. Got {v}.")
        return v

    class Config:
        """Pydantic configuration."""

        frozen = True  # Configs should be immutable once loaded


DEFAULT_TOGGLES = ReasoningToggles()
