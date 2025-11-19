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

    SAFETY_ESCALATION = "safety_escalation"
    COST_OPTIMIZATION = "cost_optimization"
    LATENCY_OPTIMIZATION = "latency_optimization"
    OBSERVABILITY_GAP = "observability_gap"
    USER_FEEDBACK = "user_feedback"
    UNKNOWN = "unknown"


# =============================================================================
# 2. GENERIC EXECUTION RESULT
# =============================================================================


PayloadT = TypeVar("PayloadT")


@dataclass
class ExecutionResult(Generic[PayloadT]):
    """
    L2 → L3 execution contract.

    This structure is deliberately minimal and must remain simple to
    serialize and log. More specialized execution payloads (RAG,
    drafting, QA, etc.) are layered as the "payload" field.
    """

    status: str = "ok"  # "ok" | "error" | "skipped"
    payload: Optional[PayloadT] = None
    errors: List[str] = field(default_factory=list)
    model: Optional[str] = None
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """True when status is ok and no errors were reported."""
        return self.status == "ok" and not self.errors

    def to_dict(self) -> Dict[str, Any]:
        # Best-effort dataclass → dict conversion for payload.
        if self.payload is None:
            payload_dict: Any = None
        elif hasattr(self.payload, "__dataclass_fields__"):
            payload_dict = asdict(self.payload)
        else:
            payload_dict = self.payload

        return {
            "status": self.status,
            "payload": payload_dict,
            "errors": list(self.errors),
            "model": self.model,
            "usage": dict(self.usage),
            "metadata": dict(self.metadata),
        }


# =============================================================================
# 3. WORKFLOW STATE
# =============================================================================


@dataclass
class WorkflowState:
    """
    High-level orchestrator state exposed to external callers.

    This is the L3 → external API contract. It intentionally mirrors
    what the orchestration layer needs to expose for:

        • monitoring
        • HIL (human-in-the-loop) surfaces
        • client applications

    but should NOT contain internal-only structures such as PlanObjects
    or low-level tool call payloads (those are kept internal).
    """

    workflow_id: str
    phase: WorkflowPhase
    node_statuses: Dict[str, NodeStatus] = field(default_factory=dict)
    summary: str = ""
    result: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "phase": self.phase.value,
            "node_statuses": {k: v.value for k, v in self.node_statuses.items()},
            "summary": self.summary,
            "result": copy.deepcopy(self.result),
            "errors": list(self.errors),
            "trace_id": self.trace_id,
            "metadata": copy.deepcopy(self.metadata),
        }


# =============================================================================
# 4. PLAN OBJECTS (L1 → L2/L3 HANDOFF)
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

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        if data is None:
            data = {}
        elif isinstance(data, DictBacked):
            data = data.to_dict()
        elif not isinstance(data, dict):
            raise TypeError(f"DictBacked expects dict-like data, got {type(data)!r}")

        # Merge explicit kwargs last.
        merged = dict(data)
        if kwargs:
            merged.update(kwargs)

        # Bypass __setattr__ to avoid recursion.
        object.__setattr__(self, "_data", merged)

    # --- core helpers ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)

    def deep_clone(self) -> "DictBacked":
        return type(self)(copy.deepcopy(self._data))

    # --- attribute-style access ----------------------------------------------

    def __getattr__(self, key: str) -> Any:
        try:
            return self._data[key]
        except KeyError as exc:
            raise AttributeError(f"{key!r} not found in {type(self).__name__}") from exc

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

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    # --- representation -------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"{type(self).__name__}({self._data!r})"


class PlanObject(DictBacked):
    """
    Canonical planning contract emitted by L1.

    It behaves like a mutable dict with a few convenience properties
    but is constrained enough that L2/L3 can rely on certain fields
    being present.

    Expected common fields:

        • layer: "l1"
        • mode:  "strategy" | "rag" | "drafting" | "bullets" |
                 "qa" | "safety" | "hil" | "meta_learning" |
                 "prompt_engineering"

        • objective: str
        • branches / steps / checks / rules / surfaces
        • handoff: {
              "target_layer": "l2",
              "target_mode": "drafting",
              ...
          }

    This structure is intentionally permissive to keep L1 flexible, but
    L2/L3 should convert portions into typed dataclasses once plans are
    stabilized.
    """

    @property
    def layer(self) -> str:
        return str(self._data.get("layer", ""))

    @property
    def mode(self) -> str:
        return str(self._data.get("mode", ""))

    @property
    def objective(self) -> str:
        return str(self._data.get("objective", ""))

    def with_updates(self, **kwargs: Any) -> "PlanObject":
        data = self.to_dict()
        data.update(kwargs)
        return PlanObject(data)


