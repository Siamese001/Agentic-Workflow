# FILE: 10_10/models.py
"""
Unified Runtime Models (v10_10) — L1–L5 Typed Contracts
=======================================================

This is the full v10_10 refactor of the v10_9 models module. It removes
all legacy v10_9 constructs (PlanObject, ExecutionResult, WorkflowState,
MultiAgentCouncilResult, HIL metadata, RouteTraceEntry, etc.) and replaces
them with a minimal, strictly layered set of typed contracts:

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
    6. ExecutionContext (DI container for L2/L3 runtime)

Everything here is *data only* — NO LLM calls, NO tool invocation,
NO orchestration logic, NO safety policy decisions.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from enum import Enum
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


# ======================================================================
# USER INPUTS
# ======================================================================

class JobInput(BaseModel):
    """
    Canonical job posting input (external → L1).
    """
    title: str
    role_type: str
    seniority: str
    posting_text: str
    requirements: List[str] = Field(default_factory=list)


class ResumeInput(BaseModel):
    """
    Canonical candidate resume input (external → L1).
    """
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    summary: Optional[str] = None
    experience_sections: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)


# ======================================================================
# WORKFLOW CONFIG
# ======================================================================

class WorkflowConfig(BaseModel):
    """
    System/user knobs for one workflow execution.
    """
    cost_budget: float = 0.10
    latency_slo_ms: int = 3000
    safety_sensitivity: int = 3
    drafting_depth: int = 3

    target_tone: str = "professional"
    target_total_tokens: int = 1800

    rag_max_job_chunks: int = 8
    rag_max_resume_chunks: int = 10
    rag_max_hybrid_chunks: int = 4
    rag_allow_hyde: bool = True
    rag_require_hybrid: bool = False

    section_max_tokens: Dict[str, int] = Field(
        default_factory=lambda: {
            "header": 256,
            "summary": 512,
            "experience": 1024,
            "skills": 512,
            "projects": 768,
        }
    )


# ======================================================================
# ROUTING HINT (L1 → L2 RoutingPolicy)
# ======================================================================

class RoutingHint(BaseModel):
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
    can_parallelize: bool = False


class StrategyPlan(BaseModel):
    complexity: ComplexityLevel
    routing_hint: RoutingHint
    steps: List[StrategyStep]


class RAGQueryHint(BaseModel):
    id: str
    description: str
    focus: str      # "job" | "resume" | "hybrid"
    max_chunks: int
    importance: float


class RAGPlan(BaseModel):
    hints: List[RAGQueryHint]
    allow_hyde: bool = True
    require_hybrid: bool = False


class DraftSectionPlan(BaseModel):
    id: str
    title: str
    required: bool
    max_tokens: int
    priority: float


class DraftingPlan(BaseModel):
    mode: DraftingMode
    sections: List[DraftSectionPlan]
    target_tone: str
    target_length_tokens: int


class QACheck(BaseModel):
    id: str
    description: str
    category: str
    severity: int = 1


class QAPlan(BaseModel):
    checks: List[QACheck]


class SafetyCheck(BaseModel):
    id: str
    description: str
    category: str
    severity: int = 1


class SafetyPlan(BaseModel):
    checks: List[SafetyCheck]


# ======================================================================
# L2 RESULTS (typed cognition/execution outputs)
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
    text: str
    score: float
    source: str


class RAGResult(BaseModel):
    evidence: List[Evidence] = Field(default_factory=list)
    used_hyde: bool = False


class DraftSectionResult(BaseModel):
    title: str
    outline: str
    text: str
    compliance_notes: str


class DraftingResult(BaseModel):
    sections: List[DraftSectionResult]
    mode: DraftingMode


class QACheckResult(BaseModel):
    id: str
    passed: bool
    reason: str
    severity: int


class QAResult(BaseModel):
    checks: List[QACheckResult]


class SafetyFinding(BaseModel):
    id: str
    category: str
    blocking: bool
    reason: str


class SafetyResult(BaseModel):
    findings: List[SafetyFinding]


# ======================================================================
# BUNDLES
# ======================================================================

class WorkflowPlanBundle(BaseModel):
    strategy: StrategyPlan
    rag: RAGPlan
    drafting: DraftingPlan
    qa: QAPlan
    safety: SafetyPlan
    routing_hint: RoutingHint


class L2ResultBundle(BaseModel):
    strategy: StrategyResult
    rag: RAGResult
    drafting: DraftingResult
    qa: QAResult
    safety: SafetyResult


# ======================================================================
# EXECUTION CONTEXT
# ======================================================================

class ExecutionContext(BaseModel):
    """
    DI container for a single workflow execution.
    Passed to all L2 agents & to L3 orchestrator.
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
        return {
            "job_title": self.job.title,
            "role_type": self.job.role_type,
            "seniority": self.job.seniority,
        }
