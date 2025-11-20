# FILE: 10_10/models.py
"""
Typed Data Models for Agentic Workflow v10_10
=============================================

This module defines ALL strict, versioned schemas that flow across layers L1–L5.

Design Goals:
    - Zero ambiguity between layers.
    - Zero free-form dicts.
    - Every interlayer handoff is typed and validated.
    - All model interactions (Strategy, RAG, Drafting, QA, Safety) use explicit contracts.
    - Meets OpenAI Agentic Pillar #3: Typed Contracts.

Everything in this file is PURE MODELING — no business logic, no execution.
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
    title: str
    role_type: str
    seniority: str
    posting_text: str
    requirements: List[str] = Field(default_factory=list)


class ResumeInput(BaseModel):
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
    # Cost / latency budgets
    cost_budget: float = 0.10
    latency_slo_ms: int = 3000
    safety_sensitivity: int = 3
    drafting_depth: int = 3

    # Tone / length
    target_tone: str = "professional"
    target_total_tokens: int = 1800

    # RAG parameters
    rag_max_job_chunks: int = 8
    rag_max_resume_chunks: int = 10
    rag_max_hybrid_chunks: int = 4
    rag_allow_hyde: bool = True
    rag_require_hybrid: bool = False

    # Drafting token budgets
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
# ROUTING HINT
# ============================================================================

class RoutingHint(BaseModel):
    complexity: ComplexityLevel
    cost_budget: float
    latency_slo_ms: int
    safety_sensitivity: int
    drafting_depth: int


# ============================================================================
# STRATEGY PLAN + RESULT
# ============================================================================

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


# ============================================================================
# RAG PLAN + RESULT
# ============================================================================

class RAGQueryHint(BaseModel):
    id: str
    description: str
    focus: str      # job / resume / hybrid
    max_chunks: int
    importance: float


class RAGPlan(BaseModel):
    hints: List[RAGQueryHint]
    allow_hyde: bool = True
    require_hybrid: bool = False


class Evidence(BaseModel):
    text: str
    score: float
    source: str


class RAGResult(BaseModel):
    evidence: List[Evidence] = Field(default_factory=list)
    used_hyde: bool = False


# ============================================================================
# DRAFTING PLAN + RESULT
# ============================================================================

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


class DraftSectionResult(BaseModel):
    title: str
    outline: str
    text: str
    compliance_notes: str


class DraftingResult(BaseModel):
    sections: List[DraftSectionResult]
    mode: DraftingMode


# ============================================================================
# QA PLAN + RESULT
# ============================================================================

class QACheck(BaseModel):
    id: str
    description: str
    category: str
    severity: int = 1


class QACheckResult(BaseModel):
    id: str
    passed: bool
    reason: str
    severity: int


class QAPlan(BaseModel):
    checks: List[QACheck]


class QAResult(BaseModel):
    checks: List[QACheckResult]


# ============================================================================
# SAFETY PLAN + RESULT
# ============================================================================

class SafetyCheck(BaseModel):
    id: str
    description: str
    category: str
    severity: int = 1


class SafetyFinding(BaseModel):
    id: str
    category: str
    blocking: bool
    reason: str


class SafetyResult(BaseModel):
    findings: List[SafetyFinding]


# ============================================================================
# WORKFLOW PLAN BUNDLE (L1 OUTPUT)
# ============================================================================

class WorkflowPlanBundle(BaseModel):
    strategy: StrategyPlan
    rag: RAGPlan
    drafting: DraftingPlan
    qa: QAPlan
    safety: SafetyPlan
    routing_hint: RoutingHint


# ============================================================================
# L2 EXECUTION RESULT BUNDLE
# ============================================================================

class L2ResultBundle(BaseModel):
    strategy: StrategyResult
    rag: RAGResult
    drafting: DraftingResult
    qa: QAResult
    safety: SafetyResult


# ============================================================================
# EXECUTION CONTEXT (passed to L2 + L3)
# ============================================================================

class ExecutionContext(BaseModel):
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
