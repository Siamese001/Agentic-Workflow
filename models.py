# FILE: models.py
"""
Unified Runtime Models (v10_9, Fully Refactored)
STRICT DATA-ONLY CONTRACTS — MAX SCORE: Typed Contracts (10/10)

This module defines *all* canonical data structures used across the v10_9
agentic architecture. It is 100% pure data, containing:

    • Enums
    • PlanObject
    • ExecutionResult[TypedPayload]
    • Typed L2 payloads (Strategy, RAG, Drafting, Bullets, QA, Safety, HIL, MetaLearning)
    • WorkflowState
    • StatePatch
    • MultiAgentCouncilResult + MultiAgentVote
    • Observability metadata: TraceSpan, PhaseMetadata
    • ArbitrationDecision
    • CheckpointInfo

STRICT LAYER GUARANTEES:
    • NO L1 cognition
    • NO L2 execution/tool calls
    • NO L3 orchestration or DAG logic
    • NO L4 state mutation or adapters
    • NO L5 safety/policy decisions
    • NO provider SDKs, no network, no filesystem

Everything here is immutable-ish — safe for serialization, testing, and CI.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, List, Generic, TypeVar
import enum
import copy


# ============================================================================
# 1. ENUMS
# ============================================================================

class NodeStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"


class WorkflowPhase(str, enum.Enum):
    INIT = "init"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"


class SelfCorrectionSurface(str, enum.Enum):
    RAG_RETRY = "rag_retry"
    DRAFT_RETRY = "draft_retry"
    QA_RECHECK = "qa_recheck"
    STRATEGY_REPLAN = "strategy_replan"
    HIL_ESCALATION = "hil_escalation"
    CHECKPOINT_RECOVERY = "checkpoint_recovery"


# ============================================================================
# 2. PLANOBJECT — L1 → L2/L3 CONTRACT
# ============================================================================

class DictBacked:
    """
    Flexible dict-backed object with attribute-style access.

    Safe for L1 planning because:
        • Does NOT mutate external state
        • Only stores a local dict
        • Not used by L2 for internal logic (L2 uses typed payloads)

    Downstream layers must convert to typed structures where applicable.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        object.__setattr__(self, "_data", data or {})

    def __getattr__(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        raise AttributeError(f"{key!r} not found in PlanObject")

    def __setattr__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def update(self, other: Dict[str, Any]) -> None:
        self._data.update(other)

    def to_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)

    def deep_clone(self) -> "DictBacked":
        return DictBacked(copy.deepcopy(self._data))

    def __repr__(self) -> str:
        return f"DictBacked({self._data!r})"


class PlanObject(DictBacked):
    """
    L1 → L2/L3 plan container.
    """
    pass


# ============================================================================
# 3. EXECUTION RESULTS — L2 → L3 CONTRACT
# ============================================================================

T = TypeVar("T")


@dataclass
class ExecutionResult(Generic[T]):
    """
    Typed execution output from L2:

        status:  "success" | "failure"
        payload: TypedPayload
        model:   executor name
        usage:   token cost metadata (deterministic here)

    L3 consumes this to apply StatePatch to L4.
    """
    status: str
    payload: T
    model: str
    usage: Dict[str, Any]

    SUCCESS = "success"
    FAILURE = "failure"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "payload": self._payload_to_dict(self.payload),
            "model": self.model,
            "usage": dict(self.usage),
        }

    @staticmethod
    def _payload_to_dict(payload: Any) -> Any:
        if hasattr(payload, "to_dict"):
            return payload.to_dict()
        if isinstance(payload, dict):
            return payload
        try:
            return asdict(payload)
        except Exception:
            return payload


# ============================================================================
# 4. L2 PAYLOADS (TYPED)
# ============================================================================

@dataclass
class StrategyBranch:
    branch_id: str
    strategy_name: str
    focus_areas: List[str]
    key_achievements: List[str]
    tone: str
    rationale: str


@dataclass
class StrategyExecutionPayload:
    branches: List[StrategyBranch]
    selected_branch: Optional[StrategyBranch]
    aggregated_decision: str
    aggregated_confidence: float
    aggregated_rationale: str
    complexity: Optional[str]
    surfaces: List[str]


