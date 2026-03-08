"""
Answer Correctness Metric

Measures answer correctness using token-overlap F1 (heuristic) or an
injected LLM-as-judge callable.  The heuristic is deterministic and
zero-dependency; the judge variant supports production scoring.
"""

from __future__ import annotations

from typing import Any, Callable

from .base import GenerationMetric
from .groundedness import _token_f1, _tokenize


class AnswerCorrectness(GenerationMetric):
    """Measures how correct the generated answer is relative to the expected answer.

    Without a judge: F1 token overlap between prediction and expected answer.
    With a judge callable: calls judge(prediction, ground_truth) -> float in [0, 1].
    """

    def __init__(self, judge: Callable[[str, str], float] | None = None):
        self._judge = judge

    @property
    def name(self) -> str:
        return "answer_correctness"

    def compute(
        self,
        prediction: str,
        ground_truth: str,
        context: Any = None,
    ) -> float:
        """Compute answer correctness score.

        Args:
            prediction: Generated answer string
            ground_truth: Expected (reference) answer string
            context: Unused

        Returns:
            Correctness score in [0, 1]
        """
        if not prediction:
            return 0.0
        if not ground_truth:
            return 0.0

        if self._judge is not None:
            return float(self._judge(prediction, ground_truth))

        pred_tokens = _tokenize(prediction)
        gt_tokens = _tokenize(ground_truth)
        return _token_f1(pred_tokens, gt_tokens)


__all__ = ["AnswerCorrectness"]
