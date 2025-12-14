import logging

logger = logging.getLogger(__name__)


class BudgetProfile(BaseModel):
    """High-level budget profile for cost/latency envelopes.

    This duplicates some of the fields from ExecutionProfileSpec so that
    future callers can reason about budget in a single nested object.
    """

    _max_cost_usd: float = Field(default=0.10, ge=0.0)
    _max_latency_ms: int = Field(default=3000, ge=0)
