"""
agentic_core/interfaces/routing_types.py

Sovereign routing types interface for apps_* consumption.

Re-exports L0 routing type definitions so apps_* reasoning files
can import from the approved interface boundary (TYPE_CHECKING use).

AUTHORITY CONSTRAINTS:
- Type re-exports only — no routing authority granted
- No access to routing logic or tier selection

USAGE (apps_*):
    from agentic_core.interfaces.routing_types import ReasoningIntensityProfile
"""

from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

try:
    from agentic_core.L0_routing.types.reasoning_intensity_types import ReasoningIntensityProfile
except ImportError:
    ReasoningIntensityProfile = None  # type: ignore[assignment,misc]

__all__ = [
    "ReasoningIntensityProfile",
]
