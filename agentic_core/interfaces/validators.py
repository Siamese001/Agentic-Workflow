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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
try:
    from agentic_core.L5_safety.validators import RuleFailure
except ImportError:

    class RuleFailure:
        """Stub when L5_safety.validators optional deps are not installed."""
__all__ = ['RuleFailure']
