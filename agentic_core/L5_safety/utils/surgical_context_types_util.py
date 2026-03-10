"""
surgical_context_types - canonical re-export shim.

The implementation lives in agentic_core.L5_safety.types.surgical_context_types.
This module re-exports for relative imports inside ``agentic_core.L5_safety.utils.*``.
"""

from agentic_core.L5_safety.types.surgical_context_types import (  # noqa: F401
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)

__all__ = [
    "ASTCoordinate",
    "SurgicalContext",
    "ViolationConstraint",
]
