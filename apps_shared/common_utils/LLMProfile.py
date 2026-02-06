# from archives.legacy_root_folders.core.models.models import ReasoningMode  # DEPRECATED: Archive import removed to protect archives from validation edits


class LLMProfile(BaseModel):
    """LLM configuration profile used by execution profiles.

    This model is intentionally minimal and mirrors the knobs already
    present in ExecutionProfileSpec: reasoning_mode, ModelTier,
    max_cost_usd, max_latency_ms.
    """

    reasoning_mode: ReasoningMode = ReasoningMode.COT
    ModelTier: str = Field(
        default="balanced", description="Model tier hint, e.g. 'cheap', 'balanced', 'premium'.",
    )
    max_cost_usd: float = Field(default=0.10, ge=0.0)
    max_latency_ms: int = Field(default=3000, ge=0)
