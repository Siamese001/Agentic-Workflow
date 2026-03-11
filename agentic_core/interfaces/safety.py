"""
agentic_core/interfaces/safety.py

Sovereign Safety and Validation interfaces for L1_cognition consumption.

Re-exports safety and validation components so L1_cognition can
access validation services without directly importing from L5_safety.

AUTHORITY CONSTRAINTS:
- Safety components provide validation and enforcement services
- No direct safety bypass through these interfaces
- All validation decisions are recorded for audit

USAGE (L1_cognition):
    from agentic_core.interfaces.safety import (
        UnifiedCSTHealer,
        # Add other safety components as needed
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

# Import from L5_safety where safety components are located
try:
    from agentic_core.L5_safety.validators.unified_cst_healer import UnifiedCSTHealer
except ImportError:
    # Fallback if UnifiedCSTHealer doesn't exist yet
    UnifiedCSTHealer = None

__all__ = [
    "UnifiedCSTHealer",
]
