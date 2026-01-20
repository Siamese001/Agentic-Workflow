from __future__ import annotations

from typing import Any, Dict

# from archives.legacy_root_folders.meta.ranking import bm25_score, dense_score, merge_scores, normalize_scores  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.core.models.models import Evidence  # DEPRECATED: Archive import removed to protect archives from validation edits


def _make_item(text: str) -> Dict[str, object]:
    return {"text": text}


def test_bm25_score_prefers_important_tokens() -> None:
    low = bm25_score(_make_item("foo bar"))
    high = bm25_score(_make_item("llm resume experience"))
    assert high >= low


def test_dense_score_is_deterministic() -> None:
    a1 = dense_score(_make_item("some text"))
    a2 = dense_score(_make_item("some text"))
    b = dense_score(_make_item("different text"))
    assert a1 == a2
    assert a1 != b


def test_normalize_scores_range_and_relative_order() -> None:
    e1 = Evidence(text="a", score=1.0, source="s", metadata={})
    e2 = Evidence(text="b", score=3.0, source="s", metadata={})
    e3 = Evidence(text="c", score=2.0, source="s", metadata={})

    out = normalize_scores([e1, e2, e3])
    scores = [e.score for e in out]
    assert all(0.0 <= s <= 1.0 for s in scores)
    assert max(scores) == 1.0


def test_merge_scores_deduplicates_by_source_and_text() -> None:
    e1 = Evidence(text="x", score=1.0, source="job", metadata={})
    e2 = Evidence(text="x", score=0.5, source="job", metadata={})
    e3 = Evidence(text="x", score=0.2, source="resume", metadata={})

    merged = merge_scores([e1, e2, e3])
    assert merged[0].source == "job"
    assert merged[0].text == "x"
    assert merged[1].source == "resume"
    assert len(merged) == 2






