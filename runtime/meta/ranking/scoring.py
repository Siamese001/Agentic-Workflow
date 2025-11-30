# Scoring functions for ranking
from typing import List, Dict, Any
import math
import re
from runtime.core.models import Evidence

def bm25_score(item: Dict[str, Any], k1: float = 1.2, b: float = 0.75) -> float:
    """Calculate BM25 score for a document item"""
    text = item.get("text", "")
    
    # Simple tokenization
    tokens = re.findall(r'\w+', text.lower())
    
    # Important tokens for resume/domain context
    important_tokens = {
        'llm', 'resume', 'experience', 'python', 'machine', 'learning',
        'engineering', 'manager', 'senior', 'lead', 'architect', 'developer'
    }
    
    # Calculate score based on important tokens
    score = 0.0
    for token in tokens:
        if token in important_tokens:
            score += 2.0  # Boost important tokens
        else:
            score += 1.0
    
    # Normalize by document length
    if tokens:
        score = score / len(tokens)
    
    return score

def dense_score(item: Dict[str, Any]) -> float:
    """Calculate dense embedding score (mock implementation)"""
    text = item.get("text", "")
    
    # Mock dense scoring based on text characteristics
    score = len(text) * 0.01  # Length factor
    
    # Boost for technical terms
    tech_terms = ['python', 'javascript', 'react', 'aws', 'docker', 'kubernetes']
    for term in tech_terms:
        if term.lower() in text.lower():
            score += 0.2
    
    return min(1.0, score)

def normalize_scores(evidence_list: List[Any]) -> List[Any]:
    """Normalize scores to [0, 1] range"""
    if not evidence_list:
        return []
    
    # Extract scores from evidence objects
    scores = [ev.score for ev in evidence_list]
    
    min_score = min(scores)
    max_score = max(scores)
    
    if max_score == min_score:
        normalized_scores = [0.5] * len(scores)
    else:
        normalized_scores = []
        for score in scores:
            norm_score = (score - min_score) / (max_score - min_score)
            normalized_scores.append(norm_score)
    
    # Update evidence objects with normalized scores
    normalized_evidence = []
    for evidence, norm_score in zip(evidence_list, normalized_scores):
        # Create a copy with normalized score
        normalized_e = Evidence(
            text=evidence.text,
            score=norm_score,
            source=evidence.source,
            metadata=evidence.metadata.copy() if evidence.metadata else {}
        )
        normalized_evidence.append(normalized_e)
    
    return normalized_evidence

def merge_scores(evidence_list: List[Any], bm25_weight: float = 0.5) -> List[Any]:
    """Merge scores from multiple sources for a list of evidence objects"""
    if not evidence_list:
        return []
    
    # Group evidence by text and merge scores, preserving highest score per source
    text_groups = {}
    for evidence in evidence_list:
        text = evidence.text
        if text not in text_groups:
            text_groups[text] = {}
        # Keep the highest score for each source
        source = evidence.source
        if source not in text_groups[text] or evidence.score > text_groups[text][source].score:
            text_groups[text][source] = evidence
    
    # Flatten grouped evidence, taking the highest scoring evidence from each source
    merged_results = []
    for text, source_dict in text_groups.items():
        for source, evidence in source_dict.items():
            merged_results.append(evidence)
    
    # Sort by score (descending)
    merged_results.sort(key=lambda x: x.score, reverse=True)
    return merged_results
