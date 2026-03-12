"""
Reranker Implementations

Heuristic reranker (zero-dependency, deterministic) and an interface stub
for cross-encoder injection.
"""
from __future__ import annotations
import re
from typing import Callable
from .interfaces import Document, IReranker
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def _query_term_overlap(query: str, content: str) -> float:
    """Count query token overlap with document content (normalized)."""

    def tokenize(text: str) -> set:
        text = text.lower()
        text = re.sub('[^\\w\\s]', ' ', text)
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

    def __init__(self, scorer: Callable[[str, str], float] | None=None, top_k: int=10):
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
        if not candidates:
            return []
        scored = []
        for doc in candidates:
            rerank_score = self._scorer(query, doc.content)
            scored.append(Document(doc_id=doc.doc_id, content=doc.content, score=rerank_score, metadata={**doc.metadata, 'rerank_score': rerank_score}))
        scored.sort(key=lambda d: -d.score)
        return scored[:self.top_k]

class PassthroughReranker(IReranker):
    """No-op reranker that preserves original order, optionally truncating to top_k."""

    def __init__(self, top_k: int=10):
        self.top_k = top_k

    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Return candidates unchanged, truncated to top_k.

        Args:
            query: Unused
            candidates: Documents to pass through

        Returns:
            First top_k candidates in original order
        """
        return candidates[:self.top_k]
__all__ = ['HeuristicReranker', 'PassthroughReranker']
