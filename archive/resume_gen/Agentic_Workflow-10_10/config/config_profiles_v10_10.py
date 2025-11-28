"""
Configures résumé analysis execution profiles for optimizing reasoning, retrieval, cost, and safety parameters.

Improves résumé processing by defining tailored analysis configurations for different job matching scenarios and use cases.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from core.models.models import (
    RetrievalConfig,
    ContextBudget,
    ReasoningMode,
    RedisCacheConfig,
    ChromaVectorConfig,
    GoogleGenAIConfig,
    BM25BackendConfig,
    ComplexityLevel,
)
from config.llm_profile import LLMProfile
from config.retrieval_profile import RetrievalProfile
from config.safety_profile import SafetyProfile
from config.context_profile import ContextProfile
from config.budget_profile import BudgetProfile


# ======================================================================
# ENUMS
# ======================================================================


class SafetyTier(str, Enum):
    """
    Defines safety validation levels for résumé processing.

    Ensures appropriate security measures for professional résumé improvement standards.
    """
    STANDARD = "standard"
    STRICT = "strict"
    RELAXED = "relaxed"
    DEBUG = "debug"


class ModelTier(str, Enum):
    """
    Specifies model performance tiers for résumé analysis.

    Balances cost and quality for optimal résumé enhancement processing.
    """
    CHEAP = "cheap"
    BALANCED = "balanced"
    PREMIUM = "premium"


class DAGMode(str, Enum):
    """
    Controls résumé processing workflow execution strategy.

    Optimizes speed and resource usage for comprehensive résumé improvement.
    """
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


# ======================================================================
# EXECUTION PROFILE SPEC
# ======================================================================


class ExecutionProfileSpec(BaseModel):
    """
    Configures comprehensive résumé analysis execution parameters.

    Optimizes processing strategy for different résumé improvement scenarios and requirements.
    """

    id: str
    description: str

    # Core behavior drivers
    reasoning_mode: ReasoningMode = ReasoningMode.COT
    safety_tier: SafetyTier = SafetyTier.STANDARD
    model_tier: ModelTier = ModelTier.BALANCED

    # Minimum complexity override (optional).
    min_complexity: ComplexityLevel | None = None

    # Budgets / SLOs
    max_cost_usd: float = 0.10
    max_latency_ms: int = 3000

    # RAG tuning (Phase 3: HYDE / RRF / council via RetrievalConfig)
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

    # ------------------------------
    # Phase-3 additions
    # ------------------------------

    # QA council size and mode
    qa_council_size: int = 1

    # Correction loop controls
    enable_correction_loop: bool = True
    max_corrections: int = 1

    # HYDE controls (RAG-level)
    rag_allow_hyde: bool = False
    hyde_model_tier: str = "balanced"

    # Routing telemetry mode
    routing_telemetry_mode: str = "simple"  # "simple", "full"


class ExecutionProfileV2(BaseModel):
    """
    Aggregates specialized profiles for comprehensive résumé processing.

    Combines LLM, retrieval, safety, context, and budget configurations for optimal résumé improvement.
    """

    llm: LLMProfile
    retrieval: RetrievalProfile
    safety: SafetyProfile
    context: ContextProfile
    budget: BudgetProfile


def build_execution_profile_v2(spec: ExecutionProfileSpec) -> ExecutionProfileV2:
    """
    Builds comprehensive résumé processing profile from specifications.

    Creates optimized configuration for different résumé improvement scenarios and requirements.
    """

    llm = LLMProfile(
        reasoning_mode=spec.reasoning_mode,
        model_tier=spec.model_tier.value if hasattr(spec.model_tier, "value") else str(spec.model_tier),
        max_cost_usd=spec.max_cost_usd,
        max_latency_ms=spec.max_latency_ms,
    )
    retrieval = RetrievalProfile(retrieval=spec.retrieval)
    safety = SafetyProfile(
        safety_tier=spec.safety_tier.value if hasattr(spec.safety_tier, "value") else str(spec.safety_tier),
        pii_detection_enabled=spec.pii_detection_enabled,
        policy_engine_enabled=spec.policy_engine_enabled,
    )
    context = ContextProfile(context_budget=spec.context_budget)
    budget = BudgetProfile(
        max_cost_usd=spec.max_cost_usd,
        max_latency_ms=spec.max_latency_ms,
    )

    return ExecutionProfileV2(
        llm=llm,
        retrieval=retrieval,
        safety=safety,
        context=context,
        budget=budget,
    )


# ======================================================================
# RAG RETRIEVAL CONFIG HELPERS (PHASE 3)
# ======================================================================


def _balanced_hybrid_retrieval(
    *,
    allow_hyde: bool,
    qa_council_size: int,
) -> RetrievalConfig:
    """
    Creates balanced retrieval configuration for résumé evidence gathering.

    Optimizes search strategy to find relevant data for comprehensive résumé improvement.
    """
    return RetrievalConfig(
        strategy="hybrid",
        use_rrf=True,
        max_hits=50,
        bm25_k1=1.2,
        bm25_b=0.75,
        bm25_backend=BM25BackendConfig(backend="rank_bm25", k1=1.2, b=0.75),
        rrf_weights=None,
        allow_hyde=allow_hyde,
        qa_council_size=qa_council_size,
        qa_council_mode="simple",
        # Default infra knobs: enable Redis + Chroma for rich RAG, allow
        # Google GenAI as an optional provider.
        redis_cache=RedisCacheConfig(enabled=True),
        chroma=ChromaVectorConfig(enabled=True, collection_name="resume_documents"),
        google_genai=GoogleGenAIConfig(enabled=True, model="gemini-pro"),
    )


def _cheap_bm25_retrieval() -> RetrievalConfig:
    """
    Creates cost-effective retrieval configuration for résumé processing.

    Provides efficient keyword-based search for budget-conscious résumé improvement.
    """
    return RetrievalConfig(
        strategy="bm25",
        use_rrf=False,
        max_hits=25,
        bm25_k1=1.0,
        bm25_b=0.75,
        bm25_backend=BM25BackendConfig(backend="rank_bm25", k1=1.0, b=0.75),
        rrf_weights=None,
        allow_hyde=False,
        qa_council_size=1,
        qa_council_mode="simple",
        # Cheap profile: enable Redis for basic caching; leave Chroma/Google
        # disabled by default.
        redis_cache=RedisCacheConfig(enabled=True),
    )


def _premium_dense_retrieval(
    *,
    allow_hyde: bool = False,
    qa_council_size: int = 1,
) -> RetrievalConfig:
    """
    Creates high-quality semantic retrieval for résumé enhancement.

    Optimizes conceptual search to find relevant evidence for comprehensive résumé improvement.
    """
    return RetrievalConfig(
        strategy="dense",
        use_rrf=False,
        max_hits=40,
        bm25_k1=1.2,
        bm25_b=0.75,
        bm25_backend=BM25BackendConfig(backend="rank_bm25", k1=1.2, b=0.75),
        rrf_weights=None,
        allow_hyde=allow_hyde,
        qa_council_size=qa_council_size,
        qa_council_mode="simple",
        # Debug / dense-oriented profile: enable Redis + Chroma; keep
        # Google GenAI available for experimentation.
        redis_cache=RedisCacheConfig(enabled=True),
        chroma=ChromaVectorConfig(enabled=True, collection_name="resume_documents"),
        google_genai=GoogleGenAIConfig(enabled=True, model="gemini-pro"),
    )


# ======================================================================
# PROFILE CATALOG
# ======================================================================

EXECUTION_PROFILES: Dict[str, ExecutionProfileSpec] = {
    # ---------------------------------------------------------
    # 🟩 High-Quality Resume Generation
    # ---------------------------------------------------------
    "RESUME_HIGH_QUALITY": ExecutionProfileSpec(
        id="RESUME_HIGH_QUALITY",
        description=(
            "High-quality resume with full RAG, HYDE, deep drafting, "
            "strict QA and safety."
        ),
        reasoning_mode=ReasoningMode.TOT,
        safety_tier=SafetyTier.STRICT,
        model_tier=ModelTier.PREMIUM,
        max_cost_usd=0.25,
        max_latency_ms=4500,
        retrieval=_balanced_hybrid_retrieval(
            allow_hyde=True,
            qa_council_size=3,
        ),
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
        qa_council_size=3,
        enable_correction_loop=True,
        max_corrections=2,
        rag_allow_hyde=True,
        hyde_model_tier="premium",
        routing_telemetry_mode="full",
    ),

    # ---------------------------------------------------------
    # 🟨 Faster Resume Generation (cheaper, shallower)
    # ---------------------------------------------------------
    "RESUME_FAST": ExecutionProfileSpec(
        id="RESUME_FAST",
        description=(
            "Faster resume generation with BM25-only RAG, shallower drafting "
            "and QA, standard safety."
        ),
        reasoning_mode=ReasoningMode.COT,
        safety_tier=SafetyTier.STANDARD,
        model_tier=ModelTier.BALANCED,
        max_cost_usd=0.10,
        max_latency_ms=2500,
        retrieval=_cheap_bm25_retrieval(),
        context_budget=ContextBudget(
            total_tokens=1400,
            planning_tokens=200,
            rag_tokens=600,
            drafting_tokens=400,
            qa_tokens=128,
            safety_tokens=128,
        ),
        drafting_depth=2,
        qa_depth="medium",
        dag_mode=DAGMode.SEQUENTIAL,
        allow_async=False,
        telemetry_granularity="standard",
        pii_detection_enabled=True,
        policy_engine_enabled=True,
        qa_council_size=1,
        enable_correction_loop=True,
        max_corrections=1,
        rag_allow_hyde=False,
        hyde_model_tier="balanced",
        routing_telemetry_mode="simple",
    ),

    # ---------------------------------------------------------
    # 🟨 Outreach / Quick Drafts
    # ---------------------------------------------------------
    "OUTREACH_QUICK": ExecutionProfileSpec(
        id="OUTREACH_QUICK",
        description=(
            "Quick outreach-style drafting with hybrid RAG but no HYDE, "
            "lighter QA and relaxed safety."
        ),
        reasoning_mode=ReasoningMode.REACT,
        safety_tier=SafetyTier.RELAXED,
        model_tier=ModelTier.CHEAP,
        max_cost_usd=0.05,
        max_latency_ms=2000,
        retrieval=_balanced_hybrid_retrieval(
            allow_hyde=False,
            qa_council_size=1,
        ),
        context_budget=ContextBudget(
            total_tokens=1200,
            planning_tokens=150,
            rag_tokens=500,
            drafting_tokens=350,
            qa_tokens=100,
            safety_tokens=100,
        ),
        drafting_depth=2,
        qa_depth="shallow",
        dag_mode=DAGMode.PARALLEL,
        allow_async=True,
        telemetry_granularity="minimal",
        pii_detection_enabled=True,
        policy_engine_enabled=False,
        qa_council_size=1,
        enable_correction_loop=False,
        max_corrections=0,
        rag_allow_hyde=False,
        hyde_model_tier="balanced",
        routing_telemetry_mode="simple",
    ),

    # ---------------------------------------------------------
    # 🟥 Debug / Diagnostic
    # ---------------------------------------------------------
    "DEBUG_DIAGNOSTIC": ExecutionProfileSpec(
        id="DEBUG_DIAGNOSTIC",
        description=(
            "Diagnostic profile: dense retrieval only, verbose telemetry, "
            "debug safety tier."
        ),
        reasoning_mode=ReasoningMode.REACT,
        safety_tier=SafetyTier.DEBUG,
        model_tier=ModelTier.CHEAP,
        max_cost_usd=1.00,
        max_latency_ms=10000,
        retrieval=_premium_dense_retrieval(allow_hyde=True, qa_council_size=1),
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
        qa_council_size=1,
        enable_correction_loop=True,
        max_corrections=3,
        rag_allow_hyde=True,
        hyde_model_tier="premium",
        routing_telemetry_mode="full",
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



