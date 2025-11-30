# Hybrid ranking module for fusing and ranking results
from typing import List, Dict, Any, Optional
from runtime.core.models import Evidence, RetrievalConfig

def fuse_and_rank(lex_results: List[Evidence], dense_results: List[Evidence], cfg: RetrievalConfig, council_vote: Optional[Any] = None) -> Any:
    """Fuse lexical and dense results using Reciprocal Rank Fusion (RRF)"""
    k = 60  # RRF constant
    
    # Create rankings
    lex_rankings = {ev.text: i+1 for i, ev in enumerate(lex_results)}
    dense_rankings = {ev.text: i+1 for i, ev in enumerate(dense_results)}
    
    # Combine scores
    combined_scores = {}
    all_texts = set(lex_rankings.keys()) | set(dense_rankings.keys())
    
    for text in all_texts:
        score = 0.0
        if text in lex_rankings:
            score += 1.0 / (k + lex_rankings[text])
        if text in dense_rankings:
            score += 1.0 / (k + dense_rankings[text])
        combined_scores[text] = score
    
    # Sort by combined score
    sorted_texts = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)
    
    # Create final results and return as RAGResult-like object
    final_results = []
    for text in sorted_texts[:cfg.max_hits]:
        # Find original evidence
        original = next((ev for ev in lex_results + dense_results if ev.text == text), None)
        if original:
            final_results.append(Evidence(
                text=original.text,
                score=combined_scores[text],
                source="hybrid",
                metadata=original.metadata.copy()
            ))
    
    # Return mock RAGResult-like object with evidence attribute
    class MockRAGResult:
        def __init__(self, evidence):
            self.evidence = evidence
    
    return MockRAGResult(final_results)
