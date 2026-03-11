"""
State utilities for common operations across the codebase.
"""

from agentic_core.mixins.safety_mixin import StateAnalysisMixin


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        # Expected state analysis errors
        logging.getLogger(__name__).warning(f"State analysis error: {e}")
        return "Unable to check past failures"
    except (OSError, RuntimeError, MemoryError) as e:
        # Critical state analysis errors
        logging.getLogger(__name__).error(f"Critical state analysis error: {e}")
        return "Unable to check past failures"
