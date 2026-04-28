"""Backward-compatibility re-export shim.

The canonical SSOT for these constants moved to
``agentic_core.L0_routing.config.pipeline_constants`` to fix a P0 layer
violation: agentic_core modules cannot import from L_APP. This shim
preserves every ``apps_*`` callsite that still imports from the old
location.

New code should import directly from
``agentic_core.L0_routing.config.pipeline_constants``.
"""

from agentic_core.L0_routing.config.pipeline_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

__all__ = [
    "MAX_RETRIES",
    "DEFAULT_SLEEP",
    "THRESHOLD",
    "BUFFER_SIZE",
    "BATCH_SIZE",
    "MAX_DEPTH",
    "MAX_FILES",
    "DEFAULT_TIMEOUT",
]
