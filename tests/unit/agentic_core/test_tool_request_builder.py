# MERGED FROM UNASSIGNED BY WINDSURF v4 — 2025-12-07T01:21:36.317503+00:00
# Original location: 10_tests\_unassigned_tests_invalid\test_tool_request_builder.py
# High-signal content preserved below — zero-loss migration
# ================================================================================

# FILE: v10_9_clean/l2/tool_router.py
"""
L2 â€” Tool Router (v10_9)

Maps an L1 PlanObject and its steps to the correct L2 execution function.

This replaces the 10_8/10_7 mixed router behavior and provides:
    â€¢ clean mode-based routing
    â€¢ no orchestration logic
    â€¢ no planning logic
    â€¢ deterministic executor selection
"""

from __future__ import annotations
from typing import Any, Dict, Callable, Awaitable

from shared.models import PlanObject
from shared.exceptions import OrchestrationError

# L2 executors
from l2.strategy_execution import execute_strategy
from l2.rag_execution import execute_rag
from l2.bullet_execution import execute_bullets
from l2.drafting_execution import execute_drafting
from l2.qa_execution import execute_qa
from l2.safety_execution import execute_safety


_EXECUTOR_MAP: Dict[str, Callable[[PlanObject, Dict[str, Any]], Awaitable[Any]]] = {
    "strategy": execute_strategy,
    "rag": execute_rag,
    "bullets": execute_bullets,
    "drafting": execute_drafting,
    "qa": execute_qa,
    "safety": execute_safety,
}


def route_executor(plan: PlanObject) -> Callable[[PlanObject, Dict[str, Any]], Awaitable[Any]]:
    """
    Determine the correct L2 executor based solely on plan.mode.
    """
    mode = (plan.mode or "").lower()

    if mode not in _EXECUTOR_MAP:
        raise OrchestrationError(f"No L2 executor found for plan mode: {mode}")

    return _EXECUTOR_MAP[mode]
