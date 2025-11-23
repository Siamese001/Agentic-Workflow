from __future__ import annotations

"""Simple relevance scoring helpers for context items.

These utilities are deterministic and do not call external services.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class ContextItem:
    id: str
    text: str
    metadata: Dict[str, Any]


def score_relevance(query: str, items: List[ContextItem]) -> List[Tuple[ContextItem, float]]:
    """Score items by simple token overlap with the query.

    This is a placeholder used to support tests and prompt assembly
    without depending on vector search.
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
