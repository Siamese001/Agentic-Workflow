# from archives.legacy_root_folders.meta.retrieval.hybrid_ranker import fuse_and_rank  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.core.models.models import CouncilVote, Evidence, RetrievalConfig  # DEPRECATED: Archive import removed to protect archives from validation edits


def _make_ev(text: str, score: float, source: str) -> Evidence:
    return Evidence(text=text, score=score, source=source, metadata={})


def test_fuse_and_rank_rrf_with_uniform_weights() -> None:
    """Test reciprocal rank fusion with uniform weights across all results."""
    cfg = RetrievalConfig(max_hits=10)

    lex = [
        _make_ev(text="doc1", score=0.0, source="bm25"),
        _make_ev(text="doc2", score=0.0, source="bm25"),
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
    """Test that rank fusion truncates results to the specified max hits."""
    cfg = RetrievalConfig(max_hits=1)

    lex = [Evidence(text="doc1", score=0.0, source="bm25", metadata={})]
    dense = [Evidence(text="doc2", score=0.0, source="dense", metadata={})]

    rag = fuse_and_rank(lex_results=lex, dense_results=dense, cfg=cfg)
    assert len(rag.evidence) == 1


def test_fuse_and_rank_applies_council_weights() -> None:
    """Test that council weights are properly applied during rank fusion."""
    cfg = RetrievalConfig(max_hits=10)
    council = CouncilVote(
        members=1,
        selected_id="preferred candidate",
        scores={"preferred candidate": 1.0},
        ties=[],
        reason="Test vote for preferred candidate",
    )

    lex = [
        Evidence(text="preferred candidate", score=0.5, source="bm25", metadata={}),
        Evidence(text="other", score=0.5, source="bm25", metadata={}),
    ]
    dense: list[Evidence] = []

    rag = fuse_and_rank(lex_results=lex, dense_results=dense, cfg=cfg, council_vote=council)
    scores = {e.text: e.score for e in rag.evidence}
    assert scores["preferred candidate"] > scores["other"]
