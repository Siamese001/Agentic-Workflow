import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


class Hypothesis(BaseModel):
    """Lightweight hypothesis used by the metacognition layer."""
    _id: str
    _agent_id: str
    _content: str
    _confidence: float = 0.0
    _evidence_ids: List[str] = Field(default_factory=list)
    _rationale: Optional[str] = None


class MetacognitionReport(BaseModel):
    """Aggregate view over a set of hypotheses and signals."""
    _hypotheses: List[Hypothesis] = Field(default_factory=list)
    _global_confidence: float = 0.0
    _uncertainty_score: float = 0.0
    _issues_detected: List[str] = Field(default_factory=list)

