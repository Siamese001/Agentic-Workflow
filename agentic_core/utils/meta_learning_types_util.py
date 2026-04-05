"""
meta_learning_types - canonical re-export shim.

The implementation lives in agentic_core.L5_safety.types.meta_learning_types.
This module re-exports for callers using
``from agentic_core.utils.meta_learning_types_util import ...``.
"""

from agentic_core.L5_safety.types.meta_learning_types import (  # noqa: F401
    LearningContext,
    LearningResult,
    MetaLearningProtocol,
)

__all__ = [
    "LearningContext",
    "LearningResult",
    "MetaLearningProtocol",
]
