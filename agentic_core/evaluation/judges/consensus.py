"""ConsensusJudge — multi-judge ensembling for LLM-as-Judge.

Wraps N ``LLMJudge`` backends and aggregates their per-dimension scores
with a trimmed-mean (drop min + max when N >= 3) plus a disagreement
flag when the range across judges for a dimension exceeds
``disagreement_threshold``.

Design choices (from W3 Author-Gate):
- Aggregation: trimmed-mean (drop highest and lowest when N >= 3);
  simple mean when N == 2; passthrough when N == 1.
- Unknown handling: Unknowns are EXCLUDED from the aggregate; if every
  judge abstained on a dimension, the consensus also returns Unknown.
- Disagreement: range (max - min) across numeric scores on a dimension.
  Emitted per-dimension in ``consensus_metadata.disagreements``. The
  caller (e.g. HITL escalation gate) decides what to do with it.
- Determinism: uses ``JudgeScore.create`` so the aggregate has a stable
  ``deterministic_digest`` derived from its final numeric scores.

This module intentionally does NOT run judges in parallel — each judge
is synchronous and may be called from different threads by the caller
if concurrency is required. Running sequentially keeps MCP serialization
discipline and makes budget accounting predictable.
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from typing import Any

from agentic_core.evaluation.judges.llm_judge import (
    DIMENSIONS,
    UNKNOWN,
    JudgeScore,
    LLMJudge,
    _is_nan,
)

_log = logging.getLogger(__name__)

DEFAULT_DISAGREEMENT_THRESHOLD = 1.5  # score range, on a 1-5 scale


@dataclass(frozen=True)
class ConsensusResult:
    """Consensus output plus per-dimension diagnostics.

    ``score`` is the aggregated :class:`JudgeScore` intended for downstream
    consumption. ``per_judge`` preserves every individual judge's score
    for audit / calibration. ``disagreements`` reports the range across
    judges per dimension; dimensions with range above
    ``disagreement_threshold`` are listed in ``flagged_dimensions`` for
    HITL escalation.
    """

    score: JudgeScore
    per_judge: tuple[JudgeScore, ...]
    disagreements: tuple[tuple[str, float], ...]
    flagged_dimensions: tuple[str, ...]
    aggregation: str = "trimmed_mean"
    metadata: dict[str, Any] = field(default_factory=dict)


class ConsensusJudge:
    """Ensemble judge that wraps N backends and returns a consensus score."""

    def __init__(
        self,
        judges: list[LLMJudge],
        disagreement_threshold: float = DEFAULT_DISAGREEMENT_THRESHOLD,
        label: str = "consensus",
    ) -> None:
        if not judges:
            raise ValueError("ConsensusJudge requires at least one judge")
        self._judges = list(judges)
        self._threshold = disagreement_threshold
        self._label = label

    @property
    def judge_count(self) -> int:
        return len(self._judges)

    @property
    def label(self) -> str:
        return self._label

    def _aggregate_dim(self, values: list[float]) -> float:
        """Aggregate a list of numeric scores, trimmed-mean when N >= 3."""
        clean = [v for v in values if not _is_nan(v)]
        if not clean:
            return UNKNOWN
        if len(clean) == 1:
            return clean[0]
        if len(clean) == 2:
            return statistics.mean(clean)
        trimmed = sorted(clean)[1:-1]
        return statistics.mean(trimmed) if trimmed else statistics.mean(clean)

    def _dim_range(self, values: list[float]) -> float:
        clean = [v for v in values if not _is_nan(v)]
        if len(clean) < 2:
            return 0.0
        return max(clean) - min(clean)

    def grade(self, query: str, context: str, answer: str) -> ConsensusResult:
        """Grade ``(query, context, answer)`` with every judge, aggregate."""
        per_judge = tuple(judge.score(query, context, answer) for judge in self._judges)

        aggregated: dict[str, float] = {}
        disagreements: list[tuple[str, float]] = []
        flagged: list[str] = []
        unknown_reasons: dict[str, str] = {}

        for dim in DIMENSIONS:
            values = [
                getattr(js, dim) for js in per_judge
            ]  # guardian: allow-hallucinated-tool-name -- getattr is Python stdlib; reads JudgeScore dataclass attr by name
            aggregated[dim] = self._aggregate_dim(values)
            rng = self._dim_range(values)
            disagreements.append((dim, round(rng, 4)))
            if rng > self._threshold:
                flagged.append(dim)
            if _is_nan(aggregated[dim]):
                # Collect merged Unknown reasons across judges.
                reasons = [reason for js in per_judge for key, reason in js.unknown_reasons if key == dim]
                unknown_reasons[dim] = "; ".join(reasons) if reasons else "all judges abstained"

        # Consensus reasoning = concatenation of each judge's free text,
        # labelled by model id.
        aggregate_reasoning = " || ".join(f"[{js.judge_model}] {js.reasoning[:200]}" for js in per_judge)
        judge_model_label = f"consensus({','.join(sorted({js.judge_model for js in per_judge}))})"

        consensus_score = JudgeScore.create(
            faithfulness=aggregated["faithfulness"],
            answer_relevancy=aggregated["answer_relevancy"],
            context_precision=aggregated["context_precision"],
            groundedness=aggregated["groundedness"],
            reasoning=aggregate_reasoning,
            judge_model=judge_model_label,
            unknown_reasons=unknown_reasons,
        )

        return ConsensusResult(
            score=consensus_score,
            per_judge=per_judge,
            disagreements=tuple(disagreements),
            flagged_dimensions=tuple(flagged),
            aggregation="trimmed_mean",
            metadata={
                "judge_count": len(self._judges),
                "judge_models": sorted({js.judge_model for js in per_judge}),
                "disagreement_threshold": self._threshold,
            },
        )

    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        """LLMJudge-protocol compatible; discards the :class:`ConsensusResult`.

        Call :meth:`grade` instead when disagreement flags / per-judge
        audit trail are needed (e.g. for HITL escalation).
        """
        return self.grade(query, context, answer).score


__all__ = [
    "ConsensusJudge",
    "ConsensusResult",
    "DEFAULT_DISAGREEMENT_THRESHOLD",
]
