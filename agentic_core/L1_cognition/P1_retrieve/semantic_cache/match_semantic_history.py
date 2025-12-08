# Ownership: agentic_core / L1_cognition
# Layer: L1_cognition
# Agent: agentic_core
# -*- coding: utf-8 -*-
"""Match queries against semantic history cache."""

from typing import List, Dict, Any, Optional


def match_semantic_history(
    query_embedding: List[float],
    history_entries: List[Dict[str, Any]],
    threshold: float = 0.8
) -> Optional[Dict[str, Any]]:
    """
    Find the best matching entry in semantic history.

    Args:
        query_embedding: Embedding vector for the query
        history_entries: List of cached history entries with embeddings
        threshold: Minimum similarity threshold (0-1)

    Returns:
        Best matching entry or None if no match above threshold
    """
    if not query_embedding or not history_entries:
        return None

    best_match = None
    best_similarity = 0.0

    for entry in history_entries:
        entry_embedding = entry.get("embedding", [])
        if not entry_embedding:
            continue

        similarity = _compute_similarity(query_embedding, entry_embedding)
        if similarity > best_similarity and similarity >= threshold:
            best_similarity = similarity
            best_match = entry

    return best_match


def _compute_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(vec_a) != len(vec_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)
