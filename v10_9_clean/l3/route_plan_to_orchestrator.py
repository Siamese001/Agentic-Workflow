# FILE: v10_9_clean/l3/route_plan_to_orchestrator.py
"""
L3 — Plan → Orchestrator Router (v10_9)

Maps an L1 PlanObject to the correct L3 orchestrator instance.

This separates:
    • plan routing (L1)
    • tool routing (L2)
    • domain orchestration (L3)

and allows the global L3 Orchestrator to delegate work cleanly.
"""

from __future__ import annotations
from typing import Dict, Any

from shared.models import PlanObject
from shared.exceptions import OrchestrationError

# Domain orchestrators
from l3.rag_orchestrator import RAGOrchestrator
from l3.bullet_orchestrator import BulletOrchestrator
from l3.draft_orchestrator import DraftOrchestrator
from l3.strategy_orchestrator import StrategyOrchestrator
from l3.qa_orchestrator import QAOrchestrator
from l3.safety_orchestrator import SafetyOrchestrator


_ORCHESTRATOR_MAP = {
    "rag": RAGOrchestrator,
    "bullets": BulletOrchestrator,
    "drafting": DraftOrchestrator,
    "strategy": StrategyOrchestrator,
    "qa": QAOrchestrator,
    "safety": SafetyOrchestrator,
}


def resolve_orchestrator(plan: PlanObject):
    """
    Select the correct L3 orchestrator class for the given plan.
    """
    mode = (plan.mode or "").lower()

    if mode not in _ORCHESTRATOR_MAP:
        raise OrchestrationError(f"No L3 orchestrator available for mode: {mode}")

    return _ORCHESTRATOR_MAP[mode]()
