"""
agentic_core/interfaces/orchestration.py

Sovereign Orchestration interfaces for L1_cognition consumption.

Re-exports orchestration components so L1_cognition can
access routing and orchestration services without directly importing from L3_orchestration.

AUTHORITY CONSTRAINTS:
- Orchestration components provide routing and coordination services
- No direct execution authority through these interfaces
- All routing decisions are recorded for audit

USAGE (L1_cognition):
    from agentic_core.interfaces.orchestration import (
        ActionRouter,
        # Add other orchestration components as needed
    )
"""

from __future__ import annotations

try:
    from agentic_core.L3_orchestration.reasoning.engines.action_router import ActionRouter
# guardian: allow-silent-swallow - optional dependency
except ImportError:
    ActionRouter = None
__all__ = ["ActionRouter"]
