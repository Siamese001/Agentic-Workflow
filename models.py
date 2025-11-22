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


class WorkflowConfig(BaseModel):
    """Workflow configuration knobs required at L1 planning time."""

    profile_id: str

    # RAG configuration used by L1
    rag_max_job_chunks: int = 8
    rag_max_resume_chunks: int = 8
    rag_max_hybrid_chunks: int = 8
    rag_allow_hyde: bool = False

    # Drafting configuration used by L1
    drafting_experience_max_tokens: int = 1024


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
    ExecutionContext is an immutable snapshot of:

        • Runtime configuration (ExecutionProfile / RetrievalConfig)
        • Routing hints
        • Meta-profile snapshot
        • Telemetry / cost containers (read-only at this layer)

    It is passed down the stack but never mutated in-place.
    """

    workflow_id: str
    profile_name: str

    # These are light-typed views into config_profiles_v10_10
    retrieval: "RetrievalConfig"
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
    strategy: "StrategyResult"
    rag: "RAGResult"
    drafting: "DraftingResult"
    qa: "QAResult"
    safety: "SafetyResult"

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


class RetrievalResultEvent(TelemetryEvent):
    method: str
    hit_count: int
    max_hits: int


class RankingEvent(TelemetryEvent):
    stage: str
    input_count: int
    output_count: int
    details: Dict[str, Any] = Field(default_factory=dict)


class RoutingDecisionEvent(TelemetryEvent):
    agent_id: str
    provider: str
    model_name: str
    reason: Optional[str] = None


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


class PolicyDecisionEvent(BaseModel):
    classifier_id: str
    outcome: str
    details: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# RESILIENCE MODELS (typed error hierarchy + decisions)
# ======================================================================


class ResilienceError(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


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


class SkillClassifierResult(BaseModel):
    """Deterministic classification of user skills (non-LLM)."""

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


class CorrectionLoopState(BaseModel):
    """Summary of a workflow's correction loop over the DAG."""

    iteration: int = 0
    max_iterations: int = 0
    surfaces_triggered: List[str] = Field(default_factory=list)
    last_signal: Optional[str] = None
    terminated_reason: Optional[str] = None
