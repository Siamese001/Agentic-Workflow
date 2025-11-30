# Metacognition models
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Hypothesis:
    """Hypothesis for metacognitive reasoning"""
    id: str
    agent_id: str
    content: str
    confidence: float
    evidence_ids: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.evidence_ids is None:
            self.evidence_ids = []
        if self.metadata is None:
            self.metadata = {}
