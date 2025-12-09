# FILE: models.py
"""
Unified Runtime Models (v10_9) — FULL AGENTIC IMPLEMENTATION (REFINED)

This module defines all canonical data structures used across the
v10_9 agentic architecture. It is intentionally *data-only* and
contains:

    • PlanObject               — L1 → L2/L3 planning contract
    • Typed payloads           — per-domain L2 execution outputs
    • ExecutionResult          — L2 → L3 contract
    • WorkflowState            — L3 → external API contract
    • StatePatch               — L4 patch container
    • Enums                    — NodeStatus, WorkflowPhase, SelfCorrectionSurface
    • ArbitrationDecision      — L5 arbitration outcome
    • CheckpointInfo           — checkpoint metadata
    • RouteTraceEntry          — L3 route trace metadata
    • CorrectionJournalEntry   — L3/L4 correction log entries
    • MultiAgentCouncilResult  — meta-layer multi-agent outcomes
    • TraceSpan / PhaseMetadata — observability metadata

Design constraints (structural guardrails):

    • NO cognition (L1) here — no planning logic.
    • NO execution (L2) — no tool/LLM calls.
    • NO orchestration (L3) — no control-flow or DAG logic.
    • NO state mutation (L4) — no state adapters or patch application.
    • NO safety/policy (L5) — no safety decisions.

Everything here is immutable-ish data (dataclasses / enums / dict
wrappers) used BY the other layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, List, Generic, TypeVar
import copy
import enum


# =============================================================================
# 1. CANONICAL ENUMS
# =============================================================================


class NodeStatus(str, enum.Enum):
    """Execution status for nodes / steps / tasks."""

    SUCCESS = "success"
    ERROR = "error"      # used by L3 for failed nodes
    PENDING = "pending"


class WorkflowPhase(str, enum.Enum):
    """Global workflow phase, aligned with orchestration phase machine."""

    INIT = "init"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"


class SelfCorrectionSurface(str, enum.Enum):
    """
    Surfaces for self-correction / recovery decisions.

    These surfaces are used by L3 orchestrators, self_correction, and
    meta-learning to decide how to adapt behavior over time.
    """

    RAG_RETRY = "rag_retry"
    DRAFT_RETRY = "draft_retry"
    QA_RECHECK = "qa_recheck"
    STRATEGY_REPLAN = "strategy_replan"
    HIL_ESCALATION = "hil_escalation"
    CHECKPOINT_RECOVERY = "checkpoint_recovery"
    SAFETY_RISK = "safety_risk"
    USER_FEEDBACK = "user_feedback"


# =============================================================================
# 2. BASE DICT-BACKED OBJECT (for PlanObject)
# =============================================================================


class DictBacked:
    """
    Base class that wraps a Python dict but provides:

        • attribute-style access
        • defensive copying
        • .get(), .update()
        • .to_dict()
        • deep_clone()

    This is intentionally flexible for L1 cognition, which builds
    rich plan dictionaries that may evolve over time. Downstream
    layers should convert into typed payloads where appropriate.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        object.__setattr__(self, "_data", data or {})

    # --- attribute access -----------------------------------------------------

    def __getattr__(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        raise AttributeError(f"{key!r} not found in {type(self).__name__}")

    def __setattr__(self, key: str, value: Any) -> None:
        self._data[key] = value

    # --- mapping style --------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def update(self, other: Dict[str, Any]) -> None:
        self._data.update(other)

    # --- serialization --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)

    def deep_clone(self) -> "DictBacked":
        return type(self)(copy.deepcopy(self._data))

    # --- representation -------------------------------------------------------

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._data!r})"


# =============================================================================
# 3. PLAN OBJECT (L1 → L2 / L3 CONTRACT)
# =============================================================================


