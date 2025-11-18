# FILE: v10_9_clean/l2/strategy_execution.py
"""
L2 — Strategy Execution (v10_9)

Executes high-level reasoning and decomposition steps produced by the
L1 StrategyReasoner.

Consumes:
    • plan.steps[*] describing reasoning actions
    • objective, constraints, dependencies, deliverables

Produces:
    • ExecutionResult payload containing structured reasoning output:
        {
            "objective": ...,
            "steps": [...],
            "deliverables": [...],
            "next_actions": [...]
        }

This replaces the executable surface of strategy_ensemble_v10_7.py and
strategy_stack.py while obeying the L1–L5 boundaries of v10_9.
"""

from __future__ import annotations
from typing import Any, Dict, List

from shared.models import ExecutionResult, PlanObject
from shared.exceptions import ToolExecutionError


async def execute_strategy(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    """
    Run through L1 strategy steps and create a deterministic strategy outline.
    """

    try:
        objective = plan.objective or "unspecified-objective"
        constraints = plan.constraints or []
        dependencies = plan.dependencies or []
        deliverables = plan.deliverables or []

        outline: List[str] = []
        next_actions: List[str] = []

        # Deterministic interpretation of steps
        for step in plan.steps or []:
            action = step.get("action", "")
            if action == "analyze_objective":
                outline.append(f"Clarify goal: {step.get('details','')}")
            elif action == "assess_context":
                outline.append("Assess context: dependencies + summary")
            elif action == "outline_deliverables":
                outline.append(
                    f"Define deliverables: {', '.join(step.get('deliverables', []))}"
                )
            else:
                outline.append(f"Process step '{action}'")

        # Next action suggestions (deterministic)
        if deliverables:
            next_actions.append(f"Generate: {deliverables[0]}")
        else:
            next_actions.append("Draft high-level summary")

        payload = {
            "objective": objective,
            "constraints": constraints,
            "dependencies": dependencies,
            "deliverables": deliverables,
            "outline": outline,
            "next_actions": next_actions,
        }

        return ExecutionResult(
            status=ExecutionResult.__fields__["status"].type_.SUCCESS,
            payload=payload,
            model="strategy-exec-v10_9",
            usage={},
        )

    except Exception as exc:
        raise ToolExecutionError(f"Strategy execution failed: {exc}") from exc
