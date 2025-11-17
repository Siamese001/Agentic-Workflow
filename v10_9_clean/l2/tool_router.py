"""
L2 — Tool Router (v10_9)

Determines which ExecutionAgent should handle a given plan step.

Responsibilities:
    • Inspect plan + step metadata (action, mode, handoff)
    • Return the correct ExecutionAgent instance
    • Never execute tools directly
    • Never mutate state
    • Keep routing deterministic and L2-local
"""

from __future__ import annotations

from typing import Dict, Any

from ..shared.exceptions import OrchestrationError
from ..shared.models import PlanObject
from .l2_tool_base import ExecutionAgent


class ToolRouter:
    """
    Registry-based tool router for L2 execution agents.

    Usage:
        router = ToolRouter(registry={
            "rag": RagExecutor(...),
            "bullet": BulletExecutor(...),
            "drafting": DraftingExecutor(...),
        })

        agent = router.route(step, plan, state)
    """

    def __init__(self, registry: Dict[str, ExecutionAgent] | None = None) -> None:
        # registry maps action/mode → Agent instance
        self.registry = registry or {}

    def register(self, key: str, agent: ExecutionAgent) -> None:
        """
        Register an ExecutionAgent for a routing key.
        Example: "rag" → RagExecutor()
        """
        self.registry[key] = agent

    def route(
        self,
        step: Dict[str, Any],
        plan: PlanObject,
        state: Dict[str, Any],
    ) -> ExecutionAgent:
        """
        Route one plan step to the appropriate ExecutionAgent.

        Routing checks (in order):
            1. step["executor"]
            2. plan.handoff["preferred_executor"]
            3. plan.mode
            4. step.action
        """

        # 1 — Step-specified executor
        explicit = step.get("executor")
        if explicit and explicit in self.registry:
            return self.registry[explicit]

        # 2 — Plan-level preferred executor
        preferred = (plan.handoff or {}).get("preferred_executor")
        if preferred and preferred in self.registry:
            return self.registry[preferred]

        # 3 — Mode-based routing ("rag", "drafting", "strategy", etc.)
        if plan.mode and plan.mode in self.registry:
            return self.registry[plan.mode]

        # 4 — Action-based routing
        action = step.get("action")
        if action and action in self.registry:
            return self.registry[action]

        # If none match → routing failure
        raise OrchestrationError(
            f"No L2 ExecutionAgent found for step={step} "
            f"mode={plan.mode!r} preferred={preferred!r}"
        )
