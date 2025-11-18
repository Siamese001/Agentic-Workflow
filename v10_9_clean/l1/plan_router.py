# FILE: v10_9_clean/l1/plan_router.py
"""
L1 — Plan Router (v10_9)

Takes:
    • raw orchestration state
    • the selected L1 mode (from mode_router.route_mode)

Produces:
    • a fully constructed PlanObject from the appropriate L1 planner.

This unifies all L1 planners under a single entrypoint.
"""

from __future__ import annotations
from typing import Any, Dict

from shared.models import PlanObject
from l1.mode_router import route_mode

# L1 planners
from l1.l1_reasoning import StrategyReasoner
from l1.rag_planning import plan as rag_plan
from l1.bullet_planning import plan as bullet_plan
from l1.draft_planning import plan as draft_plan
from l1.qa_planning import plan as qa_plan
from l1.safety_planning import plan as safety_plan


def route_plan(state: Dict[str, Any]) -> PlanObject:
    """
    Unified L1 plan dispatcher.
    Uses the selected mode to invoke the appropriate planner.
    """

    mode = route_mode(state)

    if mode == "rag":
        return rag_plan(state)

    if mode == "bullets":
        return bullet_plan(state)

    if mode == "drafting":
        return draft_plan(state)

    if mode == "qa":
        return qa_plan(state)

    if mode == "safety":
        return safety_plan(state)

    # Default → strategy planner
    reasoner = StrategyReasoner()
    return reasoner.plan(state)
