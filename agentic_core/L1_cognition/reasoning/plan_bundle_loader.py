"""load_plan_bundle — produce a :class:`PlanBundle` for the L1 planner.

Doctrine: ``02_L1_Reasoning_Plan_Generation_v4.md`` § "GATHERING RULES,
EXAMPLES, AND PRIORS" (M1-M4).

The loader is a pure-function aggregator. It takes caller-supplied
feeds (already extracted from the L4 archive or other approved sources)
and returns a frozen, hash-stable :class:`PlanBundle` plus a derived
:class:`RuleAwarePlanningFrame`.

L1 layer authority is preserved: this module never reads from L4
itself. Callers (e.g., the L1 composition root) are responsible for
sourcing each tuple from approved L4 read paths.
"""

from __future__ import annotations

from typing import Iterable

from agentic_core.L1_cognition.types.intent_frame_types import IntentFrame
from agentic_core.L1_cognition.types.plan_bundle_types import (
    PlanBundle,
    RuleAwarePlanningFrame,
)

__all__ = [
    "derive_rule_aware_frame",
    "load_plan_bundle",
]


def load_plan_bundle(
    *,
    schemas: Iterable[str] = (),
    route_heuristics: Iterable[str] = (),
    output_contracts: Iterable[str] = (),
    validation_rubric: Iterable[str] = (),
    policy_bounds: Iterable[str] = (),
    escalation_thresholds: Iterable[str] = (),
    disallowed_actions: Iterable[str] = (),
    hitl_triggers: Iterable[str] = (),
    exemplars: Iterable[str] = (),
    edge_cases: Iterable[str] = (),
    approved_templates: Iterable[str] = (),
    stopping_rules: Iterable[str] = (),
    retry_boundaries: Iterable[str] = (),
    abstain_patterns: Iterable[str] = (),
    max_steps: int = 10,
    max_wallclock_ms: int = 60_000,
) -> PlanBundle:
    """Build a frozen :class:`PlanBundle` from M1-M4 feeds."""
    return PlanBundle(
        schemas=tuple(schemas),
        route_heuristics=tuple(route_heuristics),
        output_contracts=tuple(output_contracts),
        validation_rubric=tuple(validation_rubric),
        policy_bounds=tuple(policy_bounds),
        escalation_thresholds=tuple(escalation_thresholds),
        disallowed_actions=tuple(disallowed_actions),
        hitl_triggers=tuple(hitl_triggers),
        exemplars=tuple(exemplars),
        edge_cases=tuple(edge_cases),
        approved_templates=tuple(approved_templates),
        stopping_rules=tuple(stopping_rules),
        retry_boundaries=tuple(retry_boundaries),
        abstain_patterns=tuple(abstain_patterns),
        max_steps=max_steps,
        max_wallclock_ms=max_wallclock_ms,
    )


def derive_rule_aware_frame(
    intent_frame: IntentFrame,
    bundle: PlanBundle,
) -> RuleAwarePlanningFrame:
    """Project an :class:`IntentFrame` + :class:`PlanBundle` into a
    :class:`RuleAwarePlanningFrame`.

    Cheap projection: route heuristics → ``can_be_proposed``,
    grounding-relevant policy → ``must_be_grounded``, HITL/escalation
    triggers + high-risk intent → ``must_be_escalated``.
    """
    can_be_proposed: list[str] = list(bundle.route_heuristics) + list(
        bundle.approved_templates
    )

    must_be_grounded: list[str] = []
    for predicate in bundle.policy_bounds + bundle.validation_rubric:
        lowered = predicate.lower()
        if "ground" in lowered or "evidence" in lowered or "cite" in lowered:
            must_be_grounded.append(predicate)

    must_be_escalated: list[str] = list(bundle.hitl_triggers) + list(
        bundle.escalation_thresholds
    )
    if intent_frame.high_risk:
        must_be_escalated.append("intent_frame.high_risk=True")

    return RuleAwarePlanningFrame(
        can_be_proposed=tuple(can_be_proposed),
        must_be_grounded=tuple(must_be_grounded),
        must_be_escalated=tuple(must_be_escalated),
    )
