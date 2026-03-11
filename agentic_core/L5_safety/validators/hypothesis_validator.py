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
Metacognition & Self-Analysis Schemas
====================================
Defines schemas for agentic self-reflection, hypothesis tracking,
and uncertainty quantification.
"""


from pydantic import BaseModel, ConfigDict, Field, field_validator


class Hypothesis(BaseModel):
    """A lightweight hypothesis generated during the reasoning layer."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Unique Claim identifier")
    agent_id: str = Field(..., description="The agent that proposed this hypothesis")
    content: str = Field(..., description="The specific Claim or theory")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence level (0.0 to 1.0)")
    evidence_ids: list[str] = Field(default_factory=list, description="References to SignedClaims")
    rationale: str | None = Field(default=None, description="Reasoning behind the hypothesis")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """[HARDENED] Ensure content is not empty."""
        if not v.strip():
            raise ValueError("Hypothesis content cannot be empty")
        return v.strip()


class MetacognitionReport(BaseModel):
    """Aggregate view of system-wide hypotheses and detected issues."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    hypotheses: list[Hypothesis] = Field(default_factory=list, description="List of system hypotheses")
    global_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Global confidence score")
    uncertainty_score: float = Field(default=0.0, ge=0.0, le=1.0, description="System uncertainty level")
    issues_detected: list[str] = Field(default_factory=list, description="List of detected issues")
