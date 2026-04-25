"""L1PlanContract — mandatory typed output of L1 reasoning (B04 — GAP-002, REQ-003).

L1 reasoning MUST produce this contract.  L0 routing MUST validate it before
consuming.  grounding_required=True forces the C0 retrieval path.

Layer authority: L1 (cognition plane).
L0 imports L1PlanContract for consumption; L1 must never import from L0 for this type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_dispatches_execution_plan,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "plan_contract_types")
emit_determinism_digest("p0", "plan_contract_types")
_emit_reads_policy_state("p1", "plan_contract_types", "L1")
_emit_verifies_policy("p1", "plan_contract_types", "plan_policy_check")
_emit_verifies_boundary("p1", "plan_contract_types", "plan_boundary_check")
_emit_hard_fails_untranscripted("p1", "plan_contract_types")
_emit_gated_by_confidence("p1", "plan_contract_types", "plan_confidence_gate")
_emit_dispatches_execution_plan("p1", "plan_contract_types", "l1_plan_dispatch")


class PlanContractViolation(ValueError):
    """Raised when L1PlanContract validation fails at the reasoning chokepoint.

    L0 must not consume L1 output that fails this check.
    """


class ReasoningMode(str, Enum):
    """How L1 determined the plan."""

    CHAIN_OF_THOUGHT = "CHAIN_OF_THOUGHT"
    REACT = "REACT"
    DIRECT = "DIRECT"
    DECOMPOSED = "DECOMPOSED"


@dataclass(frozen=True)
class L1PlanContract:
    """Mandatory typed output of L1 reasoning (REQ-003).

    All seven fields are required.  grounding_required drives C0 retrieval.
    L0 router validates this contract before dispatching.

    Fields:
        plan_id           — unique identifier for this plan instance
        request_id        — the upstream request this plan serves
        policy_hash       — hash of the policy snapshot used during reasoning
        reasoning_mode    — ReasoningMode enum value
        grounding_required — if True, L0 MUST invoke C0 retrieval before dispatch
        confidence_score  — 0.0–1.0; below threshold triggers ESCALATE_TO_HITL at exit gate
        steps             — ordered list of plan step dicts (non-empty)
    """

    plan_id: str
    request_id: str
    policy_hash: str
    reasoning_mode: ReasoningMode
    grounding_required: bool
    confidence_score: float
    steps: tuple

    _REQUIRED_FIELDS: tuple = field(
        default=(
            "plan_id",
            "request_id",
            "policy_hash",
            "reasoning_mode",
            "grounding_required",
            "confidence_score",
            "steps",
        ),
        init=False,
        repr=False,
        compare=False,
    )

    def validate(self) -> None:
        """Raise PlanContractViolation if any mandatory field is missing or invalid.

        Called by reasoning_chokepoint before returning plan to L0.
        """
        missing = []
        for f in self._REQUIRED_FIELDS:
            val = getattr(self, f, None)
            if val is None:
                missing.append(f)
        if missing:
            raise PlanContractViolation(
                f"L1PlanContract is missing mandatory fields: {missing}. "
                "All L1 reasoning paths must produce a complete plan contract."
            )
        if not isinstance(self.reasoning_mode, ReasoningMode):
            raise PlanContractViolation(
                f"reasoning_mode must be a ReasoningMode enum, got {type(self.reasoning_mode)}"
            )
        if not (0.0 <= self.confidence_score <= 1.0):
            raise PlanContractViolation(
                f"confidence_score must be in [0.0, 1.0], got {self.confidence_score}"
            )
        if isinstance(self.steps, str) or not hasattr(self.steps, "__iter__"):
            raise PlanContractViolation(
                "steps must be a tuple or list of plan step dicts, not a bare string or non-sequence."
            )
        if not self.steps:
            raise PlanContractViolation(
                "steps must be a non-empty sequence — L1 must produce at least one plan step."
            )
        if not self.plan_id.strip():
            raise PlanContractViolation("plan_id must be a non-empty string.")
        if not self.request_id.strip():
            raise PlanContractViolation("request_id must be a non-empty string.")
        if not self.policy_hash.strip():
            raise PlanContractViolation("policy_hash must be a non-empty string.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "request_id": self.request_id,
            "policy_hash": self.policy_hash,
            "reasoning_mode": self.reasoning_mode.value,
            "grounding_required": self.grounding_required,
            "confidence_score": self.confidence_score,
            "steps": list(self.steps),
        }


# ============================================================================
# L1PlanContract v2 — ADR-043 (Proposed)
# ----------------------------------------------------------------------------
# Adds typed fields required by the revised v33 §2 doctrine:
#   proposed_route, query_spec, task_spec (typed), route_risk,
#   declared_assumptions, unresolved_gaps, published_rationale,
#   planner_telemetry.
#
# v1 (L1PlanContract) is retained as a 90-day back-compat shim.  Callers opt
# into v2 on their own schedule; the CI gate
# ``ops_scripts/ci/check_l1_plan_contract_fields.py`` tracks migration.
#
# Redaction invariant:  private_scratchpad does NOT exist on this contract.
# Only published_rationale crosses L1 → L0.  The adapter from ReasoningPlan /
# engine state to L1PlanContractV2 is responsible for stripping scratchpad.
# ============================================================================


class ProposedRoute(str, Enum):
    """L0 route intent declared by the L1 planner.

    Mirrors the route labels in ``agentic_process_mapping_v33.md`` §3.
    CLARIFY is a distinct route that does NOT reach L0 dispatch — the exit
    gate at [5] must surface the clarification request to the user.
    """

    R1A = "R1A"
    R1B = "R1B"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"
    CLARIFY = "CLARIFY"
    # v5 doctrine: explicit managed-workflow route (was implicit via L3 dispatch).
    R3R4_MANAGED_WORKFLOW = "R3R4_MANAGED_WORKFLOW"


class ConfidenceBand(str, Enum):
    """Doctrine v5 § ROUTE_HINT — discrete confidence bucket.

    Maps to plan's ``confidence_score`` ranges:
      LOW    — score < 0.55
      MEDIUM — 0.55 ≤ score < 0.80
      HIGH   — score ≥ 0.80
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceBand":
        if score >= 0.80:
            return cls.HIGH
        if score >= 0.55:
            return cls.MEDIUM
        return cls.LOW


