"""Golden Dataset Integration for Eval Spine - Shadow Mode.

Wires GoldenDatasetEvaluator into Eval Spine for continuous golden dataset
validation without blocking L2 routing. Runs in shadow mode only.
"""

from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from agentic_core.evaluation.golden.golden_evaluator import (
    GoldenDatasetEvaluator,
    GoldenEvalResult,
    get_evaluator,
)
from agentic_core.runtime.engine.eval_spine import EvalSpine

Logger = logging.getLogger(__name__)


class GoldenEvalIntegration:
    """Integration between Eval Spine and Golden Dataset Evaluator.

    Design principles:
    - Shadow mode only (never blocks primary evaluation flow)
    - Non-blocking execution (background thread pool)
    - Immutable golden datasets (read-only)
    - L2 routing unaffected (observability-only)
    """

    def __init__(
        self,
        eval_spine: EvalSpine,
        evaluator: GoldenDatasetEvaluator | None = None,
        max_workers: int = 2,
    ):
        """Initialize integration.

        Args:
            eval_spine: The EvalSpine instance to integrate with
            evaluator: Optional evaluator instance (default: singleton)
            max_workers: Thread pool size for background evaluation
        """
        self.eval_spine = eval_spine
        self.evaluator = evaluator or get_evaluator()
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="golden_eval_")
        self._pending: list[Future] = []

    def evaluate_query_async(
        self,
        query: str,
        actual_output: str,
        actual_actions: list[dict] | None = None,
    ) -> Future[list[GoldenEvalResult]]:
        """Submit golden dataset evaluation asynchronously.

        Args:
            query: The input query/mission
            actual_output: The actual output produced
            actual_actions: Optional actions taken

        Returns:
            Future with evaluation results (non-blocking)
        """
        future = self._executor.submit(
            self._evaluate_query,
            query,
            actual_output,
            actual_actions,
        )
        self._pending.append(future)
        return future

    def _evaluate_query(
        self,
        query: str,
        actual_output: str,
        actual_actions: list[dict] | None,
    ) -> list[GoldenEvalResult]:
        """Synchronous evaluation (runs in thread pool)."""
        try:
            return self.evaluator.evaluate_against_test_cases(
                query=query,
                actual_output=actual_output,
                actual_actions=actual_actions,
            )
        except Exception:
            Logger.exception("Golden dataset evaluation failed for query: %s", query)
            return []

    def evaluate_retrieval_async(
        self,
        query: str,
        retrieved_doc_ids: list[str],
        generated_answer: str,
    ) -> Future[list[GoldenEvalResult]]:
        """Submit retrieval evaluation asynchronously.

        Args:
            query: The search query
            retrieved_doc_ids: List of document IDs retrieved
            generated_answer: The answer generated

        Returns:
            Future with evaluation results (non-blocking)
        """
        future = self._executor.submit(
            self._evaluate_retrieval,
            query,
            retrieved_doc_ids,
            generated_answer,
        )
        self._pending.append(future)
        return future

    def _evaluate_retrieval(
        self,
        query: str,
        retrieved_doc_ids: list[str],
        generated_answer: str,
    ) -> list[GoldenEvalResult]:
        """Synchronous retrieval evaluation (runs in thread pool)."""
        try:
            return self.evaluator.evaluate_retrieval_ground_truth(
                query=query,
                retrieved_doc_ids=retrieved_doc_ids,
                generated_answer=generated_answer,
            )
        except Exception:
            Logger.exception("Golden retrieval evaluation failed for query: %s", query)
            return []

    def emit_golden_metrics(self, results: list[GoldenEvalResult]) -> None:
        """Emit golden evaluation metrics to Eval Spine.

        Args:
            results: Golden evaluation results to record
        """
        for result in results:
            # Record match score as metric
            self.eval_spine._record(
                name=f"golden_match_{result.dataset_name}",
                value=result.match_score,
                metadata={
                    "case_id": result.case_id,
                    "dataset": result.dataset_name,
                    "query": result.query,
                    "passed": result.passed,
                    "missing_spans": result.missing_spans,
                },
            )

            # Emit drift alert if match score is low
            if result.match_score < 0.5:
                self.eval_spine.emit_drift_alert(
                    metric_name=f"golden_match_{result.dataset_name}",
                    current_value=result.match_score,
                    baseline_value=1.0,  # Expected perfect match
                    threshold=0.5,
                )

    def process_pending(self, timeout: float = 0.0) -> list[GoldenEvalResult]:
        """Process pending evaluations and emit metrics.

        Args:
            timeout: Seconds to wait for pending futures (0 = non-blocking)

        Returns:
            All results from completed evaluations
        """
        completed = []
        still_pending = []

        for future in self._pending:
            if future.done():
                try:
                    results = future.result(timeout=0)
                    self.emit_golden_metrics(results)
                    completed.extend(results)
                except Exception:
                    Logger.exception("Failed to process golden evaluation result")
            elif timeout > 0:
                try:
                    results = future.result(timeout=timeout)
                    self.emit_golden_metrics(results)
                    completed.extend(results)
                except Exception:
                    Logger.exception("Failed to process golden evaluation result")
                    still_pending.append(future)
            else:
                still_pending.append(future)

        self._pending = still_pending
        return completed

    def get_summary(self) -> dict[str, Any]:
        """Get summary of golden evaluation status."""
        return {
            "pending_evaluations": len(self._pending),
            "datasets_available": self.evaluator.list_available_datasets(),
            "eval_spine_metrics": len(self.eval_spine.report.metrics),
        }

    def shutdown(self) -> None:
        """Shutdown thread pool and process remaining evaluations."""
        self.process_pending(timeout=5.0)
        self._executor.shutdown(wait=False)


def attach_golden_eval(eval_spine: EvalSpine) -> GoldenEvalIntegration:
    """Attach golden dataset evaluation to an EvalSpine instance.

    Args:
        eval_spine: The EvalSpine to attach to

    Returns:
        GoldenEvalIntegration instance
    """
    integration = GoldenEvalIntegration(eval_spine)
    Logger.info(f"Golden eval attached to EvalSpine [{eval_spine.report.agent_id}]")
    return integration
