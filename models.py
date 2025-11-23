# FILE: models.py
"""
Unified Runtime Models (v10_10 · Phase 3 — FINAL)
=================================================

This file defines all structured dataclasses and Pydantic models
used throughout the v10_10 agentic runtime:

    • Core workflow dataclasses
    • Plans / Results (Strategy, RAG, Drafting, QA, Safety)
    • RetrievalConfig
    • PromptDefinition / PromptVersion
    • ExecutionProfile
    • Telemetry models (Phase 3 typed events)
    • CostSnapshot
    • PolicyDecisionEvent
    • Skill / Domain classifier results
    • CouncilVote + CorrectionLoopState (Phase-3 DAG)

Design constraints:

    1. This module is *data-only* (no I/O, no business logic).
    2. Models are intentionally verbose and explicit.
    3. All cross-layer contracts must be defined here (or imported here).
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ======================================================================
# ENUMS USED ACROSS MODELS
# ======================================================================


class ComplexityLevel(str, Enum):
    """Coarse-grained complexity buckets for planning/routing."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DraftingMode(str, Enum):
    """Drafting style for downstream drafting agents."""

    BULLET_HEAVY = "bullet_heavy"
    BALANCED = "balanced"
    NARRATIVE = "narrative"


class ReasoningMode(str, Enum):
    """Reasoning mode hint for L2 cognitive agents."""

    # Historical/short name kept for compatibility with config profiles.
    COT = "cot"
    CHAIN_OF_THOUGHT = "cot"
    TOT = "tot"
    REACT = "react"


# ======================================================================
# BASIC STRUCTURES (JOB / RESUME)
# ======================================================================


class JobDescription(BaseModel):
    id: str
    title: str
    company: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResumeProfile(BaseModel):
    id: str
    name: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    raw_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JobInput(BaseModel):
    """L1-facing view of job inputs used for planning.

    This is intentionally light-weight and mirrors the fields accessed in l1.
    """

    title: Optional[str] = None
    role_type: Optional[str] = None
    seniority: Optional[str] = None
    posting_text: Optional[str] = None
    requirements: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class ResumeInput(BaseModel):
    """L1-facing view of resume inputs used for planning."""

    summary: Optional[str] = None
    experience_sections: Optional[List[Dict[str, Any]]] = None
    skills: Optional[List[Any]] = None
    projects: Optional[List[Dict[str, Any]]] = None


@dataclass
class RuntimeInputs:
    job: JobInput
    resume: ResumeInput
    config: "WorkflowConfig"
    prompt_registry: Any
    cache_manager: Any | None = None


class WorkflowConfig(BaseModel):
    """Workflow configuration knobs required at L1 planning time."""

    profile_id: str = "RESUME_FAST"

    # RAG configuration used by L1
    rag_max_job_chunks: int = 8
    rag_max_resume_chunks: int = 8
    rag_max_hybrid_chunks: int = 8
    rag_allow_hyde: bool = False

    # Drafting configuration used by L1
    drafting_experience_max_tokens: int = 1024

    # Depth / complexity hints for drafting and routing tests
    drafting_depth: int = 1


# ======================================================================
# WORKFLOW STATE + PATCHES
# ======================================================================


class WorkflowState(BaseModel):
    """
    Canonical workflow state.

    This is the single source of truth for all cross-layer state.

    L4 is the *only* layer allowed to mutate instances of this model;
    other layers must work with copies or immutable views.
    """

    workflow_id: str
    job: JobDescription
    resume: ResumeProfile

    # High-level artifacts
    strategy_notes: Optional[str] = None
    rag_context: Optional[str] = None
    draft_text: Optional[str] = None
    qa_findings_summary: Optional[str] = None
    safety_summary: Optional[str] = None

    # Arbitrary extensions
    slots: Dict[str, Any] = Field(default_factory=dict)


# Events and rollback artifacts used by L4


class StateTransitionEvent(BaseModel):
    """Typed event describing a single WorkflowState transition.

    For v10_10 tests we only need a minimal schema: an event id and a
    patch payload (dict or WorkflowStatePatch-like object).
    """

    event_id: str
    patch: Any = None


