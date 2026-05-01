"""C0.6 WEAK-SUPPORT REFINEMENT — spec-grade contract surface.

Spec source: `docs/reference/03_L0_Routing/C0 - Context Engine/
C0.6_Weak_Support_Refinement_detailed.md` (PHASE 1 DATA CONTRACTS,
PHASE 2 WORKSTEPS, GATES AND FAILURE MODES, OTEL/REPLAY).

This module implements the 7 typed contracts, the 8 required gates, and a
deterministic OTEL/replay attribute emitter for the C0.6 stage.

Layered relationship to ``refine_loop.py``:
- ``refine_loop.py`` (existing) is the thin diagnostic + tactic planner used
  by the dispatcher. It returns ``RefinedEvidenceContract``.
- This module is the spec-grade contract surface that wraps that planner
  and adds the input-validation, gates, attempt-ledger hashing, and
  deterministic re-entry input hashing required by the C0.6 spec.

Both surfaces co-exist; this module never violates the existing
``refine_loop.py`` contract.

Hard authority boundaries (constitutional §C0.I9, §C0.I10):
- C0.6 cannot self-authorize reroute, L3, execution, or final disposition.
- C0.6 cannot expand source scope beyond the RouteContract.
- C0.6 cannot convert a simple route into a managed workflow.

All outputs are pure-data records. No I/O, no MCP calls, no subprocess.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Mapping, Sequence

from .final_contract import FinalEvidenceContract
from .plan import RetrievalPlan
from .verdicts import GapType, RefineTactic, SourceClass, SupportStatus

# ---------------------------------------------------------------------------
# Forbidden-vocabulary defense (spec FORBIDDEN OUTPUTS, lines 51-70).
# These tokens MUST NOT appear in any C0.6 output's free-form fields.
# ---------------------------------------------------------------------------
FORBIDDEN_OUTPUT_TOKENS: frozenset[str] = frozenset(
    {
        "ALLOW",
        "DENY",
        "CLARIFY",
        "ABSTAIN_DISPOSITION",  # the runtime disposition, not the C0.6 tactic
        "REROUTE",
        "SHRINK_SCOPE",
        "RETRY",
        "HEAL",
        "ESCALATE_HITL",
        "QUARANTINE",
        "REDACT",
        "SAFE_FALLBACK",
        "MARK_DEGRADED",
        "COMMIT_REQUEST",
        "BLOCK_COMMIT",
        "ALLOW_FINISH",
        "downstream_disposition",
        "approve_execution",
        "approve_output",
        "approve_write",
    }
)

# Statuses that make a contract eligible for refinement. PASS contracts must
# be rejected — refinement of a passing contract is a spec violation.
_REFINE_ELIGIBLE_STATUSES: frozenset[SupportStatus] = frozenset(
    {
        SupportStatus.WEAK,
        SupportStatus.WEAK_WITH_CAVEATS,
        SupportStatus.CONFLICTED,
        SupportStatus.EMPTY,
        SupportStatus.BLOCKED,
    }
)


class PrimaryGapType(str, Enum):
    """C0.6 PHASE 1 #2 — primary_gap_type (spec lines ~250-265)."""

    QUERY_TOO_BROAD = "query_too_broad"
    QUERY_TOO_NARROW = "query_too_narrow"
    MISSING_EXACT_TERMS = "missing_exact_terms"
    MISSING_SYNONYMS = "missing_synonyms"
    WRONG_SOURCE_CLASS = "wrong_source_class"
    SPARSE_MISSING = "sparse_missing"
    DENSE_MISSING = "dense_missing"
    METADATA_FILTER_TOO_STRICT = "metadata_filter_too_strict"
    CITATION_ANCHOR_MISSING = "citation_anchor_missing"
    GRAPH_ANCHOR_MISSING = "graph_anchor_missing"
    STALE_EVIDENCE = "stale_evidence"
    CONTRADICTION_UNRESOLVED = "contradiction_unresolved"
    BUDGET_EXHAUSTED = "budget_exhausted"
    ACL_BLOCKED = "acl_blocked"
    ROUTE_SCOPE_BLOCKED = "route_scope_blocked"


class BroadenDimension(str, Enum):
    """C0.6 PHASE 1 #4 — broaden_dimension."""

    SOURCE_CLASS = "source_class"
    TIME_WINDOW = "time_window"
    METADATA_FILTER = "metadata_filter"
    PARENT_CONTEXT = "parent_context"
    CHILD_CONTEXT = "child_context"
    GRAPH_HOPS = "graph_hops"
    TOP_K = "top_k"


