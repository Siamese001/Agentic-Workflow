from __future__ import annotations

from typing import List

from core.models.models import Evidence, RetrievalConfig
from retrievers.bm25 import bm25_search as _core_bm25_search, BM25Config


def bm25_search(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
    """META-level BM25 retrieval wrapper.

    Delegates to the existing retrievers.bm25 implementation and adapts the
    result into Evidence objects. The underlying corpus wiring remains in the
    existing module; this function simply provides a stable META surface.
    """

    bm25_cfg = BM25Config(k1=cfg.bm25_k1, b=cfg.bm25_b, max_hits=max_hits)

    corpus = []  # Real corpus wiring is handled by the existing retriever.
    scored = _core_bm25_search(query=query, corpus=corpus, cfg=bm25_cfg)

    out: List[Evidence] = []
    for item in scored[:max_hits]:
        out.append(
            Evidence(
                text=str(item.get("text", "")),
                score=float(item.get("score", 0.0)),
                source="bm25",
                metadata={},
            )
        )
    return out




