"""
Groundedness Metric

Measures whether the generated answer is supported by retrieved context.
Uses token-overlap heuristic (F1 over unigrams) as a deterministic
zero-dependency approximation.  An LLM-judge variant is available via
the optional judge callable injected at construction time.
"""

from __future__ import annotations

import re
from typing import Callable

from .base import GenerationMetric
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    text = text.lower()
    text = re.sub("[^\\w\\s]", " ", text)
    return [t for t in text.split() if t]


def _token_f1(prediction_tokens: list[str], context_tokens: list[str]) -> float:
    """Compute F1 between two token lists."""
    if not prediction_tokens or not context_tokens:
        return 0.0
    pred_set = set(prediction_tokens)
    ctx_set = set(context_tokens)
    common = pred_set & ctx_set
    if not common:
        return 0.0
    precision = len(common) / len(pred_set)
    recall = len(common) / len(ctx_set)
    if precision + recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


class Groundedness(GenerationMetric):
    """Measures whether the answer is supported by the retrieved context.

    Without a judge: uses token-overlap F1 between answer and concatenated context.
    With a judge callable: calls judge(answer, context_str) -> float in [0, 1].
    """

    def __init__(self, judge: Callable[[str, str], float] | None = None):
        self._judge = judge

    @property
    def name(self) -> str:
        return "groundedness"

    def compute(self, prediction: str, ground_truth: str, context: str | list[str] | None = None) -> float:
        """Compute groundedness score.

        Args:
            prediction: Generated answer string
            ground_truth: Expected answer (unused in heuristic mode; used by judge)
            context: Retrieved context documents (str or list of str)

        Returns:
            Groundedness score in [0, 1]
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "Groundedness.compute")

        if not prediction:
            return 0.0
        if context is None:
            context_str = ground_truth if ground_truth else ""
        elif isinstance(context, list):
            context_str = " ".join(context)
        else:
            context_str = context
        if not context_str:
            return 0.0
        if self._judge is not None:
            return float(self._judge(prediction, context_str))
        pred_tokens = _tokenize(prediction)
        ctx_tokens = _tokenize(context_str)
        return _token_f1(pred_tokens, ctx_tokens)


__all__ = ["Groundedness", "_tokenize", "_token_f1"]
