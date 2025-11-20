# FILE: 10_10/models.py
"""
Unified Runtime Models (v10_10) — L1–L5 Typed Contracts
=======================================================

This is the v10_10 refactor of the v10_9 models module. It removes
legacy constructs (PlanObject, WorkflowState, MultiAgentCouncilResult,
ExecutionResult, etc.) and replaces them with a lean, strictly layered
set of typed contracts that align with the new L1–L5 architecture:

    • L1: Planning only (no LLM, no tools)
    • L2: Execution + cognition (LLM + tools)
    • L3: DAG orchestration + retries
    • L4: Deterministic state patching
    • L5: Deterministic safety gating

This module defines:

    1. Input & Config models
    2. RoutingHint (L1 → RoutingPolicy)
    3. Plans (StrategyPlan, RAGPlan, DraftingPlan, QAPlan, SafetyPlan)
    4. Results (StrategyResult, RAGResult, DraftingResult, QAResult, SafetyResult)
    5. Bundles (WorkflowPlanBundle, L2ResultBundle)
    6. ExecutionContext (DI container for runtime)

Design constraints:
    • Data-only — NO logic, NO I/O, NO LLM calls.
    • All cross-layer contracts use these Pydantic models.
    • All agents & orchestration code must be compatible with these types.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS
# ============================================================================


class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DraftingMode(str, Enum):
    BULLET_HEAVY = "bullet_heavy"
    MIXED_NARRATIVE = "mixed_narrative"
    HYBRID_EXEC_SUMMARY = "hybrid_exec_summary"
    BALANCED = "balanced"


# ============================================================================
# CORE INPUT MODELS
# ============================================================================


class JobInput(BaseModel):
    """
    Canonical job posting input (L0 → L1).
    """

    title: str
    role_type: str
    seniority: str
    posting_text: str
    requirements: List[str] = Field(default_factory=list)


class ResumeInput(BaseModel):
    """
    Canonical candidate resume input (L0 → L1).
    """

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    summary: Optional[str] = None
    experience_sections: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# WORKFLOW CONFIG
# ============================================================================


class WorkflowConfig(BaseModel):
    """
    User- and system-configurable knobs for a single workflow run.
    """

    # Cost / latency budgets
    cost_budget: float = 0.10
    latency_slo_ms: int = 3000
    safety_sensitivity: int = 3
    drafting_depth: int = 3

    # Tone / length preferences
    target_tone: str = "professional"
    target_total_tokens: int = 1800

    # RAG parameters
    rag_max_job_chunks: int = 8
    rag_max_resume_chunks: int = 10
    rag_max_hybrid_chunks: int = 4
    rag_allow_hyde: bool = True
    rag_require_hybrid: bool = False

    # Per-section token budgets
    section_max_tokens: Dict[str, int] = Field(
        default_factory=lambda: {
            "header": 256,
            "summary": 512,
            "experience": 1024,
            "skills": 512,
            "projects": 768,
        }
    )


# ============================================================================
# ROUTING HINT (L1 → RoutingPolicy)
# ============================================================================


class RoutingHint(BaseModel):
    """
    L1 → RoutingPolicy hint for model selection.
    """

    complexity: ComplexityLevel
    cost_budget: float
    latency_slo_ms: int
    safety_sensitivity: int
    drafting_depth: int


# ============================================================================
# STRATEGY PLAN + RESULT
# ============================================================================


class StrategyStep(BaseModel):
    """
    A single step in the high-level strategy plan.
    """

    id: str
    order: int
    description: str
    must_complete: bool = True
    can_parallelize: bool = False


class StrategyPlan(BaseModel):
    """
    L1 strategy plan: purely symbolic; L2 StrategyLLMAgent realizes it.
    """

    complexity: ComplexityLevel
    routing_hint: RoutingHint
    steps: List[StrategyStep]


class StrategyBranch(BaseModel):
    """
    A candidate strategy branch proposed by StrategyLLMAgent.
    """

    id: str
    text: str


class StrategyResult(BaseModel):
    """
    L2 strategy result: multiple branches + chosen branch ID.
    """

    branches: List[StrategyBranch]
    chosen_branch_id: str

    def get_chosen_branch_text(self) -> str:
        for b in self.branches:
            if b.id == self.chosen_branch_id:
                return b.text
        return ""


# ============================================================================
# RAG PLAN + RESULT
# ============================================================================


class RAGQueryHint(BaseModel):
    """
    A hint describing how RAG should retrieve evidence.
    """

    id: str
    description: str
    focus: str      # "job" | "resume" | "hybrid"
    max_chunks: int
    importance: float


class RAGPlan(BaseModel):
    """
    L1 RAG plan: RAGQueryHints + HYDE/hybrid toggles.
    """

    hints: List[RAGQueryHint]
    allow_hyde: bool = True
    require_hybrid: bool = False


class Evidence(BaseModel):
    """
    A single evidence item surfaced by RAG.
    """

    text: str
    score: float
    source: str


class RAGResult(BaseModel):
    """
    L2 RAG result: ranked evidence and HYDE flag.
    """

    evidence: List[Evidence] = Field(default_factory=list)
    used_hyde: bool = False


# ============================================================================
# DRAFTING PLAN + RESULT
# ============================================================================


class DraftSectionPlan(BaseModel):
    """
    Configuration for a single drafted resume section.
    """

    id: str
    title: str
    required: bool
    max_tokens: int
    priority: float


class DraftingPlan(BaseModel):
    """
    L1 drafting plan: sections, tone, and length.
    """

    mode: DraftingMode
    sections: List[DraftSectionPlan]
    target_tone: str
    target_length_tokens: int


class DraftSectionResult(BaseModel):
    """
    L2 drafted section result.
    """

    title: str
    outline: str
    text: str
    compliance_notes: str


class DraftingResult(BaseModel):
    """
    L2 drafting result: full per-section output.
    """

    sections: List[DraftSectionResult]
    mode: DraftingMode


# ============================================================================
# QA PLAN + RESULT
# ============================================================================


class QACheck(BaseModel):
    """
    L1 QA check definition.
    """

    id: str
    description: str
    category: str
    severity: int = 1


class QACheckResult(BaseModel):
    """
    L2 QA check result.
    """

    id: str
    passed: bool
    reason: str
    severity: int


class QAPlan(BaseModel):
    """
    L1 QA plan: list of semantic checks.
    """

    checks: List[QACheck]


class QAResult(BaseModel):
    """
    L2 QA result: list of check results.
    """

    checks: List[QACheckResult]


# ============================================================================
# SAFETY PLAN + RESULT
# ============================================================================


class SafetyCheck(BaseModel):
    """
    L1 safety check definition.
    """

    id: str
    description: str
    category: str
    severity: int = 1


class SafetyFinding(BaseModel):
    """
    L2 safety finding.
    """

    id: str
    category: str
    blocking: bool
    reason: str


class SafetyResult(BaseModel):
    """
    L2 safety evaluation result.
    """

    findings: List[SafetyFinding]


# ============================================================================
# WORKFLOW PLAN BUNDLE (L1 → L2)
# ============================================================================


class WorkflowPlanBundle(BaseModel):
    """
    L1 aggregate plan: everything L2 needs to execute a workflow.
    """

    strategy: StrategyPlan
    rag: RAGPlan
    drafting: DraftingPlan
    qa: QAPlan
    safety: SafetyPlan
    routing_hint: RoutingHint


# ============================================================================
# L2 EXECUTION RESULT BUNDLE (L2 → L3)
# ============================================================================


class L2ResultBundle(BaseModel):
    """
    L2 aggregate results: everything L3 needs to orchestrate.
    """

    strategy: StrategyResult
    rag: RAGResult
    drafting: DraftingResult
    qa: QAResult
    safety: SafetyResult


# ============================================================================
# EXECUTION CONTEXT (Runtime DI Container)
# ============================================================================


class ExecutionContext(BaseModel):
    """
    DI container for a single workflow run.

    Owned by runtime / L3, passed to L2 (and indirectly L2 agents).

    Fields:
        job                 — JobInput
        resume              — ResumeInput
        config              — WorkflowConfig
        routing_policy      — RoutingPolicy-like object
        sandbox_config      — SandboxConfig-like object
        prompt_registry     — PromptRegistry
        cache_manager       — PredictiveCacheManager or None
        meta_profile_snapshot — MetaProfileSnapshot or None
    """

    job: JobInput
    resume: ResumeInput
    config: WorkflowConfig

    routing_policy: Any
    sandbox_config: Any
    prompt_registry: Any
    cache_manager: Optional[Any] = None
    meta_profile_snapshot: Optional[Any] = None

    def span_context(self) -> Dict[str, Any]:
        """
        Minimal span context for observability.
        """
        return {
            "job_title": self.job.title,
            "role_type": self.job.role_type,
            "seniority": self.job.seniority,
        }
