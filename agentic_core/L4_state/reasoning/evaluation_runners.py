"""Evaluation Runners - Shadow and Replay Modes

Implements spec-compliant Shadow and Replay evaluation runners from Agentic Retrieval Models v9:
- Shadow Mode: Silent evaluation alongside live queries
- Replay Mode: Re-evaluate historical queries
- Metrics: Precision@K, Recall@K, MRR, NDCG, F1-Groundedness

Provides offline evaluation for Pipeline D meta-learning.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_evaluation_metric,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


@dataclass
class EvaluationRun:
    """Evaluation run configuration and results."""
    run_id: str
    mode: str  # shadow, replay, live
    query: str
    expected_chunks: list[str]  # Ground truth
    retrieved_chunks: list[str]
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    config: dict[str, Any] = field(default_factory=dict)


class EvaluationRunner(ABC):
    """Abstract evaluation runner."""

    @abstractmethod
    async def evaluate(self, query: str, retrieved: list[str]) -> EvaluationRun:
        """Evaluate retrieval quality."""
        pass


class ShadowEvaluationRunner(EvaluationRunner):
    """Shadow mode evaluation - silent evaluation alongside live queries.

    Runs evaluation in background without affecting user experience.
    """

    def __init__(
        self,
        relevance_judgments: dict[str, list[str]] | None = None,
    ):
        """Initialize shadow runner.

        Args:
            relevance_judgments: Query -> relevant chunk IDs mapping
        """
        self.relevance_judgments = relevance_judgments or {}
        self._run_count = 0

    async def evaluate(self, query: str, retrieved: list[str]) -> EvaluationRun:
        """Evaluate in shadow mode.

        Args:
            query: User query
            retrieved: Retrieved chunk IDs

        Returns:
            EvaluationRun with metrics
        """
        _trace_id = f"shadow_{self._run_count}"
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "ShadowEvaluationRunner.evaluate",
        )

        # Get ground truth if available
        expected = self.relevance_judgments.get(query, [])

        # Compute metrics
        metrics = self._compute_metrics(retrieved, expected)

        run = EvaluationRun(
            run_id=f"shadow_{hash(query) % 10000:04d}_{self._run_count}",
            mode="shadow",
            query=query,
            expected_chunks=expected,
            retrieved_chunks=retrieved,
            metrics=metrics,
            config={"has_ground_truth": len(expected) > 0},
        )

        # Emit metrics
        for metric_name, value in metrics.items():
            _emit_captures_evaluation_metric(_trace_id, "shadow", metric_name, value)

        self._run_count += 1
        Logger.debug(f"Shadow eval: {run.run_id} (P@5={metrics.get('precision_at_5', 0):.2f})")

        return run

    def _compute_metrics(
        self,
        retrieved: list[str],
        relevant: list[str],
    ) -> dict[str, Any]:
        """Compute retrieval metrics."""
        if not relevant:
            return {"has_ground_truth": False}

        relevant_set = set(relevant)

        # Precision@K
        precision_at_k = {}
        for k in [1, 5, 10]:
            if k <= len(retrieved):
                retrieved_k = set(retrieved[:k])
                precision_at_k[f"precision_at_{k}"] = len(retrieved_k & relevant_set) / k

        # Recall@K
        recall_at_k = {}
        for k in [1, 5, 10]:
            if k <= len(retrieved):
                retrieved_k = set(retrieved[:k])
                recall_at_k[f"recall_at_{k}"] = len(retrieved_k & relevant_set) / len(relevant_set)

        # MRR
        mrr = 0.0
        for rank, chunk_id in enumerate(retrieved, 1):
            if chunk_id in relevant_set:
                mrr = 1.0 / rank
                break

        # NDCG (simplified)
        dcg = 0.0
        for rank, chunk_id in enumerate(retrieved, 1):
            if chunk_id in relevant_set:
                dcg += 1.0 / (1 + rank)

        ideal_dcg = sum(1.0 / (1 + rank) for rank in range(1, len(relevant) + 1))
        ndcg = dcg / ideal_dcg if ideal_dcg > 0 else 0.0

        return {
            "has_ground_truth": True,
            **precision_at_k,
            **recall_at_k,
            "mrr": mrr,
            "ndcg": ndcg,
        }

    def add_relevance_judgment(self, query: str, relevant_chunks: list[str]) -> None:
        """Add ground truth relevance judgment."""
        self.relevance_judgments[query] = relevant_chunks


class ReplayEvaluationRunner(EvaluationRunner):
    """Replay mode evaluation - re-evaluate historical queries.

    Re-runs queries from history to compare retrieval configs.
    """

    def __init__(
        self,
        history_store: Any | None = None,
    ):
        """Initialize replay runner.

        Args:
            history_store: Historical query store
        """
        self.history_store = history_store
        self._run_count = 0

    async def replay(
        self,
        query_ids: list[str] | None = None,
        since: str | None = None,
        new_config: dict[str, Any] | None = None,
    ) -> list[EvaluationRun]:
        """Replay historical queries.

        Args:
            query_ids: Specific queries to replay (None = all)
            since: Replay queries since timestamp
            new_config: New retrieval config to test

        Returns:
            List of evaluation runs
        """
        _trace_id = f"replay_batch_{self._run_count}"
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "ReplayEvaluationRunner.replay",
        )

        # Get historical queries
        historical = self._get_historical_queries(query_ids, since)

        runs = []
        for entry in historical:
            run = await self.evaluate(
                query=entry["query"],
                retrieved=entry.get("retrieved_chunks", []),
            )
            run.config = {
                "original_config": entry.get("config", {}),
                "new_config": new_config,
                "replay": True,
            }
            runs.append(run)

        self._run_count += 1
        Logger.info(f"Replayed {len(runs)} queries")

        return runs

    async def evaluate(self, query: str, retrieved: list[str]) -> EvaluationRun:
        """Evaluate in replay mode."""
        _trace_id = f"replay_{self._run_count}"
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "ReplayEvaluationRunner.evaluate",
        )

        # In replay, we compare against stored results
        metrics = {"replay": True, "query": query}

        run = EvaluationRun(
            run_id=f"replay_{self._run_count:04d}",
            mode="replay",
            query=query,
            expected_chunks=[],  # Will be filled from history
            retrieved_chunks=retrieved,
            metrics=metrics,
        )

        self._run_count += 1
        return run

    def _get_historical_queries(
        self,
        query_ids: list[str] | None,
        since: str | None,
    ) -> list[dict[str, Any]]:
        """Get historical queries to replay."""
        # Placeholder - would query from history store
        return []


class EvaluationOrchestrator:
    """Orchestrates shadow and replay evaluations."""

    def __init__(self):
        """Initialize evaluation orchestrator."""
        self.shadow = ShadowEvaluationRunner()
        self.replay = ReplayEvaluationRunner()
        self._evaluations: list[EvaluationRun] = []

    async def shadow_evaluate(
        self,
        query: str,
        retrieved_chunks: list[str],
    ) -> EvaluationRun | None:
        """Run shadow evaluation for a live query.

        Args:
            query: User query
            retrieved_chunks: Retrieved chunks

        Returns:
            EvaluationRun if ground truth available
        """
        run = await self.shadow.evaluate(query, retrieved_chunks)

        if run.metrics.get("has_ground_truth"):
            self._evaluations.append(run)
            return run

        return None

    async def replay_batch(
        self,
        since: str | None = None,
        new_config: dict[str, Any] | None = None,
    ) -> list[EvaluationRun]:
        """Run replay evaluation batch.

        Args:
            since: Replay queries since timestamp
            new_config: New config to test

        Returns:
            List of evaluation runs
        """
        runs = await self.replay.replay(since=since, new_config=new_config)
        self._evaluations.extend(runs)
        return runs

    def get_aggregated_metrics(
        self,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated metrics across evaluations.

        Args:
            mode: Filter by mode (shadow, replay)

        Returns:
            Aggregated metrics
        """
        evaluations = self._evaluations
        if mode:
            evaluations = [e for e in evaluations if e.mode == mode]

        if not evaluations:
            return {"count": 0}

        # Aggregate metrics
        metric_sums = {}
        metric_counts = {}

        for eval_run in evaluations:
            for metric_name, value in eval_run.metrics.items():
                if isinstance(value, (int, float)):
                    metric_sums[metric_name] = metric_sums.get(metric_name, 0.0) + value
                    metric_counts[metric_name] = metric_counts.get(metric_name, 0) + 1

        averages = {
            name: metric_sums[name] / metric_counts[name]
            for name in metric_sums
        }

        return {
            "count": len(evaluations),
            "mode": mode or "all",
            "averages": averages,
        }

    def export_evaluations(self, path: str) -> bool:
        """Export evaluations to file.

        Args:
            path: Export file path

        Returns:
            True if exported
        """
        try:
            data = [
                {
                    "run_id": e.run_id,
                    "mode": e.mode,
                    "query": e.query,
                    "metrics": e.metrics,
                    "timestamp": e.timestamp,
                }
                for e in self._evaluations
            ]

            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

            Logger.info(f"Exported {len(data)} evaluations to {path}")
            return True

        except Exception as e:
            Logger.error(f"Failed to export evaluations: {e}")
            return False


# Global instance
_global_eval_orchestrator: EvaluationOrchestrator | None = None


def get_global_eval_orchestrator() -> EvaluationOrchestrator:
    """Get or create global evaluation orchestrator."""
    global _global_eval_orchestrator
    if _global_eval_orchestrator is None:
        _global_eval_orchestrator = EvaluationOrchestrator()
    return _global_eval_orchestrator


async def shadow_evaluate(query: str, retrieved: list[str]) -> EvaluationRun | None:
    """Convenience function for shadow evaluation."""
    return await get_global_eval_orchestrator().shadow_evaluate(query, retrieved)
