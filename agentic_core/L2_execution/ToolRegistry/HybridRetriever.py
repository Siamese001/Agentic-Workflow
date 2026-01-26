from __future__ import annotations

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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

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
        }
    )

    # Configurable boost multipliers
    BOOST_FUNCTION_CLASS = 5
    BOOST_ARG = 2
    BOOST_IDENTIFIER = 3

    @staticmethod
    def split_identifier(name: str) -> list[str]:
        """Split CamelCase and snake_case identifiers into sub-tokens."""
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
                        cls.split_identifier(node.name)
                        * (cls.BOOST_FUNCTION_CLASS if boost_symbols else 1)
                    )
                elif isinstance(node, ast.ClassDef):
                    tokens.extend(
                        cls.split_identifier(node.name)
                        * (cls.BOOST_FUNCTION_CLASS if boost_symbols else 1)
                    )
                elif isinstance(node, ast.Name):
                    tokens.extend(
                        cls.split_identifier(node.id)
                        * (cls.BOOST_IDENTIFIER if boost_symbols else 1)
                    )
                elif isinstance(node, ast.arg):
                    tokens.extend(
                        cls.split_identifier(node.arg) * (cls.BOOST_ARG if boost_symbols else 1)
                    )
                elif isinstance(node, ast.Attribute):
                    tokens.extend(
                        cls.split_identifier(node.attr)
                        * (cls.BOOST_IDENTIFIER if boost_symbols else 1)
                    )
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    # Docstrings and string literals
                    doc_tokens = [
                        t.lower()
                        for t in node.value.split()
                        if t.lower() not in cls.STOP_WORDS and len(t) > 2
                    ]
                    tokens.extend(doc_tokens)

        except SyntaxError:
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
        self._init_task = asyncio.create_task(self._load_or_rebuild_local_index())

    async def _load_or_rebuild_local_index(self):
        """Thread-safe loading of the sovereign index"""
        cache_path = Path("agentic_core/L4_state/ValidationContext/.sovereign_local_index.json")
        if cache_path.exists():
            try:
                data = await asyncio.to_thread(
                    lambda: json.loads(cache_path.read_text(encoding="utf-8"))
                )
                self.local_chunks = data["chunks"]

                def _build_bm25():
                    tokenized = [self.tokenizer.tokenize_code(c["text"]) for c in self.local_chunks]
                    return BM25Okapi(tokenized)

                self.bm25_index = await asyncio.to_thread(_build_bm25)
                self.index_ready.set()
                print("   [OK] Sovereign local BM25 index loaded")
                return
            except Exception as e:
                print(f"   [!] Local index cache corrupt — rebuilding: {e}")
        await self.rebuild_from_ingestion()

    async def rebuild_from_ingestion(self) -> Any:
        """Rebuild local index from latest ingestion artifacts"""
        try:
            from agentic_core.L0_maintenance.scripts.sovereign_ingestion_mission import (
                load_latest_ingested_chunks,
            )

            chunks: Any = await asyncio.to_thread(load_latest_ingested_chunks)
            self.local_chunks = chunks
            if chunks:

                def _sync():
                    tokenized = [self.tokenizer.tokenize_code(c["text"]) for c in chunks]
                    idx = BM25Okapi(tokenized)
                    cache_path = Path(
                        "agentic_core/L4_state/ValidationContext/.sovereign_local_index.json"
                    )
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    with tempfile.NamedTemporaryFile(
                        "w", delete=False, dir=cache_path.parent
                    ) as tf:
                        json.dump({"chunks": chunks}, tf, ensure_ascii=False)
                        temp_name = tf.name
                    os.replace(temp_name, cache_path)
                    return idx

                self.bm25_index = await asyncio.to_thread(_sync)
                self.index_ready.set()
            print("   [OK] Sovereign local index synchronized")
        except Exception as e:
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
        except Exception as e:
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
                    )
                )
        return results

    def deduplicate_by_hash(
        self, results: list[RetrievalResult], request_seen: set
    ) -> list[RetrievalResult]:
        """Deduplicate by content hash — prevents redundant chunks"""
        unique: Any = []
        for r in results:
            content_hash: Any = hashlib.sha256(r.text.encode("utf-8")).hexdigest()
            if content_hash not in request_seen:
                request_seen.add(content_hash)
                unique.append(r)
        return unique

    def reciprocal_rank_fusion(
        self, dense: list[RetrievalResult], sparse: list[RetrievalResult], k: int = 60
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

    async def rerank_combined(
        self, combined: list[RetrievalResult], query: str
    ) -> list[RetrievalResult]:
        """L5 reranking via cross-encoder (guardrail)"""
        if not combined:
            return []
        return await self.guardrail.rerank_documents(combined, query)

    async def hybrid_search(self, query: str, top_k: int = 12) -> list[RetrievalResult]:
        """Sovereign hybrid search with RRF fusion"""
        dense_results, sparse_results = await asyncio.gather(
            self.dense_search(query, top_k=top_k * 2),
            asyncio.to_thread(self.sparse_search, query, top_k=top_k * 2),
        )
        if not dense_results and (not sparse_results):
            return []
        fused: Any = self.reciprocal_rank_fusion(dense_results, sparse_results)
        return await self.guardrail.rerank_documents(
            fused[: min(50, len(fused))], query, top_k=top_k
        )

    async def wait_for_index(self) -> Any:
        """Wait for BM25 index to be ready"""
        await self.index_ready.wait()
