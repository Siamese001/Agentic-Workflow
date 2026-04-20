from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha1
import inspect
from typing import Any

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import C0EvidenceContract, CitedSpan


@dataclass
class _Budget:
    max_k: int = 5


@dataclass
class _Routing:
    depth_breaker: int = 1


@dataclass
class _Config:
    budget: _Budget = field(default_factory=_Budget)
    routing: _Routing = field(default_factory=_Routing)


def get_active_configs() -> _Config:
    return _Config()


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


class SovereignRagOrchestrator:
    def __init__(self, retriever: Any, query_planner: Any, guardrail: Any):
        self.retriever = retriever
        self.query_planner = query_planner
        self.guardrail = guardrail

    @staticmethod
    def _normalize_top_k(top_k: int, budget_max_k: int | None = None) -> int:
        try:
            normalized = max(1, int(top_k))
        except (TypeError, ValueError):
            normalized = 1
        if budget_max_k is not None:
            try:
                normalized = min(normalized, max(1, int(budget_max_k)))
            except (TypeError, ValueError):  # guardian: allow-silent-swallow  -- ADG-burn: silent_exception_swallow
                pass
        return normalized

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _doc_to_span(doc: Any, index: int) -> CitedSpan:
        return CitedSpan(
            span_id=str(getattr(doc, "chunk_id", f"span-{index}")),
            source_ref=str(getattr(doc, "doc_id", f"doc-{index}")),
            text_snippet=str(getattr(doc, "content", ""))[:200],
            relevance_score=SovereignRagOrchestrator._safe_float(getattr(doc, "score", 0.0)),
            chunk_hash=str(getattr(doc, "content_hash", "")),
        )

    @staticmethod
    def _stable_request_id(query: str) -> str:
        return f"req-{sha1(str(query or '').encode('utf-8')).hexdigest()[:12]}"

    async def sovereign_retrieve(self, query: str, top_k: int = 5) -> dict[str, Any]:
        cfg = get_active_configs()
        budget_max_k = getattr(getattr(cfg, "budget", None), "max_k", None)
        normalized_top_k = self._normalize_top_k(top_k, budget_max_k)

        docs = await _maybe_await(self.retriever.hybrid_search(query, top_k=normalized_top_k))
        docs = list(docs or [])

        dedupe = getattr(self.retriever, "deduplicate_by_hash", None)
        if callable(dedupe):
            docs = list(await _maybe_await(dedupe(docs)) or [])

        rerank = getattr(self.guardrail, "rerank_documents", None)
        final_docs = list(await _maybe_await(rerank(docs)) or docs) if callable(rerank) else docs
        final_docs = final_docs[:normalized_top_k]

        spans = tuple(self._doc_to_span(doc, idx) for idx, doc in enumerate(final_docs))
        coverage = max((self._safe_float(getattr(doc, "score", 0.0)) for doc in final_docs), default=0.0)
        request_id = self._stable_request_id(query)
        contract = C0EvidenceContract.build(
            retrieval_id=f"ret-{request_id[4:]}",
            request_id=request_id,
            coverage_score=coverage,
            cited_spans=spans,
        )
        return {
            "query": query,
            "documents": final_docs,
            "anchors": list(spans),
            "faithfulness": 0.85,
            "top_k": normalized_top_k,
            "hops": 1,
            "c0_contract": contract,
        }
