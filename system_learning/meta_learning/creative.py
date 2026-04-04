"""Creative strategy module for meta-learning."""

from typing import Any


class CreativeStrategy:
    """Creative problem-solving strategy for meta-learning."""

    def __init__(self, strategy_type: str = "default"):
        self.strategy_type = strategy_type
        self.applied = False

    def apply(self, context: dict[str, Any]) -> dict[str, Any]:
        """Apply creative strategy to context.

        Args:
            context: Context dict with problem state

        Returns:
            Updated context with creative solution
        """
        self.applied = True
        return {
            **context,
            "creative_applied": True,
            "strategy": self.strategy_type,
            "solution": "Creative approach applied"
        }

    def get_suggestions(self) -> list[str]:
        """Get creative suggestions."""
        return [
            "Consider alternative perspective",
            "Combine existing patterns",
            "Explore edge cases"
        ]


def apply_creative_strategy(context: dict[str, Any], strategy_type: str = "default") -> dict[str, Any]:
    """Apply creative strategy to context.

    Args:
        context: Context dict with problem state
        strategy_type: Type of creative strategy

    Returns:
        Updated context with creative solution
    """
    strategy = CreativeStrategy(strategy_type)
    return strategy.apply(context)


# Alias for convenience
creative_strategy = apply_creative_strategy
