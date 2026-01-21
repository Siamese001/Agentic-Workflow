from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Hypothesis(BaseModel):
    """Lightweight hypothesis used by the metacognition layer."""

    id: str
    agent_id: str
    content: str
    confidence: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)
    rationale: Optional[str] = None


class MetacognitionReport(BaseModel):
    """Aggregate view over a set of hypotheses and signals."""

    hypotheses: List[Hypothesis] = Field(default_factory=list)
    global_confidence: float = 0.0
    uncertainty_score: float = 0.0
    issues_detected: List[str] = Field(default_factory=list)
