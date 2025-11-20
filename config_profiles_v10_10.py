# FILE: 10_10/config_profiles_v10_10.py
"""
Execution Profiles (v10_10 · Phase 0)
====================================

This module defines the **deterministic, hard execution profiles**
used by the v10_10→v10_11 refactor. These replace the partial,
unused meta-profile wiring in current v10_10.

Profiles here will drive:

    • Reasoning strategy (CoT, ToT, ReAct)
    • RAG retrieval strategy (BM25, Hybrid, Dense)
    • Safety tier (strict, standard, debug)
    • Context budgets
    • Model tier selection (cheap / balanced / premium)
    • Drafting depth / QA depth
    • Async / parallel execution allowances
    • DAG-level execution configs
    • Cost / latency ceilings
    • Logging & observability granularity

These values are intentionally explicit and static to satisfy
G1–G3, G18, G28, G33 from the gap table. Dynamic adjustments
will be introduced in Phase 4 (meta-learning).
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any

from pydantic import BaseModel, Field

from .models import (
    ReasoningMode,
    RetrievalConfig,
    ContextBudget,
)


# ======================================================================
# ENUMS
# ======================================================================

class SafetyTier(str, Enum):
    STANDARD = "standard"
    STRICT = "strict"
    RELAXED = "relaxed"
    DEBUG = "debug"


class ModelTier(str, Enum):
    CHEAP = "cheap"
    BALANCED = "balanced"
    PREMIUM = "premium"


class DAGMode(str, Enum):
    """
    Controls whether the workflow graph may run:
        • sequential only
        • parallel-capable
        • allow speculative execution (Phase N)
    """
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


# ======================================================================
# PROFILE DEFINITION
# ======================================================================

class ExecutionProfileSpec(BaseModel):
    """
    Canonical representation of a workflow execution profile.
    """

    id: str
    description: str

    # Core behavior drivers
    reasoning_mode: ReasoningMode = ReasoningMode.COT
    safety_tier: SafetyTier = SafetyTier.STANDARD
    model_tier: ModelTier = ModelTier.BALANCED

    # Budgets / SLOs
    max_cost_usd: float = 0.10
    max_latency_ms: int = 3000

    # RAG tuning
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)

    # Context budgeting
    context_budget: ContextBudget = Field(default_factory=ContextBudget)

    # Drafting & QA depth
    drafting_depth: int = 3
    qa_depth: str = "medium"  # "shallow", "medium", "deep"

    # DAG & async allowances
    dag_mode: DAGMode = DAGMode.SEQUENTIAL
    allow_async: bool = False

    # Logging / observability
    telemetry_granularity: str = "standard"  # "minimal", "standard", "verbose"

    # Safety-mode behavior
    pii_detection_enabled: bool = True
    policy_engine_enabled: bool = True


# ======================================================================
# PROFILE CATALOG
# ======================================================================

def _balanced_hybrid_retrieval() -> RetrievalConfig:
    return RetrievalConfig(
        strategy="hybrid",
        use_rrf=True,
        max_hits=50,
        bm25_k1=1.2,
        bm25_b=0.75,
    )


def _cheap_bm25_retrieval() -> RetrievalConfig:
    return RetrievalConfig(
        strategy="bm25",
        use_rrf=False,
        max_hits=25,
        bm25_k1=1.0,
        bm25_b=0.6,
    )


def _premium_dense_retrieval() -> RetrievalConfig:
    return RetrievalConfig(
        strategy="dense",
        use_rrf=False,
        max_hits=40,
        bm25_k1=1.2,
        bm25_b=0.75,
    )


# =============================================================
# PROFILE SET
# =============================================================

EXECUTION_PROFILES: Dict[str, ExecutionProfileSpec] = {
    # ---------------------------------------------------------
    # 🟩 High-Quality Resume Generation
    # ---------------------------------------------------------
    "RESUME_HIGH_QUALITY": ExecutionProfileSpec(
        id="RESUME_HIGH_QUALITY",
        description="High-quality resume with full RAG, deep drafting, strict QA and safety.",
        reasoning_mode=ReasoningMode.TOT,
        safety_tier=SafetyTier.STRICT,
        model_tier=ModelTier.PREMIUM,
        max_cost_usd=0.25,
        max_latency_ms=4500,
        retrieval=_balanced_hybrid_retrieval(),
        context_budget=ContextBudget(
            total_tokens=2000,
            planning_tokens=300,
            rag_tokens=1000,
            drafting_tokens=600,
            qa_tokens=256,
            safety_tokens=256,
        ),
        drafting_depth=4,
        qa_depth="deep",
        dag_mode=DAGMode.PARALLEL,
        allow_async=True,
        telemetry_granularity="verbose",
        pii_detection_enabled=True,
        policy_engine_enabled=True,
    ),

    # ---------------------------------------------------------
    # 🟨 Low-Cost Resume Generation
    # ---------------------------------------------------------
    "RESUME_LOW_COST": ExecutionProfileSpec(
        id="RESUME_LOW_COST",
        description="Low-cost profile optimized for speed and minimal token spend.",
        reasoning_mode=ReasoningMode.DIRECT,
        safety_tier=SafetyTier.STANDARD,
        model_tier=ModelTier.CHEAP,
        max_cost_usd=0.03,
        max_latency_ms=1500,
        retrieval=_cheap_bm25_retrieval(),
        context_budget=ContextBudget(
            total_tokens=1200,
            planning_tokens=150,
            rag_tokens=500,
            drafting_tokens=400,
            qa_tokens=100,
            safety_tokens=50,
        ),
        drafting_depth=2,
        qa_depth="shallow",
        dag_mode=DAGMode.SEQUENTIAL,
        allow_async=False,
        telemetry_granularity="minimal",
        pii_detection_enabled=True,
        policy_engine_enabled=True,
    ),

    # ---------------------------------------------------------
    # 🟨 LinkedIn Outreach (Low-Verbosity)
    # ---------------------------------------------------------
    "OUTREACH_QUICK": ExecutionProfileSpec(
        id="OUTREACH_QUICK",
        description="Fast LinkedIn outreach generation; low latency and minimal RAG.",
        reasoning_mode=ReasoningMode.COT,
        safety_tier=SafetyTier.RELAXED,
        model_tier=ModelTier.CHEAP,
        max_cost_usd=0.02,
        max_latency_ms=1000,
        retrieval=_cheap_bm25_retrieval(),
        context_budget=ContextBudget(
            total_tokens=900,
            planning_tokens=100,
            rag_tokens=300,
            drafting_tokens=350,
            qa_tokens=50,
            safety_tokens=25,
        ),
        drafting_depth=1,
        qa_depth="shallow",
        dag_mode=DAGMode.SEQUENTIAL,
        allow_async=False,
        telemetry_granularity="minimal",
        pii_detection_enabled=False,
        policy_engine_enabled=False,
    ),

    # ---------------------------------------------------------
    # 🟥 Debug Deep-Inspection Mode
    # ---------------------------------------------------------
    "DEBUG_PROFILE": ExecutionProfileSpec(
        id="DEBUG_PROFILE",
        description="Verbose mode for debugging; maximal logs and loose limits.",
        reasoning_mode=ReasoningMode.REACT,
        safety_tier=SafetyTier.DEBUG,
        model_tier=ModelTier.CHEAP,
        max_cost_usd=1.00,
        max_latency_ms=10000,
        retrieval=_premium_dense_retrieval(),
        context_budget=ContextBudget(
            total_tokens=2500,
            planning_tokens=500,
            rag_tokens=1200,
            drafting_tokens=800,
            qa_tokens=400,
            safety_tokens=400,
        ),
        drafting_depth=5,
        qa_depth="deep",
        dag_mode=DAGMode.PARALLEL,
        allow_async=True,
        telemetry_granularity="verbose",
        pii_detection_enabled=False,
        policy_engine_enabled=False,
    ),
}


# ======================================================================
# PROFILE LOOKUP API
# ======================================================================

def get_profile(profile_id: str) -> ExecutionProfileSpec:
    """
    Return a validated ExecutionProfileSpec by ID.
    Raises KeyError for unknown profiles.
    """
    if profile_id not in EXECUTION_PROFILES:
        raise KeyError(f"Unknown execution profile: {profile_id}")
    return EXECUTION_PROFILES[profile_id]