# =============================================================================
# 5. STRATEGY PAYLOADS
# =============================================================================


@dataclass
class StrategyBranch:
    """Single strategy branch produced by L1 and realized by L2."""

    branch_id: str
    strategy_name: str
    focus_areas: List[str] = field(default_factory=list)
    key_achievements: List[str] = field(default_factory=list)
    tone: str = "professional"
    rationale: str = ""
    complexity: Optional[str] = None
    priority: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
    complexity: Optional[str] = None
    surfaces: List[SelfCorrectionSurface] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 6. RAG PAYLOADS
# =============================================================================


@dataclass
class RAGDocument:
    """Single document/evidence item surfaced by a RAG executor."""

    query: str
    content: str
    source: str = ""
    score: float = 0.0
    rank: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RAGExecutionPayload:
    """
    Execution payload for retrieval executors.

    Typically returned under ExecutionResult.payload["rag"].
    """

    queries: List[str] = field(default_factory=list)
    documents: List[RAGDocument] = field(default_factory=list)
    external_stats: Optional[RAGExternalStats] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 7. BULLET & DRAFT PAYLOADS
# =============================================================================


@dataclass
class BulletExecutionPayload:
    """
    Execution payload for bullet generators.

    Typically returned under ExecutionResult.payload["bullets"].
    """

    bullets: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DraftExecutionPayload:
    """
    Execution payload for drafting executors.

    Typically returned under ExecutionResult.payload["draft"].
    """

    sections: List[Dict[str, Any]] = field(default_factory=list)
    full_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 8. QA PAYLOADS
# =============================================================================


@dataclass
class QAFinding:
    """Single QA finding (check result)."""

    check_id: str
    severity: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QAReport:
    """Aggregate QA report."""

    findings: List[QAFinding] = field(default_factory=list)
    passed: bool = True
    summary: str = ""
    shadow_validation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QAExecutionPayload:
    """Execution payload for QA executors."""

    report: QAReport

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 9. SAFETY PAYLOADS
# =============================================================================


@dataclass
class SafetyIssue:
    """Single safety issue detected in content or state."""

    issue_id: str
    severity: str
    category: str
    message: str
    span: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyReport:
    """Aggregate safety report."""

    issues: List[SafetyIssue] = field(default_factory=list)
    blocked: bool = False
    redacted_text: Optional[str] = None
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyExecutionPayload:
    """Execution payload for safety executors."""

    report: SafetyReport

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 10. HIL (HUMAN-IN-THE-LOOP) PAYLOADS
# =============================================================================


@dataclass
class HILPrompt:
    """Prompt shown to a human-in-the-loop reviewer."""

    prompt_id: str
    instructions: str
    artifacts: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HILResponse:
    """Response from a human-in-the-loop reviewer."""

    prompt_id: str
    accepted: bool
    feedback: str = ""
    edits: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HILExecutionPayload:
    """Execution payload for HIL executors."""

    prompt: HILPrompt
    response: Optional[HILResponse] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 11. META-LEARNING PAYLOADS
# =============================================================================


@dataclass
class MetaLearningFinding:
    """Single meta-learning finding derived from telemetry/state."""

    finding_id: str
    category: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaLearningSnapshot:
    """Snapshot of meta-learning signals for a workflow run."""

    findings: List[MetaLearningFinding] = field(default_factory=list)
    raw_logs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaLearningExecutionPayload:
    """Execution payload for meta-learning executors."""

    snapshot: MetaLearningSnapshot

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 12. MULTI-AGENT VOTING & ARBITRATION
# =============================================================================