class Checkpoint(BaseModel):
    """Immutable snapshot wrapper around WorkflowState used for rollback."""

    snapshot: WorkflowState


class RollbackRequest(BaseModel):
    checkpoint: Optional[Checkpoint] = None


class RollbackResult(BaseModel):
    ok: bool
    reason: str
    state_after: WorkflowState


class WorkflowStatePatch(BaseModel):
    """
    A typed, partial update to WorkflowState.

    L2/L3 produce patches; L4 applies them.
    """

    strategy_notes: Optional[str] = None
    rag_context: Optional[str] = None
    draft_text: Optional[str] = None
    qa_findings_summary: Optional[str] = None
    safety_summary: Optional[str] = None

    # Arbitrary dynamic slots
    slots: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# EXECUTION CONTEXT + TRANSITION EVENTS
# ======================================================================


class ExecutionContext(BaseModel):
    """
    ExecutionContext is a runtime snapshot passed down the stack.

    In v10_10 it intentionally carries both:

        • Domain inputs needed by L2/L3 orchestration (job, resume, config,
          prompt registry, cache manager).
        • Runtime configuration and META-layer hints (retrieval config,
          routing policy, sandbox config, meta-profile snapshot, cost).

    It is treated as immutable by callers.
    """

    # Domain inputs (L1/L2-facing)
    job: JobInput
    resume: ResumeInput
    config: WorkflowConfig
    prompt_registry: Any
    cache_manager: Any = None

    # High-level workflow identity
    workflow_id: str = ""
    profile_name: str = ""

    # Runtime configuration / META-layer hints
    retrieval: Optional["RetrievalConfig"] = None  # type: ignore[name-defined]
    routing_policy: Any = None
    sandbox_config: Any = None
    meta_profile_snapshot: Any = None
    meta_profile: Any = None

    # Telemetry / cost containers
    cost_snapshot: Optional["CostSnapshot"] = None

    def span_context(self) -> Dict[str, Any]:
        return {}


class ContextBudget(BaseModel):
    """Context budgeting hints used by profiles and prompt builder.

    This mirrors the fields populated in config_profiles_v10_10 and
    read in prompt_builder._build_context_budget_hints_from_plan.
    """

    total_tokens: int = 0
    planning_tokens: int = 0
    rag_tokens: int = 0
    drafting_tokens: int = 0
    qa_tokens: int = 0
    safety_tokens: int = 0


class ExecutionProfile(BaseModel):
    """Flattened execution profile used for routing hints.

    L1 maps a config-layer ExecutionProfileSpec into this simpler
    structure, which is then carried inside RoutingHint and inspected
    by routing / meta layers.
    """

    name: str
    description: str
    retrieval: "RetrievalConfig"  # type: ignore[name-defined]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RoutingHint(BaseModel):
    """Lightweight routing hint passed from L1 into L2/L3.

    Carries complexity / reasoning mode plus an ExecutionProfile and
    arbitrary metadata derived from the MetaProfileSnapshot.
    """

    complexity: ComplexityLevel
    reasoning_mode: ReasoningMode
    execution_profile: ExecutionProfile
    meta: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# L2 RESULT + FINDING MODELS
# ======================================================================


class StrategyBranch(BaseModel):
    id: str
    description: str
    weight: float = 1.0


class StrategyResult(BaseModel):
    branches: List[StrategyBranch]
    chosen_branch_id: Optional[str] = None


class DraftSection(BaseModel):
    id: str
    title: str
    body: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def text(self) -> str:
        """Compatibility alias for body used by older tests/code paths."""

        return self.body


class DraftingResult(BaseModel):
    sections: List[DraftSection]


class QAFinding(BaseModel):
    id: str
    category: str
    severity: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QACheckResult(BaseModel):
    """Result of running a single QA check.

    This groups one or more QAFinding objects under a check id so that
    L2 and downstream layers can reason about per-check outcomes.
    """

    check_id: str
    findings: List[QAFinding] = Field(default_factory=list)


class QAResult(BaseModel):
    findings: List[QAFinding]


class SafetyFinding(BaseModel):
    check_id: str
    category: str
    severity: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class SafetyResult(BaseModel):
    findings: List[SafetyFinding]


