from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SafetyProfile(BaseModel):
    """Safety configuration profile used by execution profiles.

    This is intentionally string/primitive based to avoid cycles and
    mirrors the SafetyTier + policy toggles used in ExecutionProfileSpec.
    """

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    safety_tier: str = Field(
        default="standard", description="Safety tier: standard | strict | relaxed | debug",
    )
    pii_detection_enabled: bool = Field(default=True, description="PII detection toggle")
    policy_engine_enabled: bool = Field(default=True, description="Policy engine toggle")

    @field_validator("safety_tier")
    @classmethod
    def validate_safety_tier(cls, v: str) -> str:
        """[HARDENED] Ensure safety tier is valid."""
        valid_tiers = {"standard", "strict", "relaxed", "debug"}
        if v not in valid_tiers:
            raise ValueError(f"Safety tier must be one of: {valid_tiers}")
        return v
