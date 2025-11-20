# FILE: 10_10/models.py
"""
Unified Runtime Models (v10_10 · Phase 0)
=========================================

Single, authoritative type system for the v10_10 workflow.

Goals of this revision (Phase 0):

    • Restore a *rich but coherent* model layer that can support:
        – L1–L5 layering
        – Workflow DAGs
        – RAG + fusion
        – Safety & policy
        – Telemetry & cost
        – Prompt governance
    • Preserve v10_10 public contracts that are already referenced by:
        – l1.py, l2.py, l3.py, l4.py, l5.py
        – cognitive_agents.py
        – retrieval.py, ranking.py
        – simulation.py, golden_eval.py, run_batch_v10_10.py
    • Introduce new types required by the G1–G37 gap table without
      *yet* wiring every one of them through the rest of the codebase.
      Wiring will happen in later phases.

This file is intentionally a single “source of truth” module (Option A).

Conventions
-----------
    • All runtime data models use Pydantic BaseModel for:
        – validation,
        – `.model_dump()` compatibility,
        – easy JSON serialization.
    • Enums are string-based for stable logging and telemetry.
    • New models are additive and do not remove any v10_10 symbols:
        – ComplexityLevel, DraftingMode
        – JobInput, ResumeInput, WorkflowConfig, RoutingHint
        – StrategyStep, StrategyPlan, RAGQueryHint, RAGPlan
        – DraftSectionPlan, DraftingPlan, QACheck, QAPlan
        – SafetyCheck, SafetyPlan
        – StrategyBranch, StrategyResult, Evidence, RAGResult
        – DraftSectionResult, DraftingResult, QACheckResult, QAResult
        – SafetyFinding, SafetyResult
        – WorkflowPlanBundle, L2ResultBundle, ExecutionContext

Later phases (L1–L5 refactors, RAG evolution, safety, telemetry) will
*use* these types; Phase 0 only defines them.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Mapping

from pydantic import BaseModel, Field


# ======================================================================
# ENUMS
# ======================================================================


class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DraftingMode(str, Enum):
    BULLET_HEAVY = "bullet_heavy"
    MIXED_NARRATIVE = "mixed_narrative"
    HYBRID_EXEC_SUMMARY = "hybrid_exec_summary"
    BALANCED = "balanced"


class ReasoningMode(str, Enum):
    """
    Reasoning strategy used for planning / cognition.

    This will be consumed by a future ReasoningSelector in L1/meta-layer.
    """

    DIRECT = "direct"
    COT = "chain_of_thought"
    TOT = "tree_of_thought"
    REACT = "react"


# ======================================================================
# USER INPUTS (EXTERNAL → L1)
# ======================================================================


class JobInput(BaseModel):
    """
    Canonical job posting input (external → L1).

    NOTE: Field names are chosen to be compatible with main_v10_10._build_job_input_from_state.
    """

    title: str
    role_type: str
    seniority: str
    posting_text: str
    requirements: List[str] = Field(default_factory=list)


class ResumeInput(BaseModel):
    """
    Canonical resume input (external → L1).

    NOTE: Field names are chosen to be compatible with
    main_v10_10._build_resume_input_from_state.
    """

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None

    summary: Optional[str] = None
    experience_sections: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[Any] = Field(default_factory=list)
    projects: List[Any] = Field(default_factory=list)


# ======================================================================
# CONFIGURATION & PROFILES
# ======================================================================


class WorkflowConfig(BaseModel):
    """
    Execution configuration for a single workflow.

    Existing v10_10 callsites expect:
        • cost_budget
        • latency_slo_ms
        • safety_sensitivity
        • drafting_depth
        • target_tone
        • target_total_tokens

    L1 also expects RAG-specific fields, which we provide here with defaults.
    """

    # Global budgets / SLOs
    cost_budget: float = 0.10
    latency_slo_ms: int = 3000
    safety_sensitivity: int = 3
    drafting_depth: int = 3

    # Style / content
    target_tone: str = "professional"
    target_total_tokens: int = 1800

    # RAG-related knobs (used in l1.py)
    rag_max_job_chunks: int = 8
    rag_max_resume_chunks: int = 8
    rag_max_hybrid_chunks: int = 12
    rag_allow_hyde: bool = False
    rag_require_hybrid: bool = False


class ExecutionProfile(BaseModel):
    """
    High-level execution profile (to be mapped from config/meta-profile).

    This is a forward-looking type for G1–G3 and cost/safety tuning.
    """

    id: str
    description: str
    reasoning_mode: ReasoningMode = ReasoningMode.COT
    target_model_tier: str = "balanced"  # e.g., "cheap", "balanced", "premium"
    max_cost_usd: float = 0.10
    max_latency_ms: int = 3000
    safety_tier: str = "standard"  # e.g., "standard", "strict", "debug"


class ContextBudget(BaseModel):
    """
    Token allocation across major context components.

    Used by future ContextBudgetManager for G27–G28.
    """

    total_tokens: int = 1800
    planning_tokens: int = 256
    rag_tokens: int = 800
    drafting_tokens: int = 600
    qa_tokens: int = 256
    safety_tokens: int = 128


# ======================================================================
# ROUTING HINTS
# ======================================================================


class RoutingHint(BaseModel):
    """
    Lightweight hint from L1 planning to downstream layers.

    Existing v10_10 L1 code constructs this with:
        • complexity
        • cost_budget
        • latency_slo_ms
        • safety_sensitivity
        • drafting_depth
    """

    complexity: ComplexityLevel
    cost_budget: float
    latency_slo_ms: int
    safety_sensitivity: int
    drafting_depth: int


# ======================================================================
# L1 PLANS
# ======================================================================


class StrategyStep(BaseModel):
    id: str
    order: int
    description: str
    must_complete: bool = True


class StrategyPlan(BaseModel):
    """
    High-level strategy plan for the workflow.

    • steps     – ordered list of strategy steps for L2 execution.
    • complexity – ComplexityLevel chosen by L1 for downstream use.
    """

    steps: List[StrategyStep]
    complexity: ComplexityLevel


class RAGQueryHint(BaseModel):
    """
    Hint for a single retrieval query.

    Used in l1.py to build the RAGPlan.
    """

    id: str
    description: str
    focus: str  # "job" | "resume" | "hybrid"
    max_chunks: int
    importance: float = 1.0


class RAGPlan(BaseModel):
    """
    Plan for RAG: query hints and configuration flags.
    """

    hints: List[RAGQueryHint] = Field(default_factory=list)
    allow_hyde: bool = False
    require_hybrid: bool = False


class DraftSectionPlan(BaseModel):
    """
    Desired structure of a single drafted section (title, summary, etc.).
    """

    id: str
    title: str
    required: bool = True
    max_tokens: int = 512
    priority: float = 1.0


class DraftingPlan(BaseModel):
    """
    Drafting plan describing which sections to create and how.

    Used by l1.py and cognitive_agents.DraftingGuild.
    """

    sections: List[DraftSectionPlan] = Field(default_factory=list)
    mode: DraftingMode = DraftingMode.BALANCED
    target_tone: str = "professional"


class QACheck(BaseModel):
    """
    Single QA check (e.g., grammar, alignment, hallucination risk).
    """

    id: str
    description: str
    severity: int = 3  # 1–5
    enabled: bool = True


class QAPlan(BaseModel):
    """
    QA plan describing which checks to run.
    """

    checks: List[QACheck] = Field(default_factory=list)


class SafetyCheck(BaseModel):
    """
    Single safety/policy check (e.g., PII, policy, toxicity).
    """

    id: str
    description: str
    category: str = "policy"
    enabled: bool = True


class SafetyPlan(BaseModel):
    """
    Safety plan describing which checks to run.
    """

    checks: List[SafetyCheck] = Field(default_factory=list)


class WorkflowPlanBundle(BaseModel):
    """
    Aggregated output of L1 planning.

    This is what build_workflow_plan_bundle() returns.
    """

    strategy: StrategyPlan
    rag: RAGPlan
    drafting: DraftingPlan
    qa: QAPlan
    safety: SafetyPlan

    routing_hint: RoutingHint


# ======================================================================
# L2 RESULTS (Cognition + Execution)
# ======================================================================


class StrategyBranch(BaseModel):
    id: str
    text: str


class StrategyResult(BaseModel):
    branches: List[StrategyBranch]
    chosen_branch_id: str

    def get_chosen_branch_text(self) -> str:
        for b in self.branches:
            if b.id == self.chosen_branch_id:
                return b.text
        return ""


class Evidence(BaseModel):
    """
    Single evidence item produced by retrieval + ranking.

    • text   – evidence text snippet.
    • score  – ranking score (higher = better).
    • source – which retriever/pipeline produced this.
    """

    text: str
    score: float
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGResult(BaseModel):
    evidence: List[Evidence] = Field(default_factory=list)
    used_hyde: bool = False


class DraftSectionResult(BaseModel):
    """
    Final drafted section as returned by the DraftingGuild.

    Fields are chosen to match current cognitive_agents.py usage.
    """

    title: str
    outline: str = ""
    text: str = ""
    compliance_notes: str = ""


class DraftingResult(BaseModel):
    sections: List[DraftSectionResult] = Field(default_factory=list)
    mode: DraftingMode = DraftingMode.BALANCED


class QACheckResult(BaseModel):
    check_id: str
    status: str  # "ok", "warning", "error", "pending"
    message: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)


class QAResult(BaseModel):
    """
    Aggregated QA results for a workflow run.
    """

    findings: List[QACheckResult] = Field(default_factory=list)
    summary: str = ""


class SafetyFinding(BaseModel):
    check_id: str
    category: str
    status: str  # "ok", "blocked", "warning"
    message: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)


class SafetyResult(BaseModel):
    """
    Aggregated safety results for a workflow run.
    """

    findings: List[SafetyFinding] = Field(default_factory=list)
    overall_status: str = "unknown"  # "ok", "blocked", "warning"


class L2ResultBundle(BaseModel):
    """
    Unified L2 output bundle consumed by L3/L4/L5.

    This preserves the existing v10_10 symbol and semantics.
    """

    strategy: StrategyResult
    rag: RAGResult
    drafting: DraftingResult
    qa: QAResult
    safety: SafetyResult


# ======================================================================
# WORKFLOW STATE & EVENTS (NEW FOR G34–G36)
# ======================================================================


class WorkflowState(BaseModel):
    """
    Canonical in-memory state for a workflow.

    This wraps the raw dict used by main_v10_10 and L4, but provides
    structured access where needed. For now, it keeps a generic payload
    to preserve compatibility with existing state usage.
    """

    workflow_id: str = "workflow_v10_10"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    payload: Dict[str, Any] = Field(default_factory=dict)


class StateTransitionEvent(BaseModel):
    """
    Immutable record of a state transition.

    L4 will emit these when applying patches.
    """

    event_id: str
    workflow_id: str
    kind: str  # e.g., "drafting_completed", "qa_updated"
    before: Dict[str, Any]
    after: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# TELEMETRY & COST (NEW FOR G15–G17, G20)
# ======================================================================


class TelemetryEvent(BaseModel):
    """
    Structured telemetry event emitted by observability.py.
    """

    name: str
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    workflow_id: Optional[str] = None
    ts_ms: Optional[int] = None

    attributes: Dict[str, Any] = Field(default_factory=dict)


class CostSnapshot(BaseModel):
    """
    Cost accounting snapshot for a workflow or span.
    """

    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float = 0.0


class PolicyDecisionEvent(BaseModel):
    """
    Structured record of a safety/policy decision (L5).
    """

    decision: str  # "allow", "block", "soft_block", "flag"
    reason: str
    workflow_id: Optional[str] = None
    check_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# PROMPT & VERSIONING (NEW FOR G24–G26)
# ======================================================================


class PromptVersion(BaseModel):
    """
    Semantic versioning for prompts (e.g., v1.0.0).
    """

    major: int = 1
    minor: int = 0
    patch: int = 0

    def as_str(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class PromptDefinition(BaseModel):
    """
    Single prompt definition in the prompt registry.

    This is referenced (indirectly) by cognitive agents and L1.
    """

    id: str
    version: PromptVersion = Field(default_factory=PromptVersion)
    role: str  # e.g., "system", "user"
    tags: List[str] = Field(default_factory=list)
    template: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# RAG CONFIG (NEW FOR G11–G14)
# ======================================================================


class RetrievalConfig(BaseModel):
    """
    Configuration for RAG retrieval strategy.

    This will be used by retrieval.py / ranking.py in later phases.
    """

    strategy: str = "hybrid"  # e.g., "bm25", "dense", "hybrid"
    use_rrf: bool = True
    max_hits: int = 50
    bm25_k1: float = 1.2
    bm25_b: float = 0.75


# ======================================================================
# EXECUTION CONTEXT (PRESERVED, EXTENDED)
# ======================================================================


class ExecutionContext(BaseModel):
    """
    DI container for a single workflow execution.

    Passed to all L2 agents & to the L3 orchestrator in v10_10.
    """

    job: JobInput
    resume: ResumeInput
    config: WorkflowConfig

    # Runtime wiring (kept generic to avoid circular imports)
    routing_policy: Any
    sandbox_config: Any
    prompt_registry: Any

    cache_manager: Optional[Any] = None
    meta_profile_snapshot: Optional[Any] = None

    # Optional telemetry & cost info (Phase 0: unused, Phase N: wired)
    telemetry_context: Dict[str, Any] = Field(default_factory=dict)
    cost_snapshot: Optional[CostSnapshot] = None

    def span_context(self) -> Dict[str, Any]:
        """
        Minimal span context used by observability.start_span().
        """
        return {
            "job_title": self.job.title,
            "role_type": self.job.role_type,
            "seniority": self.job.seniority,
        }
