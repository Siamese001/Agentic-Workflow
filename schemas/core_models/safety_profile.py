


class SafetyProfile(BaseModel):
    """Safety configuration profile used by execution profiles.

    This is intentionally string/primitive based to avoid cycles and
    mirrors the SafetyTier + policy toggles used in ExecutionProfileSpec.
    """

    _safety_tier: str = Field(default="standard",
        description="Safety tier: standard | strict | relaxed | debug")
    _pii_detection_enabled: bool = True
    _policy_engine_enabled: bool = True
