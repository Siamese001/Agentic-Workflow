# routing.py
"""
L3 — ExecutionEngine Router (v10_9)

Maps L1 plan modes (strategy, rag, drafting) to L2 ExecutionEngines.
This decouples L3 from tool-specific logic inside L2.
"""

from __future__ import annotations

from typing import Dict, Optional

from ..shared.models import PlanObject
from ..shared.exceptions import OrchestrationError
from ..l2.l2_execution import ExecutionEngine


class ExecutionEngineRouter:
    """Maps plan.mode → ExecutionEngine."""

    def __init__(self, registry: Optional[Dict[str, ExecutionEngine]] = None) -> None:
        self.registry = registry or {}

    def register(self, mode: str, engine: ExecutionEngine) -> None:
        self.registry[mode] = engine

    def resolve(self, plan: PlanObject) -> Optional[ExecutionEngine]:
        mode = (plan.mode or "").lower()
        return self.registry.get(mode)
