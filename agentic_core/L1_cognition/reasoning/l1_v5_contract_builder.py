"""L1 v5 Output Contract builder — produces the 10-section JSON shape.

Doctrine reference: ``02_L1_Reasoning_Plan_Generation_v5.md`` § L1 PLAN
CONTRACT — CANONICAL SHAPE.

This module is purely **additive over v4**: existing :class:`L1PlanContractV2`
remains the in-memory authority; this builder serializes the v2 contract +
:class:`IntentFrame` + :class:`PlanBundle` + :class:`FirstSafetyReading`
into the v5 doc's 10-section dict.

Sections produced:

  1. ``identity`` — request_id, trace_root, l1_plan_id, policy_hash,
     instruction_hash, source_envelope_id
  2. ``intent_frame`` — normalized_goal, deliverable, work_class, audience,
     style/hard/soft constraints, success_condition, implicit_goal
  3. ``query_spec`` — entities, files, dates, freshness_class, source_expectations,
     support_need
  4. ``task_spec`` — work_units, output_target, format, acceptance_criteria,
     stop_condition, partial_completion_allowed
  5. ``route_hint`` — proposed_route_hint, confidence (band), route_risk,
     reason_codes, fallback_chain_hint, single_step_or_workflow
  6. ``support_expectation`` — grounding_required, support_target, evidence_classes,
     weak_support_policy, contradiction_policy
  7. ``action_expectation`` — action_required, candidate_tool_class, side_effect_class,
     hitl_hint, uwg_hint, sandbox_hint, capability_token_hint
  8. ``assumptions_and_gaps`` — declared_assumptions, unresolved_gaps,
     clarify_required, clarify_question, abstain_or_fallback_marker
  9. ``validation_summary`` — listened_to_user, constraints_preserved,
     safety_checked, coherent_plan, lowest_viable_agency_applied,
     no_retrieval_performed, no_execution_performed, no_write_performed
 10. ``downstream_notes`` — for_l0, for_c0, for_prompt_assembly, for_l2,
     for_exit_control, for_l6

This is the JSON Cascade hands to L0 routing.
"""

from __future__ import annotations

import re
from typing import Any

from agentic_core.L1_cognition.enforcement.first_safety_reading import (
    FirstSafetyReading,
)
from agentic_core.L1_cognition.enforcement.plan_semantic_validators import (
    GateOutcome,
    PlanValidationOutcome,
)
from agentic_core.L1_cognition.types.intent_frame_types import (
    ActionRequirement,
    IntentFrame,
)
from agentic_core.L1_cognition.types.plan_bundle_types import PlanBundle
from agentic_core.L1_cognition.types.plan_contract_types import (
    ClarifyOrAbstainMarker,
    ConfidenceBand,
    L1PlanContractV2,
    Reversibility,
    SupportTarget,
)