class AssumptionGrade(str, Enum):
    """Fact-grading label applied to each declared_assumption (const. §20)."""

    DIRECTLY_OBSERVED = "DIRECTLY_OBSERVED"
    DERIVED = "DERIVED"
    UNRESOLVED = "UNRESOLVED"


class RiskBand(str, Enum):
    """Coarse risk banding used by route_risk to keep L0/L5 policy simple."""

    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"


class Reversibility(str, Enum):
    """Irreversibility signature for route_risk.

    READ   — pure retrieval, fully reversible
    ACTION — external side-effect but bounded/rollback-able
    WRITE  — durable state mutation (requires UWG)
    """

    READ = "READ"
    ACTION = "ACTION"
    WRITE = "WRITE"


class SupportTarget(str, Enum):
    """Answer-support expectation declared by L1.

    Mirrors ``02_L1_Reasoning_Plan_Generation_v4.md`` line 183::

        support_target: none / citation / direct span / code location
                       / policy clause / evidence bundle
    """

    NONE = "none"
    CITATION = "citation"
    DIRECT_SPAN = "direct_span"
    CODE_LOCATION = "code_location"
    POLICY_CLAUSE = "policy_clause"
    EVIDENCE_BUNDLE = "evidence_bundle"


class LowestViableAgency(str, Enum):
    """The smallest agentic posture that still satisfies the request.

    Doc reference line 133 / line 185 — V4 simplification gate.

    ANSWER_DIRECTLY — pure prose response, no retrieval, no tool use.
    GROUNDED_READ   — single C0 retrieval pass + answer.
    SINGLE_ACTION   — one bounded tool call.
    WORKFLOW        — multi-step orchestration.
    FALLBACK        — abstain / clarify / refuse.
    """

    ANSWER_DIRECTLY = "answer_directly"
    GROUNDED_READ = "grounded_read"
    SINGLE_ACTION = "single_action"
    WORKFLOW = "workflow"
    FALLBACK = "fallback"


