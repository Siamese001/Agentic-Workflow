from __future__ import annotations
'\nReasoning Strategy Pattern - Polymorphic Thought Execution\n\nReplaces if/elif branching with strategy classes for different reasoning modes.\nEach strategy encapsulates a distinct reasoning approach (CoT, ToT, ReAct, etc.).\n'
import logging
from abc import ABC, abstractmethod
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class ReasoningStrategy(ABC):
    """Base strategy for polymorphic reasoning execution."""

    # guardian: allow-magic-config
    def __init__(self, max_steps: int=8, config: dict[str, Any] | None=None):
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
            return ['Invalid input for CoT']
        steps = []
        for i in range(self.max_steps):
            step = f"Step {i + 1}: Analyze aspect of '{problem}'"
            steps.append(step)
            if context.get('solution_found'):
                break
        return steps

class TreeOfThoughtsStrategy(ReasoningStrategy):
    """Tree of Thoughts (ToT) reasoning - branching exploration."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute ToT reasoning with branching."""
        if not self._validate_input(problem, context):
            return ['Invalid input for ToT']
        steps = []
        branching_factor = self.config.get('branching_factor', 2)
        steps.append(f"Root: Explore '{problem}'")
        for branch in range(branching_factor):
            for depth in range(min(3, self.max_steps)):
                step = f'Branch {branch + 1}, Depth {depth + 1}: Evaluate path'
                steps.append(step)
        steps.append('Evaluate all branches and select best')
        return steps

class ReActStrategy(ReasoningStrategy):
    """ReAct (Reasoning + Acting) - interleaved reasoning and action."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute ReAct reasoning with actions."""
        if not self._validate_input(problem, context):
            return ['Invalid input for ReAct']
        steps = []
        for i in range(self.max_steps):
            steps.append(f"Thought {i + 1}: Reason about next action for '{problem}'")
            steps.append(f'Action {i + 1}: Execute selected action')
            steps.append(f'Observation {i + 1}: Observe action result')
            if context.get('goal_achieved'):
                break
        return steps

class ReflectionStrategy(ReasoningStrategy):
    """Reflection reasoning - self-critique and refinement."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute reflection reasoning."""
        if not self._validate_input(problem, context):
            return ['Invalid input for Reflection']
        steps = []
        steps.append(f"Initial reasoning: Approach to '{problem}'")
        for i in range(min(3, self.max_steps)):
            steps.append(f'Reflection {i + 1}: Critique current approach')
            steps.append(f'Refinement {i + 1}: Improve reasoning')
        steps.append('Synthesize refined reasoning')
        return steps

class CritiqueStrategy(ReasoningStrategy):
    """Critique reasoning - adversarial evaluation."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute critique reasoning."""
        if not self._validate_input(problem, context):
            return ['Invalid input for Critique']
        steps = []
        steps.append(f"Proposal: Solution to '{problem}'")
        for i in range(min(4, self.max_steps)):
            steps.append(f'Critique {i + 1}: Identify weaknesses')
            steps.append(f'Counter-argument {i + 1}: Challenge proposal')
            steps.append(f'Defense {i + 1}: Strengthen proposal')
        steps.append('Final evaluation: Robustness assessment')
        return steps

class MultiPathStrategy(ReasoningStrategy):
    """Multi-path reasoning - parallel exploration."""

    def execute(self, problem: str, context: dict[str, Any]) -> list[str]:
        """Execute multi-path reasoning."""
        if not self._validate_input(problem, context):
            return ['Invalid input for MultiPath']
        steps = []
        num_paths = self.config.get('num_paths', 3)
        for path in range(num_paths):
            steps.append(f'Path {path + 1}: Explore alternative approach')
            for step in range(min(3, self.max_steps)):
                steps.append(f'  Path {path + 1}, Step {step + 1}: Develop reasoning')
        steps.append('Converge paths: Identify common insights')
        return steps

class ReasoningStrategyFactory:
    """Factory for creating reasoning strategies."""
    _strategies = {'cot': ChainOfThoughtStrategy, 'chain_of_thought': ChainOfThoughtStrategy, 'tot': TreeOfThoughtsStrategy, 'tree_of_thoughts': TreeOfThoughtsStrategy, 'react': ReActStrategy, 'reflection': ReflectionStrategy, 'critique': CritiqueStrategy, 'multipath': MultiPathStrategy, 'multi_path': MultiPathStrategy}

    @classmethod
    # guardian: allow-magic-config
    def create(cls, strategy_type: str, max_steps: int=8, config: dict[str, Any] | None=None) -> ReasoningStrategy:
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
            raise ValueError(f"Unknown reasoning strategy: {strategy_type}. Available: {', '.join(cls._strategies.keys())}")
        return strategy_class(max_steps=max_steps, config=config)

    @classmethod
    def register(cls, name: str, strategy_class: type) -> None:
        """Register custom strategy."""
        cls._strategies[name.lower()] = strategy_class

    @classmethod
    def available_strategies(cls) -> list[str]:
        """Get list of available strategies."""
        return list(cls._strategies.keys())
