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
    from agentic_core.interfaces.safety_shim import (
        UnifiedCSTHealer,
        # Add other safety components as needed
    )
"""

from __future__ import annotations

try:
    from agentic_core.L5_safety.validators.unified_cst_healer import UnifiedCSTHealer
# guardian: allow-silent-swallow - optional dependency
except ImportError:
    UnifiedCSTHealer = None
__all__ = ["UnifiedCSTHealer"]