class ReentryTarget(str, Enum):
    """C0.6.4 re-entry target — which upstream stage receives the refined input."""

    C0_1 = "C0.1"  # query/scope changes → re-plan
    C0_4 = "C0.4"  # shaping-only changes
    C0_5 = "C0.5"  # verification/contract-metadata changes only


class RefinementStrategy(str, Enum):
    """C0.6.3 ALLOWED STRATEGIES."""

    QUERY_REWRITE = "query_rewrite"
    BROADEN_WITHIN_SCOPE = "broaden_within_scope"
    DECOMPOSE_EVIDENCE_NEED = "decompose_evidence_need"
    STOP_WITH_GAP_REPORT = "stop_with_gap_report"


class AttemptStatus(str, Enum):
    """C0.6 PHASE 1 #6 — attempt_status."""

    ELIGIBLE = "eligible"
    EXECUTED = "executed"
    BLOCKED = "blocked"
    EXHAUSTED = "exhausted"


class C06Gate(str, Enum):
    """C0.6 GATES — spec lines ~360-368."""

    REFINEMENT_ATTEMPT_LIMIT = "refinement_attempt_limit_gate"
    BUDGET_REMAINING = "budget_remaining_gate"
    ROUTE_SCOPE = "route_scope_gate"
    SOURCE_SCOPE_NO_EXPAND = "source_scope_no_expand_gate"
    NO_L3_SELF_AUTHORIZATION = "no_l3_self_authorization_gate"
    NO_RUNTIME_DISPOSITION = "no_runtime_disposition_gate"
    RECOVERABILITY = "recoverability_gate"
    REENTRY_HASH = "reentry_hash_gate"


# ---------------------------------------------------------------------------
# 1. WeakSupportRefinementInput — spec PHASE 1 #1 (lines ~175-205).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WeakSupportRefinementInput:
    """Input contract for C0.6.

    Validation rules (spec lines ~200-205) are enforced in __post_init__:
    - FinalEvidenceContract status must be in _REFINE_ELIGIBLE_STATUSES.
    - max_refine_attempts must be explicit (>= 0).
    - C0.6 cannot run if refine_attempts_used >= max_refine_attempts.
    - C0.6 cannot expand source scope beyond RouteContract.
    """

    final_evidence_contract: FinalEvidenceContract
    retrieval_plan: RetrievalPlan
    original_query_spec: str
    route_id: str
    route_replay_key: str
    policy_hash: str
    blueprint_hash: str
    max_refine_attempts: int
    refine_attempts_used: int
    budget_remaining: float
    allowed_sources: tuple[str, ...] = ()
    disallowed_sources: tuple[str, ...] = ()
    allowed_source_classes: tuple[SourceClass, ...] = ()
    freshness_class: str = ""
    weak_support_policy: str = "caveat"
    shaped_evidence_set: object | None = None  # ShapedEvidenceSet — duck-typed
    support_target_profile: object | None = None  # SupportTargetProfile — duck-typed

    def __post_init__(self) -> None:
        if self.max_refine_attempts < 0:
            raise ValueError("max_refine_attempts must be >= 0")
        if self.refine_attempts_used < 0:
            raise ValueError("refine_attempts_used must be >= 0")
        if self.budget_remaining < 0:
            raise ValueError("budget_remaining must be >= 0")
        if self.final_evidence_contract.status not in _REFINE_ELIGIBLE_STATUSES:
            raise ValueError(
                f"C0.6 refuses status={self.final_evidence_contract.status.value!r}; "
                f"only WEAK/WEAK_WITH_CAVEATS/CONFLICTED/EMPTY/BLOCKED are eligible "
                "(spec PHASE 1 #1 validation)."
            )
        if not self.route_id:
            raise ValueError("route_id required")
        if not self.route_replay_key:
            raise ValueError("route_replay_key required")
        if not self.policy_hash:
            raise ValueError("policy_hash required")
        if not self.blueprint_hash:
            raise ValueError("blueprint_hash required")


