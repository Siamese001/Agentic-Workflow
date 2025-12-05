"""
Relevance scoring for résumé processing context items.

Provides deterministic scoring to prioritize relevant information for résumé improvement workflows.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class ContextItem:
    """
    Represents context item for résumé processing relevance scoring.

    Enables intelligent information prioritization for comprehensive résumé enhancement.
    """
    id: str
    text: str
    metadata: Dict[str, Any]


def score_relevance(query: str, items: List[ContextItem]) -> List[Tuple[ContextItem, float]]:
    """
    Scores context items by relevance to résumé improvement queries.

    Prioritizes information that supports comprehensive résumé enhancement processing.
    """

    q_tokens = set((query or "").lower().split())
    scored: List[Tuple[ContextItem, float]] = []
    for item in items:
        tokens = set((item.text or "").lower().split())
        # Jaccard-like overlap proxy.
        if not tokens:
            score = 0.0
        else:
            inter = len(q_tokens & tokens)
            union = len(q_tokens | tokens) or 1
            score = inter / union
        scored.append((item, float(score)))
    # Sort by score descending, then id for determinism.
    scored.sort(key=lambda x: (-x[1], x[0].id))
    return scored



