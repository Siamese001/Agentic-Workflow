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

try:
    from agentic_core.L0_routing.types.reasoning_intensity_types import ReasoningIntensityProfile
# guardian: allow-silent-swallow - optional dependency
except ImportError:
    ReasoningIntensityProfile = None
__all__ = ["ReasoningIntensityProfile"]