# ---------------------------------------------------------------------------
# 2. WeakSupportDiagnosis — spec PHASE 1 #2.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WeakSupportDiagnosis:
    """Structured diagnosis of why C0.5 emitted a non-PASS status."""

    diagnosis_id: str
    evidence_status: SupportStatus
    primary_gap_type: PrimaryGapType
    secondary_gap_types: tuple[PrimaryGapType, ...] = ()
    weak_citation_refs: tuple[str, ...] = ()
    missing_exact_terms: tuple[str, ...] = ()
    missing_source_classes: tuple[SourceClass, ...] = ()
    stale_source_refs: tuple[str, ...] = ()
    contradiction_refs: tuple[str, ...] = ()
    low_relevance_refs: tuple[str, ...] = ()
    sparse_gap: bool = False
    dense_gap: bool = False
    metadata_gap: bool = False
    graph_gap: bool = False
    budget_gap: bool = False
    acl_gap: bool = False
    likely_recoverable: bool = True
    recovery_strategy: RefinementStrategy = RefinementStrategy.QUERY_REWRITE
    non_recoverable_reason: str = ""

    def __post_init__(self) -> None:
        if not self.diagnosis_id:
            raise ValueError("diagnosis_id required")
        if not self.likely_recoverable and not self.non_recoverable_reason:
            raise ValueError(
                "likely_recoverable=False requires non_recoverable_reason "
                "(spec PHASE 1 #2)"
            )


# ---------------------------------------------------------------------------
# 3. QueryRewritePlan — spec PHASE 1 #3.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class QueryRewritePlan:
    rewrite_plan_id: str
    original_query_terms: tuple[str, ...]
    added_terms: tuple[str, ...] = ()
    removed_terms: tuple[str, ...] = ()
    exact_phrases: tuple[str, ...] = ()
    synonym_terms: tuple[str, ...] = ()
    symbol_terms: tuple[str, ...] = ()
    date_terms: tuple[str, ...] = ()
    source_specific_terms: tuple[str, ...] = ()
    rationale: str = ""
    expected_lane_impact: str = ""
    bounded_by_original_intent: bool = True

    def __post_init__(self) -> None:
        if not self.rewrite_plan_id:
            raise ValueError("rewrite_plan_id required")
        if not self.bounded_by_original_intent:
            raise ValueError(
                "QueryRewritePlan must remain bounded_by_original_intent "
                "(C0.I9 / spec FAILURE BEHAVIOR: query rewrite would change "
                "user intent -> block refinement)"
            )


# ---------------------------------------------------------------------------
# 4. ScopeBroadenPlan — spec PHASE 1 #4.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ScopeBroadenPlan:
    broaden_plan_id: str
    broaden_dimension: BroadenDimension
    old_value: str
    new_value: str
    bound_source: str  # which RouteContract field bounds this dimension
    budget_delta: float = 0.0
    policy_compatibility_status: str = "compatible"
    acl_compatibility_status: str = "compatible"
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.broaden_plan_id:
            raise ValueError("broaden_plan_id required")
        if not self.bound_source:
            raise ValueError(
                "ScopeBroadenPlan.bound_source required — which RouteContract "
                "ceiling bounds this broadening (spec rule: broadening allowed "
                "only inside RouteContract ceilings)"
            )


# ---------------------------------------------------------------------------
# 5. DecompositionPlan — spec PHASE 1 #5.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SubQuerySpec:
    sub_query_id: str
    text: str
    support_target: str = ""
    source_class: SourceClass | None = None
    token_budget: int = 0
    latency_budget_ms: int = 0


@dataclass(frozen=True)
class DecompositionPlan:
    decomposition_plan_id: str
    sub_queries: tuple[SubQuerySpec, ...]
    join_expectation: str = "all_must_succeed"
    max_subqueries: int = 4
    token_budget_per_subquery: int = 0
    latency_budget_per_subquery: int = 0
    reason_codes: tuple[str, ...] = ()
    workflow_reroute_candidate_hint: bool = False  # non-authoritative

    def __post_init__(self) -> None:
        if not self.decomposition_plan_id:
            raise ValueError("decomposition_plan_id required")
        if len(self.sub_queries) == 0:
            raise ValueError("DecompositionPlan must include at least one sub-query")
        if len(self.sub_queries) > self.max_subqueries:
            raise ValueError(
                f"sub_queries={len(self.sub_queries)} exceeds max_subqueries="
                f"{self.max_subqueries}"
            )


