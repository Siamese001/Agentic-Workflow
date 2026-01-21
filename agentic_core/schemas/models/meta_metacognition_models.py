from __future__ import annotations

from pydantic import BaseModel, Field


class Hypothesis(BaseModel):
    """Lightweight hypothesis used by the metacognition layer."""

    id: str
    agent_id: str
    content: str
    confidence: float = 0.0
    evidence_ids: list[str] = Field(default_factory=list)
    rationale: str | None = None


class MetacognitionReport(BaseModel):
    """Aggregate view over a set of hypotheses and signals."""

    hypotheses: list[Hypothesis] = Field(default_factory=list)
    global_confidence: float = 0.0
    uncertainty_score: float = 0.0
    issues_detected: list[str] = Field(default_factory=list)
