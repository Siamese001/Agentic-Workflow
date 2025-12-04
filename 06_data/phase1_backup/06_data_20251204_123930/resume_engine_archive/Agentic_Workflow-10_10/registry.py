# FILE: registry.py
"""
Registry Layer (v10_10 · Phase 3)
===================================

This module defines:
    • RAG strategy registry
    • RetrievalConfig factories
    • Static mappings for BM25 / DENSE / HYBRID / HYDE / RRF

Responsibilities:
    • Provide read-only strategy definitions
    • Produce RetrievalConfig objects for the RAG pipeline

Non-Responsibilities:
    • No retrieval
    • No ranking
    • No LLM calls
    • No orchestration
    • No state mutation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from models import RetrievalConfig


# =============================================================================
# RAG STRATEGY DEFINITIONS (PHASE 3)
# =============================================================================

# Each strategy defines:
#   • retrieval_mode: "bm25" | "dense" | "hybrid"
#   • use_hyde:       bool
#   • use_rrf:        bool
#   • top_k:          int


@dataclass(frozen=True)
class RAGStrategyDefinition:
    """
    Canonical definition of a RAG strategy used by the registry.

    Fields:
        name: Human-readable name of the strategy.
        description: Short description.
        retrieval_mode: "bm25" | "dense" | "hybrid"
        use_hyde: Whether HYDE expansion should be used.
        use_rrf: Whether RRF fusion should be applied.
        top_k: Max hits to retrieve.
    """
    name: str
    description: str
    retrieval_mode: str
    use_hyde: bool
    use_rrf: bool
    top_k: int


_RAG_STRATEGIES: Dict[str, RAGStrategyDefinition] = {
    "bm25_basic": RAGStrategyDefinition(
        name="bm25_basic",
        description="Pure BM25 lexical retrieval, no HYDE, no dense.",
        retrieval_mode="bm25",
        use_hyde=False,
        use_rrf=False,
        top_k=20,
    ),
    "dense_basic": RAGStrategyDefinition(
        name="dense_basic",
        description="Dense semantic retrieval only.",
        retrieval_mode="dense",
        use_hyde=False,
        use_rrf=False,
        top_k=20,
    ),
    "hybrid_balanced": RAGStrategyDefinition(
        name="hybrid_balanced",
        description="Balanced hybrid: BM25 + dense with RRF fusion.",
        retrieval_mode="hybrid",
        use_hyde=False,
        use_rrf=True,
        top_k=30,
    ),
    "hybrid_hyde": RAGStrategyDefinition(
        name="hybrid_hyde",
        description="Hybrid retrieval with HYDE expansion and RRF fusion.",
        retrieval_mode="hybrid",
        use_hyde=True,
        use_rrf=True,
        top_k=40,
    ),
}


def get_rag_strategy(name: str) -> RAGStrategyDefinition:
    """
    Return a RAGStrategyDefinition by name.
    """
    return _RAG_STRATEGIES[name]


# =============================================================================
# RETRIEVAL CONFIG FACTORY
# =============================================================================


def build_retrieval_config(strategy: RAGStrategyDefinition) -> RetrievalConfig:
    """
    Convert a RAGStrategyDefinition → RetrievalConfig (Phase 3).

    Mapping:
        retrieval_mode → RetrievalConfig.strategy
        use_hyde      → RetrievalConfig.allow_hyde
        use_rrf       → RetrievalConfig.use_rrf
        top_k         → RetrievalConfig.max_hits
    """
    return RetrievalConfig(
        strategy=strategy.retrieval_mode,
        use_rrf=strategy.use_rrf,
        max_hits=strategy.top_k,
        bm25_k1=1.2,
        bm25_b=0.75,
        rrf_weights=None,
        allow_hyde=strategy.use_hyde,
        qa_council_size=1,
        qa_council_mode="simple",
    )
