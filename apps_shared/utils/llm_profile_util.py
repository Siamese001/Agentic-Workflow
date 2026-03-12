from pydantic import BaseModel, Field
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class LLMProfile(BaseModel):
    """LLM configuration profile used by execution profiles.

    This model is intentionally minimal and mirrors the knobs already
    present in ExecutionProfileSpec: reasoning_mode, ModelTier,
    max_cost_usd, max_latency_ms.
    """
    reasoning_mode: ReasoningMode = ReasoningMode.COT
    ModelTier: str = Field(default='balanced', description="Model tier hint, e.g. 'cheap', 'balanced', 'premium'.")
    max_cost_usd: float = Field(default=0.1, ge=0.0)
    max_latency_ms: int = Field(default=3000, ge=0)
