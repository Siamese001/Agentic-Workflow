"""BM25-based lexical retriever (v10_10 · META layer).

This module wraps the ``rank-bm25`` library behind a simple function
that can be used by the retrieval layer. It is safe to import even if
``rank_bm25`` is not installed: imports are performed lazily and
exposed as explicit errors.

Responsibilities:
    • Provide a BM25Okapi-backed search over an in-memory corpus.
    • Return results as simple dicts suitable for adaptation into
      Evidence objects or other downstream structures.

Non-responsibilities:
    • No knowledge of prompts, agents, or workflow plans.
    • No persistence or indexing beyond the in-memory corpus.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence


class BM25ClientError(RuntimeError):
    """Raised when rank-bm25 cannot be imported or used."""


def _import_bm25():
    """Import BM25Okapi lazily from rank_bm25."""

    try:  # pragma: no cover - import path is environment dependent
        from rank_bm25 import BM25Okapi  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise BM25ClientError("rank-bm25 package not installed") from exc
    return BM25Okapi


@dataclass
class BM25Config:
    """Configuration for BM25 retrieval."""

    k1: float = 1.5
    b: float = 0.75
    max_hits: int = 20


def _tokenize(text: str) -> List[str]:
    """Very simple whitespace tokenizer."""

    return (text or "").lower().split()


def bm25_search(
    query: str,
    corpus: Sequence[Dict[str, Any]],
    *,
    cfg: BM25Config,
) -> List[Dict[str, Any]]:
    """Run BM25 search over an in-memory corpus.

    Parameters
    ----------
    query:
        Query string.
    corpus:
        Sequence of dict items; each must contain a ``text`` field.
    cfg:
        BM25Config with k1 / b / max_hits.

    Returns
    -------
    List[Dict[str, Any]]
        Items annotated with ``score`` and sorted by descending score.
    """

    if not corpus:
        return []

    BM25Okapi = _import_bm25()

    documents = [item.get("text") or "" for item in corpus]
    tokenized_corpus = [_tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus, k1=cfg.k1, b=cfg.b)

    scores = bm25.get_scores(_tokenize(query))

    enriched: List[Dict[str, Any]] = []
    for item, score in zip(corpus, scores):
        new_item = dict(item)
        new_item["score"] = float(score)
        enriched.append(new_item)

    enriched.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return enriched[: cfg.max_hits]
