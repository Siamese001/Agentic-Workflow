"""Novelty judge for ``system_learning.confidence`` (LJH1.2).

Replaces the hardcoded-0.75 stub with a deterministic character n-gram
Jaccard-distance novelty metric. Zero LLM calls — this is structural
novelty, not semantic novelty. For semantic novelty use the canonical
``GeminiJudge`` via ``system_learning.confidence.gemini_judge``.
"""

from __future__ import annotations

from typing import Any

__all__ = ["NovelJudge", "evaluate_novel"]


def _char_ngrams(text: str, n: int = 4) -> set[str]:
    text = text.strip().lower()
    if len(text) < n:
        return {text} if text else set()
    return {text[i : i + n] for i in range(len(text) - n + 1)}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class NovelJudge:
    """Deterministic novelty scorer via 4-gram Jaccard distance.

    ``novelty_score = 1 - jaccard(content_ngrams, reference_ngrams)``.
    When ``reference`` is None the novelty is undefined (``None``) —
    callers MUST supply a reference corpus or accept the Unknown result.
    """

    def __init__(self, threshold: float = 0.5) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"threshold must be in [0,1], got {threshold}")
        self.threshold = threshold

    def evaluate(self, content: str, reference: str | None = None) -> dict[str, Any]:
        if reference is None:
            return {
                "novelty_score": None,
                "is_novel": None,
                "similarity": None,
                "passed": False,
                "reason": "unknown: no reference provided",
            }
        content_grams = _char_ngrams(content)
        ref_grams = _char_ngrams(reference)
        similarity = _jaccard(content_grams, ref_grams)
        novelty = 1.0 - similarity
        return {
            "novelty_score": novelty,
            "is_novel": novelty >= self.threshold,
            "similarity": similarity,
            "passed": novelty >= self.threshold,
            "reason": "scored",
        }

    def score(self, content: str, reference: str | None = None) -> float:
        result = self.evaluate(content, reference)
        score = result["novelty_score"]
        return 0.0 if score is None else float(score)


def evaluate_novel(content: str, reference: str | None = None) -> dict[str, Any]:
    return NovelJudge().evaluate(content, reference)
