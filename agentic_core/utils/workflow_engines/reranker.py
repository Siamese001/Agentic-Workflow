"""
Reranker Implementations

Heuristic reranker (zero-dependency, deterministic) and an interface stub
for cross-encoder injection.
"""

from __future__ import annotations

import re
from typing import Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from .interfaces import Document, IReranker

_emit_applies_guardrail("p0", "reranker", "p0_governance")
_emit_reads_policy_state("p0", "reranker", "policy_binding")
_emit_snapshots_state("p0", "reranker", "state_snapshot")
emit_replay_key("p0", "reranker")
emit_determinism_digest("p0", "reranker")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _query_term_overlap(query: str, content: str) -> float:
    """Count query token overlap with document content (normalized)."""

    def tokenize(text: str) -> set:
        text = text.lower()
        text = re.sub("[^\\w\\s]", " ", text)
        return set(text.split())

    query_tokens = tokenize(query)
    content_tokens = tokenize(content)
    if not query_tokens:
        return 0.0
    overlap = query_tokens & content_tokens
    return len(overlap) / len(query_tokens)


class HeuristicReranker(IReranker):
    """Deterministic reranker using query-term coverage as the rerank signal.

    Production use: inject a cross-encoder via the ``scorer`` callable.
    """

    def __init__(self, scorer: Callable[[str, str], float] | None = None, top_k: int = 10):
        self._scorer = scorer or _query_term_overlap
        self.top_k = top_k

    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Rerank candidates by scorer(query, content).

        Args:
            query: Original search query
            candidates: Documents to rerank

        Returns:
            Top-k documents sorted by descending rerank score
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HeuristicReranker.rerank")

        if not candidates:
            return []
        scored = []
        for doc in candidates:
            rerank_score = self._scorer(query, doc.content)
            scored.append(
                Document(
                    doc_id=doc.doc_id,
                    content=doc.content,
                    score=rerank_score,
                    metadata={**doc.metadata, "rerank_score": rerank_score},
                )
            )
        scored.sort(key=lambda d: -d.score)
        return scored[: self.top_k]


class PassthroughReranker(IReranker):
    """No-op reranker that preserves original order, optionally truncating to top_k."""

    def __init__(self, top_k: int = 10):
        self.top_k = top_k

    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Return candidates unchanged, truncated to top_k.

        Args:
            query: Unused
            candidates: Documents to pass through

        Returns:
            First top_k candidates in original order
        """
        return candidates[: self.top_k]


__all__ = ["HeuristicReranker", "PassthroughReranker"]
