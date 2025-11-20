# FILE: registry.py
"""
Registry Layer (v10_10 · Phase 3)
===================================

This module defines:
    • RAG strategy registry
    • RetrievalConfig factories
    • ExecutionProfile registry
    • Static mappings for BM25 / DENSE / HYBRID / HYDE / RRF

Responsibilities:
    • Provide read-only strategy definitions
    • Produce RetrievalConfig objects for the RAG pipeline
    • Provide ExecutionProfile objects used by L1 planning and L2 execution

Non-Responsibilities:
    • No retrieval
    • No ranking
    • No LLM calls
    • No orchestration
    • No state mutation
"""

from __future__ import annotations

from typing import Dict

from models import (
    RetrievalConfig,
    RAGStrategyDefinition,
    ExecutionProfile,
)


# =============================================================================
# RAG STRATEGY DEFINITIONS (PHASE 3)
# =============================================================================

# Each strategy defines:
#   • retrieval_mode: "bm25" | "dense" | "hybrid"
#   • use_hyde:       bool
#   • use_rrf:        bool
#   • top_k:          int
#   • hybrid weights: hybrid_bm25_weight, hybrid_dense_weight

_RAG_STRATEGIES: Dict[str, RAGStrategyDefinition] = {
    "bm25_basic": RAGStrategyDefinition(
        name="bm25_basic",
        description="Pure BM25 lexical retrieval, no HYDE, no dense.",
        retrieval_mode="bm25",
        use_hyde=False,
        use_rrf=False,
        top_k=20,
        hybrid_bm25_weight=1.0,
        hybrid_dense_weight=0.0,
    ),

    "dense_basic": RAGStrategyDefinition(
        name="dense_basic",
        description="Dense semantic retrieval only.",
        retrieval_mode="dense",
        use_hyde=False,
        use_rrf=False,
        top_k=20,
        hybrid_bm25_weight=0.0,
        hybrid_dense_weight=1.0,
    ),

    "hybrid_balanced": RAGStrategyDefinition(
        name="hybrid_balanced",
        description="Balanced hybrid: BM25 + dense with equal weight.",
        retrieval_mode="hybrid",
        use_hyde=False,
        use_rrf=True,
        top_k=30,
        hybrid_bm25_weight=0.5,
        hybrid_dense_weight=0.5,
    ),

    "hybrid_semantic": RAGStrategyDefinition(
        name="hybrid_semantic",
        description="Dense-tilted hybrid retrieval.",
        retrieval_mode="hybrid",
        use_hyde=False,
        use_rrf=True,
        top_k=30,
        hybrid_bm25_weight=0.3,
        hybrid_dense_weight=0.7,
    ),

    "hybrid_hyde": RAGStrategyDefinition(
        name="hybrid_hyde",
        description="Hybrid retrieval combined with HYDE query expansion.",
        retrieval_mode="hybrid",
        use_hyde=True,
        use_rrf=True,
        top_k=35,
        hybrid_bm25_weight=0.4,
        hybrid_dense_weight=0.6,
    ),

    "hyde_dense": RAGStrategyDefinition(
        name="hyde_dense",
        description="Dense retrieval enhanced with HYDE pseudo-document.",
        retrieval_mode="dense",
        use_hyde=True,
        use_rrf=True,
        top_k=25,
        hybrid_bm25_weight=0.0,
        hybrid_dense_weight=1.0,
    ),
}


def get_rag_strategy(name: str) -> RAGStrategyDefinition:
    """
    Return a RAG strategy definition by name.
    Raises KeyError on unknown names.
    """
    return _RAG_STRATEGIES[name]


# =============================================================================
# RETRIEVAL CONFIG FACTORY
# =============================================================================

def build_retrieval_config(strategy: RAGStrategyDefinition) -> RetrievalConfig:
    """
    Convert a RAGStrategyDefinition → RetrievalConfig.
    This indirection allows future per-query overrides.
    """
    return RetrievalConfig(
        retrieval_mode=strategy.retrieval_mode,
        use_hyde=strategy.use_hyde,
        use_rrf=strategy.use_rrf,
        top_k=strategy.top_k,
        hybrid_bm25_weight=strategy.hybrid_bm25_weight,
        hybrid_dense_weight=strategy.hybrid_dense_weight,
    )


# =============================================================================
# EXECUTION PROFILES (L1→L2)
# =============================================================================

_EXECUTION_PROFILES: Dict[str, ExecutionProfile] = {
    "default": ExecutionProfile(
        name="default",
        rag_strategy="hybrid_balanced",
        max_context_tokens=2800,
        llm_temperature=0.2,
        llm_top_p=0.9,
    ),

    "semantic_heavy": ExecutionProfile(
        name="semantic_heavy",
        rag_strategy="hybrid_semantic",
        max_context_tokens=3000,
        llm_temperature=0.15,
        llm_top_p=0.9,
    ),

    "hyde_mode": ExecutionProfile(
        name="hyde_mode",
        rag_strategy="hybrid_hyde",
        max_context_tokens=3200,
        llm_temperature=0.2,
        llm_top_p=0.9,
    ),

    "dense_only_high_precision": ExecutionProfile(
        name="dense_only_high_precision",
        rag_strategy="dense_basic",
        max_context_tokens=2500,
        llm_temperature=0.1,
        llm_top_p=0.85,
    ),

    "fast_bm25": ExecutionProfile(
        name="fast_bm25",
        rag_strategy="bm25_basic",
        max_context_tokens=2400,
        llm_temperature=0.0,
        llm_top_p=0.9,
    ),
}


def get_execution_profile(name: str) -> ExecutionProfile:
    """
    Return an ExecutionProfile by name.
    """
    return _EXECUTION_PROFILES[name]
