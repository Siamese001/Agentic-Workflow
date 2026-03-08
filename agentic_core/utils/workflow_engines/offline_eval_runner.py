"""
Offline Evaluation Runner

Pipeline: dataset → retrieval → reranking → LLM answer generation →
          metric computation → evaluation report → L4 persistence
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable

from ..metrics.answer_correctness import AnswerCorrectness
from ..metrics.base import EvaluationMetric
from ..metrics.groundedness import Groundedness
from ..metrics.mrr import MeanReciprocalRank
from ..metrics.ndcg import NDCG
from ..metrics.precision_at_k import PrecisionAtK
from ..metrics.recall_at_k import RecallAtK
from ..schemas.evaluation_dataset_schema import EvaluationDataset, EvaluationExample
from ..schemas.evaluation_result_schema import (
    EvaluationReport,
    EvaluationResult,
    EvaluationSnapshot,
)

RetrievalFn = Callable[[str], list[str]]
GenerationFn = Callable[[str, list[str]], str]


def _default_retrieval(query: str) -> list[str]:
    """Stub retrieval — returns empty list.  Replace with real retriever."""
    return []


def _default_generation(query: str, context_docs: list[str]) -> str:
    """Stub generation — returns empty string.  Replace with real LLM."""
    return ""


class OfflineEvaluationRunner:
    """Runs deterministic offline evaluation against a fixed dataset.

    Supports pluggable retrieval, generation, and metric functions.
    Writes an EvaluationSnapshot to the L4 store when a store is provided.
    """

    def __init__(
        self,
        metrics: list[EvaluationMetric] | None = None,
        retrieval_fn: RetrievalFn | None = None,
        generation_fn: GenerationFn | None = None,
        system_version: str = "unknown",
        l4_store: Any | None = None,
    ):
        self.metrics: list[EvaluationMetric] = metrics or _default_metrics()
        self.retrieval_fn: RetrievalFn = retrieval_fn or _default_retrieval
        self.generation_fn: GenerationFn = generation_fn or _default_generation
        self.system_version = system_version
        self.l4_store = l4_store

    def run(self, dataset: EvaluationDataset) -> EvaluationReport:
        """Execute evaluation over all examples in dataset.

        Args:
            dataset: EvaluationDataset with examples to evaluate

        Returns:
            EvaluationReport with per-example results and aggregate scores
        """
        run_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        per_example_results: list[EvaluationResult] = []

        for idx, example in enumerate(dataset.examples):
            result = self._evaluate_example(
                example_id=f"{dataset.name}_{idx}",
                example=example,
            )
            per_example_results.append(result)

        aggregate_scores = self._aggregate(per_example_results)

        report = EvaluationReport(
            run_id=run_id,
            dataset_name=dataset.name,
            dataset_version=dataset.version,
            system_version=self.system_version,
            timestamp=timestamp,
            aggregate_scores=aggregate_scores,
            per_example_results=per_example_results,
        )

        if self.l4_store is not None:
            self._persist_snapshot(report)

        return report

    def _evaluate_example(
        self, example_id: str, example: EvaluationExample
    ) -> EvaluationResult:
        """Run retrieval + generation + metric scoring for one example."""
        retrieved_docs = self.retrieval_fn(example.query)
        generated_answer = self.generation_fn(example.query, retrieved_docs)

        metric_scores: dict[str, float] = {}
        for metric in self.metrics:
            if hasattr(metric, "compute"):
                # Retrieval metrics receive (retrieved_docs, ground_truth_docs)
                # Generation metrics receive (generated_answer, expected_answer, context)
                from ..metrics.base import GenerationMetric, RetrievalMetric
                if isinstance(metric, GenerationMetric):
                    score = metric.compute(
                        prediction=generated_answer,
                        ground_truth=example.expected_answer,
                        context=retrieved_docs,
                    )
                elif isinstance(metric, RetrievalMetric):
                    score = metric.compute(
                        prediction=retrieved_docs,
                        ground_truth=example.ground_truth_documents,
                    )
                else:
                    score = metric.compute(
                        prediction=retrieved_docs,
                        ground_truth=example.ground_truth_documents,
                    )
                metric_scores[metric.name] = score

        return EvaluationResult(
            example_id=example_id,
            query=example.query,
            retrieved_doc_ids=retrieved_docs,
            generated_answer=generated_answer,
            metric_scores=metric_scores,
        )

    def _aggregate(self, results: list[EvaluationResult]) -> dict[str, float]:
        """Average per-example metric scores across all examples."""
        if not results:
            return {}

        metric_names = list(results[0].metric_scores.keys())
        aggregated: dict[str, float] = {}
        for metric_name in metric_names:
            scores = [
                r.metric_scores[metric_name]
                for r in results
                if metric_name in r.metric_scores
            ]
            aggregated[metric_name] = sum(scores) / len(scores) if scores else 0.0
        return aggregated

    def _persist_snapshot(self, report: EvaluationReport) -> None:
        """Persist EvaluationSnapshot to L4 state registry."""
        try:
            from agentic_core.L4_state.storage.persistent_store import create_artifact

            snapshot = EvaluationSnapshot(
                timestamp=report.timestamp,
                system_version=report.system_version,
                dataset_version=report.dataset_version,
                metric_results=report.aggregate_scores,
                run_id=report.run_id,
            )
            artifact = create_artifact(
                kind="evaluation_snapshot",
                logical_id=f"eval_{report.run_id[:8]}",
                payload=snapshot.to_dict(),
            )
            self.l4_store.put(artifact)
        except Exception:
            pass


def _default_metrics() -> list[EvaluationMetric]:
    """Return the default metric suite."""
    return [
        PrecisionAtK(k=5),
        RecallAtK(k=10),
        MeanReciprocalRank(),
        NDCG(k=10),
        Groundedness(),
        AnswerCorrectness(),
    ]


__all__ = [
    "OfflineEvaluationRunner",
    "_default_metrics",
    "RetrievalFn",
    "GenerationFn",
]
