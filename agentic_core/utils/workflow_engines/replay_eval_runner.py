"""
Replay Evaluation Runner

Deterministically compares two system configurations (A vs B) over the
same evaluation dataset and produces a DeltaReport.

Inputs:  eval_dataset, system_config_A, system_config_B
Output:  DeltaReport (persisted to L4 when store is provided)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..schemas.evaluation_dataset_schema import EvaluationDataset
from ..schemas.evaluation_result_schema import (
    DeltaReport,
    EvaluationReport,
)
from .offline_eval_runner import GenerationFn, OfflineEvaluationRunner, RetrievalFn


class SystemConfig:
    """Encapsulates a named system configuration for replay comparison."""

    def __init__(
        self,
        name: str,
        version: str,
        retrieval_fn: RetrievalFn | None = None,
        generation_fn: GenerationFn | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.name = name
        self.version = version
        self.retrieval_fn = retrieval_fn
        self.generation_fn = generation_fn
        self.metadata: dict[str, Any] = metadata or {}


class ReplayEvaluationRunner:
    """Runs two system configs against the same dataset and computes metric deltas.

    Both configs are evaluated deterministically — same dataset, same metrics,
    same order — ensuring reproducible comparison.
    """

    def __init__(
        self,
        metrics: list | None = None,
        l4_store: Any | None = None,
    ):
        self.metrics = metrics
        self.l4_store = l4_store

    def run(
        self,
        dataset: EvaluationDataset,
        config_a: SystemConfig,
        config_b: SystemConfig,
    ) -> DeltaReport:
        """Compare config A vs config B on the given dataset.

        Args:
            dataset: Evaluation dataset (same for both configs)
            config_a: Baseline system configuration
            config_b: Candidate system configuration

        Returns:
            DeltaReport with metric_deltas = scores_b - scores_a
        """
        runner_a = OfflineEvaluationRunner(
            metrics=self.metrics,
            retrieval_fn=config_a.retrieval_fn,
            generation_fn=config_a.generation_fn,
            system_version=config_a.version,
        )
        runner_b = OfflineEvaluationRunner(
            metrics=self.metrics,
            retrieval_fn=config_b.retrieval_fn,
            generation_fn=config_b.generation_fn,
            system_version=config_b.version,
        )

        report_a = runner_a.run(dataset)
        report_b = runner_b.run(dataset)

        delta_report = self._compute_delta(report_a, report_b, config_a, config_b)

        if self.l4_store is not None:
            self._persist_delta(delta_report)

        return delta_report

    def _compute_delta(
        self,
        report_a: EvaluationReport,
        report_b: EvaluationReport,
        config_a: SystemConfig,
        config_b: SystemConfig,
    ) -> DeltaReport:
        """Compute per-metric deltas: scores_b - scores_a."""
        scores_a = report_a.aggregate_scores
        scores_b = report_b.aggregate_scores

        all_metrics = sorted(set(list(scores_a.keys()) + list(scores_b.keys())))
        metric_deltas: dict[str, float] = {}
        for metric_name in all_metrics:
            score_a = scores_a.get(metric_name, 0.0)
            score_b = scores_b.get(metric_name, 0.0)
            metric_deltas[metric_name] = score_b - score_a

        return DeltaReport(
            run_id_a=report_a.run_id,
            run_id_b=report_b.run_id,
            config_a_name=config_a.name,
            config_b_name=config_b.name,
            timestamp=datetime.utcnow().isoformat() + "Z",
            metric_deltas=metric_deltas,
            scores_a=dict(scores_a),
            scores_b=dict(scores_b),
        )

    def _persist_delta(self, delta: DeltaReport) -> None:
        """Persist DeltaReport artifact to L4 state registry."""
        try:
            from agentic_core.L4_state.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="evaluation_delta",
                logical_id=f"delta_{delta.run_id_a[:8]}_{delta.run_id_b[:8]}",
                payload=delta.to_dict(),
            )
            self.l4_store.put(artifact)
        except Exception:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            pass


__all__ = [
    "ReplayEvaluationRunner",
    "SystemConfig",
]
