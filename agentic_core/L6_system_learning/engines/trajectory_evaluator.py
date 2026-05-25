"""V7 6B.S2B Trajectory Evaluator.

Grades the *path* (route, tool order, model lane, retry behavior, fallback
depth) of a completed run. Distinct from outcome evaluation which grades
*answer* quality.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6B S2B "TRAJECTORY EVALS".

KPI surface
-----------
Publishes ``TRAJECTORY_EVAL_COVERAGE`` (ratio of non-RET runs that received a
trajectory grade).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Mapping

logger = logging.getLogger(__name__)


# Path defects v7 S2B requires the evaluator to detect.
_DETECTABLE_DEFECTS: frozenset[str] = frozenset({
    "route_thrash",
    "silent_fallback",
    "tool_misuse",
    "tool_overreach",
    "hidden_scope_growth",
    "unbounded_loop",
    "skipped_c0_grounding",
    "skipped_prompt_validation",
    "premature_answer",
    "stale_cache_reuse",
    "excessive_model_escalation",
    "non_replayable_behavior",
    "unnecessary_hitl",
    "missing_hitl",
})


@dataclass(frozen=True)
class TrajectoryEvalRecord:
    """Per-run trajectory evaluation per v7 S2B "OUTPUT"."""

    trace_id: str
    run_id: str
    path_score: float
    span_fault_candidates: tuple[str, ...]
    route_quality: float
    tool_quality: float
    retry_quality: float
    cost_quality: float
    budget_quality: float
    evidence_path_integrity: float
    detected_defects: tuple[str, ...]


@dataclass
class _Counters:
    total_non_ret: int = 0
    graded: int = 0


class TrajectoryEvaluator:
    """Score the trajectory of a completed run."""

    def __init__(self) -> None:
        self._counters = _Counters()

    def evaluate(
        self,
        *,
        trace_id: str,
        run_id: str,
        path_features: Mapping[str, Any],
        is_retrieval_only: bool = False,
    ) -> TrajectoryEvalRecord:
        """Score the path. ``path_features`` is a free-shape mapping holding
        whatever the trace extractor produces.

        Sub-scores default to 1.0 when the feature is absent (assume good
        unless evidence says otherwise) — this is the v7 "no fabricated
        certainty" discipline applied conservatively to grading.

        Detected defects are taken from the ``defects`` key (set or
        sequence). Unknown defect names are ignored to avoid invented data.
        """
        if not is_retrieval_only:
            self._counters.total_non_ret += 1
            self._counters.graded += 1

        defects_in = path_features.get("defects", ()) or ()
        defects = tuple(d for d in defects_in if d in _DETECTABLE_DEFECTS)

        def _score(key: str, default: float = 1.0) -> float:
            value = path_features.get(key, default)
            try:
                return max(0.0, min(1.0, float(value)))
            except (TypeError, ValueError):
                return default

        route_q = _score("route_quality")
        tool_q = _score("tool_quality")
        retry_q = _score("retry_quality")
        cost_q = _score("cost_quality")
        budget_q = _score("budget_quality")
        ev_path_q = _score("evidence_path_integrity")

        # Path score is the geometric mean of sub-scores; defects discount.
        sub = [route_q, tool_q, retry_q, cost_q, budget_q, ev_path_q]
        prod = 1.0
        for s in sub:
            prod *= s
        geo = prod ** (1.0 / len(sub))
        # Each detected defect costs 5% of the path score, capped at 50%.
        defect_discount = min(0.5, 0.05 * len(defects))
        path_score = max(0.0, geo * (1.0 - defect_discount))

        return TrajectoryEvalRecord(
            trace_id=trace_id,
            run_id=run_id,
            path_score=path_score,
            span_fault_candidates=tuple(path_features.get("span_fault_candidates", ()) or ()),
            route_quality=route_q,
            tool_quality=tool_q,
            retry_quality=retry_q,
            cost_quality=cost_q,
            budget_quality=budget_q,
            evidence_path_integrity=ev_path_q,
            detected_defects=defects,
        )

    @property
    def counters(self) -> tuple[int, int]:
        """Return ``(graded, total_non_ret)``."""
        return (self._counters.graded, self._counters.total_non_ret)

    def reset(self) -> None:
        self._counters = _Counters()

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from .v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._counters.graded / self._counters.total_non_ret
                if self._counters.total_non_ret > 0
                else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.TRAJECTORY_EVAL_COVERAGE,
                value=ratio,
                timestamp=time.time(),
                source="trajectory_evaluator",
                metadata={"graded": self._counters.graded,
                          "total_non_ret": self._counters.total_non_ret},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break eval
            logger.warning("v7_kpi_trajectory_eval_coverage_failed: %s", exc)


__all__ = [
    "TrajectoryEvalRecord",
    "TrajectoryEvaluator",
]
