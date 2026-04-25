"""V1-V5 semantic validators for L1 plan output.

Doctrine: ``02_L1_Reasoning_Plan_Generation_v4.md`` § "THE THINKING DESK"
inspect/check stages V1..V5.

V1 — DID WE LISTEN?           goal alignment, constraints honored, format right
V2 — IS IT SAFE?              policy bounds, no forbidden actions, no UWG bypass
V3 — DOES IT MAKE SENSE?      deps resolve, executable, no circular deps
V4 — CAN IT BE SIMPLER?       lowest viable agency
V5 — SHOULD WE ABSTAIN?       insufficient support / clarify / abstain / fallback

These are *semantic* gates that run AFTER the structural
:meth:`L1PlanContractV2.validate` has passed. They consume an
:class:`IntentFrame` (what was asked) and a :class:`PlanBundle` (what is
allowed) plus the candidate plan, and return a typed
:class:`PlanValidationOutcome`.

L1 layer authority: pure functions, no retrieval, no tool exec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L1_cognition.types.intent_frame_types import (
    ActionRequirement,
    FreshnessClass,
    IntentFrame,
    OutputTargetKind,
)
from agentic_core.L1_cognition.types.plan_bundle_types import PlanBundle
from agentic_core.L1_cognition.types.plan_contract_types import (
    ClarifyOrAbstainMarker,
    EscalationHint,
    L1PlanContractV2,
    LowestViableAgency,
    ProposedRoute,
    Reversibility,
    SupportTarget,
)

__all__ = [
    "GateOutcome",
    "GateResult",
    "PlanValidationOutcome",
    "did_we_listen",
    "is_it_safe",
    "does_it_make_sense",
    "plan_consistency_audit_v3a",
    "can_it_be_simpler",
    "should_we_abstain_or_clarify",
    "validate_plan_semantically",
]


class GateOutcome(str, Enum):
    """Per-gate verdict."""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


@dataclass(frozen=True)
class GateResult:
    """Result of a single V-gate."""

    gate_id: str  # "V1".."V5"
    outcome: GateOutcome
    findings: tuple = ()  # (str, ...)

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "outcome": self.outcome.value,
            "findings": list(self.findings),
        }


@dataclass(frozen=True)
class PlanValidationOutcome:
    """Aggregate result of running V1..V5 over a plan."""

    overall: GateOutcome
    gates: tuple = field(default_factory=tuple)  # (GateResult, ...)

    def has_failures(self) -> bool:
        return any(g.outcome == GateOutcome.FAIL for g in self.gates)

    def has_warnings(self) -> bool:
        return any(g.outcome == GateOutcome.WARN for g in self.gates)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall.value,
            "gates": [g.to_dict() for g in self.gates],
        }


# ---------------------------------------------------------------------------
# V1 — DID WE LISTEN?
# ---------------------------------------------------------------------------


_OUTPUT_TARGET_TO_AGENCY: dict[OutputTargetKind, set[LowestViableAgency]] = {
    OutputTargetKind.ANSWER: {
        LowestViableAgency.ANSWER_DIRECTLY,
        LowestViableAgency.GROUNDED_READ,
    },
    OutputTargetKind.PLAN: {
        LowestViableAgency.ANSWER_DIRECTLY,
        LowestViableAgency.GROUNDED_READ,
        LowestViableAgency.WORKFLOW,
    },
    OutputTargetKind.ARTIFACT: {
        LowestViableAgency.SINGLE_ACTION,
        LowestViableAgency.WORKFLOW,
        LowestViableAgency.GROUNDED_READ,
    },
    OutputTargetKind.ACTION: {
        LowestViableAgency.SINGLE_ACTION,
        LowestViableAgency.WORKFLOW,
    },
    OutputTargetKind.CLARIFICATION: {LowestViableAgency.FALLBACK},
}


def did_we_listen(plan: L1PlanContractV2, intent: IntentFrame) -> GateResult:
    """V1: plan honors the goal, request_id, and explicit constraints."""
    findings: list[str] = []
    if plan.request_id != intent.request_id:
        findings.append(f"plan.request_id ({plan.request_id!r}) != intent.request_id ({intent.request_id!r})")
    # The goal must appear (verbatim or as a substring of the rationale).
    if intent.goal.lower() not in plan.published_rationale.lower():
        findings.append(
            "intent.goal not referenced in published_rationale; planner may "
            "have answered a different question"
        )
    # CLARIFICATION output requires CLARIFY route + abstain marker.
    if (
        intent.output_target_kind == OutputTargetKind.CLARIFICATION
        and plan.proposed_route != ProposedRoute.CLARIFY
    ):
        findings.append("intent requested CLARIFICATION but proposed_route is not CLARIFY")
    # ACTION output requires non-READ reversibility OR explicit grounding.
    if (
        intent.output_target_kind == OutputTargetKind.ACTION
        and plan.route_risk.reversibility == Reversibility.READ
    ):
        findings.append(
            "intent requested ACTION but route_risk.reversibility=READ (plan would not actually act)"
        )
    outcome = GateOutcome.PASS if not findings else GateOutcome.FAIL
    return GateResult(gate_id="V1", outcome=outcome, findings=tuple(findings))


# ---------------------------------------------------------------------------
# V2 — IS IT SAFE?
# ---------------------------------------------------------------------------


def is_it_safe(plan: L1PlanContractV2, bundle: PlanBundle) -> GateResult:
    """V2: plan is within policy bounds and respects disallowed actions."""
    findings: list[str] = []
    rationale_lc = plan.published_rationale.lower()
    for forbidden in bundle.disallowed_actions:
        if forbidden.lower() in rationale_lc:
            findings.append(f"published_rationale mentions disallowed action: {forbidden!r}")
    # Any escalation_hint != NONE is a WARN, not a FAIL — it tells L5 to
    # gate but the plan itself is still proposable.
    escalation_warn = plan.escalation_hint != EscalationHint.NONE
    # WRITE reversibility with NO escalation hint and NO HITL trigger
    # in the bundle is a hard fail (constitutional UWG bypass risk).
    if (
        plan.route_risk.reversibility == Reversibility.WRITE
        and plan.escalation_hint == EscalationHint.NONE
        and not bundle.hitl_triggers
    ):
        findings.append(
            "route_risk.reversibility=WRITE with no escalation_hint and no "
            "HITL trigger declared in bundle — potential UWG bypass"
        )
    if findings:
        return GateResult(gate_id="V2", outcome=GateOutcome.FAIL, findings=tuple(findings))
    if escalation_warn:
        return GateResult(
            gate_id="V2",
            outcome=GateOutcome.WARN,
            findings=(f"escalation_hint={plan.escalation_hint.value}",),
        )
    return GateResult(gate_id="V2", outcome=GateOutcome.PASS)


# ---------------------------------------------------------------------------
# V3 — DOES IT MAKE SENSE?
# ---------------------------------------------------------------------------


def does_it_make_sense(plan: L1PlanContractV2) -> GateResult:
    """V3: dependencies resolve, no circular references, executable."""
    findings: list[str] = []
    seen_ids: set[str] = set()
    for step in plan.task_spec:
        sid = step.step_id
        if not sid or not sid.strip():
            findings.append("task_spec has step with empty step_id")
            continue
        if sid in seen_ids:
            findings.append(f"task_spec has duplicate step_id: {sid!r}")
        seen_ids.add(sid)
        if not step.description.strip():
            findings.append(f"task_spec step {sid!r} has empty description")
        if not step.expected_ground_truth.success_predicate.strip():
            findings.append(
                f"task_spec step {sid!r} has empty success_predicate (BP-A4 ground-truth feedback violated)"
            )
    if plan.grounding_required and plan.query_spec is None:
        findings.append("grounding_required=True but query_spec is None")
    if plan.grounding_required and plan.query_spec is not None:
        if plan.query_spec.max_results <= 0:
            findings.append("query_spec.max_results must be positive")
    outcome = GateOutcome.PASS if not findings else GateOutcome.FAIL
    return GateResult(gate_id="V3", outcome=outcome, findings=tuple(findings))


# ---------------------------------------------------------------------------
# V3A — PLAN CONSISTENCY AUDIT (v5 doctrine, 9 sub-checks)
# ---------------------------------------------------------------------------


_CACHE_ROUTES: frozenset[ProposedRoute] = frozenset({ProposedRoute.R1A, ProposedRoute.R1B})
_GROUNDED_READ_ROUTES: frozenset[ProposedRoute] = frozenset({ProposedRoute.R3})
_SINGLE_ACTION_ROUTES: frozenset[ProposedRoute] = frozenset({ProposedRoute.R4})
_MANAGED_WORKFLOW_ROUTES: frozenset[ProposedRoute] = frozenset({ProposedRoute.R3R4_MANAGED_WORKFLOW})
_FALLBACK_ROUTES: frozenset[ProposedRoute] = frozenset({ProposedRoute.R5})

_FRESH_REQUIRED_CLASSES: frozenset[FreshnessClass] = frozenset(
    {FreshnessClass.CURRENT, FreshnessClass.RECENT, FreshnessClass.LIVE, FreshnessClass.EXACT_DATE}
)

_HARD_SUPPORT_TARGETS: frozenset[SupportTarget] = frozenset(
    {
        SupportTarget.CITATION,
        SupportTarget.DIRECT_SPAN,
        SupportTarget.EVIDENCE_BUNDLE,
        SupportTarget.POLICY_CLAUSE,
    }
)


def plan_consistency_audit_v3a(plan: L1PlanContractV2, intent: IntentFrame, bundle: PlanBundle) -> GateResult:
    """V3A: cross-field consistency between route hint, support, action, freshness.

    Doctrine reference: v5 § V3A PLAN CONSISTENCY AUDIT — 9 sub-checks.

    Outcome:
      * any inconsistency → FAIL with all findings enumerated.
      * single soft mismatch (e.g. workflow with one step) → WARN.
    """
    findings: list[str] = []
    soft_findings: list[str] = []

    route = plan.proposed_route

    # 1. Cache route + fresh-evidence support is incoherent.
    if route in _CACHE_ROUTES and intent.freshness_class in _FRESH_REQUIRED_CLASSES:
        findings.append(
            f"cache route ({route.value}) used with freshness_class="
            f"{intent.freshness_class.value} — cached answer may be stale"
        )

    # 2. Grounded-read route requires C0 grounding to be marked.
    if route in _GROUNDED_READ_ROUTES and not plan.grounding_required:
        findings.append(
            "R3 grounded-read route declared but grounding_required=False — "
            "C0 must produce an evidence contract for L2"
        )

    # 3. Single-action route must be bounded — not multi-step dependency state.
    if route in _SINGLE_ACTION_ROUTES and len(plan.task_spec) > 1:
        findings.append(
            "R4 single-action route used with multi-step task_spec — "
            "either decompose into R3R4_MANAGED_WORKFLOW or collapse steps"
        )

    # 4. Managed workflow must have a real reason for L3 multi-step machinery.
    if route in _MANAGED_WORKFLOW_ROUTES and len(plan.task_spec) <= 1:
        soft_findings.append("R3R4_MANAGED_WORKFLOW with ≤ 1 task step — simplify to R3 or R4")

    # 5. Fallback route must include a reason in published_rationale.
    if route in _FALLBACK_ROUTES:
        rationale_lc = plan.published_rationale.lower()
        if not any(
            tok in rationale_lc
            for tok in (
                "unsafe",
                "unsupported",
                "out of scope",
                "insufficient",
                "abstain",
                "fallback",
                "weak",
            )
        ):
            findings.append(
                "R5 fallback route used but published_rationale does not state "
                "why direct completion is unsafe/unsupported"
            )

    # 6. Durable mutation ⇒ UWG must be marked downstream.
    if (
        plan.route_risk.reversibility == Reversibility.WRITE
        and not bundle.hitl_triggers
        and plan.escalation_hint == EscalationHint.NONE
    ):
        # Already caught by V2; V3A surfaces it as an additional UWG-coherence note.
        soft_findings.append(
            "durable WRITE proposed without HITL trigger or escalation_hint — UWG path will reject"
        )

    # 7. High-risk action ⇒ HITL marker must be present (escalation_hint or hitl bundle).
    if (
        intent.action_requirement == ActionRequirement.HIGH_IMPACT
        and plan.escalation_hint == EscalationHint.NONE
        and not bundle.hitl_triggers
    ):
        findings.append(
            "intent.action_requirement=HIGH_IMPACT but no escalation_hint "
            "and no HITL trigger declared in bundle"
        )

    # 8. Weak evidence (support_target NONE on a grounding plan) ⇒ don't claim certainty.
    if plan.grounding_required and plan.support_target == SupportTarget.NONE:
        findings.append(
            "grounding_required=True but support_target=NONE — plan would "
            "claim grounded answer with no support"
        )

    # 9. "Full overwrite" requests (intent.goal contains 'overwrite') must preserve
    # structure: rationale should mention 'preserve', 'overwrite', or similar.
    if "overwrite" in intent.goal.lower():
        rationale_lc = plan.published_rationale.lower()
        if not any(tok in rationale_lc for tok in ("preserve", "structure", "overwrite", "in place")):
            soft_findings.append(
                "intent goal references 'overwrite' but plan rationale does not "
                "declare structure preservation — risk of appended notes"
            )

    if findings:
        return GateResult(
            gate_id="V3A",
            outcome=GateOutcome.FAIL,
            findings=tuple(findings + soft_findings),
        )
    if soft_findings:
        return GateResult(gate_id="V3A", outcome=GateOutcome.WARN, findings=tuple(soft_findings))
    return GateResult(gate_id="V3A", outcome=GateOutcome.PASS)


# ---------------------------------------------------------------------------
# V4 — CAN IT BE SIMPLER?
# ---------------------------------------------------------------------------


def can_it_be_simpler(plan: L1PlanContractV2, intent: IntentFrame) -> GateResult:
    """V4: lowest_viable_agency is consistent with output_target_kind and step count.

    Returns WARN (not FAIL) when a strictly simpler agency would still
    satisfy the request; the planner can refine but does not have to.
    """
    findings: list[str] = []
    allowed = _OUTPUT_TARGET_TO_AGENCY.get(intent.output_target_kind, set())
    if allowed and plan.lowest_viable_agency not in allowed:
        findings.append(
            f"lowest_viable_agency={plan.lowest_viable_agency.value} not in "
            f"the allowed set for output_target_kind="
            f"{intent.output_target_kind.value}"
        )
    # Single-step plans should not declare WORKFLOW agency.
    if len(plan.task_spec) == 1 and plan.lowest_viable_agency == LowestViableAgency.WORKFLOW:
        findings.append("single-step plan declared WORKFLOW agency — consider SINGLE_ACTION or GROUNDED_READ")
    # Multi-step plan with ANSWER_DIRECTLY agency is incoherent.
    if len(plan.task_spec) > 1 and plan.lowest_viable_agency == LowestViableAgency.ANSWER_DIRECTLY:
        findings.append("multi-step plan declared ANSWER_DIRECTLY agency — agency-vs-shape mismatch")
    if not findings:
        return GateResult(gate_id="V4", outcome=GateOutcome.PASS)
    # V4 never hard-fails on its own — the planner's choice is advisory.
    return GateResult(gate_id="V4", outcome=GateOutcome.WARN, findings=tuple(findings))


# ---------------------------------------------------------------------------
# V5 — SHOULD WE ABSTAIN OR CLARIFY?
# ---------------------------------------------------------------------------


def should_we_abstain_or_clarify(plan: L1PlanContractV2, intent: IntentFrame) -> GateResult:
    """V5: clarify/abstain marker matches the unresolved-ambiguity reality."""
    findings: list[str] = []
    has_unresolved = intent.ambiguity.has_unresolved()
    marker = plan.clarify_or_abstain_marker

    if has_unresolved and marker == ClarifyOrAbstainMarker.NONE:
        findings.append(
            "intent has unresolved ambiguity but clarify_or_abstain_marker=NONE and no fallback declared"
        )
    if marker == ClarifyOrAbstainMarker.CLARIFY and plan.proposed_route != ProposedRoute.CLARIFY:
        findings.append("clarify_or_abstain_marker=CLARIFY but proposed_route is not CLARIFY")
    if marker == ClarifyOrAbstainMarker.ABSTAIN and len(plan.task_spec) > 1:
        findings.append("clarify_or_abstain_marker=ABSTAIN but task_spec has multiple steps")
    if plan.escalation_hint == EscalationHint.INSUFFICIENT_SUPPORT and marker == ClarifyOrAbstainMarker.NONE:
        findings.append("escalation_hint=INSUFFICIENT_SUPPORT but no clarify/abstain marker set")
    outcome = GateOutcome.PASS if not findings else GateOutcome.FAIL
    return GateResult(gate_id="V5", outcome=outcome, findings=tuple(findings))


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------


def validate_plan_semantically(
    plan: L1PlanContractV2,
    intent: IntentFrame,
    bundle: PlanBundle,
) -> PlanValidationOutcome:
    """Run V1..V5 in order; aggregate to PASS/WARN/FAIL.

    Overall verdict:
      * any gate FAIL → overall FAIL
      * else any gate WARN → overall WARN
      * else PASS

    Callers MUST also have invoked :meth:`L1PlanContractV2.validate`
    (structural) before this function; semantic gates assume the
    contract is structurally valid.
    """
    gates: tuple[GateResult, ...] = (
        did_we_listen(plan, intent),
        is_it_safe(plan, bundle),
        does_it_make_sense(plan),
        plan_consistency_audit_v3a(plan, intent, bundle),
        can_it_be_simpler(plan, intent),
        should_we_abstain_or_clarify(plan, intent),
    )
    if any(g.outcome == GateOutcome.FAIL for g in gates):
        overall = GateOutcome.FAIL
    elif any(g.outcome == GateOutcome.WARN for g in gates):
        overall = GateOutcome.WARN
    else:
        overall = GateOutcome.PASS
    return PlanValidationOutcome(overall=overall, gates=gates)
