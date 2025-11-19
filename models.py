# FILE: models.py
"""
Unified Runtime Models (v10_9) — FULL AGENTIC IMPLEMENTATION (ENTERPRISE REFINEMENT)

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
    • TraceSpan / PhaseMetadata — observability metadata
    • MultiAgentCouncilResult  — meta-layer multi-agent outcomes

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
    FAILURE = "failure"
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
        # DictBacked instances are meant to be mutable containers.
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
# 4.1 Strategy (L2 StrategyExecutor / StrategyGuild)
# -----------------------------------------------------------------------------


@dataclass
class StrategyBranch:
    """Single strategy branch produced by L1 planning and realized by L2."""

    branch_id: str
    strategy_name: str
    focus_areas: List[str] = field(default_factory=list)
    key_achievements: List[str] = field(default_factory=list)
    tone: str = "Professional"
    rationale: str = ""


@dataclass
class StrategyExecutionPayload:
    """
    Execution payload for strategy executors.

    Typically returned under ExecutionResult.payload["strategy"].
    """

    branches: List[StrategyBranch] = field(default_factory=list)
    selected_branch: Optional[StrategyBranch] = None
    aggregated_decision: str = ""
    aggregated_confidence: float = 0.0
    aggregated_rationale: str = ""
    # Optional meta fields
    complexity: Optional[str] = None
    surfaces: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.2 RAG (L2 RAGExecutor + External RAG)
# -----------------------------------------------------------------------------


@dataclass
class RAGDocument:
    """Single document/evidence item surfaced by a RAG executor."""

    query: str
    evidence: str
    rank: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGExecutionPayload:
    """
    Execution payload for retrieval executors.

    Typically returned under ExecutionResult.payload["rag"].
    """

    queries: List[str] = field(default_factory=list)
    documents: List[RAGDocument] = field(default_factory=list)
    ranking_strategy: str = "hybrid"
    hyde_used: bool = True
    vector_source: Optional[str] = None
    bm25_used: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "queries": list(self.queries),
            "documents": [asdict(doc) for doc in self.documents],
            "ranking_strategy": self.ranking_strategy,
            "hyde_used": self.hyde_used,
            "vector_source": self.vector_source,
            "bm25_used": self.bm25_used,
        }


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


# -----------------------------------------------------------------------------
# 4.3 Bullets (L2 BulletExecutor + Bullet Guild)
# -----------------------------------------------------------------------------


@dataclass
class BulletExecutionPayload:
    """
    Execution payload for bullet generation.

    Typically returned under ExecutionResult.payload["bullets"].
    """

    bullets: List[str] = field(default_factory=list)
    guidelines: List[str] = field(default_factory=list)
    metrics_focus: List[str] = field(default_factory=list)
    # Optional guild metadata
    guild_passes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.4 Drafting (L2 DraftingExecutor + Drafting Guild)
# -----------------------------------------------------------------------------


@dataclass
class DraftSection:
    """Single draft section, for more structured drafting pipelines."""

    title: str
    content: str
    tone: str = "Professional"


@dataclass
class DraftExecutionPayload:
    """
    Execution payload for drafting.

    Typically returned under ExecutionResult.payload["draft"].
    """

    sections: List[str] = field(default_factory=list)
    tone: str = "Professional"
    draft: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    # Optional guild metadata
    passes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.5 QA (L2 QAExecutor + QA Tool Suite)
# -----------------------------------------------------------------------------


@dataclass
class QAFinding:
    """Single QA check result."""

    check: str
    status: str  # "pass" | "fail" | "pending"
    details: str = ""


@dataclass
class QAReport:
    """
    Aggregated QA report.

    This is the canonical QA structure for L3 and higher layers.
    """

    issues: List[str] = field(default_factory=list)
    passed: bool = False
    confidence: float = 0.0
    findings: List[QAFinding] = field(default_factory=list)
    # Optional suite-level signals
    tool_suite_used: bool = False
    tools_invoked: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QAExecutionPayload:
    """
    Execution payload for QA validation.

    Typically returned under ExecutionResult.payload["qa"].
    """

    qa_report: QAReport

    def to_dict(self) -> Dict[str, Any]:
        return {"qa_report": self.qa_report.to_dict()}


# -----------------------------------------------------------------------------
# 4.6 Safety (L2 SafetyExecutor / L5 SafetyEngine)
# -----------------------------------------------------------------------------


@dataclass
class SafetyIssue:
    """Single safety issue detected by safety evaluators."""

    code: str
    description: str


@dataclass
class SafetyReport:
    """
    Aggregated safety report.

    Used both by L2 SafetyExecutor and L5 SafetyEngine.
    """

    passed: bool
    issues: List[SafetyIssue] = field(default_factory=list)
    toxicity_score: float = 0.0
    audience: str = "general"
    prompt_injection: Dict[str, Any] = field(default_factory=dict)
    constitutional: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "issues": [asdict(issue) for issue in self.issues],
            "toxicity_score": self.toxicity_score,
            "audience": self.audience,
            "prompt_injection": copy.deepcopy(self.prompt_injection),
            "constitutional": copy.deepcopy(self.constitutional),
        }


@dataclass
class SafetyExecutionPayload:
    """
    Execution payload for safety evaluators.

    Typically returned under ExecutionResult.payload["safety"].
    """

    safety_report: SafetyReport
    sanitized_content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "safety_report": self.safety_report.to_dict(),
            "sanitized_content": self.sanitized_content,
        }


# -----------------------------------------------------------------------------
# 4.7 HIL (Human-in-the-loop)
# -----------------------------------------------------------------------------


@dataclass
class HILPrompt:
    """Structured representation of a HIL question to a human reviewer."""

    question: str
    context: str
    recommended_action: str = ""
    urgency: str = "normal"  # "low" | "normal" | "high"


@dataclass
class HILResponse:
    """Structured response captured from a human reviewer."""

    approved: bool
    comments: str = ""
    requested_changes: List[str] = field(default_factory=list)


@dataclass
class HILExecutionPayload:
    """
    Execution payload for HIL interactions.

    Typically returned under ExecutionResult.payload["hil"].
    """

    prompt: HILPrompt
    response: Optional[HILResponse] = None
    surface: str = SelfCorrectionSurface.HIL_ESCALATION.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": asdict(self.prompt),
            "response": asdict(self.response) if self.response else None,
            "surface": self.surface,
        }


# -----------------------------------------------------------------------------
# 4.8 Meta-Learning
# -----------------------------------------------------------------------------


@dataclass
class MetaLearningFinding:
    """Single pattern / hypothesis extracted from logs or prior runs."""

    kind: str  # "pattern" | "hypothesis" | "recommendation"
    description: str
    weight: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaLearningSnapshot:
    """
    Aggregated meta-learning snapshot summarizing a run of the
    meta-learning graph.
    """

    workflow_id: str
    raw_feedback_entries: int
    raw_preference_entries: int
    findings: List[MetaLearningFinding] = field(default_factory=list)
    proposal: Dict[str, Any] = field(default_factory=dict)
    critique: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "raw_feedback_entries": self.raw_feedback_entries,
            "raw_preference_entries": self.raw_preference_entries,
            "findings": [asdict(f) for f in self.findings],
            "proposal": copy.deepcopy(self.proposal),
            "critique": copy.deepcopy(self.critique),
        }


@dataclass
class MetaLearningExecutionPayload:
    """
    Execution payload for meta-learning passes.

    Typically attached to state under a meta_learning block, not used
    for direct user-visible output.
    """

    snapshot: MetaLearningSnapshot

    def to_dict(self) -> Dict[str, Any]:
        return {"snapshot": self.snapshot.to_dict()}


# -----------------------------------------------------------------------------
# 4.9 Multi-Agent / Arbitration / Council Metadata
# -----------------------------------------------------------------------------


@dataclass
class MultiAgentVote:
    """Single vote from a council member."""

    candidate_id: Any
    score: float
    rationale: str = ""


@dataclass
class MultiAgentCouncilResult:
    """
    Captures council-of-QA or other multi-agent consensus outcomes.

    Stored under e.g. state["multi_agent"] for introspection.
    """

    selected_id: Any
    selected_score: float
    votes: List[MultiAgentVote] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArbitrationDecision:
    """
    Normalized arbitration decision outcome used by L3/L5.

        action: "proceed" | "retry_l2" | "rerun_l1" | "halt"
        reason: short, deterministic explanation
        surface_hint: optional SelfCorrectionSurface value
    """

    action: str
    reason: str
    surface_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.10 Checkpointing / Recovery Metadata
# -----------------------------------------------------------------------------


@dataclass
class CheckpointInfo:
    """
    Summary of a persisted checkpoint for recovery and replay.

    This is metadata-only and does not contain full state blobs; those
    are left to the underlying persistence system.
    """

    checkpoint_id: str
    created_at_iso: str
    phase: str
    notes: str = ""
    surface: str = SelfCorrectionSurface.CHECKPOINT_RECOVERY.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 5. EXECUTION RESULT (L2 → L3 CONTRACT)
# =============================================================================

PayloadT = TypeVar("PayloadT")


@dataclass
class ExecutionResult(Generic[PayloadT]):
    """
    Normalized deterministic output for all L2 executors.

    Fields:
        • status: "success" | "failure"
        • payload: domain-specific object (dict OR typed dataclass)
        • model: str           — the logical executor/model label
        • usage: dict          — e.g., token counts, cost estimates

    For typed usage, ExecutionResult[StrategyExecutionPayload] (etc.)
    can be used by type checkers, while still allowing dict payloads.
    """

    status: str
    payload: PayloadT
    model: str
    usage: Dict[str, Any] = field(default_factory=dict)

    SUCCESS: str = field(init=False, default="success", repr=False)
    FAILURE: str = field(init=False, default="failure", repr=False)

    def to_dict(self) -> Dict[str, Any]:
        if hasattr(self.payload, "to_dict"):
            payload = self.payload.to_dict()  # type: ignore[assignment]
        else:
            payload = copy.deepcopy(self.payload)  # assumed dict-like
        return {
            "status": self.status,
            "payload": payload,
            "model": self.model,
            "usage": copy.deepcopy(self.usage),
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
        • workflow_id: str
        • phase: str (WorkflowPhase string)
        • nodes: dict (reserved for future graph support)
        • state: full context state dict
        • phase_metadata: dict (phase history, notes, hints)
    """

    workflow_id: str
    phase: str
    nodes: Dict[str, Any]
    state: Dict[str, Any]
    phase_metadata: Dict[str, Any]


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
        • When both existing state[key] and value are dicts, a shallow
          merge is performed.
        • Otherwise, value replaces state[key] entirely.

    NOTE:
        This is a pure data container; all application logic lives in
        the L4 StateAdapter implementation.
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

    This can be embedded under WorkflowState.phase_metadata.
    """

    phase: str
    history: List[str] = field(default_factory=list)
    notes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
