"""
Semantic Retriever for L1 Cognition
Retrieves relevant context from ChromaDB semantic memory layer.
"""

import asyncio
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
import numpy as np

# Add L4_state/utils to path for imports (client/ package lives there)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "L4_state" / "utils"))

from client.chroma_client import SovereignChromaClient
from agentic_core.embeddings.bge_runtime import BGE_MODEL, BGE_QUERY_DIM, bge_embed_query
from tqdm import tqdm

logger = logging.getLogger(__name__)

_BGE_EMBEDDING_DIM = BGE_QUERY_DIM  # backward-compat alias for external readers
_CANONICAL_CHROMA_PATH = str(Path(__file__).resolve().parents[3] / "data" / "cache" / "chromadb")


@dataclass
class RetrievalResult:
    """Result from semantic retrieval."""

    content: str
    metadata: dict[str, Any]
    score: float
    collection: str


@dataclass
class RetrievalQuery:
    """Query for semantic retrieval."""

    text: str
    collections: list[str]
    filters: dict[str, Any] | None = None
    max_results: int = 10


class SemanticRetriever:
    """
    Semantic retriever for L1 cognition layer.

    Provides intelligent retrieval from ChromaDB semantic memory
    with query routing, multi-collection fusion, and reranking.
    """

    def __init__(self, chroma_persist_dir: str = _CANONICAL_CHROMA_PATH):
        """
        Initialize semantic retriever.

        Args:
            chroma_persist_dir: ChromaDB persistence directory (defaults to canonical BGE store)
        """
        self.chroma = SovereignChromaClient(persist_dir=chroma_persist_dir)
        self._bge_chroma = chromadb.PersistentClient(path=chroma_persist_dir)

        # BGE-aligned collection routing — all targets hold BAAI/bge-m3 1024-dim vectors
        self.collection_routing = {
            "code_questions": ["code_chunks"],
            "architecture": ["code_chunks", "arch_docs"],
            "implementation": ["code_chunks"],
            "documentation": ["arch_docs"],
            "general": ["code_chunks", "arch_docs"],
        }

        # Available collections
        self.available_collections = [c.name for c in self._bge_chroma.list_collections()]
        logger.info(f"Semantic retriever initialized with collections: {self.available_collections}")

    async def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: RetrievalQuery object with text and parameters

        Returns:
            List of RetrievalResult objects
        """
        # Route query to appropriate collections
        target_collections = self._route_query(query)

        # Filter to available collections
        target_collections = [c for c in target_collections if c in self.available_collections]

        if not target_collections:
            logger.warning(f"No available collections for query: {query.text}")
            return []

        # Execute parallel queries
        results = await self._parallel_query(query, target_collections)

        # Fuse and rank results
        fused_results = self._fuse_results(results)

        logger.info(f"Retrieved {len(fused_results)} results for query: {query.text[:50]}...")
        return fused_results

    def _route_query(self, query: RetrievalQuery) -> list[str]:
        """Route query to appropriate collections based on content."""
        query_lower = query.text.lower()

        # Explicit collection specification
        if query.collections:
            return query.collections

        # Keyword-based routing
        if any(keyword in query_lower for keyword in ["function", "class", "method", "code", "implement"]):
            return self.collection_routing["code_questions"]
        elif any(keyword in query_lower for keyword in ["architecture", "design", "pattern", "structure"]):
            return self.collection_routing["architecture"]
        elif any(keyword in query_lower for keyword in ["what", "how", "explain", "describe"]):
            return self.collection_routing["general"]
        elif any(keyword in query_lower for keyword in ["documentation", "readme", "guide"]):
            return self.collection_routing["documentation"]
        else:
            return self.collection_routing["general"]

    async def _parallel_query(
        self, query: RetrievalQuery, collections: list[str]
    ) -> dict[str, list[RetrievalResult]]:
        """Execute parallel queries across collections."""
        results = {}

        # Create tasks for parallel execution
        tasks = []
        for collection in collections:
            task = self._query_collection(collection, query)
            tasks.append((collection, task))

        # Execute tasks concurrently
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

        # Process results
        for (collection, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                logger.error(f"Query failed for collection {collection}: {result}")
                results[collection] = []
            else:
                results[collection] = result

        return results

    async def _query_collection(self, collection: str, query: RetrievalQuery) -> list[RetrievalResult]:
        """Query a single BGE-aligned collection using a real BGE-m3 query embedding."""
        try:
            query_embedding = bge_embed_query(query.text)

            chroma_col = self._bge_chroma.get_collection(collection)

            # Guard: verify stored dimension matches query dimension before querying
            sample = chroma_col.get(limit=1, include=["embeddings"])
            sample_embs = sample.get("embeddings")
            if sample_embs is not None:
                arr = np.array(sample_embs)
                stored_dim = arr.shape[1] if arr.ndim == 2 else arr.shape[0]
                if stored_dim != len(query_embedding):
                    raise RuntimeError(
                        f"BGE_DIM_MISMATCH: collection='{collection}' stored dim={stored_dim} "
                        f"vs query dim={len(query_embedding)}. "
                        f"Collection must be re-ingested with {BGE_MODEL}."
                    )

            chroma_results = chroma_col.query(
                query_embeddings=[query_embedding],
                n_results=query.max_results,
                where=query.filters,
                include=["documents", "metadatas", "distances"],
            )

            results = []
            for i in range(len(chroma_results["ids"][0])):
                result = RetrievalResult(
                    content=chroma_results["documents"][0][i],
                    metadata=chroma_results["metadatas"][0][i],
                    score=1.0 - chroma_results["distances"][0][i],
                    collection=collection,
                )
                results.append(result)

            return results

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Failed to query collection {collection}: {e}")
            raise

    def _fuse_results(self, collection_results: dict[str, list[RetrievalResult]]) -> list[RetrievalResult]:
        """
        Fuse results from multiple collections using Reciprocal Rank Fusion (RRF).

        Args:
            collection_results: Results per collection

        Returns:
            Fused and ranked results
        """
        all_results = []

        # Collect all results with collection info
        for collection, results in collection_results.items():
            for result in results:
                result.collection = collection
                all_results.append(result)

        if not all_results:
            return []

        # Sort by score (descending)
        all_results.sort(key=lambda x: x.score, reverse=True)

        # Apply simple reranking based on collection priority
        collection_priority = {
            "code_chunks": 1.1,
            "docs": 1.0,
        }

        for result in all_results:
            priority = collection_priority.get(result.collection, 1.0)
            result.score *= priority

        # Final sort and limit
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:20]  # Return top 20 results

    async def answer_question(self, question: str) -> tuple[str, list[RetrievalResult]]:
        """
        Answer a question using semantic retrieval.

        Args:
            question: Question to answer

        Returns:
            Tuple of (answer, retrieval_results)
        """
        # Create query
        query = RetrievalQuery(
            text=question,
            collections=[],  # Auto-route
            max_results=10,
        )

        # Retrieve results
        results = await self.retrieve(query)

        if not results:
            return "I couldn't find relevant information to answer your question.", []

        # Format answer with citations
        answer_parts = ["Based on the retrieved information:\n"]

        for i, result in enumerate(results[:5]):  # Use top 5 results
            source = f"{result.collection}:{result.metadata.get('file_path', 'unknown')}"
            answer_parts.append(f"{i + 1}. {result.content[:200]}...")
            answer_parts.append(f"   Source: {source} (score: {result.score:.2f})")

        answer = "\n".join(answer_parts)
        return answer, results

    def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics for all collections."""
        stats = {}
        for collection in self.available_collections:
            stats[collection] = self.chroma.get_collection_stats(collection)
        return stats

    # ------------------------------------------------------------------
    # C0 Evidence Contract surface (Phase 2 — EvidenceBundle propagation)
    # ------------------------------------------------------------------

    def retrieve_as_contract(
        self,
        query: str,
        collection_name: str,
        request_id: str,
        top_k: int = 5,
    ) -> "C0EvidenceContract":
        """Run shaped hybrid retrieval and wrap the result in a C0EvidenceContract.

        This is the preferred retrieval surface for callers that need the formal
        evidence contract for prompt assembly or exit evaluation.

        Backward compatibility: existing callers using retrieve() are unaffected.

        Args:
            query:           Free-text retrieval query.
            collection_name: Target canonical collection (e.g. ``"code_chunks"``).
            request_id:      Upstream request identifier (for HMAC and replay).
            top_k:           Maximum number of ranked chunks to include.

        Returns:
            Validated ``C0EvidenceContract`` ready for prompt assembly or exit eval.
        """
        import hashlib as _hashlib
        import uuid as _uuid

        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (  # guardian: allow-layer-violation -- L1 module uses L3 orchestration; intentional cross-layer dependency in cognition layer
            get_global_hybrid_engine,
        )
        from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (  # guardian: allow-layer-violation -- L1 module uses L3 orchestration; intentional cross-layer dependency in cognition layer
            C0EvidenceContract,
            CitedSpan,
        )

        retrieval_id = str(_uuid.uuid4())
        engine = get_global_hybrid_engine(collection_name)
        bundle = engine.shape_search(query, collection_name=collection_name, top_k=top_k)

        cited_spans: list[CitedSpan] = []
        # progress_bar: not required — loop bounded to top_k items (default ≤20, sub-ms/item)
        for chunk in tqdm(bundle.ranked_chunks[:top_k], desc="Processing", unit="item"):
            anchor = bundle.citation_anchors.get(chunk.chunk_id)
            source_ref = (
                (anchor.file_path or anchor.source_url or collection_name) if anchor else collection_name
            )
            raw_digest = chunk.metadata.get("canonical_digest", "")
            chunk_hash = (
                str(raw_digest) if raw_digest else _hashlib.sha256(chunk.content.encode()).hexdigest()[:32]
            )
            cited_spans.append(
                CitedSpan(
                    span_id=chunk.chunk_id,
                    source_ref=source_ref,
                    text_snippet=chunk.content[:512],
                    relevance_score=float(chunk.combined_score),
                    chunk_hash=chunk_hash,
                )
            )

        # Coverage: mean combined_score weighted by citation completeness fraction
        top5_ids = [c.chunk_id for c in bundle.ranked_chunks[:5]]
        anchored = sum(1 for cid in top5_ids if cid in bundle.citation_anchors)
        cit_fraction = anchored / max(len(top5_ids), 1)
        mean_score = sum(c.combined_score for c in bundle.ranked_chunks[:top_k]) / max(
            len(bundle.ranked_chunks[:top_k]), 1
        )
        coverage_score = min(mean_score * (0.5 + 0.5 * cit_fraction), 1.0)

        return C0EvidenceContract.build(
            retrieval_id=retrieval_id,
            request_id=request_id,
            coverage_score=coverage_score,
            cited_spans=tuple(cited_spans),
        )

    def build_evidence_packet(
        self,
        query: str,
        collection_name: str,
        task_block: str,
        request_id: str,
        intent_hint: str = "",
        top_k: int = 5,
    ) -> "PromptEnvelope | None":
        """Full pipeline: shaped retrieval → C0EvidenceContract → PromptEnvelope.

        Wraps retrieve_as_contract() + assemble_from_c0_contract() into one
        convenience call for callers that need a ready-to-use prompt packet.

        Returns ``None`` if retrieval coverage is below the abstain threshold (0.30).

        Args:
            query:           Free-text retrieval query.
            collection_name: Target canonical collection.
            task_block:      Task instruction forwarded verbatim into the envelope.
            request_id:      Upstream request identifier.
            intent_hint:     Optional hint; graph-path keywords select a different
                             packet type inside the assembler.
            top_k:           Maximum number of chunks to retrieve.

        Returns:
            ``PromptEnvelope`` on success, ``None`` on abstain.
        """
        # guardian: allow-layer-violation -- L1 retriever convenience method uses c0_dispatcher for prompt envelope assembly; deferred import keeps dependency optional
        from tools.adg.prompt_assembly.c0_dispatcher import assemble_from_c0_contract

        contract = self.retrieve_as_contract(query, collection_name, request_id, top_k)
        return assemble_from_c0_contract(contract, task_block, intent_hint=intent_hint)


# Example usage and testing
async def main():
    """Test the semantic retriever."""
    retriever = SemanticRetriever()

    # Test questions
    questions = [
        "What does the UniversalWriteGateway do?",
        "How does the ADG scanner work?",
        "What are the L0-L6 layers?",
        "Show me the ChromaDB client implementation",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        answer, results = await retriever.answer_question(question)
        print(f"Answer: {answer}")
        print(f"Found {len(results)} results")


if __name__ == "__main__":
    asyncio.run(main())
