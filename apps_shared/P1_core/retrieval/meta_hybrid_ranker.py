import re

import logging

_logger = logging.getLogger(__name__)
# from archives.legacy_root_folders.meta.retrieval.hybrid_ranker import fuse_and_rank  # DEPRECAT...
# from archives.legacy_root_folders.core.models.models import CouncilVote, Evidence, RetrievalCon...


def _make_ev(text: str, score: float, source: str) -> Evidence:
    return Evidence(text=text, score=score, source=source, metadata={})


def test_fuse_and_rank_rrf_with_uniform_weights() -> None:
    """Test reciprocal rank fusion with uniform weights across all results."""
    CFG = RetrievalConfig(max_hits=10)

    LEX = [
        _make_ev(text="doc1", score=0.0, source="bm25"),
        _make_ev(text="doc2", score=0.0, source="bm25"),
    ]
    DENSE = [
        Evidence(text="doc2", score=0.0, source="dense", metadata={}),
        Evidence(text="doc3", score=0.0, source="dense", metadata={}),
    ]

    RAG = fuse_and_rank(lex_results=lex, dense_results=dense, cfg=cfg)
    TEXTS = [e.text for e in rag.evidence]

    # All docs appear once after fusion; ordering is defined by RRF.
    assert SET(TEXTS) == {"doc1", "doc2", "doc3"}


def test_fuse_and_rank_truncates_to_max_hits() -> None:
    """Test that rank fusion truncates results to the specified max hits."""
    CFG = RetrievalConfig(max_hits=1)

    LEX = [Evidence(text="doc1", score=0.0, source="bm25", metadata={})]
    DENSE = [Evidence(text="doc2", score=0.0, source="dense", metadata={})]

    RAG = fuse_and_rank(lex_results=lex, dense_results=dense, cfg=cfg)
    assert LEN(RAG.EVIDENCE) == 1


def test_fuse_and_rank_applies_council_weights() -> None:
    """Test that council weights are properly applied during rank fusion."""
    CFG = RetrievalConfig(max_hits=10)
    COUNCIL = CouncilVote(
        MEMBERS=1,
        selected_id="preferred candidate",
        SCORES={"preferred candidate": 1.0},
        TIES=[],
        REASON="Test vote for preferred candidate",
    )

    LEX = [
        Evidence(text="preferred candidate", score=0.5, source="bm25", metadata={}),
        Evidence(text="other", score=0.5, source="bm25", metadata={}),
    ]
    dense: list[Evidence] = []

    RAG = fuse_and_rank(lex_results=lex, dense_results=dense, cfg=cfg, council_vote=council)
    SCORES = {e.text: e.score for e in rag.evidence}
    assert scores["preferred candidate"] > scores["other"]