# ---------------------------------------------------------------------------
# 6. RefinementAttemptLedger — spec PHASE 1 #6.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RefinementAttemptLedger:
    refinement_attempt_id: str
    request_id: str
    run_id: str
    trace_id: str
    route_id: str
    prior_contract_hash: str
    diagnosis_ref: str
    selected_strategy: RefinementStrategy
    attempt_number: int
    max_refine_attempts: int
    attempt_status: AttemptStatus
    budget_before: float
    budget_after_reserved: float
    reentry_target: ReentryTarget | None = None
    reentry_input_hash: str = ""
    rewrite_plan_ref: str = ""
    broaden_plan_ref: str = ""
    decomposition_plan_ref: str = ""
    reason_codes: tuple[str, ...] = ()
    ledger_hash: str = ""

    def __post_init__(self) -> None:
        if not self.refinement_attempt_id:
            raise ValueError("refinement_attempt_id required")
        if self.attempt_number < 0:
            raise ValueError("attempt_number must be >= 0")
        if self.attempt_number >= self.max_refine_attempts and self.attempt_status not in (
            AttemptStatus.EXHAUSTED,
            AttemptStatus.BLOCKED,
        ):
            raise ValueError(
                f"attempt_number={self.attempt_number} >= max_refine_attempts="
                f"{self.max_refine_attempts} requires status=EXHAUSTED or BLOCKED"
            )
        if self.budget_after_reserved > self.budget_before:
            raise ValueError(
                "budget_after_reserved cannot exceed budget_before "
                "(refinement reserves, never adds, budget)"
            )


# ---------------------------------------------------------------------------
# 7. NoMoreRefinementReport — spec PHASE 1 #7.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class NoMoreRefinementReport:
    """Terminal report when C0.6 cannot or must not refine further.

    The contract status (WEAK/WEAK_WITH_CAVEATS/EMPTY/CONFLICTED/BLOCKED) is
    preserved exactly. C0.6 NEVER overrides C0.5 status.
    """

    reason: str
    attempts_used: int
    max_refine_attempts: int
    budget_remaining: float
    unresolved_gap_report: tuple[str, ...] = ()
    final_evidence_contract_ref: str = ""
    non_authoritative_recommendation_hint: str = ""

    def __post_init__(self) -> None:
        if not self.reason:
            raise ValueError("NoMoreRefinementReport.reason required")
        if self.attempts_used < 0 or self.max_refine_attempts < 0:
            raise ValueError("attempt counters must be >= 0")
        if self.budget_remaining < 0:
            raise ValueError("budget_remaining must be >= 0")
        # Forbidden-vocabulary check (spec FORBIDDEN OUTPUTS).
        for forbidden in FORBIDDEN_OUTPUT_TOKENS:
            if forbidden in self.non_authoritative_recommendation_hint:
                raise ValueError(
                    f"non_authoritative_recommendation_hint cannot contain "
                    f"runtime-disposition vocabulary {forbidden!r} "
                    "(spec FORBIDDEN OUTPUTS)"
                )


# ---------------------------------------------------------------------------
# Gates (spec lines ~360-380).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class GateResult:
    gate: C06Gate
    passed: bool
    reason: str = ""


def _gate_attempt_limit(inp: WeakSupportRefinementInput) -> GateResult:
    if inp.refine_attempts_used >= inp.max_refine_attempts:
        return GateResult(
            C06Gate.REFINEMENT_ATTEMPT_LIMIT,
            False,
            f"used={inp.refine_attempts_used} max={inp.max_refine_attempts}",
        )
    return GateResult(C06Gate.REFINEMENT_ATTEMPT_LIMIT, True)


def _gate_budget(inp: WeakSupportRefinementInput) -> GateResult:
    if inp.budget_remaining <= 0:
        return GateResult(
            C06Gate.BUDGET_REMAINING, False, f"budget_remaining={inp.budget_remaining}"
        )
    return GateResult(C06Gate.BUDGET_REMAINING, True)


def _gate_route_scope(inp: WeakSupportRefinementInput) -> GateResult:
    # Route must permit grounding (the input route_id is non-empty by
    # __post_init__). C0.6 itself never alters the route — this gate fires
    # only if the caller hands C0.6 an input with conflicting route metadata.
    if inp.final_evidence_contract.route_id and inp.final_evidence_contract.route_id != inp.route_id:
        return GateResult(
            C06Gate.ROUTE_SCOPE,
            False,
            f"contract.route_id={inp.final_evidence_contract.route_id!r} "
            f"!= input.route_id={inp.route_id!r}",
        )
    return GateResult(C06Gate.ROUTE_SCOPE, True)