class L2ResultBundle(BaseModel):
    strategy: StrategyResult
    rag: "RAGResult"
    drafting: DraftingResult
    qa: QAResult
    safety: SafetyResult

    @classmethod
    def empty_with_error(cls, msg: str):
        return cls(
            strategy=StrategyResult(branches=[], chosen_branch_id=None),
            rag=RAGResult(evidence=[], used_hyde=False),
            drafting=DraftingResult(sections=[]),
            qa=QAResult(findings=[]),
            safety=SafetyResult(
                findings=[
                    SafetyFinding(
                        check_id="internal_error",
                        category="internal",
                        severity="high",
                        message=msg,
                        details={},
                    )
                ]
            ),
        )


class SafetyEnforcementVerdict(BaseModel):
    """Normalized L5 safety verdict used by SafetyPolicy evaluation."""

    verdict: str  # "pass" | "warn" | "block"
    reason: str


class SafetyPolicy(BaseModel):
    """Configuration for L5 safety enforcement.

    Only the fields accessed in l5.py are modeled here.
    """

    allow_generation: bool = True
    allow_pii: bool = True
    disallowed_categories: List[str] = Field(default_factory=list)


# ======================================================================
# TELEMETRY MODELS (Phase-3)
# ======================================================================


class TelemetryEvent(BaseModel):
    name: str
    ts_ms: Optional[int] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    workflow_id: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class CostSnapshot(BaseModel):
    """Aggregated token and cost accounting for a workflow run.

    This is intentionally generic so that different cost accounting
    implementations can populate it without changing the contract
    exposed to observability and evaluation layers.
    """

    total_tokens: int = 0
    total_cost_usd: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)


class RetrievalAttemptEvent(TelemetryEvent):
    method: str
    query: str


class RetrievalResultEvent(TelemetryEvent):
    method: str
    hit_count: int
    max_hits: int


class RankingEvent(TelemetryEvent):
    stage: str
    input_count: int
    output_count: int
    details: Dict[str, Any] = Field(default_factory=dict)


class RetrievalSuccessEvent(TelemetryEvent):
    """Typed retrieval success event (Phase-3 compatibility shim).

    This is a thin wrapper over RetrievalResultEvent semantics so that
    existing telemetry surfaces importing RetrievalSuccessEvent continue
    to function without behavior changes.
    """

    method: str
    hit_count: int
    max_hits: int


class RetrievalFailureEvent(TelemetryEvent):
    """Typed retrieval failure event (Phase-3 compatibility shim)."""

    method: str
    reason: str


class RoutingDecisionEvent(TelemetryEvent):
    agent_id: str
    provider: str
    model_name: str
    reason: Optional[str] = None


class AgentMessage(BaseModel):
    """Typed message used by multi-agent META layer.

    Mirrors the fields used in multi_agent.MultiAgentCoordinator.
    """

    sender: str
    recipient: str
    content: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MultiAgentVote(BaseModel):
    """Individual council member vote (META-only)."""

    agent_id: str
    decision: str
    confidence: float
    rationale: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class MultiAgentCouncilResult(BaseModel):
    """Aggregated council result used by routing/evaluation layers."""

    votes: List[MultiAgentVote] = Field(default_factory=list)
    aggregated_decision: str
    aggregated_confidence: float
    rationale: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CorrectionEvent(TelemetryEvent):
    """
    Emitted when the workflow graph performs a correction loop
    (e.g., re-running RAG or QA).
    """

    node: str
    iteration: int
    reason: str


# ======================================================================
# PROMPT MODELS
# ======================================================================


