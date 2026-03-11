"""
Backward-compatibility shim for decorator imports.

DEPRECATED: Import from agentic_core.utils.decorators instead.
Canonical location: agentic_core/utils/decorators.py
"""

from __future__ import annotations

from agentic_core.utils.decorators_util import (  # noqa: F401
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    HEAL_RESULT_SCHEMA,
    F,
    standard_heal,
    standard_heal_async,
)

__all__ = ["F", "HEAL_RESULT_SCHEMA", "standard_heal", "standard_heal_async"]
