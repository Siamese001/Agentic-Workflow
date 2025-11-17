"""
L2 — Tool Execution Base (v10_9)

Defines the abstract interface that all L2 execution agents must implement.

Responsibilities:
    • Consume PlanObject from L1
    • Execute a single tool, model call, or action
    • Produce an ExecutionResult (NOT a state patch)
    • Never mutate state directly (L3+L4 handle that)
    • Provide a deterministic, pure interface
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..shared.models import PlanObject, ExecutionResult


class ExecutionAgent(ABC):
    """
    Abstract executor interface for L2 agents.

    Executes a plan step (NOT entire workflow).
    L3 orchestrator feeds it plan fragments one step at a time.
    """

    @abstractmethod
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
        """
        Execute a plan fragment against the current state.

        MUST:
            • Not mutate state directly
            • Return an ExecutionResult
            • Contain zero business logic outside execution
        """
        raise NotImplementedError
