# Hypothesis generation module
from typing import List, Any
from .models import Hypothesis

def generate_initial_hypotheses(agent_id: str, rag_context: Any, max_hypotheses: int = 5) -> List[Hypothesis]:
    """Generate initial hypotheses based on RAG context"""
    hypotheses = []
    
    # Extract evidence from RAG context
    evidence_count = 0
    if hasattr(rag_context, 'evidence'):
        evidence_count = len(rag_context.evidence)
    
    # Generate hypotheses based on available evidence
    for i in range(min(max_hypotheses, max(1, evidence_count))):
        h = Hypothesis(
            id=f"hypothesis_{i}",
            agent_id=agent_id,
            content=f"Generated hypothesis {i} based on evidence",
            confidence=0.8 - (i * 0.1),  # Decreasing confidence
            evidence_ids=[f"ev_{j}" for j in range(min(3, evidence_count))]
        )
        hypotheses.append(h)
    
    return hypotheses
