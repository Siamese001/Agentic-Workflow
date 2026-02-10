from __future__ import annotations

"""
Reasoning Strategy Pattern - Polymorphic Thought Execution

Replaces if/elif branching with strategy classes for different reasoning modes.
Each strategy encapsulates a distinct reasoning approach (CoT, ToT, ReAct, etc.).
"""


import logging
from abc import ABC, abstractmethod
from typing import Any

Logger = logging.getLogger(__name__)


class ReasoningStrategy(ABC):
    """Base strategy for polymorphic reasoning execution."""

    # guardian: allow-magic-config
    def __init__(self, max_steps: int = 8, config: dict[str, Any] | None = None):
        """
        Initialize reasoning strategy.

        Args:
            max_steps: Maximum reasoning steps
            config: Strategy-specific configuration
        """
        self.max_steps = max_steps
        self.config = config or {}

    @abstractmethod
    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """
        Execute reasoning strategy.

        Args:
            problem: Problem statement
            context: Execution context with state

        Returns:
            List of reasoning steps
        """
        pass

    def _validate_input(self, problem: str, context: dict) -> bool:
        """Validate inputs before execution."""
        return bool(problem) and isinstance(context, dict)


class ChainOfThoughtStrategy(ReasoningStrategy):
    """Chain of Thought (CoT) reasoning - sequential step-by-step."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute CoT reasoning."""
        if not self._validate_input(problem, context):
            return ["Invalid input for CoT"]

        steps = []
        for i in range(self.max_steps):
            step = f"Step {i + 1}: Analyze aspect of '{problem}'"
            steps.append(step)

            # Early termination if solution found
            if context.get("solution_found"):
                break

        return steps


class TreeOfThoughtsStrategy(ReasoningStrategy):
    """Tree of Thoughts (ToT) reasoning - branching exploration."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute ToT reasoning with branching."""
        if not self._validate_input(problem, context):
            return ["Invalid input for ToT"]

        steps = []
        branching_factor = self.config.get("branching_factor", 2)

        # Root level
        steps.append(f"Root: Explore '{problem}'")

        # Branch exploration
        for branch in range(branching_factor):
            for depth in range(min(3, self.max_steps)):
                step = f"Branch {branch + 1}, Depth {depth + 1}: Evaluate path"
                steps.append(step)

        # Evaluation
        steps.append("Evaluate all branches and select best")

        return steps


class ReActStrategy(ReasoningStrategy):
    """ReAct (Reasoning + Acting) - interleaved reasoning and action."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute ReAct reasoning with actions."""
        if not self._validate_input(problem, context):
            return ["Invalid input for ReAct"]

        steps = []

        for i in range(self.max_steps):
            # Reasoning step
            steps.append(f"Thought {i + 1}: Reason about next action for '{problem}'")

            # Action step
            steps.append(f"Action {i + 1}: Execute selected action")

            # Observation step
            steps.append(f"Observation {i + 1}: Observe action result")

            if context.get("goal_achieved"):
                break

        return steps


class ReflectionStrategy(ReasoningStrategy):
    """Reflection reasoning - self-critique and refinement."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute reflection reasoning."""
        if not self._validate_input(problem, context):
            return ["Invalid input for Reflection"]

        steps = []

        # Initial reasoning
        steps.append(f"Initial reasoning: Approach to '{problem}'")

        # Reflection iterations
        for i in range(min(3, self.max_steps)):
            steps.append(f"Reflection {i + 1}: Critique current approach")
            steps.append(f"Refinement {i + 1}: Improve reasoning")

        # Final synthesis
        steps.append("Synthesize refined reasoning")

        return steps


class CritiqueStrategy(ReasoningStrategy):
    """Critique reasoning - adversarial evaluation."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute critique reasoning."""
        if not self._validate_input(problem, context):
            return ["Invalid input for Critique"]

        steps = []

        # Initial proposal
        steps.append(f"Proposal: Solution to '{problem}'")

        # Critique iterations
        for i in range(min(4, self.max_steps)):
            steps.append(f"Critique {i + 1}: Identify weaknesses")
            steps.append(f"Counter-argument {i + 1}: Challenge proposal")
            steps.append(f"Defense {i + 1}: Strengthen proposal")

        # Final verdict
        steps.append("Final evaluation: Robustness assessment")

        return steps


class MultiPathStrategy(ReasoningStrategy):
    """Multi-path reasoning - parallel exploration."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute multi-path reasoning."""
        if not self._validate_input(problem, context):
            return ["Invalid input for MultiPath"]

        steps = []
        num_paths = self.config.get("num_paths", 3)

        # Parallel path exploration
        for path in range(num_paths):
            steps.append(f"Path {path + 1}: Explore alternative approach")

            for step in range(min(3, self.max_steps)):
                steps.append(f"  Path {path + 1}, Step {step + 1}: Develop reasoning")

        # Convergence
        steps.append("Converge paths: Identify common insights")

        return steps


class ReasoningStrategyFactory:
    """Factory for creating reasoning strategies."""

    _strategies = {
        "cot": ChainOfThoughtStrategy,
        "chain_of_thought": ChainOfThoughtStrategy,
        "tot": TreeOfThoughtsStrategy,
        "tree_of_thoughts": TreeOfThoughtsStrategy,
        "react": ReActStrategy,
        "reflection": ReflectionStrategy,
        "critique": CritiqueStrategy,
        "multipath": MultiPathStrategy,
        "multi_path": MultiPathStrategy,
    }

    @classmethod
    # guardian: allow-magic-config
    def create(
        cls,
        strategy_type: str,
        # guardian: allow-magic-config
        max_steps: int = 8,
        config: dict[str, Any] | None = None,
    ) -> ReasoningStrategy:
        """
        Create reasoning strategy instance.

        Args:
            strategy_type: Type of strategy (cot, tot, react, etc.)
            max_steps: Maximum reasoning steps
            config: Strategy-specific configuration

        Returns:
            ReasoningStrategy instance

        Raises:
            ValueError: If strategy type unknown
        """
        strategy_class = cls._strategies.get(strategy_type.lower())

        if not strategy_class:
            raise ValueError(
                f"Unknown reasoning strategy: {strategy_type}. Available: {', '.join(cls._strategies.keys())}",
            )

        return strategy_class(max_steps=max_steps, config=config)

    @classmethod
    def register(cls, name: str, strategy_class: type) -> None:
        """Register custom strategy."""
        cls._strategies[name.lower()] = strategy_class

    @classmethod
    def available_strategies(cls) -> list[str]:
        """Get list of available strategies."""
        return list(cls._strategies.keys())
