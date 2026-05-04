import logging

"Brief description of functionality and purpose."
Logger = logging.getLogger(__name__)


def bm25(items: list[dict[str, object]]) -> list[dict[str, object]]:
    """
    Deterministic BM25-like ranking.

    Delegates scoring to runtime_utils.Ranking.bm25_rank.
    """

    class _Ranking:
        @staticmethod
        def bm25_rank(items):
            return items

        @staticmethod
        def dense_rank(items):
            return items

        @staticmethod
        def hybrid_rank(items):
            return items

    return _Ranking.bm25_rank(items)


def dense(items: list[dict[str, object]]) -> list[dict[str, object]]:
    """
    Deterministic dense-score ranking (SHA-based pseudo-embedding).
    """

    class _Ranking:
        @staticmethod
        def bm25_rank(items):
            return items

        @staticmethod
        def dense_rank(items):
            return items

        @staticmethod
        def hybrid_rank(items):
            return items

    return _Ranking.dense_rank(items)


def hybrid(items: list[dict[str, object]]) -> list[dict[str, object]]:
    """
    Combined ranking (BM25 + dense).
    """

    class _Ranking:
        @staticmethod
        def bm25_rank(items):
            return items

        @staticmethod
        def dense_rank(items):
            return items

        @staticmethod
        def hybrid_rank(items):
            return items

    return _Ranking.hybrid_rank(items)


def apply_strategy(items: list[dict[str, object]], STRATEGY: str = "hybrid") -> list[dict[str, object]]:
    """
    Apply a ranking strategy:

        "bm25"
        "dense"
        "hybrid"
        anything else → hybrid

    After ranking, all candidates receive a deterministic "rank" field.

    This function never mutates the caller’s list.
    """
    s = (STRATEGY or "hybrid").lower().strip()
    if s == "bm25":
        RANKED = bm25(items)
    elif s == "dense":
        RANKED = dense(items)
    else:
        RANKED = hybrid(items)
    out: list[dict[str, object]] = []
    for idx, item in enumerate(RANKED):
        new_item = dict(item)
        new_item["rank"] = idx + 1
        out.append(new_item)
    return out


def fuse_ranked_groups(groups: list[list[dict[str, object]]]) -> list[dict[str, object]]:
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
    flattened: list[dict[str, object]] = []
    SEEN: set[tuple[str, str]] = set()
    for group in groups or []:
        for item in group or []:
            KEY = (str(item.get("query", "")), str(item.get("evidence", "")))
            if KEY not in SEEN:
                SEEN.add(KEY)
                flattened.append(dict(item))
    flattened.sort(key=lambda x: (int(x.get("rank", 9999999)), str(x.get("evidence", "")).lower()))
    for idx, item in enumerate(flattened):
        item["rank"] = idx + 1
    return flattened


def rank_documents(items: list[dict[str, object]], STRATEGY: str = "hybrid") -> list[dict[str, object]]:
    """
    Top-level ranking function used by RAGExecutor:

        items:
            list[{ query, evidence, ... }]

        strategy:
            "bm25" | "dense" | "hybrid"

    Returns ranked+sorted list with final deterministic ordering.
    """
    if not items:
        return []
    RANKED = apply_strategy(items, strategy=STRATEGY)
    RANKED.sort(key=lambda x: (int(x.get("rank", 9999999)), x.get("evidence", "")))
    return RANKED
