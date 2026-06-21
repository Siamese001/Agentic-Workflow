"""Reranker adapter for apps_research retrieval pipeline.

Plan §P1.3 — thin adapter with score-based stable ordering + cutoff.
Acceptance requires exactly ``cutoff`` docs returned and monotonic
(non-increasing) score ordering.

Design note
-----------
The ``apps_qna.router.reranker`` module is route-centric (reranks
capability descriptors), not document-centric. A future upgrade may wire
this adapter to the spine ``BgeRerankerAdapter`` for cross-encoder
scoring. For now we trust the search provider's ``score`` field and apply stable
sort-then-cutoff semantics, keeping the interface identical so the
upgrade path is drop-in.
"""

from __future__ import annotations

from apps_research.integrations.search_retrieval import RetrievedDoc


def rerank(
    sub_query: str,  # noqa: ARG001 — reserved for future cross-encoder path
    docs: list[RetrievedDoc],
    cutoff: int = 5,
) -> list[RetrievedDoc]:
    """Return top-``cutoff`` docs sorted by descending ``score``.

    Args:
        sub_query: the sub-query these docs were retrieved for (reserved
            for future cross-encoder rerank; unused today).
        docs: the retrieved-doc list (from :func:`search_retrieval.retrieve`).
        cutoff: maximum docs to return. If ``len(docs) < cutoff``, all
            docs are returned (no padding).

    Returns:
        A new list of at most ``cutoff`` :class:`RetrievedDoc`, sorted
        by ``score`` descending (stable for tied scores).
    """
    if cutoff <= 0:
        return []
    # stable sort preserves insertion order for ties — important for
    # diff-stability in snapshot tests (plan §P2.1 acceptance).
    ordered = sorted(docs, key=lambda d: d.score, reverse=True)
    return ordered[:cutoff]
