from __future__ import annotations

from dataclasses import dataclass
import math
import time
from typing import Any, Iterable


@dataclass
class BenchmarkMetrics:
    query_count: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_results: int
    avg_results_per_query: float


@dataclass
class RetrievalQualityMetrics:
    precision_at_k: float
    recall_at_k: float
    mean_reciprocal_rank: float
    ndcg_at_k: float


@dataclass
class BenchmarkQuery:
    query: str
    expected_chunk_ids: list[str]
    intent: str = "semantic"


class RetrievalBenchmark:
    def __init__(self, engine: Any):
        self.engine = engine

    def _search(self, query: str, collection_name: str = "code_chunks") -> list[Any]:
        try:
            results = self.engine.search(query, collection_name=collection_name)
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
            return []
        if results is None:
            return []
        if isinstance(results, list):
            return results
        try:
            return list(results)
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
            return []

    @staticmethod
    def _percentile(values: list[float], pct: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(float(v) for v in values)
        idx = max(0, math.ceil(pct * len(ordered)) - 1)
        return float(ordered[idx])

    @staticmethod
    def _chunk_ids(results: Iterable[Any]) -> list[str]:
        ids: list[str] = []
        for item in results:
            chunk_id = getattr(item, "chunk_id", None)
            if chunk_id is not None:
                ids.append(str(chunk_id))
        return ids

    def run_performance_benchmark(self, queries: list[str], iterations: int = 1) -> BenchmarkMetrics:
        if not queries:
            return BenchmarkMetrics(0, 0.0, 0.0, 0.0, 0, 0.0)
        iterations = max(1, int(iterations or 1))
        latencies: list[float] = []
        total_results = 0
        for _ in range(iterations):
            for query in queries:
                start = time.perf_counter()
                results = self._search(str(query), collection_name="code_chunks")
                latencies.append((time.perf_counter() - start) * 1000.0)
                total_results += len(results)
        query_count = len(queries) * iterations
        avg_latency = float(sum(latencies) / len(latencies)) if latencies else 0.0
        return BenchmarkMetrics(
            query_count=query_count,
            avg_latency_ms=avg_latency,
            p95_latency_ms=self._percentile(latencies, 0.95),
            p99_latency_ms=self._percentile(latencies, 0.99),
            total_results=total_results,
            avg_results_per_query=float(total_results / max(1, query_count)),
        )

    def run_quality_benchmark(self, queries: list[BenchmarkQuery], k: int = 5) -> RetrievalQualityMetrics:
        if not queries:
            return RetrievalQualityMetrics(0.0, 0.0, 0.0, 0.0)
        precision = recall = mrr = ndcg = 0.0
        k = max(1, int(k or 1))
        for item in queries:
            results = self._search(str(item.query), collection_name="code_chunks")[:k]
            returned = self._chunk_ids(results)
            expected = {str(chunk_id) for chunk_id in (item.expected_chunk_ids or [])}
            if not returned:
                precision += 0.0
                recall += 0.0 if expected else 1.0
                mrr += 0.0
                ndcg += 0.0
                continue
            hits = [cid for cid in returned if cid in expected]
            precision += len(hits) / max(1, len(returned))
            recall += len(hits) / max(1, len(expected))
            rr = 0.0
            dcg = 0.0
            ideal_rels = min(len(expected), k)
            idcg = (
                sum(1.0 / math.log2(rank + 1) for rank in range(2, ideal_rels + 2)) if ideal_rels > 0 else 0.0
            )
            for idx, cid in enumerate(returned, start=1):
                if cid in expected:
                    if rr == 0.0:
                        rr = 1.0 / idx
                    dcg += 1.0 / math.log2(idx + 1)
            mrr += rr
            ndcg += 0.0 if idcg == 0.0 else (dcg / idcg)
        n = len(queries)
        return RetrievalQualityMetrics(precision / n, recall / n, mrr / n, ndcg / n)

    def run_governance_benchmark(
        self, queries: list[str], governance_filter: dict[str, Any]
    ) -> dict[str, float]:
        if not queries:
            return {
                "avg_results_without_filter": 0.0,
                "avg_results_with_filter": 0.0,
                "filter_reduction_pct": 0.0,
            }
        without_filter: list[int] = []
        with_filter: list[int] = []
        for query in queries:
            results = self._search(str(query), collection_name="code_chunks")
            without_filter.append(len(results))
            try:
                filtered = self.engine._apply_governance_filters(results, governance_filter)
                filtered_count = len(filtered) if filtered is not None else 0
            except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
                filtered_count = 0
            with_filter.append(filtered_count)
        avg_without = sum(without_filter) / len(without_filter)
        avg_with = sum(with_filter) / len(with_filter)
        reduction = 0.0 if avg_without == 0 else ((avg_without - avg_with) / avg_without) * 100.0
        return {
            "avg_results_without_filter": float(avg_without),
            "avg_results_with_filter": float(avg_with),
            "filter_reduction_pct": float(reduction),
        }