class PromptVersion(BaseModel):
    major: int
    minor: int
    patch: int

    def as_str(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class PromptDefinition(BaseModel):
    """Canonical prompt definition stored in the prompt registry.

    This mirrors the shape expected by prompt_system_v10_10:

        • id: stable identifier for the prompt
        • text: template body
        • version: PromptVersion
        • metadata: arbitrary governance/ACL metadata
    """

    id: str
    text: str
    version: PromptVersion
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PolicyDecisionEvent(BaseModel):
    """Final L5 enforcement decision event.

    This matches the shape constructed in l5.run_l5: a simple verdict,
    human-readable reason, and the list of SafetyFinding objects that
    informed the decision.
    """

    verdict: str
    reason: str
    findings: List["SafetyFinding"] = Field(default_factory=list)


# ======================================================================
# RESILIENCE MODELS (typed error hierarchy + decisions)
# ======================================================================


class ResilienceError(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class TransientError(ResilienceError):
    """Transient, retryable error (network, provider, tool flakiness)."""


class PermanentError(ResilienceError):
    """Non-retryable error (validation, safety, logical failures)."""


class RetryExhaustedError(ResilienceError):
    """Raised when max retry attempts are exceeded for a transient error."""

    attempts: int


class CircuitBreakerOpenError(ResilienceError):
    """Error descriptor used when a circuit breaker is open."""

    breaker_name: str


class ToolInvocationError(Exception):
    """Historical tool invocation error type (compatibility shim)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CircuitBreakerState(BaseModel):
    backoff_ms: int = 0
    breaker_state: Optional[str] = None
    error: Optional[ResilienceError] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SeniorityClassifierResult(BaseModel):
    """Deterministic classification of domain / industry (non-LLM)."""

    labels: List[str] = Field(default_factory=list)
    primary_label: Optional[str] = None
    confidence: float = 0.0
    features: Dict[str, Any] = Field(default_factory=dict)


class ProfileInferenceResult(BaseModel):
    """Aggregated profile inference used by L1 and meta_profile.

    Holds seniority/domain/skills classification plus the overall
    ComplexityLevel estimate for the workflow.
    """

    seniority: Optional[SeniorityClassifierResult] = None
    domain: Optional[DomainClassifierResult] = None
    skills: Optional[SkillClusterResult] = None
    complexity: Optional[ComplexityLevel] = None


class DomainClassifierResult(BaseModel):
    """Deterministic classification of job/resume domain (non-LLM)."""

    labels: List[str] = Field(default_factory=list)
    primary_label: Optional[str] = None
    confidence: float = 0.0
    features: Dict[str, Any] = Field(default_factory=dict)


class SkillClassifierResult(BaseModel):
    """Deterministic classification of user skills (non-LLM)."""

    labels: List[str] = Field(default_factory=list)
    primary_label: Optional[str] = None
    confidence: float = 0.0
    features: Dict[str, Any] = Field(default_factory=dict)


class SkillClusterResult(BaseModel):
    """Clustered skill labels inferred from job/resume text (L1 profile inference)."""

    labels: List[str] = Field(default_factory=list)
    primary_label: Optional[str] = None
    confidence: float = 0.0
    features: Dict[str, Any] = Field(default_factory=dict)


class ResilienceDecision(BaseModel):
    """Normalized arbitration decision outcome used by orchestration/safety."""

    action: str
    reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CouncilVote(BaseModel):
    """Aggregated vote from a council / committee of agents."""

    members: int
    selected_id: Optional[str] = None
    scores: Dict[str, float] = Field(default_factory=dict)
    ties: List[str] = Field(default_factory=list)
    reason: Optional[str] = None


class StrategyStep(BaseModel):
    """Single step in a high-level strategy plan (L1 output)."""

    id: str
    order: int
    description: str


class StrategyPlan(BaseModel):
    """L1 strategy plan consumed by L2/L3 and prompt_builder."""

    steps: List[StrategyStep] = Field(default_factory=list)
    complexity: ComplexityLevel = ComplexityLevel.MEDIUM


class DraftSectionPlan(BaseModel):
    """Planned drafting section (e.g., Summary, Experience, Skills)."""

    id: str
    title: str
    required: bool = True
    max_tokens: int = 256
    priority: float = 1.0


class DraftingPlan(BaseModel):
    """Drafting plan describing which sections to generate."""

    sections: List[DraftSectionPlan] = Field(default_factory=list)
    mode: DraftingMode = DraftingMode.BALANCED


class QACheck(BaseModel):
    """Single QA check definition used in QAPlan."""

    id: str
    description: str
    severity: str


class QAPlan(BaseModel):
    """QA plan describing which checks to run and at what depth."""

    checks: List[QACheck] = Field(default_factory=list)
    depth: Any = "1"


class SafetyCheck(BaseModel):
    """Single safety check definition used in SafetyPlan."""

    id: str
    description: str
    severity: str


class SafetyPlan(BaseModel):
    checks: List[SafetyCheck] = Field(default_factory=list)
    tier: Any | None = None


class WorkflowPlanBundle(BaseModel):
    """Bundle of all L1 plans passed into L2/L3 orchestration."""

    strategy: "StrategyPlan"
    rag: RAGPlan
    drafting: "DraftingPlan"
    qa: "QAPlan"
    safety: SafetyPlan
    reason: Optional[str] = None


class CorrectionLoopState(BaseModel):
    """Summary of a workflow's correction loop over the DAG."""

    iteration: int = 0
    max_iterations: int = 0
    surfaces_triggered: List[str] = Field(default_factory=list)
    last_signal: Optional[str] = None
    terminated_reason: Optional[str] = None


# ======================================================================
# RETRIEVAL MODELS
# ======================================================================


class Evidence(BaseModel):
    """Canonical evidence item used by retrieval and RAG."""

    text: str
    score: float
    source: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RedisCacheConfig(BaseModel):
    """Configuration for Redis-backed exact / semantic caching."""

    enabled: bool = False
    url: Optional[str] = None
    ttl_s: int = 3600


class ChromaVectorConfig(BaseModel):
    """Configuration for ChromaDB-backed vector store / semantic cache."""

    enabled: bool = False
    collection_name: Optional[str] = None
    persist_directory: Optional[str] = None


class BM25BackendConfig(BaseModel):
    """Configuration for BM25 backend selection and tuning."""

    backend: str = "rank_bm25"
    k1: float = 1.2
    b: float = 0.75


class GoogleGenAIConfig(BaseModel):
    """Configuration for Google Generative AI (Gemini) usage."""

    enabled: bool = False
    model: Optional[str] = None
    api_key_env: str = "GOOGLE_API_KEY"


class RetrievalConfig(BaseModel):
    """Retrieval configuration knobs used by META/L2.

    This remains minimal but now also exposes RRF-related controls used by
    META ranking/fusion helpers.
    """

    strategy: str = "hybrid"
    max_hits: int = 16

    # Reciprocal Rank Fusion controls (optional; safe defaults preserved).
    # When rrf_weights is None or empty, uniform weights are used.
    rrf_k: int = 60
    rrf_weights: Optional[List[float]] = None
    use_rrf: bool = True


class RAGQueryHint(BaseModel):
    """Hint describing an individual RAG retrieval surface.

    Used by L1 planning to describe job/resume/hybrid retrieval
    surfaces; consumed by downstream retrieval/ranking logic.
    """

    id: str
    description: str
    focus: str
    max_chunks: int
    importance: float = 1.0

    # BM25 parameters (for built-in ranking) and backend selection.
    bm25_k1: float = 1.2
    bm25_b: float = 0.75
    bm25_backend: BM25BackendConfig = Field(default_factory=BM25BackendConfig)

    # Weighted RRF fusion (per-group weights for RRF). Registry may pass None.
    rrf_weights: Optional[List[float]] = None

    # Whether to use RRF-based fusion in RAG ranking helpers
    use_rrf: bool = True

    # Phase-3 extras used by registry/routing
    allow_hyde: bool = False
    qa_council_size: int = 1
    qa_council_mode: str = "simple"

    # Infrastructure knobs restored from v10_7 capabilities.
    redis_cache: RedisCacheConfig = Field(default_factory=RedisCacheConfig)
    chroma: ChromaVectorConfig = Field(default_factory=ChromaVectorConfig)
    google_genai: GoogleGenAIConfig = Field(default_factory=GoogleGenAIConfig)


class RAGPlan(BaseModel):
    """Minimal RAG plan model used by ranking/build_rag_result.

    This is intentionally lightweight and only encodes the fields used
    in ranking.py so that tests and helpers depending on RAGPlan can
    construct a compatible object.
    """

    strategy: str = "hybrid"
    max_hits: int = 16


class RAGResult(BaseModel):
    """Result of RAG evidence fusion and ranking."""

    evidence: List[Evidence]
    used_hyde: bool = False
