# Hypothesis generation module
from typing import List, Any
from .models import Hypothesis

def generate_initial_hypotheses(task: str, rag_context: Any, agent: Any, max_hypotheses: int = 5) -> List[Hypothesis]:
    """Generate initial hypotheses based on RAG context"""
    hypotheses = []
    
    # Extract evidence from RAG context
    evidence_count = 0
    if hasattr(rag_context, 'evidence'):
        evidence_count = len(rag_context.evidence)
    
    # Get agent_id from agent object
    agent_id = getattr(agent, 'agent_id', 'unknown')
    
    # Generate hypotheses based on available evidence
    for i in range(min(max_hypotheses, max(1, evidence_count))):
        # Lower confidence when no evidence available
        base_confidence = 0.2 if evidence_count == 0 else 0.8
        h = Hypothesis(
            id=f"hypothesis_{i}",
            agent_id=agent_id,
            content=f"Generated hypothesis {i} based on evidence",
            confidence=base_confidence - (i * 0.1),  # Decreasing confidence
            evidence_ids=[f"ev_{j}" for j in range(min(3, evidence_count))]
        )
        hypotheses.append(h)
    
    return hypotheses
