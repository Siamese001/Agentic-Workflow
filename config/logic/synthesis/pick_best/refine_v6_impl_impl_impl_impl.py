"""Implementation for refine_v6_impl_impl_impl."""

from typing import Any, Dict, List, Optional

def bm25(items: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """
    Deterministic BM25-like ranking.

    Delegates scoring to runtime_utils.Ranking.bm25_rank.
    """
    return _Ranking.bm25_rank(items)

def dense(items: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """
    Deterministic dense-score ranking (SHA-based pseudo-embedding).
    """
    return _Ranking.dense_rank(items)

def hybrid(items: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """
    Combined ranking (BM25 + dense).
    """
    return _Ranking.hybrid_rank(items)

def apply_strategy(items: List[Dict[str, object]], strategy: str='hybrid') -> List[Dict[str, object]]:
    """
    Apply a ranking strategy:

        "bm25"
        "dense"
        "hybrid"
        anything else → hybrid

    After ranking, all candidates receive a deterministic "rank" field.

    This function never mutates the caller’s list.
    """
    s = (strategy or 'hybrid').lower().strip()
    if s == 'bm25':
        ranked = bm25(items)
    elif s == 'dense':
        ranked = dense(items)
    else:
        ranked = hybrid(items)
    out: List[Dict[str, object]] = []
    for idx, item in enumerate(ranked):
        new_item = dict(item)
        new_item['rank'] = idx + 1
        out.append(new_item)
    return out

def fuse_ranked_groups(groups: List[List[Dict[str, object]]]) -> List[Dict[str, object]]:
    """
    Fuse multiple pre-ranked lists into a single deterministic list.

    Algorithm:
        1. Flatten
        2. Deduplicate by (query, evidence)
        3. Sort by minimal rank across groups
        4. Secondary sort by alphabetical evidence
        5. Re-assign ranks

    All behavior purely deterministic.
    """
    flattened: List[Dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for group in groups or []:
        for item in group or []:
            key = (str(item.get('query', '')), str(item.get('evidence', '')))
            if key not in seen:
                seen.add(key)
                flattened.append(dict(item))
    flattened.sort(key=lambda x: (int(x.get('rank', 9999999)), str(x.get('evidence', '')).lower()))
    for idx, item in enumerate(flattened):
        item['rank'] = idx + 1
    return flattened

def rank_documents(items: List[Dict[str, object]], strategy: str='hybrid') -> List[Dict[str, object]]:
    """
    Top-level ranking support used by RAGExecutor:

        items:
            list[{ query, evidence, ... }]

        strategy:
            "bm25" | "dense" | "hybrid"

    Returns ranked+sorted list with final deterministic ordering.
    """
    if not items:
        return []
    ranked = apply_strategy(items, strategy=strategy)
    ranked.sort(key=lambda x: (int(x.get('rank', 9999999)), x.get('evidence', '')))
    return ranked

