from __future__ import annotations

from meta.retrieval.hybrid_ranker import fuse_and_rank
from core.models.models import CouncilVote, Evidence, RetrievalConfig


def test_fuse_and_rank_rrf_with_uniform_weights() -> None:
    cfg = RetrievalConfig(max_hits=10)

    lex = [
        Evidence(text="doc1", score=0.0, source="bm25", metadata={}),
        Evidence(text="doc2", score=0.0, source="bm25", metadata={}),
    ]
    dense = [
        Evidence(text="doc2", score=0.0, source="dense", metadata={}),
        Evidence(text="doc3", score=0.0, source="dense", metadata={}),
    ]

    rag = fuse_and_rank(lex_results=lex, dense_results=dense, cfg=cfg)
    texts = [e.text for e in rag.evidence]

    # All docs appear once after fusion; ordering is defined by RRF.
    assert set(texts) == {"doc1", "doc2", "doc3"}


def test_fuse_and_rank_truncates_to_max_hits() -> None:
    cfg = RetrievalConfig(max_hits=1)

    lex = [Evidence(text="doc1", score=0.0, source="bm25", metadata={})]
    dense = [Evidence(text="doc2", score=0.0, source="dense", metadata={})]

    rag = fuse_and_rank(lex_results=lex, dense_results=dense, cfg=cfg)
    assert len(rag.evidence) == 1


def test_fuse_and_rank_applies_council_weights() -> None:
    cfg = RetrievalConfig(max_hits=10)
    council = CouncilVote(members=1, selected_id="preferred", scores={}, ties=[], reason=None)

    lex = [
        Evidence(text="preferred candidate", score=0.5, source="bm25", metadata={}),
        Evidence(text="other", score=0.5, source="bm25", metadata={}),
    ]
    dense: list[Evidence] = []

    rag = fuse_and_rank(lex_results=lex, dense_results=dense, cfg=cfg, council_vote=council)
    scores = {e.text: e.score for e in rag.evidence}
    assert scores["preferred candidate"] > scores["other"]







