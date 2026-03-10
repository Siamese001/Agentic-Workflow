"""
agentic_core/interfaces/validators.py

Sovereign validators interface for apps_* consumption.

Re-exports validator types from L5_safety so apps_* reasoning files
can import from the approved interface boundary.

AUTHORITY CONSTRAINTS:
- Type re-exports only — no validation execution authority
- No access to enforcement logic

USAGE (apps_*):
    from agentic_core.interfaces.validators import RuleFailure
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
    from agentic_core.L5_safety.validators import RuleFailure
except ImportError:

    class RuleFailure:  # type: ignore[no-redef]
        """Stub when L5_safety.validators optional deps are not installed."""


__all__ = [
    "RuleFailure",
]
