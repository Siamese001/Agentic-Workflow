"""
L1 — Strategy Reasoner

Responsibilities:
    • Generate multi-step strategic plans for complex objectives.
    • Coordinate decomposition of tasks for downstream execution agents.
    • Provide structured intents to L3 orchestrators without enforcing control flow.

Implements deterministic planning logic that emits only PlanObject instances.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from injection_profiles import DEFAULT_FRAMING_PROFILE
from l1_reasoner_base import Reasoner
from utils_types import PlanObject


def _as_list(value: Any) -> List[str]:
    """Normalize arbitrary input into a sorted list of strings."""

    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(item) for item in value]
    return [str(value)]


def _objective_from_state(state: Dict[str, Any]) -> str:
    """Extract a stable objective string from the orchestration state."""

    for key in ("objective", "task", "goal"):
        candidate = state.get(key)
        if candidate:
            return str(candidate)
    return "unspecified-objective"


class StrategyReasoner(Reasoner):
    """Deterministic multi-step strategy planner for L1."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = _objective_from_state(state)
        constraints = sorted(_as_list(state.get("constraints")))
        dependencies = sorted(_as_list(state.get("dependencies")))
        deliverables = sorted(_as_list(state.get("deliverables"))) or ["summary", "next-actions"]

        steps = [
            {
                "id": "clarify",
                "action": "analyze_objective",
                "details": objective,
            },
            {
                "id": "context",
                "action": "assess_context",
                "summary": state.get("summary", ""),
                "dependencies": dependencies,
            },
            {
                "id": "structure",
                "action": "outline_deliverables",
                "deliverables": deliverables,
                "constraints": constraints,
            },
        ]

        plan: PlanObject = PlanObject(
            {
                "layer": "l1",
                "mode": "strategy",
                "objective": objective,
                "constraints": constraints,
                "dependencies": dependencies,
                "deliverables": deliverables,
                "steps": steps,
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "bullet",
                    "expected_outputs": deliverables,
                },
            }
        )
        plan["injection_framing"] = {
            "global_goal": DEFAULT_FRAMING_PROFILE.global_goal,
            "success_criteria": DEFAULT_FRAMING_PROFILE.success_criteria,
            "task_mode": DEFAULT_FRAMING_PROFILE.task_mode,
            "scope_boundaries": DEFAULT_FRAMING_PROFILE.scope_boundaries,
            "cost_latency": DEFAULT_FRAMING_PROFILE.cost_latency,
        }
        plan["injection_reasoning"] = {
            "failure_anticipation_enabled": True,
            "self_consistency_enabled": True,
            "reason_then_answer": True,
            "error_simulation_enabled": True,
        }
        plan["safety_metadata"] = {
            "objective": objective,
            "sensitivity": "low",
            "audience": state.get("audience", "general"),
            "tags": ["planning"],
        }
        return plan
