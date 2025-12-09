# Ownership: agentic_core / L1_cognition
# Layer: L1_cognition
# Agent: agentic_core
# -*- coding: utf-8 -*-
"""Compute semantic distance between embeddings."""

from typing import List


def compute_semantic_distance(embedding_a: List[float], embedding_b: List[float]) -> float:
    """
    Compute cosine distance between two embedding vectors.

    Args:
        embedding_a: First embedding vector
        embedding_b: Second embedding vector

    Returns:
        Cosine distance (0 = identical, 2 = opposite)
    """
    if not embedding_a or not embedding_b:
        return 1.0

    if len(embedding_a) != len(embedding_b):
        return 1.0

    dot_product = sum(a * b for a, b in zip(embedding_a, embedding_b))
    norm_a = sum(a * a for a in embedding_a) ** 0.5
    norm_b = sum(b * b for b in embedding_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 1.0

    cosine_similarity = dot_product / (norm_a * norm_b)
    return 1.0 - cosine_similarity
