"""
L2 — Tool Execution Base

Contracts for execution agents that consume L1 plans and emit state patches.
Actual tool orchestration lives in concrete subclasses; this base focuses on
interfaces only.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any

from utils_types import PlanObject, StatePatch


class ExecutionAgent(ABC):
    """Abstract executor interface for L2 agents."""

    @abstractmethod
    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        """Execute a plan against the current state and return a state patch."""
        raise NotImplementedError
