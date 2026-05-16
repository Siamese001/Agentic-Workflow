"""Runtime Gate Mesh — shared types.

Prefer importing these symbols from :mod:`agentic_core.L5_safety.runtime_gates.contracts`
for new code (W3C fan-in hygiene); definitions remain authoritative here.

Implements the canonical types defined in
``docs/reference/05_Exit_Evaluation_&_Control/Evaluation_Runtime_Gates.md``.

Every runtime gate (G01..G29) returns a ``GateDecision`` whose
``disposition`` is one of the bounded ``Disposition`` values from the spec's
*AUTHORITATIVE RUNTIME DECISIONS* section.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


SCHEMA_VERSION = "00C-1.0.0"


class Result(str, Enum):
    """Canonical gate result vocabulary (00C.7 GateVerdict.result).

    The 5-value result is independent of ``Disposition``. UNKNOWN is never
    converted to PASS — it remains visible to Exit aggregation and triggers
    fail-closed handling on safety/policy/evidence/replay/write paths.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Severity(str, Enum):
    """Severity scale for a verdict (00C.7)."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GraderType(str, Enum):
    """How a verdict was produced (00C.7)."""

    CODE = "code"
    LLM_JUDGE = "LLM_JUDGE"
    HYBRID = "hybrid"
    HUMAN_CALIBRATED = "human_calibrated"
    POLICY_RULE = "policy_rule"


class Disposition(str, Enum):
    """The 15 bounded dispositions every runtime gate may emit.

    Source of truth: spec table *AUTHORITATIVE RUNTIME DECISIONS*.
    """

    ALLOW = "ALLOW"
    DENY = "DENY"
    CLARIFY = "CLARIFY"
    ABSTAIN = "ABSTAIN"
    REROUTE = "REROUTE"
    SHRINK_SCOPE = "SHRINK_SCOPE"
    RETRY = "RETRY"
    HEAL = "HEAL"
    ESCALATE_HITL = "ESCALATE_HITL"
    QUARANTINE = "QUARANTINE"
    REDACT = "REDACT"
    SAFE_FALLBACK = "SAFE_FALLBACK"
    MARK_DEGRADED = "MARK_DEGRADED"
    COMMIT_REQUEST = "COMMIT_REQUEST"
    BLOCK_COMMIT = "BLOCK_COMMIT"


# Per-gate aliases reused by several gates. Matches the spec verbatim where it
# enumerates richer per-gate decision sets that map onto Disposition values
# above (ROUTE_*, READ_ALLOW, etc.). Aliases are exposed as plain strings to
# avoid coupling all 29 gates' decision vocabularies into one mega-enum.
class DecisionAlias(str, Enum):
    """Spec-level decision aliases that are not in the canonical 15-value set.

    Each alias maps to an underlying canonical ``Disposition`` value. Gates
    that use the richer vocabulary store the alias on
    ``GateDecision.alias`` and the canonical resolution on
    ``GateDecision.disposition``.
    """

    THROTTLE = "THROTTLE"  # G01 — narrows ALLOW
    RESTRICT = "RESTRICT"  # G02 — narrows ALLOW
    ROUTE_R1_EXACT_CACHE = "ROUTE_R1_EXACT_CACHE"  # G07
    ROUTE_R1_SEMANTIC_CACHE = "ROUTE_R1_SEMANTIC_CACHE"
    ROUTE_R3_GROUNDED_READ = "ROUTE_R3_GROUNDED_READ"
    ROUTE_R4_SINGLE_ACTION = "ROUTE_R4_SINGLE_ACTION"
    ROUTE_R3_R4_MANAGED_WORKFLOW = "ROUTE_R3_R4_MANAGED_WORKFLOW"
    ROUTE_R5_FALLBACK = "ROUTE_R5_FALLBACK"
    RETRIEVE = "RETRIEVE"  # G08
    REFINE_RETRIEVAL = "REFINE_RETRIEVAL"
    BROADEN = "BROADEN"
    NARROW = "NARROW"
    DECOMPOSE = "DECOMPOSE"
    REROUTE_RECOMMENDATION_ONLY = "REROUTE_RECOMMENDATION_ONLY"
    PASS = "PASS"  # G09
    WEAK_WITH_CAVEATS = "WEAK_WITH_CAVEATS"
    CONFLICTED = "CONFLICTED"
    EMPTY = "EMPTY"
    BLOCKED = "BLOCKED"
    REFINE_ONCE = "REFINE_ONCE"
    EMIT = "EMIT"  # G10
    REBUILD = "REBUILD"
    REJECT = "REJECT"
    SHRINK_CONTEXT = "SHRINK_CONTEXT"
    QUARANTINE_CONTEXT = "QUARANTINE_CONTEXT"
    REQUEST_RETRIEVAL_REFINEMENT = "REQUEST_RETRIEVAL_REFINEMENT"
    BLOCK = "BLOCK"  # G11
    SUBSTITUTE_APPROVED = "SUBSTITUTE_APPROVED"
    PASS_AS_DATA = "PASS_AS_DATA"  # G13
    STRIP = "STRIP"
    REDACT_AND_ALLOW = "REDACT_AND_ALLOW"  # G14
    SANDBOX = "SANDBOX"  # G15
    READ_ALLOW = "READ_ALLOW"  # G16
    READ_DENY = "READ_DENY"
    PROPOSE_UPDATE = "PROPOSE_UPDATE"
    BLOCK_UPDATE = "BLOCK_UPDATE"
    ISOLATE = "ISOLATE"  # G17
    REQUIRE_PERMISSION = "REQUIRE_PERMISSION"
    FORCE_TENANT_SCOPED_RETRIEVAL = "FORCE_TENANT_SCOPED_RETRIEVAL"
    CONTINUE = "CONTINUE"  # G18, G20, G25
    HOLD_NODE = "HOLD_NODE"
    RETURN_BEST_PARTIAL = "RETURN_BEST_PARTIAL"
    FAIL_WORKFLOW = "FAIL_WORKFLOW"
    STOP = "STOP"  # G19
    DEGRADE_MODEL_TIER = "DEGRADE_MODEL_TIER"  # G20
    REDUCE_K = "REDUCE_K"
    STOP_ITERATION = "STOP_ITERATION"
    TIMEOUT = "TIMEOUT"
    REROUTE_PROVIDER = "REROUTE_PROVIDER"
    REPAIR = "REPAIR"  # G21
    REVISE = "REVISE"  # G22
    SAFE_COMPLETE = "SAFE_COMPLETE"  # G23
    DISABLE_TOOL_OR_CONNECTOR = "DISABLE_TOOL_OR_CONNECTOR"
    CERTIFY = "CERTIFY"  # G24
    RERUN_UNDER_FREEZE = "RERUN_UNDER_FREEZE"
    NON_REPLAYABLE = "NON_REPLAYABLE"
    DOWNGRADE_AUTONOMY = "DOWNGRADE_AUTONOMY"  # G25
    FORCE_HITL = "FORCE_HITL"
    OPEN_INCIDENT = "OPEN_INCIDENT"
    NO_WRITE = "NO_WRITE"  # G27
    COMMIT = "COMMIT"
    REJECT_WRITE = "REJECT_WRITE"
    REQUIRE_HITL = "REQUIRE_HITL"
    LOCK_SUBSTRATE = "LOCK_SUBSTRATE"
    ROLLBACK_IF_SUPPORTED = "ROLLBACK_IF_SUPPORTED"
    APPROVE_TO_CONTINUE = "APPROVE_TO_CONTINUE"  # G06
    MODIFY_THEN_RECLEAR = "MODIFY_THEN_RECLEAR"
    RETURN_TO_L1 = "RETURN_TO_L1"
    BLOCK_EXIT = "BLOCK_EXIT"  # G28
    ESCALATE = "ESCALATE"
    ARCHIVE = "ARCHIVE"  # G29
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
    REJECT_PROMOTION = "REJECT_PROMOTION"
    UWG_COMMIT_AFTER_APPROVAL = "UWG_COMMIT_AFTER_APPROVAL"
    BLOCK_LIVE_MUTATION = "BLOCK_LIVE_MUTATION"


@dataclass(frozen=True)
class RegressionSignal:
    """A single live anomaly signal emitted by a runtime gate.

    Spec: every gate's ``Regression signals`` block becomes one or more
    ``RegressionSignal`` instances on the corresponding ``GateDecision``.
    """

    name: str
    value: float = 0.0
    severity: str = "info"  # info | warn | alert
    note: str = ""


@dataclass
class GateContext:
    """The mutable per-run context every runtime gate inspects.

    Fields are intentionally permissive — each gate reads only the slice it
    needs and ignores the rest. The top-level orchestrator populates this
    progressively as the run flows U0 → L1 → L0 → C0 → L2 → L3 → Exit → UWG.
    """

    # Identity / envelope (G01, G02)
    request_id: str = ""
    session_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    trace_id: str = ""
    tenant_id: str = ""
    caller_scope_baseline: dict[str, Any] = field(default_factory=dict)

    # Policy / safety (G04, G24)
    policy_hash: str = ""
    compliance_hash: str = ""
    blueprint_hash: str = ""
    replay_key: str = ""

    # Spec-aligned packet refs for verdict carry-through (00C.7).
    evaluated_packet_ref: str = ""

    # Intent / risk (G03, G05)
    intent: dict[str, Any] = field(default_factory=dict)
    risk_tier: str = ""  # low | medium | high
    reversible: bool = True
    impact_class: str = ""  # read | action | write | egress

    # Routing (G07)
    route_contract: dict[str, Any] = field(default_factory=dict)

    # Retrieval / evidence (G08, G09)
    retrieval_plan: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)

    # Prompt assembly (G10)
    prompt_packet: dict[str, Any] = field(default_factory=dict)

    # Tool / model invocation (G11–G15)
    tool_call: dict[str, Any] = field(default_factory=dict)

    # Memory (G16)
    memory_op: dict[str, Any] = field(default_factory=dict)

    # Workflow (G18, G19)
    workflow_state: dict[str, Any] = field(default_factory=dict)

    # Budget (G20)
    budget: dict[str, Any] = field(default_factory=dict)

    # Output (G21, G22, G23)
    output: dict[str, Any] = field(default_factory=dict)

    # Anomaly baseline (G25)
    baseline: dict[str, Any] = field(default_factory=dict)
    observed: dict[str, Any] = field(default_factory=dict)

    # HITL (G06)
    hitl: dict[str, Any] = field(default_factory=dict)

    # Audit (G28)
    trace_artifacts: dict[str, Any] = field(default_factory=dict)

    # L6 learning (G29)
    learning_signal: dict[str, Any] = field(default_factory=dict)


@dataclass
class GateDecision:
    """The bounded result every runtime gate returns.

    Canonical 00C.7 ``GateVerdict`` fields are present as defaulted attributes
    so existing call sites that construct ``GateDecision(gate_id=..., disposition=...)``
    keep working. Use ``to_verdict()`` to serialize the canonical contract for
    Exit / OTEL / replay handoff.
    """

    gate_id: str  # e.g. "G01"
    disposition: Disposition
    alias: str = ""  # optional richer per-gate value (DecisionAlias)
    reason_codes: list[str] = field(default_factory=list)
    signals: list[RegressionSignal] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    stop_condition_violated: bool = False

    # Canonical 00C.7 GateVerdict fields (defaulted; populated by helpers).
    result: Result = Result.PASS
    severity: Severity = Severity.INFO
    score: float | None = None
    threshold: float | None = None
    grader_type: GraderType = GraderType.CODE
    evidence_refs: list[str] = field(default_factory=list)
    replay_refs: list[str] = field(default_factory=list)
    source_lineage_refs: list[str] = field(default_factory=list)
    confidence: float = 1.0
    abstain_flag: bool = False
    remediation_hint: str = ""
    deterministic_digest: str = ""
    created_at_run_offset: float = 0.0
    schema_version: str = SCHEMA_VERSION
    # Carried from GateContext at evaluation time (set by orchestrator).
    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    trace_id: str = ""
    tenant_id: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    replay_key: str = ""
    evaluated_packet_ref: str = ""
    gate_family: str = ""
    gate_surface: str = ""
    primary_layer: str = ""

    def to_verdict(self) -> dict[str, Any]:
        """Serialize the canonical 00C.7 ``GateVerdict`` shape.

        Field names match the doctrine schema in
        ``00C.7_Runtime_Gates_Verdict_Schema_Disposition_Matrix_detailed.md``.
        """
        return {
            "gate_id": self.gate_id,
            "gate_family": self.gate_family,
            "gate_surface": self.gate_surface,
            "primary_layer": self.primary_layer,
            "evaluated_packet_ref": self.evaluated_packet_ref,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "trace_id": self.trace_id,
            "tenant_id": self.tenant_id,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "replay_key": self.replay_key,
            "result": self.result.value,
            "disposition": self.disposition.value,
            "severity": self.severity.value,
            "reason_codes": list(self.reason_codes),
            "score": self.score,
            "threshold": self.threshold,
            "grader_type": self.grader_type.value,
            "evidence_refs": list(self.evidence_refs),
            "replay_refs": list(self.replay_refs),
            "source_lineage_refs": list(self.source_lineage_refs),
            "confidence": self.confidence,
            "abstain_flag": self.abstain_flag,
            "remediation_hint": self.remediation_hint,
            "deterministic_digest": self.deterministic_digest,
            "created_at_run_offset": self.created_at_run_offset,
            "schema_version": self.schema_version,
        }

    @property
    def is_terminal(self) -> bool:
        """A terminal decision halts the run for this gate's authority."""
        return self.disposition in {
            Disposition.DENY,
            Disposition.QUARANTINE,
            Disposition.BLOCK_COMMIT,
            Disposition.SAFE_FALLBACK,
            Disposition.ABSTAIN,
        }

    @property
    def requires_human(self) -> bool:
        return self.disposition is Disposition.ESCALATE_HITL


__all__ = [
    "Disposition",
    "DecisionAlias",
    "RegressionSignal",
    "GateContext",
    "GateDecision",
    "Result",
    "Severity",
    "GraderType",
    "SCHEMA_VERSION",
]