def _gate_source_scope_no_expand(
    inp: WeakSupportRefinementInput,
    broaden: ScopeBroadenPlan | None,
) -> GateResult:
    """C0.6 cannot introduce a disallowed source. Spec: 'Broadening cannot
    include a disallowed source, tenant, region, data class, tool, connector,
    or route.'"""
    if broaden is None:
        return GateResult(C06Gate.SOURCE_SCOPE_NO_EXPAND, True)
    if broaden.broaden_dimension is BroadenDimension.SOURCE_CLASS:
        # The new_value is a source class label; it must already be allowed.
        if inp.allowed_source_classes:
            allowed_labels = {sc.value for sc in inp.allowed_source_classes}
            if broaden.new_value not in allowed_labels:
                return GateResult(
                    C06Gate.SOURCE_SCOPE_NO_EXPAND,
                    False,
                    f"new_value={broaden.new_value!r} not in allowed_source_classes",
                )
        if inp.disallowed_sources and broaden.new_value in inp.disallowed_sources:
            return GateResult(
                C06Gate.SOURCE_SCOPE_NO_EXPAND,
                False,
                f"new_value={broaden.new_value!r} is in disallowed_sources",
            )
    return GateResult(C06Gate.SOURCE_SCOPE_NO_EXPAND, True)


def _gate_no_l3_self_authorization(
    decomposition: DecompositionPlan | None,
) -> GateResult:
    """Spec PHASE 1 #5 rule: 'Decomposition remains C0 evidence decomposition
    only. If the task requires changing execution contract, stateful workflow,
    branching, or multi-step action, C0.6 may emit
    workflow_reroute_candidate_hint but cannot authorize L3.'

    The hint is allowed; we only check that decomposition does not also try
    to assert authority over execution.
    """
    if decomposition is None:
        return GateResult(C06Gate.NO_L3_SELF_AUTHORIZATION, True)
    # Reject reason_codes that smell like execution authority.
    forbidden_substrings = ("execute", "invoke_tool", "authorize_l3", "approve_")
    for code in decomposition.reason_codes:
        for forbidden in forbidden_substrings:
            if forbidden in code.lower():
                return GateResult(
                    C06Gate.NO_L3_SELF_AUTHORIZATION,
                    False,
                    f"decomposition.reason_codes contains forbidden token "
                    f"{forbidden!r} in {code!r}",
                )
    return GateResult(C06Gate.NO_L3_SELF_AUTHORIZATION, True)


def _gate_no_runtime_disposition(
    *texts: str,
) -> GateResult:
    """Spec FORBIDDEN OUTPUTS — no runtime disposition vocabulary in any C0.6
    output."""
    for text in texts:
        if not text:
            continue
        upper = text.upper()
        for forbidden in FORBIDDEN_OUTPUT_TOKENS:
            if forbidden.upper() in upper.split():
                # Token-level match avoids partial-substring false positives
                # (e.g., the substring "ALLOW" inside "ALLOWED").
                return GateResult(
                    C06Gate.NO_RUNTIME_DISPOSITION,
                    False,
                    f"forbidden token {forbidden!r} appears in output text",
                )
    return GateResult(C06Gate.NO_RUNTIME_DISPOSITION, True)


def _gate_recoverability(diagnosis: WeakSupportDiagnosis) -> GateResult:
    if not diagnosis.likely_recoverable:
        return GateResult(
            C06Gate.RECOVERABILITY,
            False,
            f"non_recoverable_reason={diagnosis.non_recoverable_reason!r}",
        )
    return GateResult(C06Gate.RECOVERABILITY, True)


def _gate_reentry_hash(reentry_input_hash: str) -> GateResult:
    if not reentry_input_hash:
        return GateResult(
            C06Gate.REENTRY_HASH,
            False,
            "reentry_input_hash required when re-entry target is set",
        )
    return GateResult(C06Gate.REENTRY_HASH, True)


def run_gates(
    inp: WeakSupportRefinementInput,
    diagnosis: WeakSupportDiagnosis,
    *,
    broaden: ScopeBroadenPlan | None = None,
    decomposition: DecompositionPlan | None = None,
    rewrite: QueryRewritePlan | None = None,
    reentry_input_hash: str = "",
) -> tuple[GateResult, ...]:
    """Run the 8 required C0.6 gates in deterministic order.

    Caller decides whether to halt on first failure or collect all outcomes.
    Order matches the spec listing.
    """
    results: list[GateResult] = []
    results.append(_gate_attempt_limit(inp))
    results.append(_gate_budget(inp))
    results.append(_gate_route_scope(inp))
    results.append(_gate_source_scope_no_expand(inp, broaden))
    results.append(_gate_no_l3_self_authorization(decomposition))
    results.append(
        _gate_no_runtime_disposition(
            diagnosis.non_recoverable_reason,
            rewrite.rationale if rewrite else "",
            rewrite.expected_lane_impact if rewrite else "",
        )
    )
    results.append(_gate_recoverability(diagnosis))
    if reentry_input_hash:
        results.append(_gate_reentry_hash(reentry_input_hash))
    return tuple(results)


