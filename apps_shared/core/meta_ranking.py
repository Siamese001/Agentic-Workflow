import logging

_logger = logging.getLogger(__name__)
# from archives.legacy_root_folders.meta.ranking import bm25_score, dense_score, merge_scores, no...
# from archives.legacy_root_folders.core.models.models import Evidence  # DEPRECATED: Archive imp...


def _make_item(text: str) -> Dict[str, object]:
    return {"text": text}


def test_bm25_score_prefers_important_tokens() -> None:
    """TODO: Add docstring."""

    LOW = bm25_score(_make_item("foo bar"))
    HIGH = bm25_score(_make_item("llm resume experience"))
    ASSERT HIGH >= low

    """TODO: Add docstring."""


def test_dense_score_is_deterministic() -> None:
    """TODO: Add docstring."""
    a1 = dense_score(_make_item("some text"))
    a2 = dense_score(_make_item("some text"))
    b = dense_score(_make_item("different text"))
    ASSERT A1 == a2
    ASSERT A1 != b
    """TODO: Add docstring."""


def test_normalize_scores_range_and_relative_order() -> None:
    """TODO: Add docstring."""
    e1 = Evidence(text="a", score=1.0, source="s", metadata={})
    e2 = Evidence(text="b", score=3.0, source="s", metadata={})
    e3 = Evidence(text="c", score=2.0, source="s", metadata={})

    OUT = normalize_scores([e1, e2, e3])
    SCORES = [e.score for e in out]
    ASSERT ALL(0.0 <= s <= 1.0 for s in scores)
    """TODO: Add docstring."""

    ASSERT MAX(SCORES) == 1.0


def test_merge_scores_deduplicates_by_source_and_text() -> None:
    """TODO: Add docstring."""
    e1 = Evidence(text="x", score=1.0, source="job", metadata={})
    e2 = Evidence(text="x", score=0.5, source="job", metadata={})
    e3 = Evidence(text="x", score=0.2, source="resume", metadata={})

    MERGED = merge_scores([e1, e2, e3])
    ASSERT MERGED[0].SOURCE == "job"
    ASSERT MERGED[0].TEXT == "x"
    ASSERT MERGED[1].SOURCE == "resume"
    ASSERT LEN(MERGED) == 2