class EscalationHint(str, Enum):
    """Why downstream layers may need to escalate (L5 / HITL / UWG).

    Doc reference line 132 / line 186. ``NONE`` is the default; any
    other value alerts the L5 exit gate that the plan crosses a risk
    threshold even if it currently validates.
    """

    NONE = "none"
    HIGH_IMPACT = "high_impact"
    IRREVERSIBLE = "irreversible"
    AMBIGUOUS_AUTHORITY = "ambiguous_authority"
    UNSAFE = "unsafe"
    INSUFFICIENT_SUPPORT = "insufficient_support"


class ClarifyOrAbstainMarker(str, Enum):
    """V5 outcome marker — set when bounded completion is not safe.

    Doc reference line 184. ``NONE`` is the default for ordinary plans;
    the other values are mutually exclusive and instruct the exit gate
    on how to surface the situation to the user.
    """

    NONE = "none"
    CLARIFY = "clarify"
    ABSTAIN = "abstain"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class Assumption:
    """A single declared assumption with its fact-grade."""

    statement: str
    grade: AssumptionGrade

    def to_dict(self) -> dict[str, Any]:
        return {"statement": self.statement, "grade": self.grade.value}


@dataclass(frozen=True)
class RouteRisk:
    """Cost / latency / safety / reversibility signature of the proposed plan."""

    cost_band: RiskBand
    latency_band: RiskBand
    safety_band: RiskBand
    reversibility: Reversibility

    def to_dict(self) -> dict[str, Any]:
        return {
            "cost_band": self.cost_band.value,
            "latency_band": self.latency_band.value,
            "safety_band": self.safety_band.value,
            "reversibility": self.reversibility.value,
        }


@dataclass(frozen=True)
class ExpectedGroundTruth:
    """The evidence signal a plan step is expected to produce.

    Satisfies BP-A4 (ground-truth feedback each step) — the exit gate can
    compare observed evidence against this declaration to decide REPLAN.
    """

    signal_kind: str  # e.g. "document_set", "tool_result", "metric"
    shape_hint: str  # informal shape / schema hint
    success_predicate: str  # natural-language predicate describing success

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_kind": self.signal_kind,
            "shape_hint": self.shape_hint,
            "success_predicate": self.success_predicate,
        }


@dataclass(frozen=True)
class PlanTaskStep:
    """A single step on the L1 plan's task_spec.

    Distinct from ``reasoning_plan.PlanStep`` (which is a hash-based audit
    trail artifact).  PlanTaskStep is the semantic step carried across the
    L1 → L0 contract boundary.
    """

    step_id: str
    description: str
    expected_ground_truth: ExpectedGroundTruth

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "description": self.description,
            "expected_ground_truth": self.expected_ground_truth.to_dict(),
        }


@dataclass(frozen=True)
class QuerySpec:
    """Retrieval ask for C0 when grounding_required=True.

    ``query_text`` is the search string / intent; ``freshness_window_s`` caps
    how stale cached evidence may be; ``max_results`` bounds retrieval fanout.
    """

    query_text: str
    freshness_window_s: int
    max_results: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_text": self.query_text,
            "freshness_window_s": self.freshness_window_s,
            "max_results": self.max_results,
        }


@dataclass(frozen=True)
class PlannerTelemetry:
    """Observability payload for planner-on vs planner-off overhead analysis.

    Emitted alongside the contract so L6 can compare planner cost against the
    quality lift it produces (Google ADK BP-G5).
    """

    refinements_used: int
    wall_clock_ms: int
    token_usage: int
    critic_iterations: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "refinements_used": self.refinements_used,
            "wall_clock_ms": self.wall_clock_ms,
            "token_usage": self.token_usage,
            "critic_iterations": self.critic_iterations,
        }