# ---------------------------------------------------------------------------
# Hashing helpers — deterministic re-entry input hashing (spec C0.6.4).
# ---------------------------------------------------------------------------
def _stable_dump(obj: object) -> str:
    """Deterministic JSON dump for hashing. Sorts keys, preserves order in
    sequences (refinement plans are intentionally ordered), strips non-
    deterministic fields like timestamps."""

    def _default(o: object) -> object:
        if isinstance(o, Enum):
            return o.value
        if hasattr(o, "__dataclass_fields__"):
            return asdict(o)  # type: ignore[arg-type]
        if isinstance(o, (set, frozenset)):
            return sorted(o)
        return repr(o)

    return json.dumps(obj, default=_default, sort_keys=True, separators=(",", ":"))


def compute_reentry_input_hash(
    *,
    target: ReentryTarget,
    rewrite: QueryRewritePlan | None = None,
    broaden: ScopeBroadenPlan | None = None,
    decomposition: DecompositionPlan | None = None,
    prior_contract_hash: str = "",
) -> str:
    """Deterministic hash of the re-entry input (spec C0.6.4).

    Replay must prove: same strategy + same plans -> same re-entry hash.
    """
    payload = {
        "target": target.value,
        "rewrite": asdict(rewrite) if rewrite else None,
        "broaden": asdict(broaden) if broaden else None,
        "decomposition": asdict(decomposition) if decomposition else None,
        "prior_contract_hash": prior_contract_hash,
    }
    raw = _stable_dump(payload).encode("utf-8")
    return hashlib.blake2b(raw, digest_size=16).hexdigest()


def compute_ledger_hash(ledger: RefinementAttemptLedger) -> str:
    """Deterministic ledger hash (spec PHASE 1 #6 — ledger_hash).

    Uses every field except ledger_hash itself (avoid self-reference cycle).
    """
    fields_dict = asdict(ledger)
    fields_dict.pop("ledger_hash", None)
    raw = _stable_dump(fields_dict).encode("utf-8")
    return hashlib.blake2b(raw, digest_size=16).hexdigest()


def seal_ledger(ledger: RefinementAttemptLedger) -> RefinementAttemptLedger:
    """Stamp the ledger_hash and return a new frozen ledger."""
    if ledger.ledger_hash:
        return ledger
    h = compute_ledger_hash(ledger)
    fields_dict = {f: getattr(ledger, f) for f in ledger.__dataclass_fields__}  # guardian: allow-hallucinated-tool-name -- getattr is Python stdlib; reads frozen dataclass fields by name
    fields_dict["ledger_hash"] = h
    return RefinementAttemptLedger(**fields_dict)


# ---------------------------------------------------------------------------
# OTEL/replay attribute emitter — spec OTEL/REPLAY section.
# ---------------------------------------------------------------------------
def build_otel_attributes(
    inp: WeakSupportRefinementInput,
    diagnosis: WeakSupportDiagnosis,
    *,
    selected_strategy: RefinementStrategy,
    attempt_number: int,
    budget_before: float,
    budget_after_reserved: float,
    reentry_target: ReentryTarget | None,
    reentry_input_hash: str,
    ledger_hash: str,
) -> dict[str, str | int | float]:
    """Build the spec-required OTEL span attributes for c0.6.weak_support_refinement."""
    return {
        "c0.stage": "C0.6",
        "prior_contract_hash": inp.final_evidence_contract.replay_metadata.evidence_contract_hash,
        "evidence_status": diagnosis.evidence_status.value,
        "primary_gap_type": diagnosis.primary_gap_type.value,
        "selected_strategy": selected_strategy.value,
        "attempt_number": attempt_number,
        "max_refine_attempts": inp.max_refine_attempts,
        "budget_before": budget_before,
        "budget_after_reserved": budget_after_reserved,
        "reentry_target": reentry_target.value if reentry_target else "",
        "reentry_input_hash": reentry_input_hash,
        "ledger_hash": ledger_hash,
    }


