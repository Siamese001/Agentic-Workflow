from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class SafetyProfile(BaseModel):
    """Safety configuration profile used by execution profiles.

    This is intentionally string/primitive based to avoid cycles and
    mirrors the SafetyTier + policy toggles used in ExecutionProfileSpec.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    safety_tier: str = Field(
        default="standard", description="Safety tier: standard | strict | relaxed | debug"
    )
    pii_detection_enabled: bool = Field(default=True, description="PII detection toggle")
    policy_engine_enabled: bool = Field(default=True, description="Policy engine toggle")

    @field_validator("safety_tier")
    @classmethod
    def validate_safety_tier(cls, v: str) -> str:
        """[HARDENED] Ensure safety tier is valid."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyProfile.validate_safety_tier")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyProfile.validate_safety_tier".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        valid_tiers = {"standard", "strict", "relaxed", "debug"}
        if v not in valid_tiers:
            raise ValueError(f"Safety tier must be one of: {valid_tiers}")
        return v
