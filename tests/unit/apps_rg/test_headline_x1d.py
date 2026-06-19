from __future__ import annotations

from apps_rg.runtime.judges.headline_x1d import HEADLINE_RUBRIC


def test_headline_rubric_includes_adversarial_review_lens() -> None:
    rubric = HEADLINE_RUBRIC.lower()
    assert "head of talent acquisition" in rubric
    assert "ai-authenticity" in rubric
    assert "buzzword soup" in rubric
    assert "adversarial review lens" in rubric
