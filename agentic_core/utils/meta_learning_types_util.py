"""
meta_learning_types - canonical re-export shim.

The implementation lives in agentic_core.L5_safety.types.meta_learning_types.
This module re-exports for callers using
``from agentic_core.utils.meta_learning_types_util import ...``.
"""

from agentic_core.L5_safety.types.meta_learning_types import (  # noqa: F401
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    LearningContext,
    LearningResult,
    MetaLearningProtocol,
)

__all__ = [
    "LearningContext",
    "LearningResult",
    "MetaLearningProtocol",
]
