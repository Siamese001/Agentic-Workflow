from __future__ import annotations

"""Tree-of-thought (ToT) reasoning helpers.

This module defines a small, deterministic interface for exploring a
space of candidate "thoughts" and selecting a best path.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ThoughtNode:
    content: str
    score: float


def tree_search(seed: str, max_depth: int = 2, branching: int = 2) -> Tuple[List[ThoughtNode], List[ThoughtNode]]:
    """Deterministic placeholder ToT search.

    Returns (path, explored) where:
        • path is the best-scoring path (here, just the seed split).
        • explored is a flat list of all visited nodes.
    """

    seed = (seed or "").strip()
    if not seed:
        return [], []

    # Simple heuristic: split by sentences or clauses.
    parts = [p.strip() for p in seed.replace(";", ".").split(".") if p.strip()]
    explored: List[ThoughtNode] = [ThoughtNode(content=p, score=float(len(p))) for p in parts]

    # Best path is just the longest part in this placeholder.
    if not explored:
        return [], []

    best = max(explored, key=lambda n: n.score)
    return [best], explored



