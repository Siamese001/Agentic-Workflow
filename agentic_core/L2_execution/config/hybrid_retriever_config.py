from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
HybridRetriever - Dense + Sparse Retrieval with Reranking
"""
import ast
import asyncio
import hashlib
import json
import os
import re
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

try:
    from rank_bm25 import BM25Okapi
except ImportError as _err:
    raise ImportError(
        "rank-bm25 is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err

# [SSOT IMPORT] Structure blueprint is the single source of truth


class ASTAwareTokenizer:
    """AST-aware tokenizer optimised for code retrieval with configurable boosting."""

    STOP_WORDS = frozenset(
        {
            "self",
            "cls",
            "none",
            "true",
            "false",
            "return",
            "if",
            "else",
            "elif",
            "for",
            "while",
            "try",
            "except",
            "finally",
            "with",
            "as",
            "import",
            "from",
            "def",
            "class",
            "pass",
            "break",
            "continue",
            "and",
            "or",
            "not",
            "in",
            "is",
            "lambda",
            "yield",
            "raise",
            "assert",
            "del",
            "global",
            "nonlocal",
            "async",
            "await",
            "the",
            "a",
            "an",
            "of",
            "to",
        },
    )

    # Configurable boost multipliers
    BOOST_FUNCTION_CLASS = 5
    BOOST_ARG = 2
    BOOST_IDENTIFIER = 3

    @staticmethod
    def split_identifier(name: str) -> list[str]:
        """Split CamelCase and snake_case identifiers into sub-tokens."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ASTAwareTokenizer.split_identifier", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ASTAwareTokenizer.split_identifier", "p0_governance")
        # First split on underscores
        parts = name.split("_")
        result = []
        for part in parts:
            # Then split CamelCase
            camel_parts = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", part).split()
            result.extend([p.lower() for p in camel_parts if len(p) > 1])
        return result

    @classmethod
    def tokenize_code(cls, text: str, boost_symbols: bool = True) -> list[str]:
        """Tokenize code chunk with AST awareness and optional boosting."""
        tokens = []

        # Primary AST-based extraction for Python
        try:
            tree = ast.parse(text)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    tokens.extend(
                        cls.split_identifier(node.name) * (cls.BOOST_FUNCTION_CLASS if boost_symbols else 1),
                    )
                elif isinstance(node, ast.ClassDef):
                    tokens.extend(
                        cls.split_identifier(node.name) * (cls.BOOST_FUNCTION_CLASS if boost_symbols else 1),
                    )
                elif isinstance(node, ast.Name):
                    tokens.extend(
                        cls.split_identifier(node.id) * (cls.BOOST_IDENTIFIER if boost_symbols else 1),
                    )
                elif isinstance(node, ast.arg):
                    tokens.extend(cls.split_identifier(node.arg) * (cls.BOOST_ARG if boost_symbols else 1))
                elif isinstance(node, ast.Attribute):
                    tokens.extend(
                        cls.split_identifier(node.attr) * (cls.BOOST_IDENTIFIER if boost_symbols else 1),
                    )
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    # Docstrings and string literals
                    doc_tokens = [    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
                        t.lower()
                        for t in node.value.split()
                        if t.lower() not in cls.STOP_WORDS and len(t) > 2
                    ]
                    tokens.extend(doc_tokens)

        except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            # Fallback to regex-based tokenization
            pass

        # Common fallback/additional regex for identifiers (runs always for robustness)
        words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", text.lower())
        for word in words:
            if word not in cls.STOP_WORDS and len(word) > 2:
                split_tokens = cls.split_identifier(word)
                tokens.extend(split_tokens * (cls.BOOST_IDENTIFIER if boost_symbols else 1))

        return tokens

    @classmethod
    def tokenize_query(cls, query: str) -> list[str]:
        """Tokenize natural-language or code query without boosting."""
        return cls.tokenize_code(query, boost_symbols=False)


@dataclass
class RetrievalResult:
    """Brief description of functionality and purpose."""

    text: str
    score: float
    source: str
    metadata: dict
    original_score: float = 0.0  # Preserves raw BM25/dense score before RRF overwrites


