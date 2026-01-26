from __future__ import annotations

"""
Metacognition & Self-Analysis Schemas
====================================
Defines schemas for agentic self-reflection, hypothesis tracking,
and uncertainty quantification.
"""


from pydantic import BaseModel, Field


class Hypothesis(BaseModel):
    """A lightweight hypothesis generated during the reasoning layer."""

    id: str = Field(..., description="Unique Claim identifier")
    agent_id: str = Field(..., description="The agent that proposed this hypothesis")
    content: str = Field(..., description="The specific Claim or theory")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list, description="References to SignedClaims")
    rationale: str | None = None


class MetacognitionReport(BaseModel):
    """Aggregate view of system-wide hypotheses and detected issues."""

    hypotheses: list[Hypothesis] = Field(default_factory=list)
    global_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    uncertainty_score: float = Field(default=0.0, ge=0.0, le=1.0)
    issues_detected: list[str] = Field(default_factory=list)