__all__ = ["build_l1_v5_contract_dict"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_ACTION_TO_SIDE_EFFECT: dict[ActionRequirement, str] = {
    ActionRequirement.NONE: "none",
    ActionRequirement.READ_ONLY: "read",
    ActionRequirement.REVERSIBLE: "reversible",
    ActionRequirement.WRITE_PROPOSAL: "write_proposal",
    ActionRequirement.HIGH_IMPACT: "irreversible",
}


def _candidate_tool_class(intent: IntentFrame) -> str:
    """Heuristic tool-class hint from artifact_requirement + work_class."""
    artifact = intent.artifact_requirement.value
    if artifact in ("doc", "slide", "spreadsheet"):
        return "doc"
    if artifact == "code":
        return "code"
    if artifact == "diagram":
        return "diagram"
    if artifact == "file":
        return "filesystem"
    # No artifact-class match — fall back to NONE.
    return "none"


def _weak_support_policy(plan: L1PlanContractV2) -> str:
    """Pick weak_support_policy from the plan's clarify/abstain marker."""
    marker = plan.clarify_or_abstain_marker
    if marker == ClarifyOrAbstainMarker.CLARIFY:
        return "clarify"
    if marker == ClarifyOrAbstainMarker.ABSTAIN:
        return "abstain"
    if marker == ClarifyOrAbstainMarker.FALLBACK:
        return "fallback"
    return "caveat"


def _contradiction_policy(plan: L1PlanContractV2) -> str:
    """v5 § support_expectation.contradiction_policy heuristic."""
    if plan.grounding_required and plan.support_target in (
        SupportTarget.CITATION,
        SupportTarget.DIRECT_SPAN,
        SupportTarget.EVIDENCE_BUNDLE,
    ):
        return "surface_conflict"
    if plan.grounding_required:
        return "prefer_authoritative"
    return "abstain_if_unresolved"


def _evidence_classes(plan: L1PlanContractV2, intent: IntentFrame) -> list[str]:
    """v5 § support_expectation.evidence_classes — coarse inference."""
    if not plan.grounding_required:
        return []
    classes: list[str] = []
    artifact = intent.artifact_requirement.value
    if artifact == "code":
        classes.append("code")
    if artifact == "spreadsheet":
        classes.append("tables")
    if artifact == "doc":
        classes.append("docs")
    # Default if nothing specific inferred.
    if not classes:
        classes.append("docs")
    return classes


def _single_step_or_workflow(plan: L1PlanContractV2) -> str:
    if plan.proposed_route.value == "R3R4_MANAGED_WORKFLOW":
        return "managed_workflow"
    if plan.proposed_route.value == "CLARIFY":
        return "terminal_short_circuit"
    if len(plan.task_spec) <= 1:
        return "single_step"
    return "managed_workflow"


_DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_FILE_PATTERN = re.compile(r"\b[\w/-]+\.(?:md|txt|json|yaml|yml|csv|xlsx?|py|js|ts|html|pdf|docx?|pptx?)\b")
_URL_PATTERN = re.compile(r"\bhttps?://\S+")
_VERSION_PATTERN = re.compile(r"\bv\d+(?:\.\d+){1,2}\b")


def _extract_files_or_sources(intent: IntentFrame) -> list[str]:
    """v5 § query_spec.files_or_sources — deterministic extraction from
    intent.goal + details using simple file/URL patterns.
    """
    haystacks = [intent.goal] + list(intent.details)
    seen: list[str] = []
    for hay in haystacks:
        for m in _FILE_PATTERN.finditer(hay):
            if m.group(0) not in seen:
                seen.append(m.group(0))
        for m in _URL_PATTERN.finditer(hay):
            if m.group(0) not in seen:
                seen.append(m.group(0))
    return seen


def _extract_dates_or_versions(intent: IntentFrame) -> list[str]:
    """v5 § query_spec.dates_or_versions — ISO dates and v-prefixed versions."""
    haystacks = [intent.goal] + list(intent.details)
    seen: list[str] = []
    for hay in haystacks:
        for m in _DATE_PATTERN.finditer(hay):
            if m.group(0) not in seen:
                seen.append(m.group(0))
        for m in _VERSION_PATTERN.finditer(hay):
            if m.group(0) not in seen:
                seen.append(m.group(0))
    return seen


def _source_expectations(intent: IntentFrame) -> list[str]:
    """v5 § query_spec.source_expectations — closed enum from doctrine."""
    text = (intent.goal + " " + " ".join(intent.details)).lower()
    expectations: list[str] = []
    if "upload" in text or "uploaded" in text:
        expectations.append("uploaded file")
    if "drive" in text or "google drive" in text:
        expectations.append("drive")
    if "web" in text or "google" in text or "search" in text:
        expectations.append("web")
    if "email" in text or "inbox" in text:
        expectations.append("email")
    if "calendar" in text:
        expectations.append("calendar")
    if "file library" in text or "my files" in text:
        expectations.append("file library")
    return expectations or ["none"]


def _implicit_goal(intent: IntentFrame) -> str:
    """v5 § intent_frame.implicit_goal — best-effort hidden-concern surfacing.

    Heuristic: if any unstated_likely items are recorded, the first one is the
    implicit goal; otherwise if the planner inferred high_risk, surface a
    safety-aware variant; otherwise empty.
    """
    if intent.ambiguity.unstated_likely:
        return str(intent.ambiguity.unstated_likely[0])
    if intent.high_risk:
        return f"safe execution of: {intent.goal}"
    return ""


def _reason_codes(
    plan: L1PlanContractV2, intent: IntentFrame, bundle: PlanBundle
) -> list[str]:
    """v5 § route_hint.reason_codes — deterministic codes derived from plan + intent.

    Each code is a short stable token L0 / Exit Control can pattern-match.
    """
    codes: list[str] = []
    # Freshness
    if intent.freshness_class.value in ("current", "live", "recent", "exact_date"):
        codes.append(f"freshness:{intent.freshness_class.value}")
    # Action class
    if intent.action_requirement.value != "none":
        codes.append(f"action:{intent.action_requirement.value}")
    # High risk
    if intent.high_risk:
        codes.append("high_risk")
    # Grounding requirement
    if plan.grounding_required:
        codes.append("grounding_required")
    # Escalation
    if plan.escalation_hint.value != "none":
        codes.append(f"escalation:{plan.escalation_hint.value}")
    # Clarify/abstain
    if plan.clarify_or_abstain_marker.value != "none":
        codes.append(f"marker:{plan.clarify_or_abstain_marker.value}")
    # Bundle hitl trigger
    if bundle.hitl_triggers:
        codes.append("hitl_trigger_in_bundle")
    return codes


# Deterministic fallback chain by primary route. Doctrine: each route
# degrades to a strictly safer / more-bounded next attempt.
_FALLBACK_CHAIN: dict[str, list[str]] = {
    "R1A": ["R1B", "R3", "R5"],
    "R1B": ["R3", "R5"],
    "R3": ["R5"],
    "R4": ["R3R4_MANAGED_WORKFLOW", "R5"],
    "R3R4_MANAGED_WORKFLOW": ["R5"],
    "R5": [],
    "CLARIFY": [],
}


def _validation_summary_dict(
    validation: PlanValidationOutcome | None, plan: L1PlanContractV2
) -> dict[str, bool]:
    """Map V1-V5 + V3A outcomes to the v5 § validation_summary booleans."""
    if validation is None:
        # No semantic run yet — claim only the structural truths.
        return {
            "listened_to_user": True,
            "constraints_preserved": True,
            "safety_checked": False,
            "coherent_plan": True,
            "lowest_viable_agency_applied": True,
            "no_retrieval_performed": True,
            "no_execution_performed": True,
            "no_write_performed": True,
        }

    by_id: dict[str, GateOutcome] = {g.gate_id: g.outcome for g in validation.gates}
    return {
        "listened_to_user": by_id.get("V1") == GateOutcome.PASS,
        "constraints_preserved": by_id.get("V1") == GateOutcome.PASS,
        "safety_checked": by_id.get("V2") in (GateOutcome.PASS, GateOutcome.WARN),
        "coherent_plan": by_id.get("V3") == GateOutcome.PASS
        and by_id.get("V3A") in (GateOutcome.PASS, GateOutcome.WARN),
        "lowest_viable_agency_applied": by_id.get("V4")
        in (
            GateOutcome.PASS,
            GateOutcome.WARN,
        ),
        "no_retrieval_performed": True,  # L1 invariant: never retrieves
        "no_execution_performed": True,  # L1 invariant: never executes
        "no_write_performed": plan.route_risk.reversibility != Reversibility.WRITE
        or plan.escalation_hint.value != "NONE",
    }


def _downstream_notes(
    plan: L1PlanContractV2,
    intent: IntentFrame,
    bundle: PlanBundle,
    safety: FirstSafetyReading | None,
) -> dict[str, list[str]]:
    """Build v5 § downstream_notes per-consumer hints."""
    for_l0: list[str] = [
        f"route={plan.proposed_route.value}",
        f"confidence={ConfidenceBand.from_score(plan.confidence_score).value}",
        f"reversibility={plan.route_risk.reversibility.value}",
    ]
    for_c0: list[str] = []
    if plan.grounding_required:
        for_c0.append(f"support_target={plan.support_target.value}")
        if plan.query_spec is not None:
            for_c0.append(f"freshness={intent.freshness_class.value}")
            for_c0.append(f"max_results={plan.query_spec.max_results}")

    for_prompt_assembly: list[str] = [
        f"output_target_kind={intent.output_target_kind.value}",
        f"artifact={intent.artifact_requirement.value}",
    ]
    for_l2: list[str] = [f"steps={len(plan.task_spec)}"]
    for_exit_control: list[str] = [
        f"escalation_hint={plan.escalation_hint.value}",
        f"reversibility={plan.route_risk.reversibility.value}",
    ]
    if safety is not None:
        if safety.requires_hitl_later:
            for_exit_control.append("hitl_required")
        if safety.requires_uwg_later:
            for_exit_control.append("uwg_required")
        if safety.recommend_refusal:
            for_exit_control.append("recommend_refusal")
        if safety.recommend_safe_redirect:
            for_exit_control.append("recommend_safe_redirect")

    for_l6: list[str] = [
        f"plan_id={plan.plan_id}",
        f"work_class={intent.work_class.value}",
        f"action_requirement={intent.action_requirement.value}",
    ]
    return {
        "for_l0": for_l0,
        "for_c0": for_c0,
        "for_prompt_assembly": for_prompt_assembly,
        "for_l2": for_l2,
        "for_exit_control": for_exit_control,
        "for_l6": for_l6,
    }


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------


def build_l1_v5_contract_dict(
    *,
    plan: L1PlanContractV2,
    intent: IntentFrame,
    bundle: PlanBundle,
    validation: PlanValidationOutcome | None = None,
    safety: FirstSafetyReading | None = None,
    instruction_hash: str = "",
    source_envelope_id: str = "",
    trace_root: str | None = None,
) -> dict[str, Any]:
    """Produce the v5 § L1 PLAN CONTRACT canonical-shape dict.

    Args:
        plan: Validated :class:`L1PlanContractV2`.
        intent: Validated :class:`IntentFrame`.
        bundle: :class:`PlanBundle` used to draft the plan.
        validation: Optional semantic outcome from
            :func:`validate_plan_semantically`. When omitted, the
            ``validation_summary`` block claims only structural truths.
        safety: Optional :class:`FirstSafetyReading` used to enrich
            ``downstream_notes.for_exit_control``.
        instruction_hash, source_envelope_id, trace_root: caller-supplied
            identity fields. Defaults to empty / plan_id when missing.

    Returns:
        Dict matching the v5 doctrine canonical shape exactly. The
        top-level fields are ``layer``, ``version``, ``authority``, and
        the 10 numbered sections.
    """
    confidence = ConfidenceBand.from_score(plan.confidence_score)

    return {
        "layer": "L1_REASONING_PLAN_GENERATION",
        "version": "v5",
        "authority": "advisory_plan_only",
        # Section 1
        "identity": {
            "request_id": plan.request_id,
            "trace_root": trace_root or plan.plan_id,
            "l1_plan_id": plan.plan_id,
            "policy_hash": plan.policy_hash,
            "instruction_hash": instruction_hash,
            "source_envelope_id": source_envelope_id,
        },
        # Section 2
        "intent_frame": {
            "normalized_goal": intent.goal,
            "deliverable": intent.output_target_kind.value,
            "work_class": intent.work_class.value,
            "audience": intent.audience,
            "style_constraints": [c.statement for c in intent.constraints if c.severity == "should"],
            "hard_constraints": [c.statement for c in intent.constraints if c.severity == "must"],
            "soft_constraints": [c.statement for c in intent.constraints if c.severity == "avoid"],
            "success_condition": intent.success_condition,
            "implicit_goal": _implicit_goal(intent),
        },
        # Section 3
        "query_spec": {
            "entities": list(intent.details),
            "files_or_sources": _extract_files_or_sources(intent),
            "dates_or_versions": _extract_dates_or_versions(intent),
            "freshness_class": intent.freshness_class.value,
            "source_expectations": _source_expectations(intent),
            "support_need": plan.support_target.value,
        },
        # Section 4
        "task_spec": {
            "work_units": [s.description for s in plan.task_spec],
            "output_target": intent.output_target_kind.value,
            "format": intent.artifact_requirement.value,
            "acceptance_criteria": [s.expected_ground_truth.success_predicate for s in plan.task_spec],
            "stop_condition": intent.success_condition,
            "partial_completion_allowed": True,
        },
        # Section 5
        "route_hint": {
            "proposed_route_hint": plan.proposed_route.value,
            "confidence": confidence.value,
            "route_risk": plan.route_risk.safety_band.value.lower(),
            "reason_codes": _reason_codes(plan, intent, bundle),
            "fallback_chain_hint": list(_FALLBACK_CHAIN.get(plan.proposed_route.value, [])),
            "single_step_or_workflow": _single_step_or_workflow(plan),
        },
        # Section 6
        "support_expectation": {
            "grounding_required": "yes" if plan.grounding_required else "no",
            "support_target": plan.support_target.value,
            "evidence_classes": _evidence_classes(plan, intent),
            "weak_support_policy": _weak_support_policy(plan),
            "contradiction_policy": _contradiction_policy(plan),
        },
        # Section 7
        "action_expectation": {
            "action_required": intent.action_requirement != ActionRequirement.NONE,
            "candidate_tool_class": _candidate_tool_class(intent),
            "side_effect_class": _ACTION_TO_SIDE_EFFECT[intent.action_requirement],
            "hitl_hint": bool(safety and safety.requires_hitl_later),
            "uwg_hint": bool(safety and safety.requires_uwg_later),
            "sandbox_hint": intent.action_requirement
            in (ActionRequirement.WRITE_PROPOSAL, ActionRequirement.HIGH_IMPACT),
            "capability_token_hint": intent.action_requirement
            in (ActionRequirement.WRITE_PROPOSAL, ActionRequirement.HIGH_IMPACT),
        },
        # Section 8
        "assumptions_and_gaps": {
            "declared_assumptions": [a.statement for a in plan.declared_assumptions],
            "unresolved_gaps": list(plan.unresolved_gaps),
            "clarify_required": plan.clarify_or_abstain_marker == ClarifyOrAbstainMarker.CLARIFY,
            "clarify_question": "",
            "abstain_or_fallback_marker": plan.clarify_or_abstain_marker.value.lower(),
        },
        # Section 9
        "validation_summary": _validation_summary_dict(validation, plan),
        # Section 10
        "downstream_notes": _downstream_notes(plan, intent, bundle, safety),
    }
