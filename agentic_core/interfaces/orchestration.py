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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Import from L3_orchestration where orchestration components are located
# Note: This assumes ActionRouter exists - adjust if needed
try:
    from agentic_core.L3_orchestration.engines.action_router import ActionRouter
except ImportError:
    # Fallback if ActionRouter doesn't exist yet
    ActionRouter = None

__all__ = [
    "ActionRouter",
]
