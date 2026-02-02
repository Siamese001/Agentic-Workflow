"""Reasoning strategy router for selecting appropriate reasoning mode.

Phase 1 - Pillar 6: Reasoning models (Structured Reasoning)
Routes tasks to appropriate reasoning strategies (ReAct, CoT, etc.)
"""

import logging

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks for reasoning strategy selection."""

    TOOL_USE = "tool_use"
    QUESTION_ANSWERING = "qa"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    UNKNOWN = "unknown"


class ReasoningRouter:
    """Routes tasks to appropriate reasoning strategies.

    Implements a simple strategy selector that uses ReAct for tasks
    requiring tool use and simpler approaches for basic Q&A or classification.
    """

    def __init__(
        self,
        default_mode: ReasoningMode = ReasoningMode.REACT,
        enable_adaptive_routing: bool = True,
    ):
        """Initialize reasoning router.

        Args:
            default_mode: Default reasoning mode if no specific match
            enable_adaptive_routing: Enable adaptive strategy selection
        """
        self.default_mode = default_mode
        self.enable_adaptive_routing = enable_adaptive_routing

        self._strategy_map = {
            TaskType.TOOL_USE: ReasoningMode.REACT,
            TaskType.QUESTION_ANSWERING: ReasoningMode.CHAIN_OF_THOUGHT,
            TaskType.CLASSIFICATION: ReasoningMode.SHOTGUN,
            TaskType.GENERATION: ReasoningMode.CHAIN_OF_THOUGHT,
            TaskType.ANALYSIS: ReasoningMode.REACT,
            TaskType.PLANNING: ReasoningMode.TREE_OF_THOUGHTS,
            TaskType.UNKNOWN: self.default_mode,
        }

    def classify_task(self, task: str, context: dict[str, Any] | None = None) -> TaskType:
        """Classify task type based on content and context.

        Args:
            task: The task description
            context: Optional context with hints

        Returns:
            TaskType classification
        """
        if context and "task_type" in context:
            try:
                return TaskType(context["task_type"])
            except ValueError:
                pass

        task_lower = task.lower()

        tool_indicators = [
            "search",
            "retrieve",
            "lookup",
            "find",
            "fetch",
            "call",
            "execute",
            "run",
        ]

        qa_indicators = [
            "what is",
            "who is",
            "when did",
            "where is",
            "why",
            "how",
            "explain",
            "describe",
        ]

        classification_indicators = [
            "classify",
            "categorize",
            "is this",
            "does this",
            "true or false",
            "yes or no",
        ]

        planning_indicators = [
            "plan",
            "strategy",
            "approach",
            "steps to",
            "how to",
        ]

        for indicator in tool_indicators:
            if indicator in task_lower:
                return TaskType.TOOL_USE

        for indicator in classification_indicators:
            if indicator in task_lower:
                return TaskType.CLASSIFICATION

        for indicator in planning_indicators:
            if indicator in task_lower:
                return TaskType.PLANNING

        for indicator in qa_indicators:
            if indicator in task_lower:
                return TaskType.QUESTION_ANSWERING

        if len(task.split()) > 50:
            return TaskType.ANALYSIS

        return TaskType.UNKNOWN

    def select_strategy(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> ReasoningMode:
        """Select appropriate reasoning strategy for task.

        Args:
            task: The task to solve
            context: Optional context with hints

        Returns:
            Selected ReasoningMode
        """
        task_type = self.classify_task(task, context)

        strategy = self._strategy_map.get(task_type, self.default_mode)

        logger.info(
            "reasoning_strategy_selected",
            extra={
                "task_type": task_type.value,
                "strategy": strategy.value,
                "task_preview": task[:100],
            },
        )

        return strategy

    def override_strategy(self, task_type: TaskType, mode: ReasoningMode) -> None:
        """Override strategy mapping for a task type.

        Args:
            task_type: The task type to override
            mode: The reasoning mode to use
        """
        self._strategy_map[task_type] = mode

        logger.info(
            "reasoning_strategy_override",
            extra={
                "task_type": task_type.value,
                "new_strategy": mode.value,
            },
        )


def select_reasoning_strategy(
    task: str,
    context: dict[str, Any] | None = None,
    router: ReasoningRouter | None = None,
) -> ReasoningMode:
    """Convenience function to select reasoning strategy.

    Args:
        task: The task to solve
        context: Optional context
        router: Optional custom router (creates default if None)

    Returns:
        Selected ReasoningMode
    """
    if router is None:
        router = ReasoningRouter()

    return router.select_strategy(task, context)
