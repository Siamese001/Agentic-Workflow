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
        result = StateAnalysisMixin._check_past_failures([])
        return result["recommendation"]
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logging.getLogger(__name__).warning(f"State analysis error: {e}")
        return "Unable to check past failures"
    except (OSError, RuntimeError, MemoryError) as e:
        logging.getLogger(__name__).error(f"Critical state analysis error: {e}")
        return "Unable to check past failures"