class PlanObject(DictBacked):
    """
    Describes the full L1 cognitive plan for L2 execution and L3
    orchestration.

    Examples of required / common fields (depending on mode):

        • layer: "l1"
        • mode:  "strategy" | "rag" | "drafting" | "bullets" |
                 "qa" | "safety" | "hil" | "meta_learning" |
                 "prompt_engineering"

        • objective: str
        • branches / steps / checks / rules / surfaces
        • handoff: {
              "target_layer": "l2",
              "preferred_executor": "...",
              "expected_deliverables": [...]
          }
        • injection_framing / injection_reasoning
        • safety_metadata
        • compatibility hints (e.g., "compat_mode": "10_7")

    PlanObject remains dict-backed for flexibility, but L2/L3 should
    convert into typed payloads when needed.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        super().__init__(data or {})

    def copy(self) -> "PlanObject":
        return PlanObject(self.to_dict())


# =============================================================================
# 4. DOMAIN PAYLOAD MODELS FOR L2 EXECUTION
# =============================================================================
#
# These dataclasses provide typed payloads for ExecutionResult, one per
# domain. They are OPTIONAL wrappers around the generic payload dict,
# but serve as the canonical schema for each L2 executor.
# =============================================================================

# -----------------------------------------------------------------------------
# 4.1 Strategy (L2 StrategyExecutor)
# -----------------------------------------------------------------------------


@dataclass
class StrategyBranch:
    """Single strategy branch produced by L1 planning and realized by L2."""

    branch_id: str
    strategy_name: str
    focus_areas: List[str] = field(default_factory=list)
    key_achievements: List[str] = field(default_factory=list)
    tone: str = "professional"
    rationale: str = ""
    complexity: Optional[str] = None
    priority: Optional[int] = None


@dataclass
class StrategyExecutionPayload:
    """
    Execution payload for strategy executors.

    Typically returned as ExecutionResult.payload for "strategy".
    """

    branches: List[StrategyBranch] = field(default_factory=list)
    selected_branch: Optional[StrategyBranch] = None
    aggregated_decision: str = ""
    aggregated_confidence: float = 0.0
    aggregated_rationale: str = ""
    complexity: Optional[str] = None
    surfaces: List[SelfCorrectionSurface] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert enums to values
        d["surfaces"] = [s.value for s in self.surfaces]
        return d


# -----------------------------------------------------------------------------
# 4.2 RAG (L2 RAGExecutor)
# -----------------------------------------------------------------------------


@dataclass
class RAGDocument:
    """Single document/evidence item surfaced by a RAG executor."""

    query: str
    content: str
    source: str = "synthetic"
    score: float = 0.0
    rank: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGExternalStats:
    """
    Metadata-only payload describing external/vector RAG behavior.

    Used for observability and optimization, not for direct user output.
    """

    provider: str
    collection: str
    retrieved_count: int
    latency_ms: float
    cache_hit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RAGExecutionPayload:
    """
    Execution payload for retrieval executors.

    Typically returned as ExecutionResult.payload for "rag".
    """

    queries: List[str] = field(default_factory=list)
    documents: List[RAGDocument] = field(default_factory=list)
    external_stats: Optional[RAGExternalStats] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "queries": list(self.queries),
            "documents": [asdict(doc) for doc in self.documents],
            "external_stats": self.external_stats.to_dict() if self.external_stats else None,
            "metadata": copy.deepcopy(self.metadata),
        }


# -----------------------------------------------------------------------------
# 4.3 Bullets (L2 BulletExecutor)
# -----------------------------------------------------------------------------


@dataclass
class BulletExecutionPayload:
    """
    Execution payload for bullet generation.

    Typically returned as ExecutionResult.payload for "bullets".
    """

    bullets: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.4 Drafting (L2 DraftingExecutor)
# -----------------------------------------------------------------------------


@dataclass
class DraftExecutionPayload:
    """
    Execution payload for drafting.

    Typically returned as ExecutionResult.payload for "drafting".
    """

    sections: List[Dict[str, Any]] = field(default_factory=list)
    full_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.5 QA (L2 QAExecutor)
# -----------------------------------------------------------------------------


@dataclass
class QAFinding:
    """Single QA check result."""

    check_id: str
    severity: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QAReport:
    """
    Aggregated QA report.

    Used by L2 QAExecutor and higher layers.
    """

    findings: List[QAFinding] = field(default_factory=list)
    passed: bool = False
    summary: str = ""
    shadow_validation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QAExecutionPayload:
    """
    Execution payload for QA validation.

    Typically returned as ExecutionResult.payload for "qa".
    """

    report: QAReport

    def to_dict(self) -> Dict[str, Any]:
        return {"report": self.report.to_dict()}


# -----------------------------------------------------------------------------
# 4.6 Safety (L2 SafetyExecutor / L5 SafetyEngine)
# -----------------------------------------------------------------------------


@dataclass
class SafetyIssue:
    """Single safety issue detected by safety evaluators."""

    issue_id: str
    severity: str
    category: str
    message: str
    span: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyReport:
    """
    Aggregated safety report.

    Used both by L2 SafetyExecutor and L5 SafetyEngine.
    """

    issues: List[SafetyIssue] = field(default_factory=list)
    blocked: bool = False
    redacted_text: Optional[str] = None
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issues": [asdict(issue) for issue in self.issues],
            "blocked": self.blocked,
            "redacted_text": self.redacted_text,
            "summary": self.summary,
            "metadata": copy.deepcopy(self.metadata),
        }


@dataclass
class SafetyExecutionPayload:
    """
    Execution payload for safety evaluators.

    Typically returned as ExecutionResult.payload for "safety".
    """

    report: SafetyReport

    def to_dict(self) -> Dict[str, Any]:
        return {"report": self.report.to_dict()}


# -----------------------------------------------------------------------------
# 4.7 HIL (Human-in-the-loop)
# -----------------------------------------------------------------------------


@dataclass
class HILPrompt:
    """Structured representation of a HIL question to a human reviewer."""

    prompt_id: str
    instructions: str
    artifacts: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HILResponse:
    """Structured response captured from a human reviewer."""

    prompt_id: str
    accepted: bool
    feedback: str = ""
    edits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HILExecutionPayload:
    """
    Execution payload for HIL interactions.

    Typically returned as ExecutionResult.payload for "hil".
    """

    prompt: HILPrompt
    response: Optional[HILResponse] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": asdict(self.prompt),
            "response": asdict(self.response) if self.response else None,
        }


# -----------------------------------------------------------------------------
# 4.8 Meta-Learning
# -----------------------------------------------------------------------------


@dataclass
class MetaLearningFinding:
    """Single pattern / hypothesis extracted from logs or prior runs."""

    finding_id: str
    category: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaLearningSnapshot:
    """
    Aggregated meta-learning snapshot summarizing a run of the
    meta-learning graph.
    """

    findings: List[MetaLearningFinding] = field(default_factory=list)
    raw_logs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetaLearningExecutionPayload:
    """
    Execution payload for meta-learning passes.

    Typically attached to state under a meta_learning block.
    """

    snapshot: MetaLearningSnapshot

    def to_dict(self) -> Dict[str, Any]:
        return {"snapshot": self.snapshot.to_dict()}


# -----------------------------------------------------------------------------
# 4.9 Multi-Agent / Arbitration / Council Metadata
# -----------------------------------------------------------------------------


@dataclass
class MultiAgentVote:
    """Single agent vote within a council."""

    agent_id: str
    decision: str
    confidence: float = 0.0
    rationale: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiAgentCouncilResult:
    """
    Aggregate result of a multi-agent council vote.

    Used by meta-layer and L3/L5 as advisory input.
    """

    votes: List[MultiAgentVote] = field(default_factory=list)
    aggregated_decision: str = ""
    aggregated_confidence: float = 0.0
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "votes": [asdict(v) for v in self.votes],
            "aggregated_decision": self.aggregated_decision,
            "aggregated_confidence": self.aggregated_confidence,
            "rationale": self.rationale,
            "metadata": copy.deepcopy(self.metadata),
        }


@dataclass
class ArbitrationDecision:
    """
    Normalized arbitration decision outcome used by L3/L5.

        action: "proceed" | "retry_l2" | "rerun_l1" | "halt" | "escalate"
        reason: short, deterministic explanation
        metadata: arbitrary additional metadata (e.g. mode, safety report)
    """

    action: str
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "metadata": copy.deepcopy(self.metadata),
        }


@dataclass
class CheckpointInfo:
    """
    Summary of a persisted checkpoint for recovery and replay.

    This is metadata-only and does not contain full state blobs; those
    are left to the underlying persistence system.
    """

    checkpoint_id: str
    phase: WorkflowPhase
    created_at: float  # epoch seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["phase"] = self.phase.value
        return d


# -----------------------------------------------------------------------------
# 4.10 Route Trace & Correction Journal
# -----------------------------------------------------------------------------

@dataclass
class RouteTraceEntry:
    """
    Route trace metadata for routing decisions or node executions.

    Used by L3 for observability.
    """

    step: str
    model: Optional[str] = None
    endpoint: Optional[str] = None
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CorrectionJournalEntry:
    """
    Single entry in a correction journal used by L3/L4/L5/meta-learning.

    This provides a unified way to track self-correction signals across runs.
    """

    event_id: str
    surface: str
    message: str
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 5. EXECUTION RESULT (L2 → L3 CONTRACT)
# =============================================================================

PayloadT = TypeVar("PayloadT")


@dataclass
class ExecutionResult(Generic[PayloadT]):
    """
    Normalized deterministic output for all L2 executors.

    Fields:
        • status:  "success" | "error" | "skipped" | ...
        • payload: domain-specific object (dict OR typed dataclass)
        • errors:  list of error strings
        • model:   logical executor/model label
        • usage:   token/cost/latency metrics
        • metadata: arbitrary metadata (e.g. domain, surfaces)

    ExecutionResult.ok is True for status == "success" and no errors.
    """

    status: str = "success"
    payload: Optional[PayloadT] = None
    errors: List[str] = field(default_factory=list)
    model: Optional[str] = None
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == "success" and not self.errors

    def to_dict(self) -> Dict[str, Any]:
        if self.payload is None:
            payload = None
        elif hasattr(self.payload, "to_dict"):
            payload = self.payload.to_dict()  # type: ignore[assignment]
        else:
            payload = copy.deepcopy(self.payload)
        return {
            "status": self.status,
            "payload": payload,
            "errors": list(self.errors),
            "model": self.model,
            "usage": copy.deepcopy(self.usage),
            "metadata": copy.deepcopy(self.metadata),
        }

    def __repr__(self) -> str:
        return f"ExecutionResult(status={self.status!r}, model={self.model!r})"


# =============================================================================
# 6. WORKFLOW STATE (L3 → EXTERNAL API CONTRACT)
# =============================================================================


@dataclass
class WorkflowState:
    """
    Final output of the L3 orchestrator for a single execution pass.

    Fields:
        • workflow_id:  str
        • phase:        WorkflowPhase
        • node_statuses: mapping `node_name -> NodeStatus`
        • summary:      short string summary of the run (complete/failed)
        • result:       full state dict (L4 adapter state)
        • errors:       list of errors encountered across nodes
        • trace_id:     optional trace id
        • metadata:     additional orchestration metadata
    """

    workflow_id: str
    phase: WorkflowPhase
    node_statuses: Dict[str, NodeStatus]
    summary: str
    result: Dict[str, Any]
    errors: List[str]
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 7. STATE PATCH (L4 CONTRACT)
# =============================================================================


@dataclass
class StatePatch:
    """
    Minimal, key-scoped state patch used by L4.StateAdapter.

    In v10_9, StateAdapter.apply_patch expects:

        StatePatch(key=<top_level_key>, value=<replacement_or_partial_dict>)

    Semantics:
        • If both existing state[key] and patch.value are dicts,
          we perform a shallow merge.
        • If both are lists, we append.
        • Else, we replace the top-level key entirely.
    """

    key: str
    value: Any


# =============================================================================
# 8. META / OBSERVABILITY TYPES
# =============================================================================


@dataclass
class TraceSpan:
    """
    Lightweight representation of a timing span for observability.

    This is used only for typed observability payloads and is distinct
    from the runtime_utils telemetry implementation.
    """

    name: str
    duration_ms: float
    tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PhaseMetadata:
    """
    Metadata describing phase transitions for a workflow.

    This can be embedded under WorkflowState.metadata if desired.
    """

    phase: str
    history: List[str] = field(default_factory=list)
    notes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