@dataclass
class MultiAgentVote:
    """
    Single agent vote within a council.

    Mirrors the council structures used in prior versions while providing a
    stable typed structure for v10_9 multi_agent.py and agents.py.
    """

    agent_id: str
    decision: str
    confidence: float = 0.0
    rationale: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiAgentCouncilResult:
    """Aggregate result of a multi-agent council vote."""

    votes: List[MultiAgentVote] = field(default_factory=list)
    aggregated_decision: str = ""
    aggregated_confidence: float = 0.0
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArbitrationDecision:
    """
    Safety/policy arbitration decision.

    Typically produced by L5 based on safety + QA + council signals.
    """

    action: str  # e.g. "allow", "block", "revise", "escalate"
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckpointInfo:
    """Checkpoint metadata for long-running workflows."""

    checkpoint_id: str
    phase: WorkflowPhase
    created_at: float  # epoch seconds
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 13. STATE PATCHES
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

    This container is intentionally dumb; all application logic lives
    in L4.
    """

    key: str
    value: Any


# =============================================================================
# 14. ORCHESTRATION NODE RESULT (ADDED FOR v10_8 PARITY)
# =============================================================================


@dataclass
class NodeResult:
    """
    Result of a single DAG node execution.

    This recovers the v10_8 NodeResult behavior (status + metadata)
    in a typed v10_9 form for use by L3 orchestration and
    observability, without embedding control-flow logic here.
    """

    node_id: str
    status: NodeStatus
    result: Optional[ExecutionResult[Any]] = None
    started_at: Optional[float] = None  # epoch seconds
    finished_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "metadata": copy.deepcopy(self.metadata),
        }


# =============================================================================
# 15. TRACE SPAN & PHASE METADATA
# =============================================================================


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


# =============================================================================
# 16. CONFIGURATION PROFILES (RESTORED FROM v10_8 CAPABILITIES)
# =============================================================================


class SafetyMode(str, enum.Enum):
    """
    High-level safety modes.

    These map the richer v10_8 safety configuration surface into a
    typed, centralized representation that L5 can consult when making
    decisions. Logic still resides in the safety layer; this file only
    defines the data contract.
    """

    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


@dataclass
class SafetyOutputProfile:
    """
    Configuration struct capturing the *output* side of safety behavior.

    This recovers the functionality of the v10_8 SafetyOutputProfile
    and related defaults without bringing back the legacy format.

    Typical usage:
        • L5 constructs a SafetyOutputProfile per run (or per tenant).
        • Safety engines consult the profile when evaluating content.
    """

    mode: SafetyMode = SafetyMode.BALANCED
    enable_pii_detection: bool = True
    enable_toxicity_detection: bool = True
    enable_bias_detection: bool = True
    enable_self_harm_detection: bool = True
    enable_prompt_injection_detection: bool = True
    enable_policy_deny_lists: bool = True
    enable_policy_allow_lists: bool = False
    redact_on_block: bool = True
    allow_partial_redaction: bool = True
    stability_required: bool = False  # output stability / minimality guarantees

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FramingProfile:
    """
    Configuration for task framing (goal, success criteria, boundaries).

    This restores the intent of v10_8 FramingProfile in a typed form
    that L1 planners can reference when constructing PlanObjects.
    """

    goal: str
    success_criteria: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    guardrails: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    audience: Optional[str] = None
    tone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContextProfile:
    """
    Configuration for context ingestion and sanitization.

    This enables the richer v10_8 behavior:
        • canonicalization
        • pruning / ordering
        • structured ordering guarantees
    """

    canonicalize_case: bool = True
    strip_html: bool = True
    normalize_whitespace: bool = True
    drop_low_priority_sections: bool = True
    enforce_structured_ordering: bool = False
    max_jd_tokens: Optional[int] = None
    max_resume_tokens: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ToolingProfile:
    """
    Configuration for tool behavior and feedback routing.

    This is the modern v10_9 replacement for the v10_8 ToolingProfile.
    """

    enable_shadow_validation: bool = False
    enable_cross_tool_reconciliation: bool = False
    enable_evidence_binding: bool = True
    max_parallel_tools: int = 4
    retry_on_tool_error: bool = True
    max_retries: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 17. PERMISSIONS & ACCESS CONTROL
# =============================================================================


@dataclass
class ToolPermission:
    """
    Per-tool permission descriptor.

    This recovers the behavior of v10_8 tool allow/deny lists in a
    typed, explicit form.
    """

    tool_name: str
    allowed: bool = True
    reason: str = ""
    max_calls_per_run: Optional[int] = None


@dataclass
class RoutingPermission:
    """
    Controls whether a model/endpoint may be used for a given domain
    or mode.

    v10_8 had PERMITTED_MODELS / PERMITTED_ENDPOINTS; this structure
    replaces them with a stricter schema.
    """

    model: str
    endpoint: Optional[str] = None
    allowed: bool = True
    reason: str = ""
    domains: List[str] = field(default_factory=list)
    modes: List[str] = field(default_factory=list)


@dataclass
class AccessPolicy:
    """
    Aggregate permissions configuration for a run or tenant.
    """

    tool_permissions: List[ToolPermission] = field(default_factory=list)
    routing_permissions: List[RoutingPermission] = field(default_factory=list)

    def is_tool_allowed(self, tool_name: str) -> bool:
        for perm in self.tool_permissions:
            if perm.tool_name == tool_name:
                return perm.allowed
        return True

    def is_route_allowed(self, model: str, endpoint: Optional[str] = None) -> bool:
        for perm in self.routing_permissions:
            if perm.model == model and (endpoint is None or perm.endpoint == endpoint):
                return perm.allowed
        return True


# =============================================================================
# 18. PROMPT INJECTION & SAFETY RULE STRUCTURES
# =============================================================================


class InjectionPatternType(str, enum.Enum):
    """
    High-level categories of prompt injection patterns.

    This replaces the large v10_8 injection taxonomy with a typed but
    extensible set of categories, sufficient for L5 and the safety
    stack to reason about attacks.
    """

    GOAL_OVERRIDE = "goal_override"
    ROLE_OVERRIDE = "role_override"
    DATA_EXFILTRATION = "data_exfiltration"
    TOOL_ABUSE = "tool_abuse"
    SAFETY_BYPASS = "safety_bypass"
    PROMPT_LEAK = "prompt_leak"
    META_PROMPTING = "meta_prompting"
    OTHER = "other"


@dataclass
class InjectionPattern:
    """
    Structured description of a known or suspected injection pattern.
    """

    pattern_id: str
    type: InjectionPatternType
    description: str
    severity: str = "medium"
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyRule:
    """
    Granular safety rule.

    v10_8 had SafetyRule / PolicyRule systems; these dataclasses allow
    v10_9 L5 to implement equivalent or stronger behavior.
    """

    rule_id: str
    description: str
    severity: str
    enabled: bool = True
    categories: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyRule:
    """
    Policy rule controlling allowed/denied operations.

    This is intentionally generic so it can represent deny-lists,
    allow-lists, and stability constraints.
    """

    rule_id: str
    action: str  # e.g. "allow", "deny", "escalate"
    target: str  # e.g. "tool:browser", "mode:safety", "domain:resume"
    reason: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 19. OBSERVABILITY & CORRECTION JOURNAL
# =============================================================================


@dataclass
class TraceContext:
    """
    Minimal distributed tracing context.

    v10_8 exposed richer TraceContext structures; here we provide the
    essential fields needed for correlation across logs and spans.
    """

    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    sampled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricEvent:
    """
    Structured metric event emitted by orchestrators or tools.
    """

    name: str
    value: float
    tags: Dict[str, Any] = field(default_factory=dict)
    trace: Optional[TraceContext] = None


@dataclass
class SpanEvent:
    """
    Structured span event for observability, complementing TraceSpan.
    """

    name: str
    duration_ms: float
    tags: Dict[str, Any] = field(default_factory=dict)
    trace: Optional[TraceContext] = None


@dataclass
class CorrectionJournalEntry:
    """
    Single entry in the CORRECTION_JOURNAL used by L4/L5 and
    meta-learning.

    This recovers v10_8's persistent correction logging behavior in a
    typed, append-only form.
    """

    event_id: str
    surface: SelfCorrectionSurface
    message: str
    created_at: float  # epoch seconds
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteTraceEntry:
    """
    Route trace metadata for routing decisions.

    v10_8 tracked route_trace lists; this dataclass exposes the same
    capability in a typed way for routing.py and observability.
    """

    step: str
    model: Optional[str] = None
    endpoint: Optional[str] = None
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
