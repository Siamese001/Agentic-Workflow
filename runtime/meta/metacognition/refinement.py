# Hypothesis refinement module
from typing import List
from .models import Hypothesis

def refine_low_confidence(hypotheses: List[Hypothesis], threshold: float = 0.2) -> List[Hypothesis]:
    """Refine hypotheses with confidence below a threshold"""
    refined = []
    
    for h in hypotheses:
        if h.confidence < threshold:
            # Mark very low confidence as discarded
            refined_h = Hypothesis(
                id=f"{h.id}_refined",
                agent_id=h.agent_id,
                content=f"[DISCARDED_CANDIDATE] {h.content}",
                confidence=h.confidence * 1.1,  # Slight boost
                evidence_ids=h.evidence_ids.copy(),
                metadata=h.metadata.copy() if h.metadata else {}
            )
        else:
            # Normal refinement - add evidence requirement note
            refined_h = Hypothesis(
                id=f"{h.id}_refined",
                agent_id=h.agent_id,
                content=f"{h.content} (needs further evidence)",
                confidence=h.confidence * 1.1,  # Slight boost
                evidence_ids=h.evidence_ids.copy(),
                metadata=h.metadata.copy() if h.metadata else {}
            )
        
        refined.append(refined_h)
    
    return refined
