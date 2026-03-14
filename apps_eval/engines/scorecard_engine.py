"""
Scorecard Engine — apps_eval.

Computes weighted scorecard from suite results.
Maps suite pass_rates to scorecard dimensions.
Produces a ranked, weighted overall score.

Deterministic: all scoring logic is arithmetic — no model calls.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from apps_eval.types.eval_types import ScorecardRow, SuiteResult

_log = logging.getLogger(__name__)

_SUITE_TO_DIMENSION: dict[str, str] = {
    "routing_enforcement": "governance",
    "determinism_contracts": "determinism",
    "orchestration_hop": "correctness",
    "output_contracts": "correctness",
    "exec_brief_generation": "output_richness",
    "ml_metrics_validation": "ml_metric_correctness",
}


@dataclass
class ScorecardResult:
    """Output of scorecard computation."""

    rows: list[ScorecardRow] = field(default_factory=list)
    overall_score: float = 0.0
    total_weight: float = 0.0


class ScorecardEngine:
    """Compute weighted evaluation scorecard from suite results.

    Each suite result maps to one or more scorecard dimensions.
    Dimensions have weights — the overall score is a weighted mean.
    """

    AGENT_ID = "EVAL_SCORECARD"

    def __init__(self, dimension_configs: list | None = None) -> None:
        self._dimensions = dimension_configs or []

    def compute(self, suite_results: list[SuiteResult]) -> ScorecardResult:
        """Compute scorecard from suite results.

        Args:
            suite_results: List of completed SuiteResult objects.

        Returns:
            ScorecardResult with rows and overall weighted score.
        """
        suite_scores: dict[str, float] = {sr.suite_id: sr.pass_rate for sr in suite_results}

        dim_scores: dict[str, list[float]] = {}
        for suite_id, score in suite_scores.items():
            dim = _SUITE_TO_DIMENSION.get(suite_id, "correctness")
            dim_scores.setdefault(dim, []).append(score)

        dim_means: dict[str, float] = {dim: sum(scores) / len(scores) for dim, scores in dim_scores.items()}

        rows: list[ScorecardRow] = []
        total_weight = 0.0
        weighted_sum = 0.0

        dim_weight_map: dict[str, float] = {}
        if self._dimensions:
            for d in self._dimensions:
                dim_weight_map[d.dimension_id] = d.weight
        else:
            default_dims = {
                "correctness": 3.0,
                "determinism": 3.0,
                "governance": 2.5,
                "latency": 1.5,
                "output_richness": 1.0,
                "ml_metric_correctness": 2.0,
            }
            dim_weight_map = default_dims

        for dim_id, weight in dim_weight_map.items():
            score = dim_means.get(dim_id, 0.0)
            weighted = score * weight
            weighted_sum += weighted
            total_weight += weight

            if score >= 0.80:
                verdict = "PASS"
            elif score >= 0.70:
                verdict = "WARN"
            else:
                verdict = "FAIL"

            rows.append(
                ScorecardRow(
                    dimension_id=dim_id,
                    display_name=dim_id.replace("_", " ").title(),
                    score=round(score, 4),
                    weight=weight,
                    weighted_score=round(weighted, 4),
                    verdict=verdict,
                )
            )

        overall = weighted_sum / total_weight if total_weight > 0 else 0.0
        rows_sorted = sorted(rows, key=lambda r: -r.weight)

        _log.info("[ScorecardEngine] overall_score=%.3f dimensions=%d", overall, len(rows))
        return ScorecardResult(
            rows=rows_sorted,
            overall_score=round(overall, 4),
            total_weight=total_weight,
        )
