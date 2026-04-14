from __future__ import annotations

from dataclasses import dataclass
import inspect
import time
import uuid
from typing import Any, Iterable

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_captures_evaluation_metric
from . import hybrid_search_engine as _hybrid_search_engine


@dataclass
class TitaniumRetrievalResult:
    chunk_id: str
    content: str
    retrieval_score: float
    metadata: dict[str, Any]


class TitaniumRAGPipeline:
    def __init__(
        self,
        retriever: Any | None = None,
        enable_decomposition: bool = True,
        enable_compression: bool = True,
        enable_reranking: bool = True,
    ):
        self.retriever = (
            retriever if retriever is not None else _hybrid_search_engine.get_global_hybrid_engine()
        )
        self.enable_decomposition = enable_decomposition
        self.enable_compression = enable_compression
        self.enable_reranking = enable_reranking

    @staticmethod
    def _normalize_top_k(top_k: int) -> int:
        try:
            return max(0, int(top_k))
        except Exception:
            return 0

    @staticmethod
    def _iter_results(results: Iterable[Any]) -> list[Any]:
        if results is None:
            return []
        return list(results)

    @staticmethod
    async def _maybe_await(value: Any) -> Any:
        if inspect.isawaitable(value):
            return await value
        return value

    @staticmethod
    def _result_score(result: Any) -> float:
        for attr in ("combined_score", "vector_score", "score"):
            value = getattr(result, attr, None)
            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return 0.0
        return 0.0

    async def _retrieve_single(self, query: str, top_k: int) -> list[TitaniumRetrievalResult]:
        if self.retriever is None:
            return []
        normalized_top_k = self._normalize_top_k(top_k)
        if normalized_top_k == 0:
            return []
        try:
            raw_results = await self._maybe_await(self.retriever.search(query, collection_name="code_chunks"))
        except Exception:
            return []
        converted: list[TitaniumRetrievalResult] = []
        for result in self._iter_results(raw_results)[:normalized_top_k]:
            converted.append(
                TitaniumRetrievalResult(
                    chunk_id=str(getattr(result, "chunk_id", "")),
                    content=str(getattr(result, "content", "")),
                    retrieval_score=self._result_score(result),
                    metadata=dict(getattr(result, "metadata", {}) or {}),
                )
            )
        return converted

    async def retrieve(self, query: str, top_k: int = 5) -> dict[str, Any]:
        trace_id = str(uuid.uuid4())
        started = time.perf_counter()
        results = await self._retrieve_single(query, top_k)
        _emit_captures_evaluation_metric(trace_id, "titanium", "retrieval_time_ms")
        return {
            "trace_id": trace_id,
            "query": query,
            "results": results,
            "result_count": len(results),
            "latency_ms": (time.perf_counter() - started) * 1000.0,
        }