class HybridRetriever:
    """
    Hybrid retrieval combining semantic search with BM25 sparse retrieval
    """

    def __init__(self, vector_store, guardrail):
        self.vector_store = vector_store
        self.guardrail = guardrail
        self.bm25_index: BM25Okapi | None = None
        self.local_chunks: list[dict] = []
        self.index_ready = asyncio.Event()
        self.tokenizer = ASTAwareTokenizer()
        self._index_initialized = False  # Lazy init: no asyncio.create_task at construction

    async def _load_or_rebuild_local_index(self):
        """Thread-safe loading of the sovereign index"""
        cache_path = Path("agentic_core/L4_state/memory/.sovereign_local_index.json")
        if cache_path.exists():
            try:
                data = await asyncio.to_thread(lambda: json.loads(cache_path.read_text(encoding="utf-8")))
                self.local_chunks = data["chunks"]

                def _build_bm25():
                    tokenized = [self.tokenizer.tokenize_code(c["text"]) for c in self.local_chunks]
                    return BM25Okapi(tokenized)

                self.bm25_index = await asyncio.to_thread(_build_bm25)
                self.index_ready.set()
                print("   [OK] Sovereign local BM25 index loaded")
                return
            # guardian: allow-silent-swallow
            except (RuntimeError, ValueError) as e:
                print(f"   [!] Local index cache corrupt — rebuilding: {e}")
        await self.rebuild_from_ingestion()

    async def rebuild_from_ingestion(self) -> Any:
        """Rebuild local index from latest ingestion artifacts"""

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "HybridRetrieverConfig.rebuild_from_ingestion"
        )
        try:
            from agentic_core.L0_routing.scripts.sovereign_ingestion_mission import (
                load_latest_ingested_chunks,
            )

            chunks: Any = await asyncio.to_thread(load_latest_ingested_chunks)
            self.local_chunks = chunks
            if chunks:

                def _sync():
                    tokenized = [self.tokenizer.tokenize_code(c["text"]) for c in chunks]
                    idx = BM25Okapi(tokenized)
                    cache_path = Path("agentic_core/L4_state/memory/.sovereign_local_index.json")
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    with tempfile.NamedTemporaryFile("w", delete=False, dir=cache_path.parent) as tf:
                        json.dump({"chunks": chunks}, tf, ensure_ascii=False)
                        temp_name = tf.name
                    os.replace(temp_name, cache_path)
                    return idx

                self.bm25_index = await asyncio.to_thread(_sync)
                self.index_ready.set()
            print("   [OK] Sovereign local index synchronized")
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            print(f"   [X] Local index rebuild failed: {e}")

    async def dense_search(self, query: str, top_k: int = 15) -> list[RetrievalResult]:
        """Dense semantic search via vector store"""
        try:
            results: Any = await self.vector_store.similarity_search(query, top_k=top_k)
            return [
                RetrievalResult(
                    text=r.page_content,
                    score=r.score if hasattr(r, "score") else 0.0,
                    source=r.metadata.get("source", "unknown"),
                    metadata=r.metadata,
                )
                for r in results
            ]
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            print(f"   [!] Dense search failed: {e}")
            return []

    def sparse_search(self, query: str, top_k: int = 15) -> list[RetrievalResult]:
        """Sparse BM25 search on local chunks"""
        if not self.index_ready.is_set():
            print("   [!] BM25 search skipped: Index not ready")
            return []
        tokenized_query: Any = self.tokenizer.tokenize_query(query)
        doc_scores: Any = self.bm25_index.get_scores(tokenized_query)
        top_indices: Any = doc_scores.argsort()[-top_k:][::-1]
        results: Any = []
        for idx in top_indices:
            if doc_scores[idx] > 0:
                chunk: Any = self.local_chunks[idx]
                results.append(
                    RetrievalResult(
                        text=chunk["text"],
                        score=float(doc_scores[idx]),
                        source="local_bm25",
                        metadata=chunk.get("metadata", {}),
                    ),
                )
        return results

    def deduplicate_by_hash(self, results: list[RetrievalResult], request_seen: set) -> list[RetrievalResult]:
        """Deduplicate by content hash — prevents redundant chunks"""
        unique: Any = []
        for r in results:
            content_hash: Any = hashlib.sha256(r.text.encode("utf-8")).hexdigest()
            if content_hash not in request_seen:
                request_seen.add(content_hash)
                unique.append(r)
        return unique

    def reciprocal_rank_fusion(
        self,
        dense: list[RetrievalResult],
        sparse: list[RetrievalResult],
        k: int = 60,
    ) -> list[RetrievalResult]:
        """
        Fused rankings using optimized RRF (O(N) performance)
        """
        rank_map: Any = {}
        for rank, r in enumerate(dense, start=1):
            h: Any = hashlib.sha256(r.text.encode()).hexdigest()
            if h not in rank_map:
                rank_map[h] = {"result": r, "rrf_score": 0.0}
            rank_map[h]["rrf_score"] += 1 / (k + rank)
        for rank, r in enumerate(sparse, start=1):
            h: Any = hashlib.sha256(r.text.encode()).hexdigest()
            if h not in rank_map:
                rank_map[h] = {"result": r, "rrf_score": 0.0}
            rank_map[h]["rrf_score"] += 1 / (k + rank)
        fused: Any = []
        for info in rank_map.values():
            res: Any = info["result"]
            res.score = info["rrf_score"]
            fused.append(res)
        fused.sort(key=lambda x: x.score, reverse=True)
        return fused

    async def rerank_combined(self, combined: list[RetrievalResult], query: str) -> list[RetrievalResult]:
        """L5 reranking via cross-encoder (guardrail)"""
        if not combined:
            return []
        return await self.guardrail.rerank_documents(combined, query)

    async def _ensure_index(self) -> None:
        """Lazy index init: called on first hybrid_search invocation."""
        if not self._index_initialized:
            self._index_initialized = True
            await self._load_or_rebuild_local_index()

    # P4-4C: default context budget (tokens; 4 chars ≈ 1 token)
    MAX_CONTEXT_TOKENS: int = 4096

    async def hybrid_search(self, query: str, top_k: int = 12) -> list[RetrievalResult]:
        """Sovereign hybrid search with RRF fusion and context budget enforcement."""
        await self._ensure_index()
        dense_results, sparse_results = await asyncio.gather(
            self.dense_search(query, top_k=top_k * 2),
            asyncio.to_thread(self.sparse_search, query, top_k=top_k * 2),
        )
        if not dense_results and (not sparse_results):
            return []
        fused: Any = self.reciprocal_rank_fusion(dense_results, sparse_results)
        reranked = await self.guardrail.rerank_documents(fused[: min(50, len(fused))], query, top_k=top_k)
        # P4-4C: enforce context budget — drop trailing docs that exceed token ceiling
        return self._enforce_context_budget(reranked)

    def _enforce_context_budget(
        self,
        docs: list[RetrievalResult],
        max_tokens: int | None = None,
    ) -> list[RetrievalResult]:
        """P4-4C: Return the longest prefix of *docs* whose cumulative token estimate
        stays within *max_tokens* (default MAX_CONTEXT_TOKENS).

        Token estimate: len(doc.text) // 4 per document (4 chars ≈ 1 token).
        Always includes at least one document to prevent empty-result on large chunks.
        """
        budget = max_tokens if max_tokens is not None else self.MAX_CONTEXT_TOKENS
        if not docs:
            return docs
        accumulated = 0
        pruned: list[RetrievalResult] = []
        for doc in docs:
            doc_tokens = len(doc.text) // 4
            if pruned and accumulated + doc_tokens > budget:
                break
            accumulated += doc_tokens
            pruned.append(doc)
        return pruned

    async def wait_for_index(self) -> Any:
        """Wait for BM25 index to be ready"""
        await self.index_ready.wait()


