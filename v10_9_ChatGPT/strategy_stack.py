"""L1 strategy planning logic."""
from __future__ import annotations

from typing import Dict

from .models import StrategyPlan
from .services import ServiceBundle
from .telemetry import log_event


class StrategyStack:
    def __init__(self, services: ServiceBundle) -> None:
        self.services = services

    def plan(self, goal: str) -> Dict[str, str | StrategyPlan]:
        log_event("strategy_plan", {"goal": goal})
        steps = ["analyze requirements", "collect evidence", "draft response"]
        plan = StrategyPlan(summary=goal, steps=steps)
        return {"plan": plan}