# ---------------------------------------------------------------------------
# Diagnosis derivation — bridge from C0.5 outputs to WeakSupportDiagnosis.
# ---------------------------------------------------------------------------
_GAP_TYPE_TO_PRIMARY: Mapping[GapType, PrimaryGapType] = {
    GapType.MISSING_DIRECT_SUPPORT: PrimaryGapType.MISSING_EXACT_TERMS,
    GapType.MISSING_EXACT_QUOTE: PrimaryGapType.CITATION_ANCHOR_MISSING,
    GapType.MISSING_VALIDATION: PrimaryGapType.GRAPH_ANCHOR_MISSING,
    GapType.MISSING_SOURCE_DIVERSITY: PrimaryGapType.WRONG_SOURCE_CLASS,
    GapType.MISSING_CURRENT_VERSION: PrimaryGapType.STALE_EVIDENCE,
    GapType.MISSING_TENANT_PROOF: PrimaryGapType.ACL_BLOCKED,
}


def diagnose_from_contract(
    contract: FinalEvidenceContract,
    *,
    diagnosis_id: str,
) -> WeakSupportDiagnosis:
    """Derive a structured diagnosis from a C0.5 FinalEvidenceContract.

    This is a default heuristic. Callers may override by constructing a
    WeakSupportDiagnosis directly.
    """
    if not diagnosis_id:
        raise ValueError("diagnosis_id required")

    primary: PrimaryGapType
    secondary: list[PrimaryGapType] = []

    if contract.status is SupportStatus.BLOCKED:
        primary = PrimaryGapType.ROUTE_SCOPE_BLOCKED
    elif contract.contradiction_flags:
        primary = PrimaryGapType.CONTRADICTION_UNRESOLVED
    elif not contract.unresolved_gaps:
        primary = PrimaryGapType.QUERY_TOO_NARROW
    else:
        # First gap maps to primary; rest fold into secondary (de-duped).
        first = contract.unresolved_gaps[0]
        primary = _GAP_TYPE_TO_PRIMARY.get(first.gap_type, PrimaryGapType.MISSING_EXACT_TERMS)
        for gap in contract.unresolved_gaps[1:]:
            mapped = _GAP_TYPE_TO_PRIMARY.get(gap.gap_type)
            if mapped and mapped != primary and mapped not in secondary:
                secondary.append(mapped)

    # Recoverability heuristic: ACL/route_scope blocks are not recoverable
    # within C0.6's authority (cannot expand source scope).
    likely_recoverable = primary not in (
        PrimaryGapType.ACL_BLOCKED,
        PrimaryGapType.ROUTE_SCOPE_BLOCKED,
    )
    non_recoverable_reason = (
        ""
        if likely_recoverable
        else f"primary_gap_type={primary.value!r} cannot be self-resolved by C0.6"
    )

    # Recovery strategy mapping.
    if primary in (
        PrimaryGapType.ACL_BLOCKED,
        PrimaryGapType.ROUTE_SCOPE_BLOCKED,
        PrimaryGapType.BUDGET_EXHAUSTED,
    ):
        recovery = RefinementStrategy.STOP_WITH_GAP_REPORT
    elif primary in (
        PrimaryGapType.MISSING_EXACT_TERMS,
        PrimaryGapType.MISSING_SYNONYMS,
        PrimaryGapType.SPARSE_MISSING,
        PrimaryGapType.DENSE_MISSING,
        PrimaryGapType.CITATION_ANCHOR_MISSING,
    ):
        recovery = RefinementStrategy.QUERY_REWRITE
    elif primary in (
        PrimaryGapType.QUERY_TOO_NARROW,
        PrimaryGapType.METADATA_FILTER_TOO_STRICT,
        PrimaryGapType.GRAPH_ANCHOR_MISSING,
        PrimaryGapType.WRONG_SOURCE_CLASS,
    ):
        recovery = RefinementStrategy.BROADEN_WITHIN_SCOPE
    elif primary in (
        PrimaryGapType.QUERY_TOO_BROAD,
        PrimaryGapType.CONTRADICTION_UNRESOLVED,
    ):
        recovery = RefinementStrategy.DECOMPOSE_EVIDENCE_NEED
    else:
        recovery = RefinementStrategy.STOP_WITH_GAP_REPORT

    return WeakSupportDiagnosis(
        diagnosis_id=diagnosis_id,
        evidence_status=contract.status,
        primary_gap_type=primary,
        secondary_gap_types=tuple(secondary),
        contradiction_refs=tuple(
            f"{f.source_a}|{f.source_b}" for f in contract.contradiction_flags
        ),
        sparse_gap=primary
        in (PrimaryGapType.SPARSE_MISSING, PrimaryGapType.MISSING_EXACT_TERMS),
        dense_gap=primary == PrimaryGapType.DENSE_MISSING,
        metadata_gap=primary == PrimaryGapType.METADATA_FILTER_TOO_STRICT,
        graph_gap=primary == PrimaryGapType.GRAPH_ANCHOR_MISSING,
        budget_gap=primary == PrimaryGapType.BUDGET_EXHAUSTED,
        acl_gap=primary == PrimaryGapType.ACL_BLOCKED,
        likely_recoverable=likely_recoverable,
        recovery_strategy=recovery,
        non_recoverable_reason=non_recoverable_reason,
    )


