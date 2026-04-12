"""
Backward compatibility module for decorators.

This module provides backward compatibility for imports expecting
agentic_core.utils.decorators by re-exporting from decorators_util.
"""

from .decorators_util import (
    HEAL_RESULT_SCHEMA,
    TimeoutError,
    standard_heal,
    standard_heal_async,
    timeout,
)

__all__ = [
    "HEAL_RESULT_SCHEMA",
    "TimeoutError",
    "standard_heal",
    "standard_heal_async",
    "timeout",
]