# ---------------------------------------------------------------------------
# P4-2B: NoOpGuardrail — rerank_documents returns input unchanged (top_k slice)
# ---------------------------------------------------------------------------


class NoOpGuardrail:
    """Passthrough guardrail: rerank_documents returns candidates[:top_k] unchanged.

    Used by HybridRetrieverFactory for test/dev environments where no
    cross-encoder reranker is available.
    """

    async def rerank_documents(
        self,
        candidates: list[RetrievalResult],
        query: str,  # noqa: ARG002
        top_k: int = 12,
    ) -> list[RetrievalResult]:
        return candidates[:top_k]


# ---------------------------------------------------------------------------
# P4-2B: In-memory vector store for factory default
# ---------------------------------------------------------------------------


class _InMemoryVectorStore:
    """Minimal in-memory vector store for HybridRetrieverFactory default."""

    def __init__(self) -> None:
        self._docs: list[dict] = []

    def add_documents(self, docs: list[dict]) -> None:
        self._docs.extend(docs)

    async def similarity_search(self, query_embedding: list[float], top_k: int = 12) -> list[dict]:
        return self._docs[:top_k]


# ---------------------------------------------------------------------------
# P4-2B: Factory + singleton
# ---------------------------------------------------------------------------


class HybridRetrieverFactory:
    """Factory for constructing HybridRetriever with injectable dependencies."""

    @classmethod
    def from_in_memory_store(cls) -> HybridRetriever:
        """Construct a HybridRetriever with InMemoryVectorStore + NoOpGuardrail.

        Allows synchronous construction in tests without an event loop.
        """
        return HybridRetriever(
            vector_store=_InMemoryVectorStore(),
            guardrail=NoOpGuardrail(),
        )


_hybrid_retriever_singleton: HybridRetriever | None = None


def get_hybrid_retriever() -> HybridRetriever:
    """Return the process-global HybridRetriever singleton (lazy-initialized).

    Uses HybridRetrieverFactory.from_in_memory_store() on first call.
    Production callers may replace this singleton by assigning to
    ``_hybrid_retriever_singleton`` before first call.
    """
    global _hybrid_retriever_singleton
    if _hybrid_retriever_singleton is None:
        _hybrid_retriever_singleton = HybridRetrieverFactory.from_in_memory_store()
    return _hybrid_retriever_singleton
