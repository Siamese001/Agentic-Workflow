"""
Decorators - canonical re-export shim.

The implementation lives in agentic_core.utils.decorators_util.
This module re-exports for callers using ``from agentic_core.utils.schemas.decorators_shim_util import ...``.
"""

from agentic_core.utils.schemas.decorators_util import (  # noqa: F401
    HEAL_RESULT_SCHEMA,
    F,
    standard_heal,
    standard_heal_async,
)

__all__ = [
    "HEAL_RESULT_SCHEMA",
    "F",
    "standard_heal",
    "standard_heal_async",
]
