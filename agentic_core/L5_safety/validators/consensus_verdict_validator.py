from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Consensus & Deliberation Schemas
===============================
Defines the structures for multi-model consensus and individual
model opinions. Used to ensure plan safety and agreement across
the agentic collective.
"""


from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConsensusVerdict(BaseModel):
    """Result of a consensus deliberation across multiple models."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    chosen_plan: str = Field(..., description="The definitive plan agreed upon by the collective")
    consensus_score: float = Field(..., ge=0.0, le=1.0, description="Level of agreement (0.0 to 1.0)")
    dissenting_opinions: list[str] = Field(
        default_factory=list,
        description="Summary of non-concurring views",
    )
    reasoning: str = Field(..., description="The logic used to synthesize the final Verdict")
    safe_to_proceed: bool = Field(..., description="Final gate check based on consensus risks")


class ModelOpinion(BaseModel):
    """Individual model's opinion on a proposed plan."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    model_name: str = Field(..., description="The identifier of the contributing model")
    plan: str = Field(..., description="The specific plan being evaluated")
    reasoning: str = Field(..., description="Individual model's logic for its stance")
    risk_assessment: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this specific opinion")

    @field_validator("risk_assessment")
    @classmethod
    def validate_risk_assessment(cls, v: str) -> str:
        """[HARDENED] Ensure risk assessment is valid."""
        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Risk assessment must be one of: {valid_levels}")
        return v.upper()
