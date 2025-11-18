# FILE: models.py
"""
Unified Runtime Models (v10_9) — FULL AGENTIC IMPLEMENTATION (REFINED)

This module defines all canonical data structures used across the
v10_9 agentic architecture, with enhancements to fully support:

    • Typed PlanObjects for L1 planning outputs
    • Typed Execution payloads for each L2 domain:
        - Strategy
        - RAG
        - Bullets
        - Drafting
        - QA
        - Safety
        - Multi-agent meta signals
    • WorkflowState as the single L3 → external API contract
    • StatePatch as the L4 patch container (for future extensions)
    • PhaseMetadata & TraceSpan for observability and debugging

Design goals:
    • NO cognition (L1) here — only data structures.
    • NO execution (L2) — only models used BY executors.
    • NO orchestration (L3) — only WorkflowState representation.
    • NO state mutation (L4) — only patch container types.
    • NO safety/policy logic (L5) — only data formats.

This file is intentionally import-light and depends only on Python
standard library types.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, List, Iterable, TypeVar, Generic
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


# =============================================================================
# 2. BASE DICT-BACKED OBJECT (for PlanObject)
# =============================================================================


class DictBacked:
    """
    Base class that wraps a Python dict but provides:

        • attribute-style access
        • defensive copying
        • .get(), .set(), .update()
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
    Describes the full L1 cognitive plan for L2 execution.

    Examples of required / common fields (depending on mode):
        • mode: "strategy" | "rag" | "drafting" | "bullets" | "qa" | "safety"
        • objective: str
        • branches / steps / checks / rules
        • handoff: {target_layer: "l2", preferred_executor: "..."}
        • injection_framing / injection_reasoning
        • safety_metadata

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
#
# This closes the “raw dicts” gap while preserving backward compatibility.
# =============================================================================

# -----------------------------------------------------------------------------
# 4.1 Strategy (L2 StrategyExecutor)
# -----------------------------------------------------------------------------


@dataclass
class StrategyBranch:
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.2 RAG (L2 RAGExecutor)
# -----------------------------------------------------------------------------


@dataclass
class RAGDocument:
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "queries": list(self.queries),
            "documents": [asdict(doc) for doc in self.documents],
            "ranking_strategy": self.ranking_strategy,
            "hyde_used": self.hyde_used,
        }


# -----------------------------------------------------------------------------
# 4.3 Bullets (L2 BulletExecutor)
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.4 Drafting (L2 DraftingExecutor)
# -----------------------------------------------------------------------------


@dataclass
class DraftSection:
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# 4.5 QA (L2 QAExecutor)
# -----------------------------------------------------------------------------


@dataclass
class QAFinding:
    check: str
    status: str  # "pass" | "fail" | "pending"
    details: str = ""


@dataclass
class QAReport:
    issues: List[str] = field(default_factory=list)
    passed: bool = False
    confidence: float = 0.0
    findings: List[QAFinding] = field(default_factory=list)

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
    code: str
    description: str


@dataclass
class SafetyReport:
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
# 4.7 Multi-Agent / Arbitration Payloads
# -----------------------------------------------------------------------------


@dataclass
class MultiAgentVote:
    candidate_id: Any
    score: float
    rationale: str = ""


@dataclass
class MultiAgentCouncilResult:
    """
    Captures council-of-QA or other multi-agent consensus outcomes.
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
    """

    action: str
    reason: str
    surface_hint: Optional[str] = None

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
        • model: str
        • usage: dict (e.g., token counts, cost estimates)

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
        • phase: WorkflowPhase (string value for API)
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
    Typed patch container for L4.

    This is intentionally simple for v10_9:

        key: top-level state key to update
        value: value to assign (or merge, depending on adapter logic)
        scope: reserved for future multi-session/multi-agent contexts
    """

    key: str
    value: Any
    scope: str = "local"


# =============================================================================
# 8. PHASE METADATA (OPTIONAL)
# =============================================================================


@dataclass
class PhaseMetadata:
    """
    Annotates a workflow phase with human-readable context.
    """

    phase: str
    note: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 9. TRACE SPAN / OBSERVABILITY (OPTIONAL)
# =============================================================================


@dataclass
class TraceSpan:
    """
    Simple trace span for L2/L3/L4 observability.

    Fields:
        • name: span name (e.g., "planning", "execution")
        • start_ms, end_ms: timestamps
        • tags: metadata for debugging / optimization
    """

    name: str
    start_ms: float
    end_ms: float
    tags: Dict[str, Any] = field(default_factory=dict)

    def duration_ms(self) -> float:
        return max(0.0, self.end_ms - self.start_ms)


# =============================================================================
# 10. EVENT ENVELOPE (OPTIONAL TELEMETRY)
# =============================================================================


@dataclass
class EventEnvelope:
    """
    Generic event envelope for optional global telemetry integration.

    Example:
        EventEnvelope(
            event="qa_validation",
            timestamp=time.time(),
            payload={"plan_mode": "qa", "issues": [...]},
        )
    """

    event: str
    timestamp: float
    payload: Dict[str, Any]