@dataclass(frozen=True)
class L1PlanContractV2:
    """ADR-043 L1PlanContract v2 — typed planner output for L1 → L0 handoff.

    All fields are required unless typed as ``Optional``.  query_spec is
    required iff grounding_required=True.  published_rationale MUST have
    been run through the redaction adapter — private scratchpad must not
    appear here.
    """

    plan_id: str
    request_id: str
    policy_hash: str
    proposed_route: ProposedRoute
    reasoning_mode: ReasoningMode
    query_spec: Optional[QuerySpec]
    task_spec: tuple
    route_risk: RouteRisk
    confidence_score: float
    grounding_required: bool
    declared_assumptions: tuple
    unresolved_gaps: tuple
    published_rationale: str
    planner_telemetry: PlannerTelemetry
    # ── v4 doctrine extensions (additive, default-safe) ────────────────
    # Doc: 02_L1_Reasoning_Plan_Generation_v4.md § L1 PLAN OUTPUT CONTRACT.
    # Defaults preserve back-compat with v2 callers that pre-date these
    # fields; new callers SHOULD populate them.
    support_target: SupportTarget = SupportTarget.NONE
    lowest_viable_agency: LowestViableAgency = LowestViableAgency.ANSWER_DIRECTLY
    escalation_hint: EscalationHint = EscalationHint.NONE
    clarify_or_abstain_marker: ClarifyOrAbstainMarker = ClarifyOrAbstainMarker.NONE

    _REQUIRED_FIELDS: tuple = field(
        default=(
            "plan_id",
            "request_id",
            "policy_hash",
            "proposed_route",
            "reasoning_mode",
            "task_spec",
            "route_risk",
            "confidence_score",
            "grounding_required",
            "declared_assumptions",
            "unresolved_gaps",
            "published_rationale",
            "planner_telemetry",
            "support_target",
            "lowest_viable_agency",
            "escalation_hint",
            "clarify_or_abstain_marker",
        ),
        init=False,
        repr=False,
        compare=False,
    )

    def validate(self) -> None:
        """Raise PlanContractViolation if any mandatory field is missing or invalid."""
        missing = []
        for f in self._REQUIRED_FIELDS:
            val = getattr(self, f, None)
            if val is None:
                missing.append(f)
        if missing:
            raise PlanContractViolation(f"L1PlanContractV2 is missing mandatory fields: {missing}.")
        if not isinstance(self.proposed_route, ProposedRoute):
            raise PlanContractViolation(
                f"proposed_route must be ProposedRoute enum, got {type(self.proposed_route)}"
            )
        if not isinstance(self.reasoning_mode, ReasoningMode):
            raise PlanContractViolation(
                f"reasoning_mode must be ReasoningMode enum, got {type(self.reasoning_mode)}"
            )
        if not isinstance(self.route_risk, RouteRisk):
            raise PlanContractViolation(f"route_risk must be RouteRisk, got {type(self.route_risk)}")
        if not isinstance(self.planner_telemetry, PlannerTelemetry):
            raise PlanContractViolation(
                f"planner_telemetry must be PlannerTelemetry, got {type(self.planner_telemetry)}"
            )
        if not (0.0 <= self.confidence_score <= 1.0):
            raise PlanContractViolation(
                f"confidence_score must be in [0.0, 1.0], got {self.confidence_score}"
            )
        # task_spec shape
        if isinstance(self.task_spec, str) or not hasattr(self.task_spec, "__iter__"):
            raise PlanContractViolation(
                "task_spec must be a tuple of PlanTaskStep, not a bare string or non-sequence."
            )
        if not self.task_spec:
            raise PlanContractViolation("task_spec must be non-empty — L1 must produce at least one step.")
        for idx, step in enumerate(self.task_spec):
            if not isinstance(step, PlanTaskStep):
                raise PlanContractViolation(f"task_spec[{idx}] must be PlanTaskStep, got {type(step)}")
        # declared_assumptions shape
        if isinstance(self.declared_assumptions, str) or not hasattr(self.declared_assumptions, "__iter__"):
            raise PlanContractViolation("declared_assumptions must be a tuple of Assumption.")
        for idx, a in enumerate(self.declared_assumptions):
            if not isinstance(a, Assumption):
                raise PlanContractViolation(f"declared_assumptions[{idx}] must be Assumption, got {type(a)}")
        # unresolved_gaps shape
        if isinstance(self.unresolved_gaps, str) or not hasattr(self.unresolved_gaps, "__iter__"):
            raise PlanContractViolation("unresolved_gaps must be a tuple of str.")
        for idx, g in enumerate(self.unresolved_gaps):
            if not isinstance(g, str):
                raise PlanContractViolation(f"unresolved_gaps[{idx}] must be str, got {type(g)}")
        # grounding_required ⇒ query_spec required
        if self.grounding_required and self.query_spec is None:
            raise PlanContractViolation("grounding_required=True requires a non-None query_spec.")
        if self.query_spec is not None and not isinstance(self.query_spec, QuerySpec):
            raise PlanContractViolation(f"query_spec must be QuerySpec or None, got {type(self.query_spec)}")
        # non-empty string invariants
        for fname in ("plan_id", "request_id", "policy_hash", "published_rationale"):
            val = getattr(self, fname)
            if not val or not val.strip():
                raise PlanContractViolation(f"{fname} must be a non-empty string.")
        # CLARIFY route carries its own contract — cannot be dispatched
        # to L0 as a normal plan.  Exit gate surfaces it to the user.
        if self.proposed_route == ProposedRoute.CLARIFY and self.grounding_required:
            raise PlanContractViolation(
                "proposed_route=CLARIFY is incompatible with grounding_required=True."
            )
        # Scratchpad redaction canary — if caller accidentally left the
        # private scratchpad tag in the published rationale, fail closed.
        if "<<<PRIVATE_SCRATCHPAD" in self.published_rationale:
            raise PlanContractViolation(
                "published_rationale contains unredacted private scratchpad; "
                "adapter must strip scratchpad before crossing L1 → L0."
            )
        # v4 doctrine extensions — enum-typed fields must be the right enum.
        if not isinstance(self.support_target, SupportTarget):
            raise PlanContractViolation(
                f"support_target must be SupportTarget enum, got {type(self.support_target)}"
            )
        if not isinstance(self.lowest_viable_agency, LowestViableAgency):
            raise PlanContractViolation(
                f"lowest_viable_agency must be LowestViableAgency enum, got {type(self.lowest_viable_agency)}"
            )
        if not isinstance(self.escalation_hint, EscalationHint):
            raise PlanContractViolation(
                f"escalation_hint must be EscalationHint enum, got {type(self.escalation_hint)}"
            )
        if not isinstance(self.clarify_or_abstain_marker, ClarifyOrAbstainMarker):
            raise PlanContractViolation(
                "clarify_or_abstain_marker must be ClarifyOrAbstainMarker enum, "
                f"got {type(self.clarify_or_abstain_marker)}"
            )
        # CLARIFY route ⇔ clarify_or_abstain_marker must agree on intent.
        if (
            self.proposed_route == ProposedRoute.CLARIFY
            and self.clarify_or_abstain_marker == ClarifyOrAbstainMarker.NONE
        ):
            raise PlanContractViolation("proposed_route=CLARIFY requires clarify_or_abstain_marker != NONE.")
        # Plans flagged with support_target != NONE must declare grounding,
        # otherwise the support claim is unbounded (V2 safety check).
        if (
            self.support_target
            in (
                SupportTarget.CITATION,
                SupportTarget.DIRECT_SPAN,
                SupportTarget.EVIDENCE_BUNDLE,
                SupportTarget.POLICY_CLAUSE,
            )
            and not self.grounding_required
        ):
            raise PlanContractViolation(
                f"support_target={self.support_target.value} requires grounding_required=True."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "request_id": self.request_id,
            "policy_hash": self.policy_hash,
            "proposed_route": self.proposed_route.value,
            "reasoning_mode": self.reasoning_mode.value,
            "query_spec": self.query_spec.to_dict() if self.query_spec else None,
            "task_spec": [s.to_dict() for s in self.task_spec],
            "route_risk": self.route_risk.to_dict(),
            "confidence_score": self.confidence_score,
            "grounding_required": self.grounding_required,
            "declared_assumptions": [a.to_dict() for a in self.declared_assumptions],
            "unresolved_gaps": list(self.unresolved_gaps),
            "published_rationale": self.published_rationale,
            "planner_telemetry": self.planner_telemetry.to_dict(),
            "support_target": self.support_target.value,
            "lowest_viable_agency": self.lowest_viable_agency.value,
            "escalation_hint": self.escalation_hint.value,
            "clarify_or_abstain_marker": self.clarify_or_abstain_marker.value,
        }

    def to_v1(self) -> L1PlanContract:
        """Back-compat projection to v1 shape for legacy L0 consumers.

        Drops v2-only fields.  Used by the shim during the 90-day migration
        window while downstream callers migrate to v2.
        """
        return L1PlanContract(
            plan_id=self.plan_id,
            request_id=self.request_id,
            policy_hash=self.policy_hash,
            reasoning_mode=self.reasoning_mode,
            grounding_required=self.grounding_required,
            confidence_score=self.confidence_score,
            steps=tuple(s.to_dict() for s in self.task_spec),
        )

    @classmethod
    def from_v1(
        cls,
        v1: L1PlanContract,
        *,
        proposed_route: ProposedRoute,
        route_risk: RouteRisk,
        task_spec: tuple,
        declared_assumptions: tuple = (),
        unresolved_gaps: tuple = (),
        published_rationale: str = "",
        planner_telemetry: Optional[PlannerTelemetry] = None,
        query_spec: Optional[QuerySpec] = None,
        # v4 doctrine extensions — optional for back-compat with old call sites.
        support_target: SupportTarget = SupportTarget.NONE,
        lowest_viable_agency: LowestViableAgency = LowestViableAgency.ANSWER_DIRECTLY,
        escalation_hint: EscalationHint = EscalationHint.NONE,
        clarify_or_abstain_marker: ClarifyOrAbstainMarker = ClarifyOrAbstainMarker.NONE,
    ) -> "L1PlanContractV2":
        """Forward-migrate a v1 contract by supplying the v2-only fields.

        Used by callers that still produce v1 today but want to emit v2 with
        defaulted enrichments.  The supplied task_spec replaces v1.steps.
        v4 doctrine fields default to their NONE/ANSWER_DIRECTLY sentinels.
        """
        telemetry = planner_telemetry or PlannerTelemetry(
            refinements_used=0,
            wall_clock_ms=0,
            token_usage=0,
            critic_iterations=0,
        )
        # If the caller is upgrading a CLARIFY route from v1, ensure the
        # v4 invariant (CLARIFY ⇒ marker != NONE) holds without requiring
        # the caller to know about the new field.
        if (
            proposed_route == ProposedRoute.CLARIFY
            and clarify_or_abstain_marker == ClarifyOrAbstainMarker.NONE
        ):
            clarify_or_abstain_marker = ClarifyOrAbstainMarker.CLARIFY
        return cls(
            plan_id=v1.plan_id,
            request_id=v1.request_id,
            policy_hash=v1.policy_hash,
            proposed_route=proposed_route,
            reasoning_mode=v1.reasoning_mode,
            query_spec=query_spec,
            task_spec=task_spec,
            route_risk=route_risk,
            confidence_score=v1.confidence_score,
            grounding_required=v1.grounding_required,
            declared_assumptions=declared_assumptions,
            unresolved_gaps=unresolved_gaps,
            published_rationale=published_rationale
            or (f"Auto-migrated from L1PlanContract v1 for plan_id={v1.plan_id}"),
            planner_telemetry=telemetry,
            support_target=support_target,
            lowest_viable_agency=lowest_viable_agency,
            escalation_hint=escalation_hint,
            clarify_or_abstain_marker=clarify_or_abstain_marker,
        )


__all__ = [
    "Assumption",
    "AssumptionGrade",
    "ClarifyOrAbstainMarker",
    "ConfidenceBand",
    "EscalationHint",
    "ExpectedGroundTruth",
    "L1PlanContract",
    "L1PlanContractV2",
    "LowestViableAgency",
    "PlanContractViolation",
    "PlanTaskStep",
    "PlannerTelemetry",
    "ProposedRoute",
    "QuerySpec",
    "ReasoningMode",
    "Reversibility",
    "RiskBand",
    "RouteRisk",
    "SupportTarget",
]
