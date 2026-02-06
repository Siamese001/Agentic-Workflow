from __future__ import annotations

"""Cognitive Plane Interface - The Brain.

Phase 2 - Pillar 1: Layering Model
Defines the contract for all planning, reasoning, and decision-making.
L1 Cognition: Pure thought, no side effects.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CognitiveCapability(Enum):
    """Capabilities provided by the cognitive plane."""

    PLANNING = "planning"
    REASONING = "reasoning"
    DECISION_MAKING = "decision_making"
    SELF_REFLECTION = "self_reflection"
    TASK_DECOMPOSITION = "task_decomposition"
    STRATEGY_SELECTION = "strategy_selection"


@dataclass
class PlanningRequest:
    """Request for cognitive planning."""

    Task: str
    context: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    capabilities_required: list[CognitiveCapability] = field(default_factory=list)
    max_steps: int = 10
    reasoning_mode: str = "react"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "Task": self.Task,
            "context": self.context,
            "constraints": self.constraints,
            "capabilities_required": [c.value for c in self.capabilities_required],
            "max_steps": self.max_steps,
            "reasoning_mode": self.reasoning_mode,
        }


@dataclass
class PlanningResult:
    """Result from cognitive planning."""

    success: bool
    plan: list[dict[str, Any]]
    reasoning_trace: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "plan": self.plan,
            "reasoning_trace": self.reasoning_trace,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "errors": self.errors,
        }


class ICognitivePlane(ABC):
    """Interface for the Cognitive Plane (Brain).

    The cognitive plane is responsible for:
    - Planning: Breaking down tasks into actionable steps
    - Reasoning: Applying logic and inference
    - Decision Making: Choosing between alternatives
    - Self-Reflection: Evaluating own performance

    L1 Constraint: All methods must be pure (no side effects).
    Outputs are plans and decisions, not actions.
    """

    @abstractmethod
    async def plan(self, request: PlanningRequest) -> PlanningResult:
        """Generate a plan for the given Task.

        Args:
            request: Planning request with Task and context

        Returns:
            PlanningResult with step-by-step plan
        """
        pass

    @abstractmethod
    async def reason(
        self,
        query: str,
        context: dict[str, Any],
        mode: str = "react",
    ) -> dict[str, Any]:
        """Apply reasoning to a query.

        Args:
            query: The question or problem to reason about
            context: Contextual information
            mode: Reasoning mode (react, cot, shotgun, tot)

        Returns:
            Reasoning result with conclusion and trace
        """
        pass

    @abstractmethod
    async def decide(
        self,
        options: list[dict[str, Any]],
        criteria: dict[str, Any],
    ) -> dict[str, Any]:
        """Make a decision between options.

        Args:
            options: List of possible choices
            criteria: Decision criteria and weights

        Returns:
            Selected option with justification
        """
        pass

    @abstractmethod
    async def reflect(
        self,
        execution_trace: list[dict[str, Any]],
        outcome: dict[str, Any],
    ) -> dict[str, Any]:
        """Reflect on execution to identify improvements.

        Args:
            execution_trace: History of actions taken
            outcome: Final result achieved

        Returns:
            Reflection with lessons learned and improvements
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[CognitiveCapability]:
        """Get list of supported cognitive capabilities.

        Returns:
            List of capabilities this plane supports
        """
        pass
