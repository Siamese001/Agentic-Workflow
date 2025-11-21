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

The Phase-3 upgrade adds:
    • Typed retrieval events:
          – RetrievalAttemptEvent
          – RetrievalSuccessEvent
          – RetrievalFailureEvent
    • Typed ranking event:
          – RankingEvent
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ======================================================================
# BASIC STRUCTURES (JOB / RESUME)
# ======================================================================

class Job(BaseModel):
    id: str
    title: Optional[str] = None
    posting_text: Optional[str] = None
    requirements: List[str] = Field(default_factory=list)


class Resume(BaseModel):
    id: str
    summary: Optional[str] = None
    experience_sections: List[Dict[str, Any]] = Field(default_factory=list)


# ======================================================================
# PROMPTS AND PROMPT VERSIONS (Phase-2)
# ======================================================================

class PromptVersion(BaseModel):
    major: int
    minor: int
    patch: int

    def as_str(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class PromptDefinition(BaseModel):
    id: str
    text: str
    version: PromptVersion
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# RETRIEVAL CONFIG (used by Phase-3 RAG)
# ======================================================================

class RetrievalConfig(BaseModel):
    strategy: str = "hybrid"
    use_rrf: bool = True
    max_hits: int = 20

    # BM25 tuning
    bm25_k1: float = 1.2
    bm25_b: float = 0.75

    # Optional weights for weighted RRF
    rrf_weights: Optional[List[float]] = None


# ======================================================================
# EVIDENCE + RAG MODELS
# ======================================================================

class Evidence(BaseModel):
    text: str
    score: float
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGResult(BaseModel):
    evidence: List[Evidence] = Field(default_factory=list)
    used_hyde: bool = False


class RAGPlan(BaseModel):
    allow_hyde: bool = False
    require_hybrid: bool = False
    strategy_hint: Optional[str] = None


# ======================================================================
# STRATEGY / DRAFTING / QA / SAFETY RESULTS
# ======================================================================

class StrategyBranch(BaseModel):
    id: str
    text: str


class StrategyResult(BaseModel):
    branches: List[StrategyBranch]
    chosen_branch_id: Optional[str] = None

    def get_chosen_branch_text(self) -> str:
        for b in self.branches:
            if b.id == self.chosen_branch_id:
                return b.text
        return ""


class DraftingResult(BaseModel):
    sections: List[Dict[str, Any]] = Field(default_factory=list)


class QACheckResult(BaseModel):
    check_id: str
    category: str
    status: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class QAResult(BaseModel):
    findings: List[QACheckResult] = Field(default_factory=list)


class SafetyFinding(BaseModel):
    check_id: str
    category: str
    status: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class SafetyResult(BaseModel):
    findings: List[SafetyFinding] = Field(default_factory=list)


# ======================================================================
# EXECUTION PROFILE / WORKFLOW CONTEXT
# ======================================================================

class ExecutionProfile(BaseModel):
    id: str
    model_tier: str
    retrieval: RetrievalConfig
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowConfig(BaseModel):
    target_total_tokens: int = 1800
    rag_max_job_chunks: int = 8
    rag_max_resume_chunks: int = 8
    rag_max_hybrid_chunks: int = 12
    rag_allow_hyde: bool = False
    rag_require_hybrid: bool = False


class ExecutionContext(BaseModel):
    job: Job
    resume: Resume
    config: WorkflowConfig

    routing_policy: Any = None
    sandbox_config: Any = None
    meta_profile_snapshot: Any = None

    cost_snapshot: Optional["CostSnapshot"] = None

    def span_context(self) -> Dict[str, Any]:
        return {}


# ======================================================================
# L2 RESULT BUNDLE (returned by L2.run)
# ======================================================================

class L2ResultBundle(BaseModel):
    strategy: StrategyResult
    rag: RAGResult
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
            safety=SafetyResult(findings=[SafetyFinding(
                check_id="internal_error",
                category="internal",
                status="blocked",
                message=msg,
                details={}
            )]),
        )


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


class RetrievalAttemptEvent(TelemetryEvent):
    method: str
    query: str


class RetrievalSuccessEvent(TelemetryEvent):
    method: str
    query: str
    count: int


class RetrievalFailureEvent(TelemetryEvent):
    method: str
    query: str
    error: str


class RankingEvent(TelemetryEvent):
    stage: str
    strategy: str
    use_rrf: bool


class CostSnapshot(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float = 0.0


class PolicyDecisionEvent(BaseModel):
    classifier_id: str
    outcome: str
    details: Dict[str, Any] = Field(default_factory=dict)