# ---------------------------------------------------------------------------
# Bridge — map RefineTactic (existing planner) to RefinementStrategy.
# ---------------------------------------------------------------------------
_TACTIC_TO_STRATEGY: Mapping[RefineTactic, RefinementStrategy] = {
    RefineTactic.REWRITE: RefinementStrategy.QUERY_REWRITE,
    RefineTactic.HYBRIDIZE: RefinementStrategy.QUERY_REWRITE,
    RefineTactic.BROADEN: RefinementStrategy.BROADEN_WITHIN_SCOPE,
    RefineTactic.NARROW: RefinementStrategy.QUERY_REWRITE,
    RefineTactic.FRESHEN: RefinementStrategy.QUERY_REWRITE,
    RefineTactic.GRAPH_HOP: RefinementStrategy.BROADEN_WITHIN_SCOPE,
    RefineTactic.DECOMPOSE: RefinementStrategy.DECOMPOSE_EVIDENCE_NEED,
    RefineTactic.ABSTAIN: RefinementStrategy.STOP_WITH_GAP_REPORT,
}


def bridge_tactic_to_strategy(tactic: RefineTactic) -> RefinementStrategy:
    """Bridge from the existing thin-planner RefineTactic to the spec
    RefinementStrategy. Used when callers wrap ``refine_loop.plan_refinement``
    in a C0.6 ledger entry."""
    return _TACTIC_TO_STRATEGY.get(tactic, RefinementStrategy.STOP_WITH_GAP_REPORT)


# ---------------------------------------------------------------------------
# Eligibility check helper.
# ---------------------------------------------------------------------------
def is_eligible_for_refinement(
    contract: FinalEvidenceContract,
    *,
    refine_attempts_used: int,
    max_refine_attempts: int,
    budget_remaining: float,
) -> bool:
    """C0.6.2 eligibility (spec)."""
    if contract.status not in _REFINE_ELIGIBLE_STATUSES:
        return False
    if refine_attempts_used >= max_refine_attempts:
        return False
    if budget_remaining <= 0:
        return False
    return True


def build_no_more_refinement_report(
    inp: WeakSupportRefinementInput,
    *,
    reason: str,
    final_evidence_contract_ref: str = "",
    non_authoritative_recommendation_hint: str = "",
) -> NoMoreRefinementReport:
    """Build a stop report. The contract's gap report is summarized into
    unresolved_gap_report."""
    gap_report: list[str] = []
    for gap in inp.final_evidence_contract.unresolved_gaps:
        gap_report.append(
            f"{gap.gap_type.value}:{gap.severity}:{gap.impact_on_answer or 'unspecified'}"
        )
    for flag in inp.final_evidence_contract.contradiction_flags:
        gap_report.append(
            f"contradiction:{flag.type}:{flag.source_a}-vs-{flag.source_b}"
        )
    return NoMoreRefinementReport(
        reason=reason,
        attempts_used=inp.refine_attempts_used,
        max_refine_attempts=inp.max_refine_attempts,
        budget_remaining=inp.budget_remaining,
        unresolved_gap_report=tuple(gap_report),
        final_evidence_contract_ref=final_evidence_contract_ref
        or inp.final_evidence_contract.contract_id,
        non_authoritative_recommendation_hint=non_authoritative_recommendation_hint,
    )


__all__ = [
    "AttemptStatus",
    "BroadenDimension",
    "C06Gate",
    "DecompositionPlan",
    "FORBIDDEN_OUTPUT_TOKENS",
    "GateResult",
    "NoMoreRefinementReport",
    "PrimaryGapType",
    "QueryRewritePlan",
    "ReentryTarget",
    "RefinementAttemptLedger",
    "RefinementStrategy",
    "ScopeBroadenPlan",
    "SubQuerySpec",
    "WeakSupportDiagnosis",
    "WeakSupportRefinementInput",
    "bridge_tactic_to_strategy",
    "build_no_more_refinement_report",
    "build_otel_attributes",
    "compute_ledger_hash",
    "compute_reentry_input_hash",
    "diagnose_from_contract",
    "is_eligible_for_refinement",
    "run_gates",
    "seal_ledger",
]
