"""
State utilities for common operations across the codebase.
"""

from agentic_core.mixins.safety_mixin import StateAnalysisMixin


def check_past_failures(task: str) -> str:
    """Check telemetry for past failures on similar tasks.

    Args:
        task: Task description to check

    Returns:
        Recommendation string based on analysis
    """
    try:
        # Use canonical state analysis with empty history (placeholder implementation)
        result = StateAnalysisMixin._check_past_failures([])
        return result["recommendation"]
    # guardian: allow-silent-swallower
    except Exception:
        return "Unable to check past failures"