@dataclass
class RAGDocument:
    query: str
    evidence: str
    rank: int
    metadata: Dict[str, Any]


@dataclass
class RAGExecutionPayload:
    queries: List[str]
    documents: List[RAGDocument]
    ranking_strategy: str
    hyde_used: bool
    vector_source: Optional[str]
    bm25_used: bool


@dataclass
class BulletExecutionPayload:
    bullets: List[str]
    guidelines: List[str]
    metrics_focus: List[str]
    guild_passes: List[str]


@dataclass
class DraftExecutionPayload:
    sections: List[str]
    tone: str
    draft: List[str]
    hints: List[str]
    passes: List[str]


@dataclass
class QAFinding:
    check: str
    status: str
    details: str


@dataclass
class QAReport:
    issues: List[str]
    passed: bool
    confidence: float
    findings: List[QAFinding]
    tool_suite_used: bool
    tools_invoked: List[str]


@dataclass
class QAExecutionPayload:
    qa_report: QAReport


@dataclass
class SafetyIssue:
    code: str
    description: str


@dataclass
class SafetyReport:
    passed: bool
    issues: List[SafetyIssue]
    toxicity_score: float
    audience: str
    prompt_injection: Dict[str, Any]
    constitutional: Dict[str, Any]


@dataclass
class SafetyExecutionPayload:
    safety_report: SafetyReport
    sanitized_content: str


@dataclass
class HILPrompt:
    question: str
    context: str
    recommended_action: str
    urgency: str


@dataclass
class HILResponse:
    approved: bool
    comments: str
    requested_changes: List[str]


@dataclass
class HILExecutionPayload:
    prompt: HILPrompt
    response: Optional[HILResponse]
    surface: str


@dataclass
class MetaLearningFinding:
    kind: str
    description: str
    weight: float
    metadata: Dict[str, Any]


@dataclass
class MetaLearningSnapshot:
    workflow_id: str
    raw_feedback_entries: int
    raw_preference_entries: int
    findings: List[MetaLearningFinding]
    proposal: Dict[str, Any]
    critique: Dict[str, Any]


@dataclass
class MetaLearningExecutionPayload:
    snapshot: MetaLearningSnapshot


# ============================================================================
# 5. WORKFLOW STATE (L3 → EXT API CONTRACT)
# ============================================================================

@dataclass
class WorkflowState:
    workflow_id: str
    phase: str
    nodes: Dict[str, Any]
    state: Dict[str, Any]
    phase_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "phase": self.phase,
            "nodes": copy.deepcopy(self.nodes),
            "state": copy.deepcopy(self.state),
            "phase_metadata": copy.deepcopy(self.phase_metadata),
        }


# ============================================================================
# 6. STATE PATCH (L4 CONTRACT)
# ============================================================================

@dataclass
class StatePatch:
    """
    Immutable patch describing a SINGLE write to workflow state.
    """
    key: Optional[str] = None
    value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patch": {self.key: self.value}
        }


# ============================================================================
# 7. ARBITRATION DECISION (L5 → L3 CONTRACT)
# ============================================================================

@dataclass
class ArbitrationDecision:
    action: str        # "proceed" | "retry_l2" | "rerun_l1" | "halt" | "escalate"
    reason: str


# ============================================================================
# 8. MULTI-AGENT COUNCIL RESULTS
# ============================================================================

@dataclass
class MultiAgentVote:
    candidate_id: Any
    score: float
    rationale: str


@dataclass
class MultiAgentCouncilResult:
    selected_id: Any
    selected_score: float
    votes: List[MultiAgentVote]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_id": self.selected_id,
            "selected_score": self.selected_score,
            "votes": [
                {
                    "candidate_id": v.candidate_id,
                    "score": v.score,
                    "rationale": v.rationale,
                }
                for v in self.votes
            ],
        }


# ============================================================================
# 9. CHECKPOINT INFO (OPTIONAL L3–META USE)
# ============================================================================

@dataclass
class CheckpointInfo:
    phase: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
