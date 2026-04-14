"""L6 Golden Evaluation Metrics Emitter.

Emits golden dataset evaluation metrics to L6 observability layer.
Wires golden eval results into telemetry streams for monitoring and alerting.
"""

from __future__ import annotations

import logging
from typing import Any

from .golden_evaluator import GoldenEvalResult

try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        _emit_captures_evaluation_metric,
        _emit_emits_metric_event,
        _emit_records_telemetry_event,
    )
except ModuleNotFoundError:

    def _emit_captures_evaluation_metric(*args: Any, **kwargs: Any) -> None:
        return None

    def _emit_emits_metric_event(*args: Any, **kwargs: Any) -> None:
        return None

    def _emit_records_telemetry_event(*args: Any, **kwargs: Any) -> None:
        return None


Logger = logging.getLogger(__name__)


class GoldenL6Emitter:
    """Emits golden evaluation metrics to L6 observability.

    Design:
    - Non-blocking emission (fire-and-forget)
    - Structured telemetry for dashboard aggregation
    - Metric event emission for alerting
    """

    def __init__(self) -> None:
        """Initialize L6 emitter."""
        self._emit_count = 0

    def emit_golden_eval_result(self, result: GoldenEvalResult) -> None:
        """Emit a single golden evaluation result to L6.

        Args:
            result: Golden evaluation result to emit
        """
        # Primary metric: match score (encoded in metric name)
        _emit_captures_evaluation_metric(
            "golden_eval",
            result.dataset_name,
            f"match_score_{result.case_id}_{int(result.match_score * 100)}",
        )

        # Telemetry event for monitoring
        _emit_records_telemetry_event(
            "golden_eval",
            result.dataset_name,
            {
                "case_id": result.case_id,
                "query": result.query,
                "passed": result.passed,
                "match_score": result.match_score,
                "eval_duration_ms": result.eval_duration_ms,
            },
        )

        # Metric event for dashboard/alerting
        _emit_emits_metric_event(
            "golden_eval",
            result.dataset_name,
            {
                "metric_name": f"golden_match_{result.dataset_name}",
                "value": result.match_score,
                "case_id": result.case_id,
                "passed": result.passed,
            },
        )

        self._emit_count += 3
        Logger.debug(
            "Emitted golden eval metrics for %s: score=%.2f",
            result.case_id,
            result.match_score,
        )

    def emit_batch_results(self, results: list[GoldenEvalResult]) -> dict[str, Any]:
        """Emit a batch of golden evaluation results.

        Args:
            results: List of golden evaluation results

        Returns:
            Summary of emitted metrics
        """
        if not results:
            return {"emitted": 0, "datasets": []}

        dataset_names = set()
        pass_count = 0

        for result in results:
            self.emit_golden_eval_result(result)
            dataset_names.add(result.dataset_name)
            if result.passed:
                pass_count += 1

        # Emit aggregate metric
        if results:
            avg_score = sum(r.match_score for r in results) / len(results)
            avg_score_pct = int(avg_score * 100)
            _emit_captures_evaluation_metric(
                "golden_eval",
                "aggregate",
                f"avg_match_score_{avg_score_pct}",
            )

        summary = {
            "emitted": len(results),
            "datasets": list(dataset_names),
            "passed": pass_count,
            "failed": len(results) - pass_count,
            "avg_match_score": avg_score if results else 0.0,
        }

        Logger.info(
            "Emitted batch of %d golden eval metrics (avg_score=%.2f)",
            len(results),
            summary["avg_match_score"],
        )

        return summary

    def get_emit_stats(self) -> dict[str, Any]:
        """Get emission statistics."""
        return {
            "total_emits": self._emit_count,
        }


# Module-level singleton
_l6_emitter: GoldenL6Emitter | None = None


def get_l6_emitter() -> GoldenL6Emitter:
    """Get or create singleton L6 emitter."""
    global _l6_emitter
    if _l6_emitter is None:
        _l6_emitter = GoldenL6Emitter()
    return _l6_emitter


def emit_golden_result(result: GoldenEvalResult) -> None:
    """Convenience function to emit a single golden result."""
    get_l6_emitter().emit_golden_eval_result(result)


def emit_golden_batch(results: list[GoldenEvalResult]) -> dict[str, Any]:
    """Convenience function to emit a batch of golden results."""
    return get_l6_emitter().emit_batch_results(results)
