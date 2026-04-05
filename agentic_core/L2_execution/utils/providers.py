"""
DEPRECATED: Moved to agentic_core.utils.providers (L_SHARED).

This module now provides a backward-compatible shim. Please update imports to:
    from agentic_core.utils.runners.providers import get_clock, get_random

Reason for move: L0 (routing/foundation) needs clock access but cannot depend
on L2 (execution) per layer gravity rules. Clock providers are cross-cutting
utilities that belong in L_SHARED.

This shim will be removed in a future release.
"""

from __future__ import annotations

import warnings

# Backward-compatible re-exports
from agentic_core.utils.runners.providers import (  # noqa: F401
    ClockProvider,
    FrozenClock,
    MonotonicSequenceClock,
    OsRandom,
    RandomProvider,
    SeededRandom,
    WallClock,
    get_clock,
    get_random,
    reset_providers,
    set_clock,
    set_random,
)

warnings.warn(
    "agentic_core.L2_execution.providers is deprecated. Import from agentic_core.utils.providers instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ClockProvider",
    "RandomProvider",
    "WallClock",
    "OsRandom",
    "FrozenClock",
    "SeededRandom",
    "MonotonicSequenceClock",
    "get_clock",
    "get_random",
    "set_clock",
    "set_random",
    "reset_providers",
]
