from __future__ import annotations

"\nRAGGuardrail - L5 RAG Content Filtering and Reranking\n\nModel library imports (torch, FlagEmbedding) are forbidden in L0-L6.\nReranker creation is delegated to tools/rag_reranker_shim.py which\nlives outside the layer boundary. The shim result is injected here.\n"
import asyncio
import math
import re
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.path_constants import BATCH_SIZE
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class ExternalKnowledgeAccessViolation(Exception):
    """Raised when retrieved context is consumed without a valid CitationBundle.

    REQ-RAGX-006: ExternalKnowledgeAccessViolation MUST be emitted and wave
    aborted if context used without CitationBundle.  Fail-closed.
    """


@dataclass(frozen=True)
class CitationBundle:
    """Immutable citation binding for retrieved chunks.

    Every chunk of external knowledge entering the execution pipeline MUST
    carry a CitationBundle proving provenance.  Fields mirror REQ-RAGX-003.
    """

    chunk_id: str
    source_ref: str
    byte_sha256: str
    byte_range: tuple[int, int]
    score: float


def validate_citation_custody(
    context_chunks: list[dict[str, Any]], citation_bundles: list[CitationBundle] | None
) -> None:
    """Enforce that every external-knowledge chunk has a matching CitationBundle.

    Args:
        context_chunks: list of dicts representing retrieved context.  Each dict
            MUST contain at least ``chunk_id``.
        citation_bundles: corresponding CitationBundle objects.  ``None`` or
            empty list when chunks are present triggers the violation.

    Raises:
        ExternalKnowledgeAccessViolation: when context is present but citations
            are missing, empty, or do not cover every chunk_id.
    """
    if not context_chunks:
        return
    if citation_bundles is None or len(citation_bundles) == 0:
        raise ExternalKnowledgeAccessViolation(
            f"CITATION_MISSING: {len(context_chunks)} context chunk(s) present but no CitationBundle provided — wave aborted"
        )
    cited_ids = {cb.chunk_id for cb in citation_bundles}
    for chunk in context_chunks:
        cid = chunk.get("chunk_id")
        if cid is None:
            raise ExternalKnowledgeAccessViolation("CHUNK_ID_MISSING: context chunk lacks 'chunk_id' field")
        if cid not in cited_ids:
            raise ExternalKnowledgeAccessViolation(
                f"CITATION_GAP: chunk_id={cid!r} has no matching CitationBundle — wave aborted"
            )


class RagGuardrail:
    """Brief description of functionality and purpose."""

    def __init__(self, reranker: Any = None, reranker_available: bool = False, status_message: str = ""):
        self.bge_reranker = reranker
        self.reranker_available = reranker_available
        if status_message:
            print(f"   [OK] {status_message}")
        elif not reranker_available:
            print("   [!] No reranker injected — falling back to RRF only")

    async def rerank_documents(self, documents: list[Any], query: str, top_k: int = 10) -> list[Any]:
        """
        L5 reranking using BGE-v2-m3 for sovereign precision
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "RagGuardrail.rerank_documents")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:RagGuardrail.rerank_documents".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not self.reranker_available or not documents:
            return documents
        try:
            pairs: Any = [[query, doc.text] for doc in documents]

            def _compute():
                return self.bge_reranker.compute_score(pairs, batch_size=BATCH_SIZE)

            raw_logits: Any = await asyncio.to_thread(_compute)
            if isinstance(raw_logits, float | int):
                raw_logits: Any = [raw_logits]
            confident_docs: Any = []
            min_confidence: Any = 0.75
            for doc, logit in zip(documents, raw_logits, strict=False):
                confidence: Any = 1 / (1 + math.exp(-logit))
                if confidence >= min_confidence:
                    doc.score = float(confidence)
                    confident_docs.append(doc)
            confident_docs.sort(key=lambda x: x.score, reverse=True)
            dropped: Any = len(documents) - len(confident_docs)
            if dropped > 0:
                print(f"   [FILTER] Dropped {dropped} low-confidence docs (<{min_confidence})")
            if not confident_docs:
                print("   [!] SOVEREIGN ALERT: Zero documents passed confidence threshold.")
            return confident_docs[:top_k]
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"   [!] BGE reranking failed: {e}")
            return documents

    async def filter_hallucinations(self, documents: list[Any], query: str) -> list[Any]:
        """
        Heuristic: Checks if key entities in the query/response are supported by documents.
        """
        if not documents:
            return documents
        combined_context = " ".join([d.text.lower() for d in documents])
        query_entities = set(re.findall("\\b[A-Z][a-z]+\\b", query))
        if not query_entities:
            return documents
        supported_entities = 0
        for entity in query_entities:
            if entity.lower() in combined_context:
                supported_entities += 1
        ratio = supported_entities / len(query_entities)
        if ratio < 0.5:
            print(f"   [WARN] Retrieval Validity Low: Only {ratio:.1%} of query entities found in context.")
        return documents

    async def apply_safety_filters(self, documents: list[Any]) -> list[Any]:
        """
        Apply L5 safety filters to RAG results
        """
        filtered: Any = []
        for doc in documents:
            if not doc.text or len(doc.text.strip()) < 10:
                continue
            forbidden: Any = ["password", "secret", "api_key", "private_key"]
            text_lower: Any = doc.text.lower()
            if any(word in text_lower for word in forbidden):
                continue
            filtered.append(doc)
        return filtered

    async def process(self, documents: list[Any], query: str) -> list[Any]:
        """
        Full RAG guardrail processing pipeline
        """
        filtered: Any = await self.apply_safety_filters(documents)
        safe: Any = await self.filter_hallucinations(filtered, query)
        reranked: Any = await self.rerank_documents(safe, query)
        return reranked
