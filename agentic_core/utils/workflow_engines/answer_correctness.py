"""
Answer Correctness Metric

Measures answer correctness using token-overlap F1 (heuristic) or an
injected LLM-as-judge callable.  The heuristic is deterministic and
zero-dependency; the judge variant supports production scoring.
"""

from __future__ import annotations

from typing import Any, Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from .base import GenerationMetric
from .groundedness import _token_f1, _tokenize

_emit_applies_guardrail("p0", "answer_correctness", "p0_governance")
_emit_reads_policy_state("p0", "answer_correctness", "policy_binding")
_emit_snapshots_state("p0", "answer_correctness", "state_snapshot")
emit_replay_key("p0", "answer_correctness")
emit_determinism_digest("p0", "answer_correctness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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

    def compute(self, prediction: str, ground_truth: str, context: Any = None) -> float:
        """Compute answer correctness score.

        Args:
            prediction: Generated answer string
            ground_truth: Expected (reference) answer string
            context: Unused

        Returns:
            Correctness score in [0, 1]
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AnswerCorrectness.compute")

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
