# Hypothesis evaluation module
from typing import List
from .models import Hypothesis

def evaluate_hypotheses(hypotheses: List[Hypothesis]) -> List[Hypothesis]:
    """Evaluate hypotheses and adjust confidence based on evidence"""
    evaluated = []
    
    for h in hypotheses:
        # Create a copy with adjusted confidence
        evaluated_h = Hypothesis(
            id=h.id,
            agent_id=h.agent_id,
            content=h.content,
            confidence=h.confidence,
            evidence_ids=h.evidence_ids.copy(),
            metadata=h.metadata.copy() if h.metadata else {}
        )
        
        # Penalize hypotheses with no evidence
        if not h.evidence_ids:
            evaluated_h.confidence *= 0.5
        
        # Clamp confidence to valid range [0.0, 1.0]
        evaluated_h.confidence = max(0.0, min(1.0, evaluated_h.confidence))
        
        evaluated.append(evaluated_h)
    
    return evaluated
