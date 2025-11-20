# FILE: models.py
"""
Unified Runtime Models (v10_10) — TYPED CONTRACTS & SCHEMA DEFINITIONS

This module defines all canonical data structures used across the
v10_10 agentic architecture. It upgrades v10_9 structures to STRICT
PYDANTIC MODELS to satisfy Agentic Pillar 3 (Typed Contracts).

It contains:
    • Core Enums               — Phase, Status, Safety Modes
    • Registry Models          — Schemas for Prompts, Policies, Tools (Pillar 13, 9)
    • PlanObject               — L1 → L2/L3 planning contract
    • Domain Payloads          — Typed outputs for Strategy, RAG, Drafting, etc.
    • ExecutionResult          — L2 → L3 contract
    • WorkflowState            — L3 → External API contract
    • Meta & Observability     — Spans, Summaries, Multi-Agent Councils

Design Constraints:
    • PURE DATA: No logic, execution, or state mutation.
    • STRICT TYPES: Runtime validation via Pydantic.
    • ZERO LOSS: Preserves all fields from v10_9 while enforcing schema.
"""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict, model_validator


# =============================================================================
# 1. CANONICAL ENUMS
# =============================================================================

class NodeStatus(str, enum.Enum):
    """Execution status for nodes / steps / tasks."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    SKIPPED = "skipped"


class WorkflowPhase(str, enum.Enum):
    """Global workflow phase."""
    INIT = "init"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"


class SafetyMode(str, enum.Enum):
    """Safety operating modes (Pillar 9)."""
    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


class SelfCorrectionSurface(str, enum.Enum):
    """Surfaces for self-correction / recovery decisions."""
    RAG_RETRY = "rag_retry"
    DRAFT_RETRY = "draft_retry"
    QA_RECHECK = "qa_recheck"
    STRATEGY_REPLAN = "strategy_replan"
    HIL_ESCALATION = "hil_escalation"
    CHECKPOINT_RECOVERY = "checkpoint_recovery"
    SAFETY_RISK = "safety_risk"
    USER_FEEDBACK = "user_feedback"


# =============================================================================
# 2. BASE MODEL CONFIG
# =============================================================================

class AgenticBaseModel(BaseModel):
    """Base model for all agentic structures with standard config."""
    model_config = ConfigDict(
        extra='ignore',              # Default strictness
        validate_assignment=True,    # Validate on update
        arbitrary_types_allowed=True # For compatibility
    )


# =============================================================================
# 3. REGISTRY & GOVERNANCE MODELS (NEW for v10_10)
# =============================================================================

class PromptSpec(AgenticBaseModel):
    """Schema for a versioned prompt in the Registry (Pillar 13)."""
    prompt_id: str
    version: str
    template: str
    input_variables: List[str]
    description: Optional[str] = None
    safety_tier: str = "standard"
    model_constraints: Dict[str, Any] = Field(default_factory=dict)


class SafetyPolicy(AgenticBaseModel):
    """Schema for a safety policy rule (Pillar 9)."""
    policy_id: str
    version: str
    rules: List[str]
    mode: SafetyMode
    threshold: float = 0.5


class ToolSpec(AgenticBaseModel):
    """Schema for a registered tool (Pillar 8/14)."""
    tool_id: str
    description: str
    schema_definition: Dict[str, Any]
    timeout_seconds: int = 30
    requires_sandbox: bool = True


# =============================================================================
# 4. PLAN OBJECT (L1 → L2 / L3 CONTRACT)
# =============================================================================

class PlanObject(AgenticBaseModel):
    """
    Strictly typed L1 Plan.
    Allows extra fields to support diverse L1 modes (Strategy, RAG, etc.).
    """
    model_config = ConfigDict(extra='allow')  # Flexibility for diverse modes

    layer: str = "l1"
    mode: str
    objective: str
    workflow_id: Optional[str] = None
    
    # Core planning components
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: Dict[str, Any] = Field(default_factory=dict)
    
    # Profiles & Context (migrated from v10_9 dicts)
    framing_profile: Dict[str, Any] = Field(default_factory=dict)
    context_profile: Dict[str, Any] = Field(default_factory=dict)
    tooling_profile: Dict[str, Any] = Field(default_factory=dict)
    safety_profile: Dict[str, Any] = Field(default_factory=dict)
    
    # Reasoning & Meta
    complexity: str = "moderate"
    reasoning_strategy: str = "direct"  # direct, cot, tot
    surfaces: List[str] = Field(default_factory=list)


# =============================================================================
# 5. DOMAIN PAYLOADS (L2 OUTPUTS)
# =============================================================================

# --- 5.1 Strategy ---

class StrategyBranch(AgenticBaseModel):
    branch_id: str
    strategy_name: str
    focus_areas: List[str] = Field(default_factory=list)
    key_achievements: List[str] = Field(default_factory=list)
    tone: str = "professional"
    rationale: str = ""
    complexity: Optional[str] = None
    priority: Optional[int] = None


class StrategyExecutionPayload(AgenticBaseModel):
    branches: List[StrategyBranch] = Field(default_factory=list)
    selected_branch: Optional[StrategyBranch] = None
    aggregated_decision: str = ""
    aggregated_confidence: float = 0.0
    aggregated_rationale: str = ""
    complexity: Optional[str] = None
    surfaces: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# --- 5.2 RAG ---

class RAGDocument(AgenticBaseModel):
    query: str
    content: str
    source: str = "synthetic"
    score: float = 0.0
    rank: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGExternalStats(AgenticBaseModel):
    provider: str
    collection: str
    retrieved_count: int
    latency_ms: float
    cache_hit: bool = False


class RAGExecutionPayload(AgenticBaseModel):
    queries: List[str] = Field(default_factory=list)
    documents: List[RAGDocument] = Field(default_factory=list)
    external_stats: Optional[RAGExternalStats] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# --- 5.3 Bullets ---

class BulletExecutionPayload(AgenticBaseModel):
    bullets: List[str] = Field(default_factory=list)
    sections: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# --- 5.4 Drafting ---

class DraftSection(AgenticBaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DraftExecutionPayload(AgenticBaseModel):
    sections: List[Dict[str, Any]] = Field(default_factory=list) # Keeping dict for compat, ideally DraftSection
    full_text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


# --- 5.5 QA ---

class QAFinding(AgenticBaseModel):
    check_id: str
    severity: str
    message: str
    context: Dict[str, Any] = Field(default_factory=dict)


class QAReport(AgenticBaseModel):
    findings: List[QAFinding] = Field(default_factory=list)
    passed: bool = False
    summary: str = ""
    shadow_validation: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QAExecutionPayload(AgenticBaseModel):
    report: QAReport


# --- 5.6 Safety ---

class SafetyIssue(AgenticBaseModel):
    issue_id: str
    severity: str
    category: str
    message: str
    span: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SafetyReport(AgenticBaseModel):
    issues: List[SafetyIssue] = Field(default_factory=list)
    blocked: bool = False
    redacted_text: Optional[str] = None
    summary: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SafetyExecutionPayload(AgenticBaseModel):
    report: SafetyReport


# --- 5.7 HIL ---

class HILPrompt(AgenticBaseModel):
    prompt_id: str
    instructions: str
    artifacts: Dict[str, Any] = Field(default_factory=dict)


class HILResponse(AgenticBaseModel):
    prompt_id: str
    accepted: bool
    feedback: str = ""
    edits: Dict[str, Any] = Field(default_factory=dict)


class HILExecutionPayload(AgenticBaseModel):
    prompt: HILPrompt
    response: Optional[HILResponse] = None


# --- 5.8 Meta-Learning ---

class MetaLearningFinding(AgenticBaseModel):
    finding_id: str
    category: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetaLearningSnapshot(AgenticBaseModel):
    findings: List[MetaLearningFinding] = Field(default_factory=list)
    raw_logs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetaLearningExecutionPayload(AgenticBaseModel):
    snapshot: MetaLearningSnapshot


# --- 5.9 Multi-Agent / Council ---

class MultiAgentVote(AgenticBaseModel):
    agent_id: str
    decision: str
    confidence: float = 0.0
    rationale: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)


class MultiAgentCouncilResult(AgenticBaseModel):
    votes: List[MultiAgentVote] = Field(default_factory=list)
    aggregated_decision: str = ""
    aggregated_confidence: float = 0.0
    rationale: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# 6. EXECUTION RESULT (L2 → L3 CONTRACT)
# =============================================================================

PayloadT = TypeVar("PayloadT")

class ExecutionResult(Generic[PayloadT], AgenticBaseModel):
    """
    Normalized deterministic output for all L2 executors.
    Generic wrapper around domain-specific payloads.
    """
    status: str = "success"
    payload: Optional[PayloadT] = None
    errors: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    usage: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == "success" and not self.errors


# =============================================================================
# 7. STATE & ORCHESTRATION MODELS
# =============================================================================

class StatePatch(AgenticBaseModel):
    """Atomic state update operation (Pillar 4/10)."""
    key: str
    value: Any


class WorkflowState(AgenticBaseModel):
    """Final output of L3 orchestrator (External Contract)."""
    workflow_id: str
    phase: WorkflowPhase
    node_statuses: Dict[str, NodeStatus]
    summary: str
    result: Dict[str, Any]
    errors: List[str]
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# 8. ARBITRATION & RECOVERY (L5 / META)
# =============================================================================

class ArbitrationDecision(AgenticBaseModel):
    """L5 Policy decision outcome."""
    action: str  # proceed, retry_l2, rerun_l1, halt, escalate
    reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheckpointInfo(AgenticBaseModel):
    """Checkpoint metadata."""
    checkpoint_id: str
    phase: WorkflowPhase
    created_at: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CorrectionRecommendation(AgenticBaseModel):
    """Self-Correction recommendation."""
    needed: bool
    surface: Optional[str] = None
    rationale: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# 9. OBSERVABILITY & TRACE MODELS
# =============================================================================

class TraceSpan(AgenticBaseModel):
    """Performance span."""
    name: str
    start_time_ms: float
    end_time_ms: float
    tags: Dict[str, Any] = Field(default_factory=dict)
    
    def duration_ms(self) -> float:
        return max(0.0, self.end_time_ms - self.start_time_ms)


class RunSummary(AgenticBaseModel):
    """Aggregated run statistics."""
    workflow_id: str
    phases: List[str] = Field(default_factory=list)
    timings: Dict[str, float] = Field(default_factory=dict)
    counts: Dict[str, int] = Field(default_factory=dict)
    issues: Dict[str, List[str]] = Field(default_factory=dict)
    meta_profile: Dict[str, Any] = Field(default_factory=dict)


class RouteTraceEntry(AgenticBaseModel):
    """Route tracing metadata."""
    step: str
    model: Optional[str] = None
    endpoint: Optional[str] = None
    rationale: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CorrectionJournalEntry(AgenticBaseModel):
    """Correction history log."""
    event_id: str
    surface: str
    message: str
    created_at: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
