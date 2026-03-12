from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class BudgetProfile(BaseModel):
    """High-level budget profile for cost/latency envelopes.

    This duplicates some of the fields from ExecutionProfileSpec so that
    future callers can reason about budget in a single nested object.
    """
    model_config = ConfigDict(frozen=True, extra='forbid')
    max_cost_usd: float = Field(default=0.1, ge=0.0, description='Maximum cost in USD')
    max_latency_ms: int = Field(default=3000, ge=0, description='Maximum allowed latency in ms')

    @field_validator('max_latency_ms')
    @classmethod
    def validate_latency(cls, value: int) -> int:
        """[HARDENED] Ensure latency ceiling is positive."""
        if value <= 0:
            raise ValueError('max_latency_ms must be greater than 0')
        return value
