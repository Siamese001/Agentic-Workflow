"""
Past Evaluation Retrieval System — apps_eval.enterprise.

Vector-based semantic retrieval of past evaluation results for
trend analysis, regression detection, and benchmark comparison.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from tqdm import tqdm

from apps_eval._telemetry import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)
from apps_eval.integrations.meta_bus_publisher import (
    KIND_RETRIEVAL,
    publish_eval_outcome,
)
from apps_eval.integrations.tracing import eval_span

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedEvaluation:
    """An evaluation result retrieved from the store."""

    eval_id: str
    trace_id: str
    timestamp: str
    overall_score: float
    dimension_scores: dict[str, float]
    suite_results: dict[str, float]
    content_preview: str
    metadata: dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0


@dataclass(frozen=True)
class TrendAnalysis:
    """Trend analysis across multiple evaluations."""

    dimension_id: str
    values: list[float]
    trend_direction: str  # improving, stable, declining
    slope: float
    volatility: float
    prediction_next: float


class InMemoryEvaluationStore:
    """In-memory store for evaluation results."""

    def __init__(self) -> None:
        self._evaluations: dict[str, dict[str, Any]] = {}
        self._embeddings: dict[str, list[float]] = {}

    @traces_execute(layer="L4_STATE")
    def add_evaluation(
        self,
        eval_id: str,
        result_data: dict[str, Any],
        metadata: dict[str, Any],
    ) -> bool:
        """Store an evaluation result."""
        _emit_stores_embedding("enterprise", "InMemoryEvaluationStore", eval_id)

        self._evaluations[eval_id] = {
            "data": result_data,
            "metadata": metadata,
        }
        # Mock embedding from result content
        content_str = json.dumps(result_data, sort_keys=True)
        self._embeddings[eval_id] = self._mock_embed(content_str)
        return True

    def query_similar(
        self,
        query: dict[str, Any],
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedEvaluation]:
        """Query for similar evaluations."""
        _emit_reads_through("enterprise", "InMemoryEvaluationStore", "query_similar")

        if not self._evaluations:
            return []

        # Create query embedding
        query_str = json.dumps(query, sort_keys=True)
        query_emb = self._mock_embed(query_str)

        # Score all evaluations
        scored: list[tuple[str, float]] = []
        for eval_id, emb in tqdm(self._embeddings.items(), desc="Processing", unit="item"):
            score = self._cosine_similarity(query_emb, emb)

            # Apply filters
            if filters:
                meta = self._evaluations[eval_id]["metadata"]
                if not all(meta.get(k) == v for k, v in filters.items()):
                    continue

            scored.append((eval_id, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results: list[RetrievedEvaluation] = []
        for eval_id, score in tqdm(scored[:n_results], desc="Processing", unit="item"):
            ev = self._evaluations[eval_id]
            meta = ev["metadata"]
            data = ev["data"]

            results.append(
                RetrievedEvaluation(
                    eval_id=eval_id,
                    trace_id=meta.get("trace_id", eval_id),
                    timestamp=meta.get("timestamp", ""),
                    overall_score=data.get("overall_score", 0.0),
                    dimension_scores=data.get("dimension_scores", {}),
                    suite_results=data.get("suite_results", {}),
                    content_preview=json.dumps(data)[:500],
                    metadata=meta,
                    similarity_score=score,
                ),
            )

        return results

    def get_by_suite(self, suite_id: str, limit: int = 10) -> list[RetrievedEvaluation]:
        """Get evaluations that tested a specific suite."""
        results: list[RetrievedEvaluation] = []

        for eval_id, ev in tqdm(self._evaluations.items(), desc="Processing", unit="item"):
            meta = ev["metadata"]
            if suite_id in meta.get("suite_ids", []):
                data = ev["data"]
                results.append(
                    RetrievedEvaluation(
                        eval_id=eval_id,
                        trace_id=meta.get("trace_id", eval_id),
                        timestamp=meta.get("timestamp", ""),
                        overall_score=data.get("overall_score", 0.0),
                        dimension_scores=data.get("dimension_scores", {}),
                        suite_results=data.get("suite_results", {}),
                        content_preview=json.dumps(data)[:500],
                        metadata=meta,
                        similarity_score=1.0,
                    ),
                )

        return sorted(results, key=lambda x: x.timestamp, reverse=True)[:limit]

    def _mock_embed(self, text: str) -> list[float]:
        """Generate mock embedding from text."""
        hash_val = hashlib.sha256(text.encode()).hexdigest()
        return [int(hash_val[i : i + 2], 16) / 255.0 for i in range(0, 20, 2)]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class EvaluationRetrievalEngine:
    """Engine for retrieving and analyzing past evaluations."""

    def __init__(self, store: InMemoryEvaluationStore | None = None) -> None:
        self.store = store or InMemoryEvaluationStore()
        self._query_history: list[dict[str, Any]] = []

    def index_evaluation(
        self,
        result: dict[str, Any],
        suite_ids: list[str],
        trace_id: str,
    ) -> str:
        """Index an evaluation result for future retrieval."""
        eval_id = f"eval_{trace_id[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        meta = {
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "suite_ids": suite_ids,
            "overall_score": result.get("overall_score", 0.0),
        }

        success = self.store.add_evaluation(eval_id, result, meta)

        if success:
            _emit_records_execution_trace("enterprise", "EvaluationRetrievalEngine", f"indexed_{eval_id}")

        return eval_id

    def find_similar_evaluations(
        self,
        current_result: dict[str, Any],
        suite_ids: list[str],
        n_results: int = 5,
    ) -> list[RetrievedEvaluation]:
        """Find evaluations similar to the current result."""
        _emit_pulls_context("enterprise", "EvaluationRetrievalEngine", "find_similar")

        # Build query from current result
        query = {
            "suite_ids": suite_ids,
            "dimension_scores": current_result.get("dimension_scores", {}),
        }

        results = self.store.query_similar(query, n_results=n_results)

        self._query_history.append(
            {
                "query_type": "similar",
                "suite_ids": suite_ids,
                "results_count": len(results),
                "timestamp": datetime.now().isoformat(),
            }
        )

        return results

    def get_suite_history(self, suite_id: str, limit: int = 10) -> list[RetrievedEvaluation]:
        """Get historical results for a specific suite."""
        return self.store.get_by_suite(suite_id, limit=limit)

    def analyze_trends(
        self,
        dimension_id: str,
        window_size: int = 10,
    ) -> TrendAnalysis | None:
        """Analyze score trends for a dimension."""
        with eval_span(
            "apps_eval.v1.retrieval.analyze_trends",
            attributes={
                "eval.dimension_id": dimension_id,
                "eval.window_size": window_size,
            },
        ):
            result = self._analyze_trends_impl(dimension_id, window_size)
            if result is not None:
                publish_eval_outcome(
                    kind=KIND_RETRIEVAL,
                    payload={
                        "engine": "EvaluationRetrievalEngine",
                        "op": "trend_analysis",
                        "dimension_id": result.dimension_id,
                        "trend_direction": result.trend_direction,
                        "slope": result.slope,
                        "volatility": result.volatility,
                        "prediction_next": result.prediction_next,
                        "value_count": len(result.values),
                    },
                )
            return result

    def _analyze_trends_impl(
        self,
        dimension_id: str,
        window_size: int,
    ) -> TrendAnalysis | None:
        # Get recent evaluations
        all_evals: list[RetrievedEvaluation] = []
        for ev_data in tqdm(self.store._evaluations.values(), desc="Processing", unit="item"):
            if dimension_id in ev_data["data"].get("dimension_scores", {}):
                meta = ev_data["metadata"]
                data = ev_data["data"]
                all_evals.append(
                    RetrievedEvaluation(
                        eval_id=meta.get("trace_id", ""),
                        trace_id=meta.get("trace_id", ""),
                        timestamp=meta.get("timestamp", ""),
                        overall_score=data.get("overall_score", 0.0),
                        dimension_scores=data.get("dimension_scores", {}),
                        suite_results=data.get("suite_results", {}),
                        content_preview="",
                    ),
                )

        if len(all_evals) < 3:
            return None

        # Sort by timestamp
        sorted_evals = sorted(all_evals, key=lambda x: x.timestamp)
        recent = sorted_evals[-window_size:]

        values = [e.dimension_scores.get(dimension_id, 0.0) for e in recent]

        # Calculate trend
        if len(values) >= 2:
            slope = (values[-1] - values[0]) / len(values)
        else:
            slope = 0.0

        # Volatility (standard deviation)
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        volatility = variance**0.5

        # Direction
        if slope > 0.05:
            direction = "improving"
        elif slope < -0.05:
            direction = "declining"
        else:
            direction = "stable"

        # Simple prediction (linear extrapolation)
        prediction = values[-1] + slope if values else 0.0

        return TrendAnalysis(
            dimension_id=dimension_id,
            values=values,
            trend_direction=direction,
            slope=slope,
            volatility=volatility,
            prediction_next=prediction,
        )

    def generate_baseline_comparison(
        self,
        current_result: dict[str, Any],
        baseline_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate comparison against baseline or historical average."""
        with eval_span(
            "apps_eval.v1.retrieval.generate_baseline_comparison",
            attributes={
                "eval.has_explicit_baseline": baseline_result is not None,
            },
        ):
            comparison = self._generate_baseline_comparison_impl(current_result, baseline_result)
            publish_eval_outcome(
                kind=KIND_RETRIEVAL,
                payload={
                    "engine": "EvaluationRetrievalEngine",
                    "op": "baseline_comparison",
                    "comparison_type": comparison.get("comparison_type", ""),
                    "overall_delta": comparison.get("overall_delta", 0.0),
                    "historical_count": comparison.get("historical_count", 0),
                },
            )
            return comparison

    def _generate_baseline_comparison_impl(
        self,
        current_result: dict[str, Any],
        baseline_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if baseline_result:
            # Compare against specific baseline
            return {
                "comparison_type": "baseline",
                "overall_delta": current_result.get("overall_score", 0.0)
                - baseline_result.get("overall_score", 0.0),
                "dimension_deltas": {
                    dim: current_result.get("dimension_scores", {}).get(dim, 0.0)
                    - baseline_result.get("dimension_scores", {}).get(dim, 0.0)
                    for dim in set(current_result.get("dimension_scores", {}).keys())
                    | set(baseline_result.get("dimension_scores", {}).keys())
                },
            }

        # Compare against historical average
        similar = self.find_similar_evaluations(current_result, [], n_results=10)
        if not similar:
            return {"comparison_type": "none", "reason": "no_historical_data"}

        avg_score = sum(e.overall_score for e in similar) / len(similar)

        return {
            "comparison_type": "historical_average",
            "historical_count": len(similar),
            "overall_delta": current_result.get("overall_score", 0.0) - avg_score,
            "historical_avg_score": avg_score,
        }

    def detect_regression_signals(
        self,
        current_result: dict[str, Any],
        threshold: float = 0.05,
    ) -> list[dict[str, Any]]:
        """Detect potential regression signals."""
        with eval_span(
            "apps_eval.v1.retrieval.detect_regression_signals",
            attributes={
                "eval.threshold": threshold,
            },
        ):
            signals = self._detect_regression_signals_impl(current_result, threshold)
            publish_eval_outcome(
                kind=KIND_RETRIEVAL,
                payload={
                    "engine": "EvaluationRetrievalEngine",
                    "op": "regression_signals",
                    "signal_count": len(signals),
                    "high_severity_count": sum(1 for s in signals if s.get("severity") == "high"),
                    "threshold": threshold,
                },
            )
            return signals

    def _detect_regression_signals_impl(
        self,
        current_result: dict[str, Any],
        threshold: float = 0.05,
    ) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []

        # Find similar past evaluations
        similar = self.find_similar_evaluations(current_result, [], n_results=5)

        if not similar:
            return signals

        # Compare dimension scores
        current_dims = current_result.get("dimension_scores", {})

        for dim, current_score in tqdm(current_dims.items(), desc="Processing", unit="item"):
            past_scores = [e.dimension_scores.get(dim) for e in similar if dim in e.dimension_scores]

            if not past_scores:
                continue

            avg_past = sum(past_scores) / len(past_scores)
            delta = current_score - avg_past

            if delta < -threshold:
                signals.append(
                    {
                        "type": "dimension_regression",
                        "dimension": dim,
                        "current_score": current_score,
                        "historical_avg": avg_past,
                        "delta": delta,
                        "severity": "high" if delta < -0.15 else "medium",
                    }
                )

        return signals


def create_retrieval_engine(
    chromadb_path: str | None = None,
    collection_name: str = "evaluations",
) -> EvaluationRetrievalEngine:
    """Factory for creating a retrieval engine."""
    _log.info("[create_retrieval_engine] Using in-memory store (install chromadb for persistence)")
    return EvaluationRetrievalEngine(store=InMemoryEvaluationStore())
